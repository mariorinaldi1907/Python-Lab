"""
Date: 2026-07-27
Wrote a parser for nginx access logs that calculates stats like request counts, status code distribution, and flags potential security issues like SQL injection attempts or excessive 404s from the same IP.
"""

#!/usr/bin/env python3
"""
Nginx Access Log Parser
Parses standard nginx combined log format and extracts useful metrics.
"""

import re
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Tuple


class NginxLogParser:
    """
    Parser for nginx access logs in combined format.
    Extracts metrics and identifies suspicious patterns.
    """
    
    # Regex for nginx combined log format
    # Example: 192.168.1.1 - - [10/Oct/2023:13:55:36 +0000] "GET /api/users HTTP/1.1" 200 1234 "..." "Mozilla..."
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d\.]+) - - \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\w+) (?P<path>[^\s]+) HTTP/[\d\.]+" '
        r'(?P<status>\d+) (?P<size>\d+) "(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)"'
    )
    
    def __init__(self):
        """Initialize counters and storage for analysis."""
        self.total_requests = 0
        self.status_codes = Counter()
        self.ip_requests = defaultdict(int)
        self.ip_errors = defaultdict(int)
        self.paths = Counter()
        self.methods = Counter()
        self.suspicious_ips = set()
        
    def parse_line(self, line: str) -> Dict[str, str]:
        """
        Parse a single log line into structured data.
        
        Returns a dict with keys: ip, timestamp, method, path, status, size, referer, user_agent
        Returns None if the line doesn't match expected format.
        """
        match = self.LOG_PATTERN.match(line.strip())
        if match:
            return match.groupdict()
        return None
    
    def analyze_entry(self, entry: Dict[str, str]):
        """
        Analyze a parsed log entry and update internal metrics.
        Also checks for suspicious patterns like SQL injection attempts.
        """
        if not entry:
            return
        
        ip = entry['ip']
        status = int(entry['status'])
        path = entry['path']
        method = entry['method']
        
        # Update basic counters
        self.total_requests += 1
        self.status_codes[status] += 1
        self.ip_requests[ip] += 1
        self.paths[path] += 1
        self.methods[method] += 1
        
        # Track error rates per IP (4xx and 5xx responses)
        if status >= 400:
            self.ip_errors[ip] += 1
        
        # Flag suspicious patterns in the path
        # Looking for SQL injection attempts, path traversal, etc.
        suspicious_patterns = ['../', 'union select', 'drop table', '<script', 'etc/passwd']
        if any(pattern in path.lower() for pattern in suspicious_patterns):
            self.suspicious_ips.add(ip)
    
    def process_file(self, filepath: str):
        """Read and analyze an entire log file."""
        with open(filepath, 'r') as f:
            for line in f:
                entry = self.parse_line(line)
                self.analyze_entry(entry)
    
    def get_top_ips(self, n: int = 10) -> List[Tuple[str, int]]:
        """Return the top N IPs by request count."""
        return self.ip_requests.most_common(n)
    
    def get_error_rate_by_ip(self) -> Dict[str, float]:
        """
        Calculate error rate (4xx/5xx) for each IP.
        Returns dict of {ip: error_percentage}.
        """
        error_rates = {}
        for ip in self.ip_requests:
            total = self.ip_requests[ip]
            errors = self.ip_errors[ip]
            error_rates[ip] = (errors / total) * 100 if total > 0 else 0
        return error_rates
    
    def print_summary(self):
        """Print a formatted summary of the analysis."""
        print("=" * 60)
        print("NGINX LOG ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"\nTotal Requests: {self.total_requests}")
        
        print("\nStatus Code Distribution:")
        for status, count in sorted(self.status_codes.items()):
            percentage = (count / self.total_requests) * 100
            print(f"  {status}: {count} ({percentage:.1f}%)")
        
        print("\nTop 5 Requested Paths:")
        for path, count in self.paths.most_common(5):
            print(f"  {path}: {count}")
        
        print("\nHTTP Methods:")
        for method, count in self.methods.items():
            print(f"  {method}: {count}")
        
        print("\nTop 5 IPs by Request Count:")
        for ip, count in self.get_top_ips(5):
            error_rate = self.get_error_rate_by_ip()[ip]
            print(f"  {ip}: {count} requests (error rate: {error_rate:.1f}%)")
        
        if self.suspicious_ips:
            print("\n⚠️  SUSPICIOUS ACTIVITY DETECTED from IPs:")
            for ip in self.suspicious_ips:
                print(f"  {ip} - possible attack patterns in request paths")
        else:
            print("\n✓ No obvious suspicious patterns detected")


if __name__ == "__main__":
    # Create a sample log file for demonstration
    sample_log = """192.168.1.100 - - [10/Oct/2023:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
192.168.1.101 - - [10/Oct/2023:13:55:37 +0000] "POST /api/login HTTP/1.1" 200 512 "-" "curl/7.64.1"
192.168.1.100 - - [10/Oct/2023:13:55:38 +0000] "GET /images/logo.png HTTP/1.1" 200 5678 "http://example.com/" "Mozilla/5.0"
192.168.1.102 - - [10/Oct/2023:13:55:39 +0000] "GET /admin HTTP/1.1" 404 162 "-" "Python-urllib/3.8"
192.168.1.101 - - [10/Oct/2023:13:55:40 +0000] "GET /api/users HTTP/1.1" 200 8901 "-" "curl/7.64.1"
192.168.1.103 - - [10/Oct/2023:13:55:41 +0000] "GET /../../etc/passwd HTTP/1.1" 403 162 "-" "BadBot/1.0"
192.168.1.100 - - [10/Oct/2023:13:55:42 +0000] "GET /about.html HTTP/1.1" 200 2345 "-" "Mozilla/5.0"
192.168.1.102 - - [10/Oct/2023:13:55:43 +0000] "GET /missing HTTP/1.1" 404 162 "-" "Python-urllib/3.8"
192.168.1.101 - - [10/Oct/2023:13:55:44 +0000] "PUT /api/settings HTTP/1.1" 500 0 "-" "curl/7.64.1"
192.168.1.100 - - [10/Oct/2023:13:55:45 +0000] "GET /contact.html HTTP/1.1" 200 3456 "-" "Mozilla/5.0"
"""
    
    # Write sample log to a temporary file
    with open('sample_nginx.log', 'w') as f:
        f.write(sample_log)
    
    # Parse and analyze the log
    parser = NginxLogParser()
    parser.process_file('sample_nginx.log')
    parser.print_summary()
    
    # Clean up
    import os
    os.remove('sample_nginx.log')