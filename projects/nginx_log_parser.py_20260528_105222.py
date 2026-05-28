"""
Date: 2026-05-28
Wrote a parser for nginx access logs that gives me quick insights into traffic patterns and flags potential security issues like brute force attempts.
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
    Parses nginx access logs in combined format and provides traffic analysis.
    
    Combined log format:
    $remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent"
    """
    
    # Regex pattern for nginx combined log format
    # I spent way too long perfecting this regex, but it handles edge cases pretty well
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d\.]+) - (?P<user>\S+) \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\S+) (?P<path>\S+) (?P<protocol>[^"]+)" '
        r'(?P<status>\d+) (?P<bytes>\d+) "(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)"'
    )
    
    def __init__(self):
        """Initialize counters and storage for parsed log data."""
        self.total_requests = 0
        self.status_codes = Counter()
        self.paths = Counter()
        self.ip_requests = defaultdict(int)
        self.method_counts = Counter()
        self.failed_logins = defaultdict(list)  # Track IPs with multiple 401s
        self.errors = []  # Store lines that couldn't be parsed
        
    def parse_line(self, line: str) -> Dict[str, str]:
        """
        Parse a single log line into structured data.
        
        Returns dict with parsed fields or None if parsing fails.
        """
        match = self.LOG_PATTERN.match(line.strip())
        if not match:
            return None
        return match.groupdict()
    
    def analyze_file(self, filepath: str) -> None:
        """
        Read and analyze an entire log file.
        
        This is the main workhorse - reads line by line to keep memory usage low
        even for huge log files.
        """
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                parsed = self.parse_line(line)
                
                if parsed is None:
                    self.errors.append((line_num, line.strip()))
                    continue
                
                self.total_requests += 1
                self.status_codes[parsed['status']] += 1
                self.paths[parsed['path']] += 1
                self.ip_requests[parsed['ip']] += 1
                self.method_counts[parsed['method']] += 1
                
                # Track potential brute force - multiple 401s from same IP
                if parsed['status'] == '401':
                    self.failed_logins[parsed['ip']].append(parsed['timestamp'])
    
    def get_suspicious_ips(self, threshold: int = 5) -> List[Tuple[str, int]]:
        """
        Find IPs with excessive failed auth attempts.
        
        Default threshold of 5 is pretty conservative - adjust based on your use case.
        """
        suspicious = [
            (ip, len(attempts)) 
            for ip, attempts in self.failed_logins.items() 
            if len(attempts) >= threshold
        ]
        return sorted(suspicious, key=lambda x: x[1], reverse=True)
    
    def get_top_paths(self, n: int = 10) -> List[Tuple[str, int]]:
        """Return the N most requested paths."""
        return self.paths.most_common(n)
    
    def get_top_ips(self, n: int = 10) -> List[Tuple[str, int]]:
        """Return the N most active IP addresses."""
        return sorted(self.ip_requests.items(), key=lambda x: x[1], reverse=True)[:n]
    
    def print_summary(self) -> None:
        """Print a human-readable summary of the analysis."""
        print(f"{'='*60}")
        print(f"Nginx Log Analysis Summary")
        print(f"{'='*60}\n")
        
        print(f"Total Requests: {self.total_requests:,}")
        print(f"Parsing Errors: {len(self.errors)}\n")
        
        print("Status Code Distribution:")
        for status, count in sorted(self.status_codes.items()):
            percentage = (count / self.total_requests) * 100
            print(f"  {status}: {count:,} ({percentage:.1f}%)")
        
        print("\nHTTP Methods:")
        for method, count in self.method_counts.most_common():
            print(f"  {method}: {count:,}")
        
        print("\nTop 10 Requested Paths:")
        for path, count in self.get_top_paths(10):
            print(f"  {count:>6,}x  {path}")
        
        print("\nTop 10 Most Active IPs:")
        for ip, count in self.get_top_ips(10):
            print(f"  {count:>6,}x  {ip}")
        
        # Security insights
        suspicious = self.get_suspicious_ips()
        if suspicious:
            print("\n⚠️  Suspicious Activity Detected:")
            print(f"IPs with 5+ failed auth attempts (potential brute force):")
            for ip, attempts in suspicious[:5]:
                print(f"  {ip}: {attempts} failed attempts")
        
        if self.errors:
            print(f"\n⚠️  Warning: {len(self.errors)} lines could not be parsed")


def create_sample_log(filename: str = "sample_nginx.log") -> str:
    """
    Generate a sample nginx log file for testing.
    
    I'm creating this so the demo actually works out of the box.
    """
    sample_logs = [
        '192.168.1.100 - - [10/Jan/2024:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"',
        '192.168.1.100 - - [10/Jan/2024:13:55:37 +0000] "GET /api/users HTTP/1.1" 200 5678 "-" "curl/7.68.0"',
        '10.0.0.50 - admin [10/Jan/2024:13:55:38 +0000] "POST /admin/login HTTP/1.1" 401 89 "-" "Mozilla/5.0"',
        '10.0.0.50 - admin [10/Jan/2024:13:55:39 +0000] "POST /admin/login HTTP/1.1" 401 89 "-" "Mozilla/5.0"',
        '10.0.0.50 - admin [10/Jan/2024:13:55:40 +0000] "POST /admin/login HTTP/1.1" 401 89 "-" "Mozilla/5.0"',
        '10.0.0.50 - admin [10/Jan/2024:13:55:41 +0000] "POST /admin/login HTTP/1.1" 401 89 "-" "Mozilla/5.0"',
        '10.0.0.50 - admin [10/Jan/2024:13:55:42 +0000] "POST /admin/login HTTP/1.1" 401 89 "-" "Mozilla/5.0"',
        '10.0.0.50 - admin [10/Jan/2024:13:55:43 +0000] "POST /admin/login HTTP/1.1" 401 89 "-" "Mozilla/5.0"',
        '192.168.1.101 - - [10/Jan/2024:13:55:44 +0000] "GET /api/data HTTP/1.1" 200 9876 "-" "Python-requests/2.28"',
        '192.168.1.102 - - [10/Jan/2024:13:55:45 +0000] "GET /nonexistent HTTP/1.1" 404 162 "-" "Mozilla/5.0"',
        '192.168.1.100 - - [10/Jan/2024:13:55:46 +0000] "POST /api/submit HTTP/1.1" 201 45 "-" "curl/7.68.0"',
        '192.168.1.100 - - [10/Jan/2024:13:55:47 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"',
        '203.0.113.42 - - [10/Jan/2024:13:55:48 +0000] "GET /wp-admin HTTP/1.1" 404 162 "-" "Suspicious-Bot/1.0"',
    ]
    
    with open(filename, 'w') as f:
        f.write('\n'.join(sample_logs))
    
    return filename


if __name__ == "__main__":
    # Create a sample log file for demonstration
    print("Generating sample nginx log file...\n")
    log_file = create_sample_log()
    
    # Parse and analyze the log
    parser = NginxLogParser()
    parser.analyze_file(log_file)
    
    # Print