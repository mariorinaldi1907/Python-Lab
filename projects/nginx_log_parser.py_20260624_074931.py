"""
Date: 2026-06-24
Wrote a parser for nginx access logs that extracts IPs, status codes, and endpoints so I can quickly analyze traffic patterns without grep-ing through gigabytes of logs.
"""

#!/usr/bin/env python3
"""
Nginx access log parser with basic traffic analysis.

Parses standard nginx combined log format and gives me quick insights
into what's hitting my servers. I got tired of manually grep-ing logs
every time I wanted to check for suspicious traffic or see which endpoints
are getting hammered.
"""

import re
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Optional


class LogEntry:
    """Represents a single nginx access log entry."""
    
    def __init__(self, ip: str, timestamp: str, method: str, endpoint: str, 
                 status: int, size: int, user_agent: str):
        self.ip = ip
        self.timestamp = timestamp
        self.method = method
        self.endpoint = endpoint
        self.status = status
        self.size = size
        self.user_agent = user_agent
    
    def __repr__(self):
        return f"LogEntry({self.ip}, {self.method} {self.endpoint}, {self.status})"


class NginxLogParser:
    """
    Parser for nginx combined log format.
    
    The regex pattern matches the standard nginx combined format:
    IP - - [timestamp] "METHOD /path HTTP/version" status size "referer" "user-agent"
    """
    
    # This regex handles the combined log format I use on my servers
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d\.]+) - - \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\w+) (?P<endpoint>[^\s]+) HTTP/[\d\.]+" '
        r'(?P<status>\d+) (?P<size>\d+) '
        r'"[^"]*" "(?P<user_agent>[^"]*)"'
    )
    
    def __init__(self):
        self.entries: List[LogEntry] = []
    
    def parse_line(self, line: str) -> Optional[LogEntry]:
        """
        Parse a single log line into a LogEntry object.
        
        Returns None if the line doesn't match the expected format,
        which happens sometimes with malformed requests.
        """
        match = self.LOG_PATTERN.match(line)
        if not match:
            return None
        
        data = match.groupdict()
        return LogEntry(
            ip=data['ip'],
            timestamp=data['timestamp'],
            method=data['method'],
            endpoint=data['endpoint'],
            status=int(data['status']),
            size=int(data['size']),
            user_agent=data['user_agent']
        )
    
    def parse_file(self, filepath: str) -> None:
        """Load and parse an entire log file."""
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                entry = self.parse_line(line.strip())
                if entry:
                    self.entries.append(entry)
    
    def parse_lines(self, lines: List[str]) -> None:
        """Parse a list of log lines (useful for testing or streaming)."""
        for line in lines:
            entry = self.parse_line(line.strip())
            if entry:
                self.entries.append(entry)
    
    def get_status_summary(self) -> Dict[int, int]:
        """Count how many times each status code appears."""
        return dict(Counter(entry.status for entry in self.entries))
    
    def get_top_ips(self, n: int = 10) -> List[tuple]:
        """Find the most frequent IP addresses (useful for spotting bots/attacks)."""
        ip_counter = Counter(entry.ip for entry in self.entries)
        return ip_counter.most_common(n)
    
    def get_top_endpoints(self, n: int = 10) -> List[tuple]:
        """Find the most requested endpoints."""
        endpoint_counter = Counter(entry.endpoint for entry in self.entries)
        return endpoint_counter.most_common(n)
    
    def get_error_endpoints(self) -> Dict[str, int]:
        """
        Find endpoints that frequently return errors (4xx or 5xx).
        
        This helps me quickly spot broken links or backend issues.
        """
        error_endpoints = defaultdict(int)
        for entry in self.entries:
            if entry.status >= 400:
                error_endpoints[entry.endpoint] += 1
        return dict(sorted(error_endpoints.items(), key=lambda x: x[1], reverse=True))
    
    def get_traffic_by_method(self) -> Dict[str, int]:
        """Break down traffic by HTTP method."""
        return dict(Counter(entry.method for entry in self.entries))
    
    def get_total_bandwidth(self) -> int:
        """Calculate total bytes transferred."""
        return sum(entry.size for entry in self.entries)


def format_bytes(size: int) -> str:
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


if __name__ == "__main__":
    # Sample nginx log lines for demo purposes
    sample_logs = [
        '192.168.1.100 - - [15/Jan/2024:10:23:45 +0000] "GET /api/users HTTP/1.1" 200 1234 "-" "Mozilla/5.0"',
        '192.168.1.101 - - [15/Jan/2024:10:24:12 +0000] "POST /api/login HTTP/1.1" 200 567 "-" "curl/7.68.0"',
        '192.168.1.100 - - [15/Jan/2024:10:25:33 +0000] "GET /api/users HTTP/1.1" 200 1234 "-" "Mozilla/5.0"',
        '10.0.0.50 - - [15/Jan/2024:10:26:01 +0000] "GET /nonexistent HTTP/1.1" 404 162 "-" "bot/1.0"',
        '10.0.0.50 - - [15/Jan/2024:10:26:05 +0000] "GET /admin HTTP/1.1" 403 95 "-" "bot/1.0"',
        '192.168.1.102 - - [15/Jan/2024:10:27:18 +0000] "GET /api/products HTTP/1.1" 200 8192 "-" "PostmanRuntime/7.26.8"',
        '192.168.1.100 - - [15/Jan/2024:10:28:42 +0000] "GET /api/users HTTP/1.1" 200 1234 "-" "Mozilla/5.0"',
        '192.168.1.103 - - [15/Jan/2024:10:29:55 +0000] "POST /api/orders HTTP/1.1" 500 234 "-" "Mozilla/5.0"',
    ]
    
    print("=== Nginx Log Parser Demo ===\n")
    
    parser = NginxLogParser()
    parser.parse_lines(sample_logs)
    
    print(f"Parsed {len(parser.entries)} log entries\n")
    
    print("Status Code Summary:")
    for status, count in sorted(parser.get_status_summary().items()):
        print(f"  {status}: {count} requests")
    
    print("\nTop IP Addresses:")
    for ip, count in parser.get_top_ips(5):
        print(f"  {ip}: {count} requests")
    
    print("\nTop Endpoints:")
    for endpoint, count in parser.get_top_endpoints(5):
        print(f"  {endpoint}: {count} requests")
    
    print("\nError Endpoints (4xx/5xx):")
    error_endpoints = parser.get_error_endpoints()
    if error_endpoints:
        for endpoint, count in list(error_endpoints.items())[:5]:
            print(f"  {endpoint}: {count} errors")
    else:
        print("  No errors found!")
    
    print("\nTraffic by HTTP Method:")
    for method, count in parser.get_traffic_by_method().items():
        print(f"  {method}: {count} requests")
    
    print(f"\nTotal Bandwidth: {format_bytes(parser.get_total_bandwidth())}")