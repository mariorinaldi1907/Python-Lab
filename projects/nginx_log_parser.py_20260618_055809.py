"""
Date: 2026-06-18
Created a parser for nginx-style access logs because I wanted to quickly analyze traffic patterns without spinning up ELK stack for small projects.
"""

#!/usr/bin/env python3
"""
Nginx Access Log Parser
Parses standard nginx access logs and provides summary statistics.
Format: IP - - [timestamp] "METHOD /path HTTP/1.1" status bytes "referrer" "user-agent"
"""

import re
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Optional


class LogEntry:
    """Represents a single parsed log entry from nginx access log."""
    
    def __init__(self, ip: str, timestamp: str, method: str, path: str, 
                 status: int, bytes_sent: int, user_agent: str):
        self.ip = ip
        self.timestamp = timestamp
        self.method = method
        self.path = path
        self.status = status
        self.bytes_sent = bytes_sent
        self.user_agent = user_agent
    
    def __repr__(self):
        return f"<LogEntry {self.method} {self.path} [{self.status}]>"


class NginxLogParser:
    """
    Parser for nginx access logs with analytics capabilities.
    
    I built this to handle the most common nginx log format. It's regex-based
    because the format is predictable enough that it's faster than trying to
    be too clever with string splits.
    """
    
    # This regex matches the combined log format that nginx uses by default
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d.]+) - - \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\w+) (?P<path>[^\s]+) HTTP/[^"]*" '
        r'(?P<status>\d+) (?P<bytes>\d+) '
        r'"[^"]*" "(?P<user_agent>[^"]*)"'
    )
    
    def __init__(self):
        self.entries: List[LogEntry] = []
        self.parse_errors = 0
    
    def parse_line(self, line: str) -> Optional[LogEntry]:
        """
        Parse a single log line into a LogEntry object.
        Returns None if the line doesn't match the expected format.
        """
        match = self.LOG_PATTERN.match(line.strip())
        if not match:
            return None
        
        data = match.groupdict()
        
        # Convert numeric fields, handling edge cases where they might be "-"
        try:
            status = int(data['status'])
            bytes_sent = int(data['bytes']) if data['bytes'] != '-' else 0
        except ValueError:
            return None
        
        return LogEntry(
            ip=data['ip'],
            timestamp=data['timestamp'],
            method=data['method'],
            path=data['path'],
            status=status,
            bytes_sent=bytes_sent,
            user_agent=data['user_agent']
        )
    
    def parse_file(self, filepath: str) -> None:
        """Load and parse an entire log file."""
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                entry = self.parse_line(line)
                if entry:
                    self.entries.append(entry)
                else:
                    self.parse_errors += 1
    
    def get_top_ips(self, n: int = 10) -> List[tuple]:
        """Return the top N IP addresses by request count."""
        ip_counter = Counter(entry.ip for entry in self.entries)
        return ip_counter.most_common(n)
    
    def get_top_paths(self, n: int = 10) -> List[tuple]:
        """Return the most requested paths."""
        path_counter = Counter(entry.path for entry in self.entries)
        return path_counter.most_common(n)
    
    def get_status_distribution(self) -> Dict[int, int]:
        """Get count of each HTTP status code."""
        status_counter = Counter(entry.status for entry in self.entries)
        return dict(sorted(status_counter.items()))
    
    def get_method_distribution(self) -> Dict[str, int]:
        """Get count of each HTTP method (GET, POST, etc)."""
        method_counter = Counter(entry.method for entry in self.entries)
        return dict(method_counter)
    
    def get_total_bandwidth(self) -> int:
        """Calculate total bytes sent across all requests."""
        return sum(entry.bytes_sent for entry in self.entries)
    
    def print_summary(self) -> None:
        """Print a formatted summary of the parsed logs."""
        print(f"\n{'='*60}")
        print(f"Nginx Log Analysis Summary")
        print(f"{'='*60}")
        print(f"Total requests parsed: {len(self.entries)}")
        print(f"Parse errors: {self.parse_errors}")
        print(f"Total bandwidth: {self.get_total_bandwidth() / (1024*1024):.2f} MB")
        
        print(f"\n--- HTTP Methods ---")
        for method, count in self.get_method_distribution().items():
            print(f"  {method}: {count}")
        
        print(f"\n--- Status Code Distribution ---")
        for status, count in self.get_status_distribution().items():
            print(f"  {status}: {count}")
        
        print(f"\n--- Top 5 IP Addresses ---")
        for ip, count in self.get_top_ips(5):
            print(f"  {ip}: {count} requests")
        
        print(f"\n--- Top 5 Requested Paths ---")
        for path, count in self.get_top_paths(5):
            # Truncate long paths for readability
            display_path = path if len(path) <= 50 else path[:47] + "..."
            print(f"  {display_path}: {count}")
        
        print(f"{'='*60}\n")


if __name__ == "__main__":
    # Demo with synthetic log data since most people won't have nginx logs handy
    # This mimics what you'd see in /var/log/nginx/access.log
    
    sample_logs = """192.168.1.100 - - [15/Jan/2024:14:32:10 +0000] "GET /api/users HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
192.168.1.101 - - [15/Jan/2024:14:32:15 +0000] "POST /api/login HTTP/1.1" 200 456 "-" "curl/7.68.0"
192.168.1.100 - - [15/Jan/2024:14:32:20 +0000] "GET /static/style.css HTTP/1.1" 304 0 "-" "Mozilla/5.0"
10.0.0.50 - - [15/Jan/2024:14:32:25 +0000] "GET /admin/dashboard HTTP/1.1" 403 178 "-" "Python-requests/2.28"
192.168.1.102 - - [15/Jan/2024:14:32:30 +0000] "GET / HTTP/1.1" 200 5678 "-" "Mozilla/5.0"
192.168.1.100 - - [15/Jan/2024:14:32:35 +0000] "GET /api/posts?page=2 HTTP/1.1" 200 2345 "-" "Mozilla/5.0"
10.0.0.50 - - [15/Jan/2024:14:32:40 +0000] "GET /admin/users HTTP/1.1" 403 178 "-" "Python-requests/2.28"
192.168.1.101 - - [15/Jan/2024:14:32:45 +0000] "GET /about HTTP/1.1" 200 890 "-" "curl/7.68.0"
192.168.1.103 - - [15/Jan/2024:14:32:50 +0000] "GET /notfound HTTP/1.1" 404 153 "-" "GoogleBot/2.1"
192.168.1.100 - - [15/Jan/2024:14:32:55 +0000] "POST /api/comments HTTP/1.1" 201 234 "-" "Mozilla/5.0"
"""
    
    # Write sample logs to a temp file for the demo
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        f.write(sample_logs)
        temp_log_path = f.name
    
    try:
        parser = NginxLogParser()
        parser.parse_file(temp_log_path)
        parser.print_summary()
    finally:
        # Clean up temp file
        os.unlink(temp_log_path)