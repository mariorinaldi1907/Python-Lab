"""
Date: 2026-08-18
Created a parser for nginx access logs because I got tired of grepping through massive log files manually — it aggregates requests by status code, IP, and calculates total bandwidth.
"""

#!/usr/bin/env python3
"""
Nginx access log parser with basic analytics.

Parses standard nginx log formats (common and combined) and provides
summary statistics. I built this after realizing I was constantly
ssh-ing into servers just to run basic awk commands on logs.
"""

import re
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Optional


class NginxLogEntry:
    """Represents a single parsed nginx log line."""
    
    def __init__(self, ip: str, timestamp: str, method: str, path: str, 
                 status: int, size: int, referrer: str = "-", user_agent: str = "-"):
        self.ip = ip
        self.timestamp = timestamp
        self.method = method
        self.path = path
        self.status = status
        self.size = size  # bytes transferred
        self.referrer = referrer
        self.user_agent = user_agent
    
    def __repr__(self):
        return f"<LogEntry {self.method} {self.path} - {self.status}>"


class NginxLogParser:
    """
    Parses nginx access logs and computes basic statistics.
    
    Handles both common and combined log formats. The regex is a bit gnarly
    but it's faster than splitting and dealing with quoted strings manually.
    """
    
    # This regex handles both common and combined formats
    # Group breakdown: IP, timestamp, method, path, protocol, status, size, referrer, user_agent
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d\.]+) - - \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\w+) (?P<path>[^\s]+) [^"]*" '
        r'(?P<status>\d+) (?P<size>\d+|-)'
        r'(?: "(?P<referrer>[^"]*)" "(?P<user_agent>[^"]*)")?'
    )
    
    def __init__(self):
        self.entries: List[NginxLogEntry] = []
        self.parse_errors = 0
    
    def parse_line(self, line: str) -> Optional[NginxLogEntry]:
        """
        Parse a single log line into a LogEntry object.
        
        Returns None if the line doesn't match expected format — happens
        with malformed requests or when nginx logs errors inline.
        """
        match = self.LOG_PATTERN.match(line.strip())
        if not match:
            self.parse_errors += 1
            return None
        
        data = match.groupdict()
        
        # Size can be "-" if no bytes were sent (e.g., some errors)
        size = 0 if data['size'] == '-' else int(data['size'])
        
        return NginxLogEntry(
            ip=data['ip'],
            timestamp=data['timestamp'],
            method=data['method'],
            path=data['path'],
            status=int(data['status']),
            size=size,
            referrer=data.get('referrer', '-'),
            user_agent=data.get('user_agent', '-')
        )
    
    def parse_file(self, filename: str) -> None:
        """Parse an entire log file, storing all valid entries."""
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                entry = self.parse_line(line)
                if entry:
                    self.entries.append(entry)
    
    def get_status_distribution(self) -> Counter:
        """Count requests by HTTP status code."""
        return Counter(entry.status for entry in self.entries)
    
    def get_top_ips(self, n: int = 10) -> List[tuple]:
        """Return the top N IPs by request count."""
        ip_counts = Counter(entry.ip for entry in self.entries)
        return ip_counts.most_common(n)
    
    def get_top_paths(self, n: int = 10) -> List[tuple]:
        """Return the most frequently requested paths."""
        path_counts = Counter(entry.path for entry in self.entries)
        return path_counts.most_common(n)
    
    def get_total_bandwidth(self) -> int:
        """Calculate total bytes transferred across all requests."""
        return sum(entry.size for entry in self.entries)
    
    def get_error_rate(self) -> float:
        """
        Calculate percentage of 4xx and 5xx responses.
        
        Useful for quick health checks — if this spikes something's wrong.
        """
        if not self.entries:
            return 0.0
        
        error_count = sum(1 for entry in self.entries if entry.status >= 400)
        return (error_count / len(self.entries)) * 100
    
    def print_summary(self) -> None:
        """Print a human-readable summary of the parsed logs."""
        print(f"\n{'='*60}")
        print(f"Nginx Log Analysis Summary")
        print(f"{'='*60}\n")
        
        print(f"Total requests parsed: {len(self.entries)}")
        print(f"Parse errors encountered: {self.parse_errors}")
        print(f"Total bandwidth: {self.get_total_bandwidth() / (1024**2):.2f} MB")
        print(f"Error rate (4xx/5xx): {self.get_error_rate():.2f}%\n")
        
        print("Status Code Distribution:")
        for status, count in sorted(self.get_status_distribution().items()):
            print(f"  {status}: {count}")
        
        print("\nTop 5 IPs:")
        for ip, count in self.get_top_ips(5):
            print(f"  {ip}: {count} requests")
        
        print("\nTop 5 Paths:")
        for path, count in self.get_top_paths(5):
            # Truncate really long paths for readability
            display_path = path[:50] + "..." if len(path) > 50 else path
            print(f"  {display_path}: {count} requests")


if __name__ == "__main__":
    # Demo with sample log data — represents typical nginx access log entries
    sample_log = """192.168.1.100 - - [10/Jan/2024:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
192.168.1.101 - - [10/Jan/2024:13:55:37 +0000] "POST /api/login HTTP/1.1" 200 567 "https://example.com" "curl/7.68.0"
192.168.1.100 - - [10/Jan/2024:13:55:38 +0000] "GET /static/style.css HTTP/1.1" 200 8192 "https://example.com/index.html" "Mozilla/5.0"
192.168.1.102 - - [10/Jan/2024:13:55:39 +0000] "GET /missing.html HTTP/1.1" 404 178 "-" "Bot/1.0"
192.168.1.100 - - [10/Jan/2024:13:55:40 +0000] "GET /api/users HTTP/1.1" 200 4096 "-" "Mozilla/5.0"
192.168.1.103 - - [10/Jan/2024:13:55:41 +0000] "GET /admin HTTP/1.1" 403 234 "-" "Suspicious-Bot"
192.168.1.101 - - [10/Jan/2024:13:55:42 +0000] "GET /api/data HTTP/1.1" 500 512 "-" "curl/7.68.0"
192.168.1.100 - - [10/Jan/2024:13:55:43 +0000] "GET /blog/post-1 HTTP/1.1" 200 16384 "https://google.com" "Mozilla/5.0"
192.168.1.104 - - [10/Jan/2024:13:55:44 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
192.168.1.100 - - [10/Jan/2024:13:55:45 +0000] "POST /api/submit HTTP/1.1" 201 89 "https://example.com/form" "Mozilla/5.0"
"""
    
    # Write sample data to a temp file and parse it
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        f.write(sample_log)
        temp_path = f.name
    
    try:
        parser = NginxLogParser()
        parser.parse_file(temp_path)
        parser.print_summary()
    finally:
        os.unlink(temp_path)