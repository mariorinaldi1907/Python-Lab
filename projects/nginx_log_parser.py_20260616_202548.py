"""
Date: 2026-06-16
Created a parser for nginx access logs that breaks down requests by status code, IP, and endpoint — helps me quickly audit traffic on my personal servers.
"""

#!/usr/bin/env python3
"""
Nginx access log parser for combined log format.
Parses standard nginx logs and provides basic traffic analytics.
"""

import re
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Optional


class LogEntry:
    """Represents a single parsed line from an nginx access log."""
    
    def __init__(self, ip: str, timestamp: str, method: str, path: str, 
                 status: int, size: int, referer: str, user_agent: str):
        self.ip = ip
        self.timestamp = timestamp
        self.method = method
        self.path = path
        self.status = status
        self.size = size
        self.referer = referer
        self.user_agent = user_agent
    
    def __repr__(self):
        return f"<LogEntry {self.method} {self.path} [{self.status}]>"


class NginxLogParser:
    """
    Parser for nginx combined format access logs.
    
    Combined format:
    '$remote_addr - $remote_user [$time_local] "$request" '
    '$status $body_bytes_sent "$http_referer" "$http_user_agent"'
    """
    
    # Regex pattern for combined log format
    # Built this incrementally by testing against real logs from my VPS
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d\.]+) - (?P<user>\S+) \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\S+) (?P<path>\S+) (?P<protocol>[^"]+)" '
        r'(?P<status>\d+) (?P<size>\d+) '
        r'"(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)"'
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
        
        groups = match.groupdict()
        
        try:
            entry = LogEntry(
                ip=groups['ip'],
                timestamp=groups['timestamp'],
                method=groups['method'],
                path=groups['path'],
                status=int(groups['status']),
                size=int(groups['size']),
                referer=groups['referer'],
                user_agent=groups['user_agent']
            )
            return entry
        except (ValueError, KeyError):
            # Malformed data in an otherwise matching line
            return None
    
    def parse_file(self, filepath: str) -> int:
        """
        Parse an entire log file. Returns the number of successfully parsed lines.
        """
        parsed_count = 0
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                entry = self.parse_line(line.strip())
                if entry:
                    self.entries.append(entry)
                    parsed_count += 1
        return parsed_count
    
    def get_status_summary(self) -> Dict[int, int]:
        """Count requests by HTTP status code."""
        counter = Counter(entry.status for entry in self.entries)
        return dict(counter)
    
    def get_top_ips(self, n: int = 10) -> List[tuple]:
        """Get the top N IP addresses by request count."""
        counter = Counter(entry.ip for entry in self.entries)
        return counter.most_common(n)
    
    def get_top_paths(self, n: int = 10) -> List[tuple]:
        """Get the top N requested paths."""
        counter = Counter(entry.path for entry in self.entries)
        return counter.most_common(n)
    
    def get_error_requests(self) -> List[LogEntry]:
        """Return all requests with 4xx or 5xx status codes."""
        return [entry for entry in self.entries if entry.status >= 400]
    
    def get_traffic_by_method(self) -> Dict[str, int]:
        """Count requests by HTTP method (GET, POST, etc)."""
        counter = Counter(entry.method for entry in self.entries)
        return dict(counter)
    
    def total_bandwidth(self) -> int:
        """Calculate total bytes served."""
        return sum(entry.size for entry in self.entries)


def format_bytes(bytes_count: int) -> str:
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.2f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.2f} TB"


if __name__ == "__main__":
    # Demo with a sample log content (simulating what I'd see on my servers)
    sample_log = """127.0.0.1 - - [10/Jan/2024:13:55:36 +0000] "GET /api/health HTTP/1.1" 200 15 "-" "Python-urllib/3.8"
192.168.1.100 - - [10/Jan/2024:13:56:12 +0000] "POST /api/data HTTP/1.1" 201 2048 "https://example.com" "Mozilla/5.0"
10.0.0.5 - - [10/Jan/2024:13:57:03 +0000] "GET /static/styles.css HTTP/1.1" 200 4096 "https://mysite.com" "Mozilla/5.0"
192.168.1.100 - - [10/Jan/2024:13:58:45 +0000] "GET /admin/login HTTP/1.1" 404 162 "-" "curl/7.68.0"
127.0.0.1 - - [10/Jan/2024:13:59:21 +0000] "GET /api/health HTTP/1.1" 200 15 "-" "Python-urllib/3.8"
192.168.1.100 - - [10/Jan/2024:14:00:10 +0000] "GET /api/users HTTP/1.1" 500 512 "https://example.com" "Mozilla/5.0"
10.0.0.5 - - [10/Jan/2024:14:01:33 +0000] "GET / HTTP/1.1" 200 8192 "-" "Mozilla/5.0"
192.168.1.100 - - [10/Jan/2024:14:02:05 +0000] "DELETE /api/data/123 HTTP/1.1" 204 0 "https://example.com" "Mozilla/5.0"
"""
    
    # Write sample log to a temp file for demonstration
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        f.write(sample_log)
        temp_log_path = f.name
    
    try:
        parser = NginxLogParser()
        parsed = parser.parse_file(temp_log_path)
        
        print(f"=== Nginx Log Analysis ===\n")
        print(f"Total requests parsed: {parsed}\n")
        
        print("Status Code Summary:")
        for status, count in sorted(parser.get_status_summary().items()):
            print(f"  {status}: {count} requests")
        
        print(f"\nHTTP Methods:")
        for method, count in parser.get_traffic_by_method().items():
            print(f"  {method}: {count} requests")
        
        print(f"\nTop 5 Requested Paths:")
        for path, count in parser.get_top_paths(5):
            print(f"  {path}: {count} times")
        
        print(f"\nTop 3 IP Addresses:")
        for ip, count in parser.get_top_ips(3):
            print(f"  {ip}: {count} requests")
        
        print(f"\nTotal Bandwidth: {format_bytes(parser.total_bandwidth())}")
        
        errors = parser.get_error_requests()
        if errors:
            print(f"\nError Requests ({len(errors)} total):")
            for entry in errors:
                print(f"  [{entry.status}] {entry.method} {entry.path} from {entry.ip}")
    
    finally:
        # Clean up temp file
        os.unlink(temp_log_path)