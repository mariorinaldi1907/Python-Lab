"""
Date: 2026-07-12
Built a parser for nginx access logs that breaks down traffic patterns, response codes, and user agents — helps me analyze my VPS logs without installing anything.
"""

#!/usr/bin/env python3
"""
nginx access log parser - analyzes common nginx log formats
Parses lines, extracts fields, and provides stats about traffic patterns.
"""

import re
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Optional


class LogEntry:
    """
    Represents a single parsed nginx log entry.
    Stores the important fields I care about when debugging traffic issues.
    """
    
    def __init__(self, ip: str, timestamp: str, method: str, path: str, 
                 status: int, size: int, user_agent: str):
        self.ip = ip
        self.timestamp = timestamp
        self.method = method
        self.path = path
        self.status = status
        self.size = size
        self.user_agent = user_agent
    
    def __repr__(self):
        return f"LogEntry({self.ip}, {self.method} {self.path}, status={self.status})"


class NginxLogParser:
    """
    Parser for nginx access logs in the combined format.
    
    The regex handles the standard combined log format which looks like:
    IP - - [timestamp] "METHOD /path HTTP/1.1" status size "referer" "user-agent"
    
    I built this because I got tired of grepping through logs manually
    when trying to figure out which endpoints were getting hammered.
    """
    
    # This regex matches the nginx combined log format
    # Breaking it down: IP, then skip two fields, timestamp in brackets,
    # request in quotes, status, size, referer (ignored), and user agent
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d\.]+) - - \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\w+) (?P<path>[^\s]+) HTTP/[\d\.]+" '
        r'(?P<status>\d+) (?P<size>\d+) '
        r'"[^"]*" "(?P<user_agent>[^"]*)"'
    )
    
    def __init__(self):
        self.entries: List[LogEntry] = []
    
    def parse_line(self, line: str) -> Optional[LogEntry]:
        """
        Parse a single log line into a LogEntry object.
        Returns None if the line doesn't match the expected format.
        """
        match = self.LOG_PATTERN.match(line)
        if not match:
            return None
        
        data = match.groupdict()
        
        # Convert numeric fields - I used to forget this and get string comparisons
        try:
            status = int(data['status'])
            size = int(data['size'])
        except ValueError:
            return None
        
        return LogEntry(
            ip=data['ip'],
            timestamp=data['timestamp'],
            method=data['method'],
            path=data['path'],
            status=status,
            size=size,
            user_agent=data['user_agent']
        )
    
    def parse_file(self, filepath: str) -> int:
        """
        Parse an entire log file and store entries.
        Returns the number of successfully parsed lines.
        """
        parsed_count = 0
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                entry = self.parse_line(line.strip())
                if entry:
                    self.entries.append(entry)
                    parsed_count += 1
        
        return parsed_count
    
    def get_status_distribution(self) -> Counter:
        """Count how many times each HTTP status code appears."""
        return Counter(entry.status for entry in self.entries)
    
    def get_top_paths(self, n: int = 10) -> List[tuple]:
        """Get the most frequently accessed paths."""
        path_counter = Counter(entry.path for entry in self.entries)
        return path_counter.most_common(n)
    
    def get_top_ips(self, n: int = 10) -> List[tuple]:
        """
        Get the IPs making the most requests.
        Useful for spotting potential scrapers or attacks.
        """
        ip_counter = Counter(entry.ip for entry in self.entries)
        return ip_counter.most_common(n)
    
    def get_traffic_by_method(self) -> Counter:
        """Break down traffic by HTTP method (GET, POST, etc)."""
        return Counter(entry.method for entry in self.entries)
    
    def get_total_bandwidth(self) -> int:
        """Calculate total bytes transferred."""
        return sum(entry.size for entry in self.entries)
    
    def get_error_entries(self) -> List[LogEntry]:
        """
        Get all entries with 4xx or 5xx status codes.
        These are the ones I actually need to investigate.
        """
        return [entry for entry in self.entries if entry.status >= 400]


def format_bytes(bytes_count: int) -> str:
    """Convert bytes to human-readable format (KB, MB, GB)."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.2f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.2f} PB"


if __name__ == "__main__":
    # Demo with sample nginx log data
    # These are realistic log lines I've seen on my servers
    sample_log = """127.0.0.1 - - [15/Jan/2024:10:23:45 +0000] "GET /api/users HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
192.168.1.100 - - [15/Jan/2024:10:24:12 +0000] "POST /api/login HTTP/1.1" 200 567 "-" "curl/7.68.0"
10.0.0.50 - - [15/Jan/2024:10:25:33 +0000] "GET /static/app.js HTTP/1.1" 304 0 "-" "Mozilla/5.0 Chrome/120.0"
127.0.0.1 - - [15/Jan/2024:10:26:01 +0000] "GET /api/posts HTTP/1.1" 200 8912 "-" "Mozilla/5.0"
192.168.1.100 - - [15/Jan/2024:10:27:15 +0000] "GET /nonexistent HTTP/1.1" 404 162 "-" "Mozilla/5.0"
10.0.0.50 - - [15/Jan/2024:10:28:22 +0000] "POST /api/data HTTP/1.1" 500 89 "-" "Python-requests/2.28"
127.0.0.1 - - [15/Jan/2024:10:29:45 +0000] "GET /api/users HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
"""
    
    # Write sample data to a temp file for testing
    with open('/tmp/nginx_sample.log', 'w') as f:
        f.write(sample_log)
    
    # Parse and analyze
    parser = NginxLogParser()
    parsed_count = parser.parse_file('/tmp/nginx_sample.log')
    
    print(f"=== Nginx Log Analysis ===\n")
    print(f"Total entries parsed: {parsed_count}\n")
    
    print("Status Code Distribution:")
    for status, count in sorted(parser.get_status_distribution().items()):
        print(f"  {status}: {count}")
    
    print(f"\nHTTP Methods:")
    for method, count in parser.get_traffic_by_method().items():
        print(f"  {method}: {count}")
    
    print(f"\nTop Paths:")
    for path, count in parser.get_top_paths(5):
        print(f"  {path}: {count} requests")
    
    print(f"\nTop IPs:")
    for ip, count in parser.get_top_ips(5):
        print(f"  {ip}: {count} requests")
    
    print(f"\nTotal Bandwidth: {format_bytes(parser.get_total_bandwidth())}")
    
    errors = parser.get_error_entries()
    if errors:
        print(f"\nErrors Found ({len(errors)}):")
        for entry in errors:
            print(f"  {entry.status} - {entry.method} {entry.path} from {entry.ip}")