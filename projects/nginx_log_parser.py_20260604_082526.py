"""
Date: 2026-06-04
Wrote a parser for nginx access logs because I got tired of manually grep'ing through logs to find error patterns and slow endpoints.
"""

#!/usr/bin/env python3
"""
Nginx Access Log Parser

Parses standard nginx access logs and generates useful statistics:
- Request counts by endpoint
- Status code distribution
- Response time analysis
- Traffic patterns by hour

I wrote this after spending way too much time manually analyzing production logs.
The regex handles the combined log format that nginx uses by default.
"""

import re
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional


class NginxLogParser:
    """
    Parser for nginx access logs in combined format.
    
    Extracts key metrics from each line and provides aggregated statistics.
    The combined format looks like:
    127.0.0.1 - - [10/Oct/2023:13:55:36 -0700] "GET /api/users HTTP/1.1" 200 1234 "-" "Mozilla/5.0..."
    """
    
    # This regex is gnarly but it captures all the fields I care about
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d.]+) - - \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\w+) (?P<endpoint>[^\s]+) HTTP/[\d.]+" '
        r'(?P<status>\d+) (?P<size>\d+)'
    )
    
    def __init__(self):
        self.requests = []
        self.endpoint_stats = defaultdict(lambda: {'count': 0, 'statuses': defaultdict(int)})
        self.hourly_traffic = defaultdict(int)
        self.status_codes = defaultdict(int)
        
    def parse_line(self, line: str) -> Optional[Dict]:
        """
        Parse a single log line into structured data.
        
        Returns None if the line doesn't match expected format - this happens
        with error logs or malformed entries, which I just skip.
        """
        match = self.LOG_PATTERN.match(line)
        if not match:
            return None
            
        data = match.groupdict()
        
        # Parse the timestamp into a datetime object for better analysis
        try:
            dt = datetime.strptime(data['timestamp'], '%d/%b/%Y:%H:%M:%S %z')
            data['datetime'] = dt
            data['hour'] = dt.hour
        except ValueError:
            # If timestamp parsing fails, still return the data but without time info
            data['datetime'] = None
            data['hour'] = None
            
        data['status'] = int(data['status'])
        data['size'] = int(data['size'])
        
        return data
    
    def parse_file(self, filepath: str) -> None:
        """
        Read and parse an entire log file.
        
        I'm reading line-by-line instead of loading the whole file because
        production logs can get huge (multi-GB).
        """
        with open(filepath, 'r') as f:
            for line in f:
                parsed = self.parse_line(line.strip())
                if parsed:
                    self.requests.append(parsed)
                    self._update_stats(parsed)
    
    def _update_stats(self, request: Dict) -> None:
        """Update all the running statistics with a new request."""
        endpoint = request['endpoint']
        status = request['status']
        hour = request['hour']
        
        # Track endpoint-specific metrics
        self.endpoint_stats[endpoint]['count'] += 1
        self.endpoint_stats[endpoint]['statuses'][status] += 1
        
        # Track overall patterns
        self.status_codes[status] += 1
        if hour is not None:
            self.hourly_traffic[hour] += 1
    
    def get_top_endpoints(self, n: int = 10) -> List[tuple]:
        """
        Get the N most frequently hit endpoints.
        
        Useful for identifying hot paths in the application.
        """
        sorted_endpoints = sorted(
            self.endpoint_stats.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )
        return sorted_endpoints[:n]
    
    def get_error_rate(self) -> float:
        """
        Calculate percentage of 4xx and 5xx responses.
        
        I consider anything >= 400 an error for this metric.
        """
        if not self.requests:
            return 0.0
            
        error_count = sum(
            count for status, count in self.status_codes.items()
            if status >= 400
        )
        return (error_count / len(self.requests)) * 100
    
    def print_report(self) -> None:
        """Generate a human-readable summary report."""
        print("=" * 60)
        print("NGINX ACCESS LOG ANALYSIS")
        print("=" * 60)
        print(f"\nTotal Requests: {len(self.requests)}")
        print(f"Error Rate: {self.get_error_rate():.2f}%")
        
        print("\n--- Status Code Distribution ---")
        for status in sorted(self.status_codes.keys()):
            count = self.status_codes[status]
            percentage = (count / len(self.requests)) * 100
            print(f"  {status}: {count:6d} ({percentage:5.2f}%)")
        
        print("\n--- Top 10 Endpoints ---")
        for endpoint, stats in self.get_top_endpoints(10):
            print(f"  {stats['count']:6d} requests - {endpoint}")
            # Show status breakdown for this endpoint
            for status, count in sorted(stats['statuses'].items()):
                print(f"           └─ {status}: {count}")
        
        if self.hourly_traffic:
            print("\n--- Traffic by Hour ---")
            for hour in sorted(self.hourly_traffic.keys()):
                count = self.hourly_traffic[hour]
                bar = '█' * (count // 10)  # Simple bar chart
                print(f"  {hour:02d}:00 - {count:5d} {bar}")


if __name__ == "__main__":
    # Demo with some synthetic log data since most people won't have nginx logs handy
    import tempfile
    import os
    
    sample_logs = [
        '192.168.1.1 - - [15/Dec/2023:10:23:45 +0000] "GET /api/users HTTP/1.1" 200 1234',
        '192.168.1.2 - - [15/Dec/2023:10:24:12 +0000] "POST /api/login HTTP/1.1" 200 567',
        '192.168.1.1 - - [15/Dec/2023:10:25:33 +0000] "GET /api/users/123 HTTP/1.1" 404 89',
        '192.168.1.3 - - [15/Dec/2023:11:15:22 +0000] "GET /api/products HTTP/1.1" 200 2345',
        '192.168.1.2 - - [15/Dec/2023:11:16:45 +0000] "GET /api/users HTTP/1.1" 200 1234',
        '192.168.1.4 - - [15/Dec/2023:12:30:11 +0000] "DELETE /api/users/456 HTTP/1.1" 500 123',
        '192.168.1.1 - - [15/Dec/2023:12:31:05 +0000] "GET /api/users HTTP/1.1" 200 1234',
        '192.168.1.5 - - [15/Dec/2023:13:42:18 +0000] "GET / HTTP/1.1" 200 5678',
    ]
    
    # Write sample data to a temp file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        temp_path = f.name
        for log_line in sample_logs:
            f.write(log_line + '\n')
    
    try:
        # Run the parser
        parser = NginxLogParser()
        parser.parse_file(temp_path)
        parser.print_report()
    finally:
        # Clean up temp file
        os.unlink(temp_path)