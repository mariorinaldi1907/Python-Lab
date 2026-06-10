"""
Date: 2026-06-10
Created a parser for nginx access logs that breaks down request patterns, response codes, and user agents — useful for quickly analyzing traffic without spinning up a full analytics stack.
"""

#!/usr/bin/env python3
"""
Nginx access log parser - extracts meaningful stats from combined log format.

I got tired of grepping through logs manually when debugging production issues,
so I built this to quickly surface patterns in traffic, error rates, and user agents.
"""

import re
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Optional


class NginxLogEntry:
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
    
    def is_error(self) -> bool:
        """Check if this was an error response (4xx or 5xx)."""
        return self.status >= 400


class NginxLogParser:
    """
    Parses nginx access logs in combined format and extracts traffic statistics.
    
    The combined format is:
    $remote_addr - - [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent"
    """
    
    # Regex for nginx combined log format - built piece by piece because it's gnarly
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d\.]+)\s+-\s+-\s+'
        r'\[(?P<timestamp>[^\]]+)\]\s+'
        r'"(?P<method>\w+)\s+(?P<path>[^\s]+)\s+[^"]+"\s+'
        r'(?P<status>\d{3})\s+'
        r'(?P<size>\d+)\s+'
        r'"(?P<referer>[^"]*)"\s+'
        r'"(?P<user_agent>[^"]*)"'
    )
    
    def __init__(self):
        self.entries: List[NginxLogEntry] = []
        self.parse_errors = 0
    
    def parse_file(self, filepath: str) -> None:
        """
        Read and parse an entire log file.
        
        Gracefully handles malformed lines because production logs are messy.
        """
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                entry = self._parse_line(line.strip())
                if entry:
                    self.entries.append(entry)
                else:
                    self.parse_errors += 1
    
    def _parse_line(self, line: str) -> Optional[NginxLogEntry]:
        """Parse a single log line into an NginxLogEntry object."""
        match = self.LOG_PATTERN.match(line)
        if not match:
            return None
        
        try:
            return NginxLogEntry(
                ip=match.group('ip'),
                timestamp=match.group('timestamp'),
                method=match.group('method'),
                path=match.group('path'),
                status=int(match.group('status')),
                size=int(match.group('size')),
                referer=match.group('referer'),
                user_agent=match.group('user_agent')
            )
        except (ValueError, AttributeError):
            return None
    
    def get_status_distribution(self) -> Dict[int, int]:
        """Count how many times each HTTP status code appeared."""
        return dict(Counter(entry.status for entry in self.entries))
    
    def get_top_paths(self, n: int = 10) -> List[tuple]:
        """Return the most frequently requested paths."""
        path_counts = Counter(entry.path for entry in self.entries)
        return path_counts.most_common(n)
    
    def get_error_rate(self) -> float:
        """Calculate percentage of requests that resulted in errors."""
        if not self.entries:
            return 0.0
        errors = sum(1 for entry in self.entries if entry.is_error())
        return (errors / len(self.entries)) * 100
    
    def get_top_user_agents(self, n: int = 5) -> List[tuple]:
        """Find the most common user agents (useful for spotting bots)."""
        ua_counts = Counter(entry.user_agent for entry in self.entries)
        return ua_counts.most_common(n)
    
    def get_traffic_by_method(self) -> Dict[str, int]:
        """Break down requests by HTTP method."""
        return dict(Counter(entry.method for entry in self.entries))
    
    def generate_report(self) -> str:
        """
        Create a human-readable summary of the parsed logs.
        
        This is what I actually use when debugging - gives me a quick overview
        without having to remember all the method names.
        """
        lines = [
            "=" * 60,
            "NGINX ACCESS LOG ANALYSIS",
            "=" * 60,
            f"\nTotal requests parsed: {len(self.entries)}",
            f"Parse errors (malformed lines): {self.parse_errors}",
            f"Error rate: {self.get_error_rate():.2f}%",
            "\n--- HTTP Methods ---"
        ]
        
        for method, count in sorted(self.get_traffic_by_method().items()):
            lines.append(f"  {method}: {count}")
        
        lines.append("\n--- Status Code Distribution ---")
        for status, count in sorted(self.get_status_distribution().items()):
            lines.append(f"  {status}: {count}")
        
        lines.append("\n--- Top 10 Requested Paths ---")
        for path, count in self.get_top_paths(10):
            lines.append(f"  {count:5d}  {path}")
        
        lines.append("\n--- Top 5 User Agents ---")
        for ua, count in self.get_top_user_agents(5):
            # Truncate long user agent strings
            ua_display = ua[:70] + "..." if len(ua) > 70 else ua
            lines.append(f"  {count:5d}  {ua_display}")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)


if __name__ == "__main__":
    # Create a sample log file for demo purposes
    sample_log = """127.0.0.1 - - [10/Jan/2024:13:55:36 +0000] "GET /api/users HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
127.0.0.1 - - [10/Jan/2024:13:55:37 +0000] "POST /api/login HTTP/1.1" 200 567 "-" "Mozilla/5.0"
192.168.1.5 - - [10/Jan/2024:13:55:38 +0000] "GET /static/style.css HTTP/1.1" 304 0 "https://example.com/" "Chrome/120.0"
192.168.1.5 - - [10/Jan/2024:13:55:39 +0000] "GET /api/data HTTP/1.1" 404 178 "-" "Mozilla/5.0"
10.0.0.1 - - [10/Jan/2024:13:55:40 +0000] "GET /api/users HTTP/1.1" 200 2048 "-" "Python-requests/2.31"
10.0.0.1 - - [10/Jan/2024:13:55:41 +0000] "DELETE /api/users/42 HTTP/1.1" 500 89 "-" "Python-requests/2.31"
127.0.0.1 - - [10/Jan/2024:13:55:42 +0000] "GET /api/users HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
192.168.1.5 - - [10/Jan/2024:13:55:43 +0000] "GET / HTTP/1.1" 200 5432 "-" "Chrome/120.0"
"""
    
    # Write sample to a temp file
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        f.write(sample_log)
        temp_path = f.name
    
    try:
        # Parse the log file
        parser = NginxLogParser()
        parser.parse_file(temp_path)
        
        # Print the full report
        print(parser.generate_report())
        
    finally:
        # Clean up temp file
        os.unlink(temp_path)