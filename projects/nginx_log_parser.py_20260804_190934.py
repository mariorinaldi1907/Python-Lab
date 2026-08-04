"""
Date: 2026-08-04
I needed a quick way to analyze nginx access logs without installing anything, so I wrote this parser that summarizes requests, errors, and bandwidth in one go.
"""

#!/usr/bin/env python3
"""
Nginx Access Log Parser
Parses standard nginx combined log format and generates useful statistics.
"""

import re
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class NginxLogParser:
    """
    Parser for nginx access logs in combined format.
    
    The combined format looks like:
    $remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent"
    """
    
    # This regex is gnarly but it matches the combined log format perfectly
    LOG_PATTERN = re.compile(
        r'(?P<ip>\S+) '
        r'- '
        r'(?P<user>\S+) '
        r'\[(?P<time>[^\]]+)\] '
        r'"(?P<request>[^"]*)" '
        r'(?P<status>\d{3}) '
        r'(?P<size>\S+) '
        r'"(?P<referer>[^"]*)" '
        r'"(?P<user_agent>[^"]*)"'
    )
    
    def __init__(self):
        """Initialize counters and storage for parsed data."""
        self.total_requests = 0
        self.status_codes = Counter()
        self.ip_addresses = Counter()
        self.request_methods = Counter()
        self.total_bytes = 0
        self.error_requests = []  # Store 4xx and 5xx for detailed review
        self.parsed_lines = 0
        self.failed_lines = 0
    
    def parse_line(self, line: str) -> Optional[Dict]:
        """
        Parse a single log line.
        
        Returns a dict with parsed fields, or None if parsing fails.
        I'm not raising exceptions here because log files can be messy
        and I want to parse as much as possible.
        """
        match = self.LOG_PATTERN.match(line.strip())
        if not match:
            self.failed_lines += 1
            return None
        
        self.parsed_lines += 1
        return match.groupdict()
    
    def analyze_entry(self, entry: Dict) -> None:
        """
        Update statistics based on a parsed log entry.
        
        This is where we extract the interesting bits from each request.
        """
        self.total_requests += 1
        
        # Track status codes
        status = int(entry['status'])
        self.status_codes[status] += 1
        
        # Track IPs for rate limiting analysis
        self.ip_addresses[entry['ip']] += 1
        
        # Parse the HTTP method from the request string
        request_parts = entry['request'].split()
        if request_parts:
            method = request_parts[0]
            self.request_methods[method] += 1
        
        # Calculate bandwidth (size might be '-' for 0 bytes)
        size_str = entry['size']
        if size_str != '-':
            self.total_bytes += int(size_str)
        
        # Keep track of errors for later inspection
        if status >= 400:
            self.error_requests.append({
                'ip': entry['ip'],
                'status': status,
                'request': entry['request'],
                'time': entry['time']
            })
    
    def parse_file(self, filepath: str) -> None:
        """
        Parse an entire log file line by line.
        
        I'm using a generator approach here to handle large files
        without loading everything into memory.
        """
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                entry = self.parse_line(line)
                if entry:
                    self.analyze_entry(entry)
    
    def get_summary(self) -> str:
        """
        Generate a human-readable summary of the parsed logs.
        
        This is what I actually care about when analyzing logs quickly.
        """
        lines = [
            "=" * 60,
            "NGINX LOG ANALYSIS SUMMARY",
            "=" * 60,
            f"\nTotal Requests: {self.total_requests}",
            f"Successfully Parsed: {self.parsed_lines}",
            f"Failed to Parse: {self.failed_lines}",
            f"\nTotal Bandwidth: {self._format_bytes(self.total_bytes)}",
            f"\n{'HTTP Status Codes:':<30}",
        ]
        
        # Sort status codes for cleaner output
        for status, count in sorted(self.status_codes.items()):
            percentage = (count / self.total_requests * 100) if self.total_requests > 0 else 0
            lines.append(f"  {status}: {count:>6} ({percentage:>5.1f}%)")
        
        lines.append(f"\n{'Request Methods:':<30}")
        for method, count in self.request_methods.most_common():
            percentage = (count / self.total_requests * 100) if self.total_requests > 0 else 0
            lines.append(f"  {method}: {count:>6} ({percentage:>5.1f}%)")
        
        lines.append(f"\n{'Top 10 IP Addresses:':<30}")
        for ip, count in self.ip_addresses.most_common(10):
            lines.append(f"  {ip:<15} {count:>6} requests")
        
        # Show some error details if we have them
        if self.error_requests:
            lines.append(f"\n{'Recent Errors (last 5):':<30}")
            for err in self.error_requests[-5:]:
                lines.append(f"  [{err['status']}] {err['ip']} - {err['request']}")
        
        return "\n".join(lines)
    
    @staticmethod
    def _format_bytes(bytes_count: int) -> str:
        """Format bytes into human-readable units."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.2f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.2f} PB"


if __name__ == "__main__":
    # Create a sample log file for demonstration
    # This simulates what real nginx logs look like
    sample_log = """192.168.1.100 - - [10/Jan/2024:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
192.168.1.101 - - [10/Jan/2024:13:55:37 +0000] "POST /api/login HTTP/1.1" 200 512 "https://example.com" "curl/7.68.0"
192.168.1.100 - - [10/Jan/2024:13:55:38 +0000] "GET /static/style.css HTTP/1.1" 200 2048 "https://example.com" "Mozilla/5.0"
192.168.1.102 - - [10/Jan/2024:13:55:39 +0000] "GET /missing.html HTTP/1.1" 404 162 "-" "Bot/1.0"
192.168.1.100 - - [10/Jan/2024:13:55:40 +0000] "GET /api/data HTTP/1.1" 500 1024 "-" "Mozilla/5.0"
192.168.1.103 - - [10/Jan/2024:13:55:41 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
192.168.1.101 - - [10/Jan/2024:13:55:42 +0000] "DELETE /api/users/5 HTTP/1.1" 204 - "-" "MyApp/2.1"
192.168.1.102 - - [10/Jan/2024:13:55:43 +0000] "GET /admin HTTP/1.1" 403 278 "-" "Bot/1.0"
192.168.1.100 - - [10/Jan/2024:13:55:44 +0000] "GET /images/logo.png HTTP/1.1" 200 8192 "https://example.com" "Mozilla/5.0"
192.168.1.104 - - [10/Jan/2024:13:55:45 +0000] "POST /api/submit HTTP/1.1" 201 64 "-" "curl/7.68.0"
"""
    
    # Write sample data to a temp file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        f.write(sample_log)
        temp_path = f.name
    
    print("Parsing sample nginx access log...\n")
    
    # Actually use the parser
    parser = NginxLogParser()
    parser.parse_file(temp_path)
    
    # Print the summary
    print(parser.get_summary())
    
    # Clean up
    import os
    os.unlink(temp_path)