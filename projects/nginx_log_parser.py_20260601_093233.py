"""
Date: 2026-06-01
Built a parser for nginx access logs that breaks down traffic by endpoint, method, and status code — helps me understand my server usage patterns without opening Splunk.
"""

#!/usr/bin/env python3
"""
Nginx access log parser - extracts traffic patterns and response statistics.
Parses standard nginx combined log format and generates a summary report.
"""

import re
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Tuple


class NginxLogParser:
    """
    Parses nginx access logs and generates traffic analytics.
    
    Handles the combined log format which looks like:
    127.0.0.1 - - [10/Oct/2023:13:55:36 +0000] "GET /api/users HTTP/1.1" 200 1234 "-" "Mozilla/5.0..."
    """
    
    # Regex pattern for nginx combined log format
    # I spent way too long getting this right, but it handles most edge cases now
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d\.]+) - - \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\w+) (?P<path>[^\s]+) HTTP/[\d\.]+" '
        r'(?P<status>\d{3}) (?P<bytes>\d+|-) '
        r'"(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)"'
    )
    
    def __init__(self):
        self.requests = []
        self.endpoints = defaultdict(int)
        self.status_codes = Counter()
        self.methods = Counter()
        self.total_bytes = 0
        self.errors = []  # Keep track of lines we couldn't parse
        
    def parse_line(self, line: str) -> Dict:
        """
        Parse a single log line into structured data.
        Returns None if the line doesn't match the expected format.
        """
        match = self.LOG_PATTERN.match(line.strip())
        if not match:
            return None
            
        data = match.groupdict()
        
        # Convert bytes to int, handle "-" which means no data sent
        data['bytes'] = 0 if data['bytes'] == '-' else int(data['bytes'])
        data['status'] = int(data['status'])
        
        return data
    
    def parse_file(self, filepath: str) -> None:
        """
        Parse an entire log file and accumulate statistics.
        I'm reading line by line instead of loading everything to memory
        because production logs can get huge.
        """
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue
                    
                data = self.parse_line(line)
                if data is None:
                    self.errors.append((line_num, line.strip()))
                    continue
                
                self.requests.append(data)
                self.endpoints[data['path']] += 1
                self.status_codes[data['status']] += 1
                self.methods[data['method']] += 1
                self.total_bytes += data['bytes']
    
    def get_top_endpoints(self, n: int = 10) -> List[Tuple[str, int]]:
        """Return the N most frequently accessed endpoints."""
        return sorted(self.endpoints.items(), key=lambda x: x[1], reverse=True)[:n]
    
    def get_error_rate(self) -> float:
        """Calculate percentage of 4xx and 5xx responses."""
        if not self.requests:
            return 0.0
        
        errors = sum(count for status, count in self.status_codes.items() 
                    if status >= 400)
        return (errors / len(self.requests)) * 100
    
    def generate_report(self) -> str:
        """
        Generate a human-readable summary report.
        This is what I actually look at when debugging traffic issues.
        """
        if not self.requests:
            return "No valid log entries found."
        
        report_lines = [
            "=" * 60,
            "NGINX ACCESS LOG ANALYSIS",
            "=" * 60,
            f"\nTotal requests: {len(self.requests)}",
            f"Total bytes served: {self.total_bytes:,} ({self.total_bytes / (1024**2):.2f} MB)",
            f"Parse errors: {len(self.errors)}",
            f"\nHTTP METHODS:",
        ]
        
        for method, count in self.methods.most_common():
            percentage = (count / len(self.requests)) * 100
            report_lines.append(f"  {method:6s}: {count:6d} ({percentage:5.1f}%)")
        
        report_lines.append(f"\nSTATUS CODE DISTRIBUTION:")
        for status in sorted(self.status_codes.keys()):
            count = self.status_codes[status]
            percentage = (count / len(self.requests)) * 100
            report_lines.append(f"  {status}: {count:6d} ({percentage:5.1f}%)")
        
        report_lines.append(f"\nERROR RATE (4xx/5xx): {self.get_error_rate():.2f}%")
        
        report_lines.append(f"\nTOP 10 ENDPOINTS:")
        for path, count in self.get_top_endpoints(10):
            percentage = (count / len(self.requests)) * 100
            # Truncate long paths so the report doesn't get messy
            display_path = path if len(path) <= 50 else path[:47] + "..."
            report_lines.append(f"  {count:5d} ({percentage:5.1f}%) {display_path}")
        
        return "\n".join(report_lines)


def create_sample_log(filepath: str) -> None:
    """
    Generate a sample nginx log file for testing.
    This creates realistic-looking log entries so the demo actually works.
    """
    sample_entries = [
        '192.168.1.100 - - [15/Jan/2024:10:23:45 +0000] "GET /api/users HTTP/1.1" 200 1523 "-" "Mozilla/5.0"',
        '192.168.1.101 - - [15/Jan/2024:10:24:12 +0000] "POST /api/login HTTP/1.1" 200 456 "-" "curl/7.68.0"',
        '192.168.1.102 - - [15/Jan/2024:10:24:55 +0000] "GET /api/users/123 HTTP/1.1" 404 78 "-" "Mozilla/5.0"',
        '192.168.1.100 - - [15/Jan/2024:10:25:33 +0000] "GET / HTTP/1.1" 200 2048 "-" "Mozilla/5.0"',
        '192.168.1.103 - - [15/Jan/2024:10:26:01 +0000] "GET /api/products HTTP/1.1" 200 3456 "-" "Python-requests/2.28.0"',
        '192.168.1.101 - - [15/Jan/2024:10:27:15 +0000] "DELETE /api/users/456 HTTP/1.1" 403 124 "-" "curl/7.68.0"',
        '192.168.1.104 - - [15/Jan/2024:10:28:42 +0000] "GET /api/users HTTP/1.1" 200 1523 "-" "Mozilla/5.0"',
        '192.168.1.105 - - [15/Jan/2024:10:29:33 +0000] "POST /api/orders HTTP/1.1" 201 892 "-" "Mozilla/5.0"',
        '192.168.1.102 - - [15/Jan/2024:10:30:12 +0000] "GET /favicon.ico HTTP/1.1" 404 23 "-" "Mozilla/5.0"',
        '192.168.1.100 - - [15/Jan/2024:10:31:45 +0000] "GET /api/products HTTP/1.1" 500 156 "-" "Mozilla/5.0"',
    ]
    
    with open(filepath, 'w') as f:
        for entry in sample_entries:
            f.write(entry + '\n')


if __name__ == "__main__":
    # Create a sample log file to demonstrate the parser
    sample_log_path = "sample_nginx.log"
    print("Creating sample nginx log file...")
    create_sample_log(sample_log_path)
    
    # Parse the log and generate report
    print(f"\nParsing {sample_log_path}...\n")
    parser = NginxLogParser()
    parser.parse_file(sample_log_path)
    
    # Print the analysis report
    print(parser.generate_report())
    
    # Show any parse errors if they occurred
    if parser.errors:
        print("\n" + "=" * 60)
        print("PARSE ERRORS:")
        for line_num, line in parser.errors[:5]:  # Show first 5 errors
            print(f"  Line {line_num}: {line[:70]}...")