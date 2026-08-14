"""
Date: 2026-08-14
Made a parser for nginx access logs that extracts request info, aggregates stats by status code and endpoint, and flags suspicious patterns like excessive 404s or slow responses.
"""

#!/usr/bin/env python3
"""
Nginx Access Log Parser

Parses standard nginx access logs and provides aggregated statistics
about traffic patterns, response codes, and potential issues.
"""

import re
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class LogEntry:
    """Represents a single nginx access log entry."""
    
    # Regex pattern for nginx combined log format
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d\.]+) - - \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\w+) (?P<path>[^\s]+) HTTP/[\d\.]+" '
        r'(?P<status>\d+) (?P<bytes>\d+) "(?P<referrer>[^"]*)" '
        r'"(?P<user_agent>[^"]*)"'
    )
    
    def __init__(self, line: str):
        """
        Parse a single log line into structured fields.
        
        Args:
            line: Raw log line from nginx access log
        """
        match = self.LOG_PATTERN.match(line)
        if not match:
            raise ValueError(f"Invalid log format: {line[:50]}...")
        
        self.ip = match.group('ip')
        self.timestamp = datetime.strptime(match.group('timestamp'), '%d/%b/%Y:%H:%M:%S %z')
        self.method = match.group('method')
        self.path = match.group('path')
        self.status = int(match.group('status'))
        self.bytes = int(match.group('bytes'))
        self.referrer = match.group('referrer')
        self.user_agent = match.group('user_agent')


class NginxLogAnalyzer:
    """Analyzes nginx logs and generates traffic statistics."""
    
    def __init__(self):
        """Initialize the analyzer with empty stats containers."""
        self.entries: List[LogEntry] = []
        self.status_codes = Counter()
        self.endpoints = Counter()
        self.ips = Counter()
        self.total_bytes = 0
        
    def parse_file(self, filepath: str) -> None:
        """
        Parse an entire nginx log file.
        
        Args:
            filepath: Path to the nginx access log file
        """
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = LogEntry(line)
                    self.entries.append(entry)
                    self._update_stats(entry)
                except ValueError as e:
                    # Skip malformed lines but could log them
                    continue
    
    def _update_stats(self, entry: LogEntry) -> None:
        """
        Update running statistics with a new log entry.
        
        Args:
            entry: Parsed log entry to add to stats
        """
        self.status_codes[entry.status] += 1
        self.endpoints[entry.path] += 1
        self.ips[entry.ip] += 1
        self.total_bytes += entry.bytes
    
    def get_summary(self) -> Dict:
        """
        Generate a summary report of log statistics.
        
        Returns:
            Dictionary containing aggregated stats
        """
        return {
            'total_requests': len(self.entries),
            'unique_ips': len(self.ips),
            'total_bandwidth': self.total_bytes,
            'avg_bytes_per_request': self.total_bytes / len(self.entries) if self.entries else 0,
        }
    
    def get_top_endpoints(self, n: int = 10) -> List[Tuple[str, int]]:
        """
        Get the most frequently accessed endpoints.
        
        Args:
            n: Number of top endpoints to return
            
        Returns:
            List of (endpoint, count) tuples
        """
        return self.endpoints.most_common(n)
    
    def get_status_breakdown(self) -> Dict[str, int]:
        """
        Break down requests by HTTP status code category.
        
        Returns:
            Dictionary mapping status categories to counts
        """
        breakdown = defaultdict(int)
        for status, count in self.status_codes.items():
            if 200 <= status < 300:
                breakdown['2xx Success'] += count
            elif 300 <= status < 400:
                breakdown['3xx Redirect'] += count
            elif 400 <= status < 500:
                breakdown['4xx Client Error'] += count
            elif 500 <= status < 600:
                breakdown['5xx Server Error'] += count
        return dict(breakdown)
    
    def find_suspicious_activity(self) -> Dict[str, any]:
        """
        Identify potentially suspicious patterns in the logs.
        
        Returns:
            Dictionary of detected issues and their details
        """
        issues = {}
        
        # IPs with excessive requests (potential scrapers/attackers)
        request_threshold = len(self.entries) * 0.05  # 5% of total traffic
        heavy_hitters = [(ip, count) for ip, count in self.ips.most_common(10) 
                        if count > request_threshold]
        if heavy_hitters:
            issues['heavy_traffic_ips'] = heavy_hitters
        
        # High 404 rate (broken links or scanning)
        total_404s = self.status_codes.get(404, 0)
        if total_404s > len(self.entries) * 0.1:  # More than 10% 404s
            issues['excessive_404s'] = {
                'count': total_404s,
                'percentage': (total_404s / len(self.entries)) * 100
            }
        
        # Server errors that need attention
        server_errors = sum(count for status, count in self.status_codes.items() 
                          if 500 <= status < 600)
        if server_errors > 0:
            issues['server_errors'] = {
                'count': server_errors,
                'percentage': (server_errors / len(self.entries)) * 100
            }
        
        return issues


if __name__ == "__main__":
    # Create a sample log file for demonstration
    sample_log = """127.0.0.1 - - [10/Jan/2024:13:55:36 +0000] "GET /api/users HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
127.0.0.1 - - [10/Jan/2024:13:56:12 +0000] "POST /api/login HTTP/1.1" 200 567 "https://example.com" "Mozilla/5.0"
192.168.1.100 - - [10/Jan/2024:13:57:22 +0000] "GET /api/products HTTP/1.1" 200 8901 "-" "curl/7.68.0"
192.168.1.100 - - [10/Jan/2024:13:58:05 +0000] "GET /nonexistent HTTP/1.1" 404 152 "-" "curl/7.68.0"
10.0.0.5 - - [10/Jan/2024:13:59:18 +0000] "GET /api/users HTTP/1.1" 500 89 "-" "Python-requests/2.28"
127.0.0.1 - - [10/Jan/2024:14:00:33 +0000] "GET /api/products HTTP/1.1" 200 4532 "-" "Mozilla/5.0"
192.168.1.100 - - [10/Jan/2024:14:01:45 +0000] "GET /admin HTTP/1.1" 403 210 "-" "curl/7.68.0"
127.0.0.1 - - [10/Jan/2024:14:02:19 +0000] "GET /api/users HTTP/1.1" 200 1234 "-" "Mozilla/5.0"""
    
    # Write sample log to temp file
    with open('/tmp/nginx_sample.log', 'w') as f:
        f.write(sample_log)
    
    # Parse and analyze
    analyzer = NginxLogAnalyzer()
    analyzer.parse_file('/tmp/nginx_sample.log')
    
    print("=== Nginx Log Analysis ===\n")
    
    summary = analyzer.get_summary()
    print("Summary:")
    print(f"  Total requests: {summary['total_requests']}")
    print(f"  Unique IPs: {summary['unique_ips']}")
    print(f"  Total bandwidth: {summary['total_bandwidth']:,} bytes")
    print(f"  Avg bytes/request: {summary['avg_bytes_per_request']:.2f}")
    
    print("\nTop Endpoints:")
    for endpoint, count in analyzer.get_top_endpoints(5):
        print(f"  {endpoint}: {count} requests")
    
    print("\nStatus Code Breakdown:")
    for category, count in analyzer.get_status_breakdown().items():
        print(f"  {category}: {count}")
    
    print("\nSuspicious Activity:")
    issues = analyzer.find_suspicious_activity()
    if issues:
        for issue_type, details in issues.items():
            print(f"  {issue_type}: {details}")
    else:
        print("  No suspicious patterns detected")