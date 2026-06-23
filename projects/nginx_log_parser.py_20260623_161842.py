"""
Date: 2026-06-23
Wrote a parser for nginx access logs to analyze traffic patterns, count status codes, and flag potential security issues like port scans or SQL injection attempts.
"""

#!/usr/bin/env python3
"""
Nginx Access Log Parser
Parses standard nginx access logs and extracts useful metrics.
"""

import re
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Optional


class NginxLogEntry:
    """Represents a single line from an nginx access log."""
    
    # Regex pattern for common nginx log format
    # Example: 192.168.1.1 - - [10/Oct/2000:13:55:36 -0700] "GET /index.html HTTP/1.0" 200 2326
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d\.]+) - (?P<user>[\w-]+) \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\w+) (?P<path>[^\s]+) HTTP/[\d\.]+" '
        r'(?P<status>\d+) (?P<size>\d+)'
    )
    
    def __init__(self, line: str):
        """Parse a single log line into structured fields."""
        match = self.LOG_PATTERN.match(line)
        if not match:
            raise ValueError(f"Invalid log format: {line}")
        
        self.ip = match.group('ip')
        self.user = match.group('user')
        self.timestamp_str = match.group('timestamp')
        self.method = match.group('method')
        self.path = match.group('path')
        self.status = int(match.group('status'))
        self.size = int(match.group('size'))
        
        # Parse timestamp - nginx default is like "10/Oct/2000:13:55:36 -0700"
        try:
            self.timestamp = datetime.strptime(
                self.timestamp_str.split()[0], 
                '%d/%b/%Y:%H:%M:%S'
            )
        except ValueError:
            self.timestamp = None


class LogAnalyzer:
    """Analyzes nginx access logs for patterns and potential security issues."""
    
    def __init__(self):
        """Initialize counters and tracking structures."""
        self.entries: List[NginxLogEntry] = []
        self.status_codes = Counter()
        self.ip_requests = defaultdict(int)
        self.path_requests = Counter()
        self.suspicious_ips = set()
        
    def parse_file(self, filepath: str) -> None:
        """Read and parse an entire log file."""
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    entry = NginxLogEntry(line)
                    self.entries.append(entry)
                    self._update_metrics(entry)
                except ValueError as e:
                    # In real usage, might want to log these, but for now just skip
                    pass
    
    def _update_metrics(self, entry: NginxLogEntry) -> None:
        """Update internal counters based on a log entry."""
        self.status_codes[entry.status] += 1
        self.ip_requests[entry.ip] += 1
        self.path_requests[entry.path] += 1
        
        # Flag suspicious patterns
        if self._is_suspicious(entry):
            self.suspicious_ips.add(entry.ip)
    
    def _is_suspicious(self, entry: NginxLogEntry) -> bool:
        """
        Detect potentially malicious requests.
        This is a simple heuristic — real security tools are way more sophisticated.
        """
        path_lower = entry.path.lower()
        
        # Common attack patterns
        sql_injection_indicators = ['union', 'select', 'drop', 'insert', '--', 'or 1=1']
        path_traversal = ['../', '..\\']
        
        for indicator in sql_injection_indicators:
            if indicator in path_lower:
                return True
        
        for pattern in path_traversal:
            if pattern in entry.path:
                return True
        
        # Excessive 404s from same IP might indicate scanning
        if entry.status == 404 and self.ip_requests[entry.ip] > 20:
            return True
            
        return False
    
    def generate_report(self) -> Dict:
        """
        Generate a summary report of log analysis.
        Returns a dict because it's easy to extend or serialize to JSON.
        """
        total_requests = len(self.entries)
        
        # Find top offenders
        top_ips = self.ip_requests.most_common(5)
        top_paths = self.path_requests.most_common(5)
        
        # Calculate success vs error rates
        success_count = sum(count for status, count in self.status_codes.items() if 200 <= status < 400)
        error_count = sum(count for status, count in self.status_codes.items() if status >= 400)
        
        return {
            'total_requests': total_requests,
            'status_codes': dict(self.status_codes),
            'success_rate': f"{(success_count / total_requests * 100):.2f}%" if total_requests > 0 else "0%",
            'error_count': error_count,
            'top_ips': [(ip, count) for ip, count in top_ips],
            'top_paths': [(path, count) for path, count in top_paths],
            'suspicious_ips': list(self.suspicious_ips),
            'suspicious_count': len(self.suspicious_ips)
        }
    
    def print_report(self) -> None:
        """Pretty-print the analysis report to console."""
        report = self.generate_report()
        
        print("=" * 60)
        print("NGINX LOG ANALYSIS REPORT")
        print("=" * 60)
        print(f"\nTotal Requests: {report['total_requests']}")
        print(f"Success Rate: {report['success_rate']}")
        print(f"Error Count: {report['error_count']}")
        
        print("\n--- Status Code Distribution ---")
        for status, count in sorted(report['status_codes'].items()):
            print(f"  {status}: {count}")
        
        print("\n--- Top 5 IPs by Request Volume ---")
        for ip, count in report['top_ips']:
            flag = " [SUSPICIOUS]" if ip in report['suspicious_ips'] else ""
            print(f"  {ip}: {count} requests{flag}")
        
        print("\n--- Top 5 Most Requested Paths ---")
        for path, count in report['top_paths']:
            print(f"  {path}: {count}")
        
        if report['suspicious_ips']:
            print(f"\n⚠️  Flagged {report['suspicious_count']} suspicious IP(s):")
            for ip in report['suspicious_ips']:
                print(f"  - {ip}")


if __name__ == "__main__":
    # Demo with synthetic log data since most people don't have nginx logs lying around
    demo_log = """192.168.1.100 - - [10/Jan/2024:10:15:23 -0800] "GET /index.html HTTP/1.1" 200 1234
192.168.1.101 - - [10/Jan/2024:10:16:45 -0800] "GET /api/users HTTP/1.1" 200 5678
192.168.1.102 - - [10/Jan/2024:10:17:01 -0800] "POST /login HTTP/1.1" 302 0
192.168.1.100 - - [10/Jan/2024:10:18:12 -0800] "GET /admin HTTP/1.1" 403 89
192.168.1.103 - - [10/Jan/2024:10:19:33 -0800] "GET /page?id=1 union select * from users-- HTTP/1.1" 200 999
192.168.1.104 - - [10/Jan/2024:10:20:44 -0800] "GET /missing HTTP/1.1" 404 162
192.168.1.100 - - [10/Jan/2024:10:21:05 -0800] "GET /about.html HTTP/1.1" 200 3456
192.168.1.105 - - [10/Jan/2024:10:22:16 -0800] "GET /../../../etc/passwd HTTP/1.1" 404 162
192.168.1.101 - - [10/Jan/2024:10:23:27 -0800] "GET /api/products HTTP/1.1" 500 234"""
    
    # Write demo data to a temp file
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        f.write(demo_log)
        temp_path = f.name
    
    try:
        # Run the analyzer
        analyzer = LogAnalyzer()
        analyzer.parse_file(temp_path)
        analyzer.print_report()
    finally:
        # Clean up temp file
        os.unlink(temp_path)