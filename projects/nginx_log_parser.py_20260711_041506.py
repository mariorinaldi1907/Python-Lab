"""
Date: 2026-07-11
Wrote a parser for nginx access logs that breaks down traffic patterns — helps me spot suspicious activity on my personal server.
"""

#!/usr/bin/env python3
"""
Nginx access log parser - helps me understand what's hitting my server.
Parses the standard combined log format and extracts useful metrics.
"""

import re
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Optional


class LogEntry:
    """Represents a single nginx access log entry."""
    
    # Regex for nginx combined log format
    # IP - - [datetime] "METHOD path HTTP/x.x" status size "referrer" "user-agent"
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d\.]+) - - \[(?P<datetime>[^\]]+)\] '
        r'"(?P<method>\w+) (?P<path>[^\s]+) HTTP/[\d\.]+"\s+'
        r'(?P<status>\d{3}) (?P<size>\d+|-) '
        r'"(?P<referrer>[^"]*)" "(?P<user_agent>[^"]*)"'
    )
    
    def __init__(self, line: str):
        """Parse a log line into structured data."""
        self.raw = line.strip()
        match = self.LOG_PATTERN.match(self.raw)
        
        if not match:
            raise ValueError(f"Could not parse log line: {line[:50]}...")
        
        self.ip = match.group('ip')
        self.method = match.group('method')
        self.path = match.group('path')
        self.status = int(match.group('status'))
        
        # Size might be "-" for 0 bytes
        size_str = match.group('size')
        self.size = 0 if size_str == '-' else int(size_str)
        
        self.referrer = match.group('referrer')
        self.user_agent = match.group('user_agent')
        
        # Parse datetime - nginx format: "10/Oct/2023:13:55:36 +0000"
        dt_str = match.group('datetime')
        self.timestamp = datetime.strptime(dt_str, '%d/%b/%Y:%H:%M:%S %z')


class NginxLogAnalyzer:
    """Analyzes nginx access logs and generates useful statistics."""
    
    def __init__(self):
        """Initialize empty analyzer."""
        self.entries: List[LogEntry] = []
        self.total_bytes = 0
        
    def parse_file(self, filepath: str) -> None:
        """Read and parse a log file, storing all valid entries."""
        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    entry = LogEntry(line)
                    self.entries.append(entry)
                    self.total_bytes += entry.size
                except ValueError as e:
                    # Skip malformed lines but warn about them
                    print(f"Warning: Skipped line {line_num}: {e}")
    
    def top_ips(self, limit: int = 10) -> List[tuple]:
        """Return most frequent IP addresses."""
        ip_counter = Counter(entry.ip for entry in self.entries)
        return ip_counter.most_common(limit)
    
    def status_breakdown(self) -> Dict[int, int]:
        """Count occurrences of each HTTP status code."""
        status_counter = Counter(entry.status for entry in self.entries)
        return dict(sorted(status_counter.items()))
    
    def top_paths(self, limit: int = 10) -> List[tuple]:
        """Return most requested paths."""
        path_counter = Counter(entry.path for entry in self.entries)
        return path_counter.most_common(limit)
    
    def requests_by_method(self) -> Dict[str, int]:
        """Count requests by HTTP method."""
        method_counter = Counter(entry.method for entry in self.entries)
        return dict(method_counter)
    
    def traffic_by_hour(self) -> Dict[int, int]:
        """Group requests by hour of day (0-23)."""
        hourly = defaultdict(int)
        for entry in self.entries:
            hour = entry.timestamp.hour
            hourly[hour] += 1
        return dict(sorted(hourly.items()))
    
    def error_entries(self) -> List[LogEntry]:
        """Return all entries with 4xx or 5xx status codes."""
        return [e for e in self.entries if e.status >= 400]
    
    def summary(self) -> str:
        """Generate a human-readable summary of the logs."""
        if not self.entries:
            return "No log entries parsed."
        
        lines = []
        lines.append(f"=== Nginx Log Analysis ===")
        lines.append(f"Total requests: {len(self.entries)}")
        lines.append(f"Total bandwidth: {self.total_bytes / (1024**2):.2f} MB")
        lines.append(f"Time range: {self.entries[0].timestamp} to {self.entries[-1].timestamp}")
        
        lines.append(f"\nStatus Code Breakdown:")
        for status, count in self.status_breakdown().items():
            lines.append(f"  {status}: {count}")
        
        lines.append(f"\nTop 5 IPs:")
        for ip, count in self.top_ips(5):
            lines.append(f"  {ip}: {count} requests")
        
        lines.append(f"\nTop 5 Paths:")
        for path, count in self.top_paths(5):
            lines.append(f"  {path}: {count} requests")
        
        lines.append(f"\nHTTP Methods:")
        for method, count in self.requests_by_method().items():
            lines.append(f"  {method}: {count}")
        
        error_count = len(self.error_entries())
        if error_count > 0:
            lines.append(f"\n⚠ Found {error_count} error responses (4xx/5xx)")
        
        return "\n".join(lines)


if __name__ == "__main__":
    # Create a sample log file for demo purposes
    sample_log = """127.0.0.1 - - [15/Jan/2024:10:23:45 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
192.168.1.100 - - [15/Jan/2024:10:24:12 +0000] "POST /api/login HTTP/1.1" 200 512 "https://example.com" "Chrome/90.0"
10.0.0.5 - - [15/Jan/2024:10:25:03 +0000] "GET /static/style.css HTTP/1.1" 200 8192 "-" "Mozilla/5.0"
127.0.0.1 - - [15/Jan/2024:10:26:18 +0000] "GET /admin HTTP/1.1" 403 234 "-" "curl/7.68.0"
192.168.1.100 - - [15/Jan/2024:10:27:45 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Chrome/90.0"
10.0.0.5 - - [15/Jan/2024:10:28:02 +0000] "GET /missing.html HTTP/1.1" 404 152 "-" "Mozilla/5.0"
127.0.0.1 - - [15/Jan/2024:11:15:33 +0000] "GET /api/data HTTP/1.1" 500 89 "-" "Python-requests/2.28"
192.168.1.100 - - [15/Jan/2024:11:16:22 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Chrome/90.0"
"""
    
    # Write sample data to temp file
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        f.write(sample_log)
        temp_path = f.name
    
    try:
        # Parse and analyze
        analyzer = NginxLogAnalyzer()
        analyzer.parse_file(temp_path)
        
        print(analyzer.summary())
        
    finally:
        # Clean up temp file
        os.unlink(temp_path)