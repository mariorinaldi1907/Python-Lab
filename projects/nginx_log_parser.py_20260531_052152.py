"""
Date: 2026-05-31
Created a parser for nginx access logs that computes request stats, identifies potential attack patterns, and groups data by endpoint — helps me monitor my personal server.
"""

#!/usr/bin/env python3
"""
Nginx access log parser and analyzer.
Parses standard nginx combined log format and extracts useful metrics.
"""

import re
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Tuple


class NginxLogParser:
    """
    Parses nginx access logs in combined format and extracts statistics.
    
    Combined format example:
    127.0.0.1 - - [10/Oct/2000:13:55:36 -0700] "GET /index.html HTTP/1.0" 200 2326
    """
    
    # Regex for nginx combined log format
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d\.]+) - (?P<user>\S+) \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\S+) (?P<path>\S+) (?P<protocol>[^"]+)" '
        r'(?P<status>\d+) (?P<size>\d+|-)'
    )
    
    def __init__(self):
        """Initialize counters and storage for parsed data."""
        self.requests = []
        self.ip_counter = Counter()
        self.status_counter = Counter()
        self.endpoint_counter = Counter()
        self.method_counter = Counter()
        self.total_bytes = 0
        self.parse_errors = 0
    
    def parse_line(self, line: str) -> Dict[str, str]:
        """
        Parse a single log line into its components.
        
        Returns dict with keys: ip, user, timestamp, method, path, protocol, status, size
        Returns None if line doesn't match expected format.
        """
        match = self.LOG_PATTERN.match(line.strip())
        if not match:
            self.parse_errors += 1
            return None
        
        return match.groupdict()
    
    def parse_file(self, filepath: str) -> None:
        """
        Parse an entire log file and update internal statistics.
        
        I'm reading line-by-line instead of loading everything into memory
        because log files can get massive on production servers.
        """
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                parsed = self.parse_line(line)
                if parsed:
                    self.requests.append(parsed)
                    self.ip_counter[parsed['ip']] += 1
                    self.status_counter[parsed['status']] += 1
                    self.endpoint_counter[parsed['path']] += 1
                    self.method_counter[parsed['method']] += 1
                    
                    # Handle missing size values (represented as '-' in logs)
                    size = parsed['size']
                    if size != '-':
                        self.total_bytes += int(size)
    
    def get_top_ips(self, n: int = 10) -> List[Tuple[str, int]]:
        """Return top N IP addresses by request count."""
        return self.ip_counter.most_common(n)
    
    def get_top_endpoints(self, n: int = 10) -> List[Tuple[str, int]]:
        """Return top N most requested endpoints."""
        return self.endpoint_counter.most_common(n)
    
    def get_status_distribution(self) -> Dict[str, int]:
        """Return counts grouped by HTTP status code."""
        return dict(self.status_counter)
    
    def detect_suspicious_activity(self) -> List[str]:
        """
        Identify potentially suspicious patterns.
        
        This is pretty basic — just looking for high-volume IPs and lots of 4xx errors.
        In a real system I'd add rate limiting detection and path traversal attempts.
        """
        suspicious = []
        
        # Flag IPs with more than 100 requests (arbitrary threshold)
        for ip, count in self.ip_counter.items():
            if count > 100:
                suspicious.append(f"High volume from {ip}: {count} requests")
        
        # Flag IPs with lots of 404s (possible scanning)
        ip_404s = defaultdict(int)
        for req in self.requests:
            if req['status'] == '404':
                ip_404s[req['ip']] += 1
        
        for ip, count in ip_404s.items():
            if count > 20:
                suspicious.append(f"Many 404s from {ip}: {count} not found errors")
        
        return suspicious
    
    def print_summary(self) -> None:
        """Print a formatted summary of parsed log data."""
        print("=" * 60)
        print("NGINX LOG ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"\nTotal requests parsed: {len(self.requests)}")
        print(f"Parse errors: {self.parse_errors}")
        print(f"Total bytes transferred: {self.total_bytes:,}")
        
        print("\n--- HTTP Methods ---")
        for method, count in self.method_counter.most_common():
            print(f"  {method}: {count}")
        
        print("\n--- Status Codes ---")
        for status, count in sorted(self.status_counter.items()):
            print(f"  {status}: {count}")
        
        print("\n--- Top 5 IP Addresses ---")
        for ip, count in self.get_top_ips(5):
            print(f"  {ip}: {count} requests")
        
        print("\n--- Top 5 Endpoints ---")
        for endpoint, count in self.get_top_endpoints(5):
            print(f"  {endpoint}: {count} requests")
        
        suspicious = self.detect_suspicious_activity()
        if suspicious:
            print("\n--- ⚠️  Suspicious Activity Detected ---")
            for item in suspicious:
                print(f"  • {item}")


if __name__ == "__main__":
    # Demo with synthetic log data since most people won't have nginx logs handy
    import tempfile
    import os
    
    # Create sample log data that mimics real nginx logs
    sample_logs = """192.168.1.100 - - [15/Jan/2024:10:23:45 +0000] "GET /index.html HTTP/1.1" 200 1234
192.168.1.100 - - [15/Jan/2024:10:23:46 +0000] "GET /style.css HTTP/1.1" 200 5678
192.168.1.101 - - [15/Jan/2024:10:24:10 +0000] "POST /api/login HTTP/1.1" 200 89
10.0.0.50 - - [15/Jan/2024:10:25:00 +0000] "GET /admin.php HTTP/1.1" 404 162
10.0.0.50 - - [15/Jan/2024:10:25:01 +0000] "GET /wp-admin.php HTTP/1.1" 404 162
10.0.0.50 - - [15/Jan/2024:10:25:02 +0000] "GET /phpmyadmin HTTP/1.1" 404 162
192.168.1.100 - - [15/Jan/2024:10:26:00 +0000] "GET /about.html HTTP/1.1" 200 2048
192.168.1.102 - - [15/Jan/2024:10:27:15 +0000] "GET /contact HTTP/1.1" 200 1500
192.168.1.100 - - [15/Jan/2024:10:28:00 +0000] "GET /favicon.ico HTTP/1.1" 200 512
10.0.0.50 - - [15/Jan/2024:10:29:00 +0000] "GET /config.php HTTP/1.1" 404 162"""
    
    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        f.write(sample_logs)
        temp_path = f.name
    
    try:
        # Parse the log file
        parser = NginxLogParser()
        parser.parse_file(temp_path)
        parser.print_summary()
    finally:
        # Clean up temp file
        os.unlink(temp_path)