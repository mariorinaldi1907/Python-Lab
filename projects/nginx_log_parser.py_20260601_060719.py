"""
Date: 2026-06-01
Created a parser for nginx access logs that breaks down traffic by status code, identifies potential bot traffic, and flags suspicious request patterns like directory traversal attempts.
"""

#!/usr/bin/env python3
"""
Nginx Access Log Parser
Parses standard nginx access logs and extracts useful statistics.
"""

import re
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class NginxLogEntry:
    """Represents a single parsed nginx log line."""
    
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
        return f"<LogEntry {self.method} {self.path} -> {self.status}>"


class NginxLogParser:
    """
    Parses nginx access logs in combined format.
    The regex handles the standard format that includes IP, timestamp, request, status, etc.
    """
    
    # Standard nginx combined log format pattern
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d\.]+) - - \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\S+) (?P<path>\S+) HTTP/[\d\.]+" '
        r'(?P<status>\d{3}) (?P<size>\d+) '
        r'"[^"]*" "(?P<user_agent>[^"]*)"'
    )
    
    def __init__(self):
        self.entries: List[NginxLogEntry] = []
        self.parse_errors: List[str] = []
    
    def parse_line(self, line: str) -> Optional[NginxLogEntry]:
        """
        Parse a single log line into a structured entry.
        Returns None if the line doesn't match expected format.
        """
        match = self.LOG_PATTERN.match(line)
        if not match:
            return None
        
        groups = match.groupdict()
        return NginxLogEntry(
            ip=groups['ip'],
            timestamp=groups['timestamp'],
            method=groups['method'],
            path=groups['path'],
            status=int(groups['status']),
            size=int(groups['size']),
            user_agent=groups['user_agent']
        )
    
    def parse_file(self, filepath: str) -> None:
        """
        Read and parse an entire log file.
        Keeps track of lines that fail to parse.
        """
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                entry = self.parse_line(line)
                if entry:
                    self.entries.append(entry)
                else:
                    self.parse_errors.append(f"Line {line_num}: {line[:60]}...")
    
    def get_status_distribution(self) -> Counter:
        """Returns count of each HTTP status code seen."""
        return Counter(entry.status for entry in self.entries)
    
    def get_top_paths(self, n: int = 10) -> List[Tuple[str, int]]:
        """Returns the most frequently requested paths."""
        path_counter = Counter(entry.path for entry in self.entries)
        return path_counter.most_common(n)
    
    def get_top_ips(self, n: int = 10) -> List[Tuple[str, int]]:
        """Returns IPs with most requests (useful for identifying bots)."""
        ip_counter = Counter(entry.ip for entry in self.entries)
        return ip_counter.most_common(n)
    
    def find_suspicious_requests(self) -> List[NginxLogEntry]:
        """
        Flag potentially malicious requests.
        Looks for directory traversal, SQL injection attempts, etc.
        This is a basic heuristic — real detection needs more sophistication.
        """
        suspicious_patterns = [
            r'\.\.',           # directory traversal
            r'\/etc\/passwd',  # common file access attempt
            r'union.*select',  # SQL injection
            r'<script',        # XSS attempt
            r'cmd=',           # command injection
        ]
        
        combined_pattern = re.compile('|'.join(suspicious_patterns), re.IGNORECASE)
        
        return [
            entry for entry in self.entries
            if combined_pattern.search(entry.path)
        ]
    
    def get_error_rate(self) -> float:
        """Calculate percentage of 4xx/5xx responses."""
        if not self.entries:
            return 0.0
        
        error_count = sum(1 for entry in self.entries if entry.status >= 400)
        return (error_count / len(self.entries)) * 100
    
    def print_summary(self) -> None:
        """Print a human-readable summary of the parsed logs."""
        print(f"\n{'='*60}")
        print(f"Nginx Log Analysis Summary")
        print(f"{'='*60}\n")
        
        print(f"Total entries parsed: {len(self.entries)}")
        print(f"Parse errors: {len(self.parse_errors)}\n")
        
        # Status code breakdown
        print("Status Code Distribution:")
        for status, count in sorted(self.get_status_distribution().items()):
            print(f"  {status}: {count:,}")
        
        print(f"\nError rate (4xx/5xx): {self.get_error_rate():.2f}%\n")
        
        # Top paths
        print("Top 5 Requested Paths:")
        for path, count in self.get_top_paths(5):
            print(f"  {count:>5}x  {path}")
        
        # Top IPs (potential bots)
        print("\nTop 5 IPs by Request Count:")
        for ip, count in self.get_top_ips(5):
            print(f"  {count:>5}x  {ip}")
        
        # Security concerns
        suspicious = self.find_suspicious_requests()
        if suspicious:
            print(f"\n⚠️  Found {len(suspicious)} suspicious requests:")
            for entry in suspicious[:5]:  # show first 5
                print(f"  {entry.ip} -> {entry.path[:60]}")


if __name__ == "__main__":
    # Create sample nginx log data for demo purposes
    sample_logs = """192.168.1.100 - - [15/Jan/2024:10:23:45 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
192.168.1.101 - - [15/Jan/2024:10:23:46 +0000] "GET /api/users HTTP/1.1" 200 5678 "-" "curl/7.68.0"
192.168.1.100 - - [15/Jan/2024:10:23:47 +0000] "POST /login HTTP/1.1" 302 0 "-" "Mozilla/5.0"
192.168.1.102 - - [15/Jan/2024:10:23:48 +0000] "GET /../../../etc/passwd HTTP/1.1" 404 162 "-" "python-requests/2.28"
192.168.1.103 - - [15/Jan/2024:10:23:49 +0000] "GET /admin HTTP/1.1" 403 178 "-" "Googlebot/2.1"
192.168.1.100 - - [15/Jan/2024:10:23:50 +0000] "GET /static/style.css HTTP/1.1" 200 9876 "-" "Mozilla/5.0"
192.168.1.104 - - [15/Jan/2024:10:23:51 +0000] "GET /api/data?id=1%20union%20select HTTP/1.1" 400 45 "-" "sqlmap/1.0"
192.168.1.100 - - [15/Jan/2024:10:23:52 +0000] "GET /images/logo.png HTTP/1.1" 200 4532 "-" "Mozilla/5.0"
192.168.1.105 - - [15/Jan/2024:10:23:53 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "bot-scanner"
192.168.1.100 - - [15/Jan/2024:10:23:54 +0000] "GET /about HTTP/1.1" 200 2341 "-" "Mozilla/5.0"
"""
    
    # Write sample data to a temp file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        f.write(sample_logs)
        temp_path = f.name
    
    # Parse and analyze
    parser = NginxLogParser()
    parser.parse_file(temp_path)
    parser.print_summary()
    
    # Clean up
    import os
    os.unlink(temp_path)