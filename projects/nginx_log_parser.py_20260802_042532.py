"""
Date: 2026-08-02
Wrote a parser for nginx access logs that groups requests by IP, finds error patterns, and flags potential scanning activity based on 404 rates.
"""

#!/usr/bin/env python3
"""
Nginx access log parser — analyzes request patterns, status codes, and potential threats.
Parses standard nginx combined log format and generates stats I actually care about.
"""

import re
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Tuple


class NginxLogParser:
    """
    Parses nginx access logs in combined format and extracts useful metrics.
    Handles malformed lines without crashing because real logs are messy.
    """
    
    # Regex for nginx combined log format — yeah it's ugly but it works
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d\.]+) - (?P<user>\S+) \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\S+) (?P<path>\S+) (?P<protocol>[^"]+)" '
        r'(?P<status>\d{3}) (?P<size>\d+|-) "(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)"'
    )
    
    def __init__(self):
        """Initialize counters and storage for parsed data."""
        self.ip_requests = defaultdict(int)
        self.ip_errors = defaultdict(int)  # Track 4xx/5xx per IP
        self.status_codes = Counter()
        self.paths_requested = Counter()
        self.total_lines = 0
        self.parsed_lines = 0
        self.suspicious_ips = set()  # IPs with high 404 rates
    
    def parse_line(self, line: str) -> Dict[str, str]:
        """
        Parse a single nginx log line into structured data.
        Returns empty dict if line doesn't match expected format.
        """
        match = self.LOG_PATTERN.match(line)
        if match:
            return match.groupdict()
        return {}
    
    def analyze_log_file(self, filepath: str) -> None:
        """
        Read and analyze an nginx log file line by line.
        Updates internal counters and identifies patterns.
        """
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                self.total_lines += 1
                data = self.parse_line(line.strip())
                
                if not data:
                    continue  # Skip malformed lines
                
                self.parsed_lines += 1
                ip = data['ip']
                status = int(data['status'])
                path = data['path']
                
                # Count requests per IP
                self.ip_requests[ip] += 1
                
                # Track errors (4xx and 5xx)
                if status >= 400:
                    self.ip_errors[ip] += 1
                
                self.status_codes[status] += 1
                self.paths_requested[path] += 1
        
        # Flag suspicious IPs — more than 50% error rate and at least 5 requests
        # This usually means someone's scanning for vulnerabilities
        for ip, error_count in self.ip_errors.items():
            total_requests = self.ip_requests[ip]
            if total_requests >= 5 and (error_count / total_requests) > 0.5:
                self.suspicious_ips.add(ip)
    
    def get_top_ips(self, n: int = 10) -> List[Tuple[str, int]]:
        """Return the top N IPs by request count."""
        return self.ip_requests.most_common(n)
    
    def get_top_paths(self, n: int = 10) -> List[Tuple[str, int]]:
        """Return the top N most requested paths."""
        return self.paths_requested.most_common(n)
    
    def get_status_breakdown(self) -> Dict[str, int]:
        """
        Group status codes into categories (2xx, 3xx, 4xx, 5xx).
        More useful than raw counts for quick health checks.
        """
        breakdown = {'2xx': 0, '3xx': 0, '4xx': 0, '5xx': 0, 'other': 0}
        for status, count in self.status_codes.items():
            if 200 <= status < 300:
                breakdown['2xx'] += count
            elif 300 <= status < 400:
                breakdown['3xx'] += count
            elif 400 <= status < 500:
                breakdown['4xx'] += count
            elif 500 <= status < 600:
                breakdown['5xx'] += count
            else:
                breakdown['other'] += count
        return breakdown
    
    def print_report(self) -> None:
        """Print a human-readable analysis report."""
        print("=" * 60)
        print("NGINX LOG ANALYSIS REPORT")
        print("=" * 60)
        print(f"\nTotal lines: {self.total_lines}")
        print(f"Successfully parsed: {self.parsed_lines}")
        print(f"Malformed lines: {self.total_lines - self.parsed_lines}")
        
        print("\n--- STATUS CODE BREAKDOWN ---")
        status_breakdown = self.get_status_breakdown()
        for category, count in sorted(status_breakdown.items()):
            if count > 0:
                print(f"  {category}: {count}")
        
        print("\n--- TOP 5 MOST ACTIVE IPs ---")
        for ip, count in self.get_top_ips(5):
            flag = " [SUSPICIOUS]" if ip in self.suspicious_ips else ""
            print(f"  {ip}: {count} requests{flag}")
        
        print("\n--- TOP 5 REQUESTED PATHS ---")
        for path, count in self.get_top_paths(5):
            print(f"  {path}: {count} requests")
        
        if self.suspicious_ips:
            print("\n--- SUSPICIOUS IPs (high error rate) ---")
            for ip in self.suspicious_ips:
                error_rate = self.ip_errors[ip] / self.ip_requests[ip] * 100
                print(f"  {ip}: {error_rate:.1f}% errors ({self.ip_errors[ip]}/{self.ip_requests[ip]})")
        
        print("=" * 60)


if __name__ == "__main__":
    # Create a sample log file for demonstration
    sample_log = """192.168.1.100 - - [10/Jan/2024:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
192.168.1.101 - - [10/Jan/2024:13:55:37 +0000] "GET /api/users HTTP/1.1" 200 567 "-" "curl/7.68.0"
192.168.1.102 - - [10/Jan/2024:13:55:38 +0000] "GET /admin HTTP/1.1" 404 162 "-" "python-requests/2.25.1"
192.168.1.102 - - [10/Jan/2024:13:55:39 +0000] "GET /wp-admin HTTP/1.1" 404 162 "-" "python-requests/2.25.1"
192.168.1.102 - - [10/Jan/2024:13:55:40 +0000] "GET /.env HTTP/1.1" 404 162 "-" "python-requests/2.25.1"
192.168.1.100 - - [10/Jan/2024:13:55:41 +0000] "POST /api/login HTTP/1.1" 200 89 "-" "Mozilla/5.0"
192.168.1.103 - - [10/Jan/2024:13:55:42 +0000] "GET /dashboard HTTP/1.1" 500 1024 "-" "Mozilla/5.0"
192.168.1.100 - - [10/Jan/2024:13:55:43 +0000] "GET /images/logo.png HTTP/1.1" 200 4567 "https://example.com/" "Mozilla/5.0"
192.168.1.102 - - [10/Jan/2024:13:55:44 +0000] "GET /phpMyAdmin HTTP/1.1" 404 162 "-" "python-requests/2.25.1"
192.168.1.102 - - [10/Jan/2024:13:55:45 +0000] "GET /config.php HTTP/1.1" 404 162 "-" "python-requests/2.25.1"
malformed log line here that won't parse
192.168.1.101 - - [10/Jan/2024:13:55:46 +0000] "GET /api/products HTTP/1.1" 200 2345 "-" "curl/7.68.0"
192.168.1.100 - - [10/Jan/2024:13:55:47 +0000] "GET /about HTTP/1.1" 200 678 "-" "Mozilla/5.0"
"""
    
    # Write sample log to a temp file
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        f.write(sample_log)
        temp_log_path = f.name
    
    try:
        # Parse and analyze the log
        parser = NginxLogParser()
        parser.analyze_log_file(temp_log_path