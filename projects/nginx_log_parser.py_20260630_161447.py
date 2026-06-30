"""
Date: 2026-06-30
Wrote a parser for nginx access logs that breaks down request methods, status codes, and finds the slowest endpoints — helps me debug my side projects quickly.
"""

#!/usr/bin/env python3
"""
nginx_log_parser.py

Parses nginx access logs and extracts useful stats about requests.
I got tired of grepping through logs manually when debugging my deployed apps,
so I built this to quickly see what's actually happening on the server.
"""

import re
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Tuple


class NginxLogParser:
    """
    Parses nginx access logs in the combined format.
    
    Handles the standard format like:
    127.0.0.1 - - [10/Oct/2023:13:55:36 +0000] "GET /api/users HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
    """
    
    # Regex pattern for the combined log format
    # This matches IP, timestamp, method, path, status, bytes, etc.
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d\.]+) - - \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\w+) (?P<path>[^\s]+) HTTP/[\d\.]+" '
        r'(?P<status>\d{3}) (?P<bytes>\d+|-) '
        r'"[^"]*" "(?P<user_agent>[^"]*)"'
    )
    
    def __init__(self):
        """Initialize empty containers for parsed data."""
        self.entries = []
        self.status_counts = Counter()
        self.method_counts = Counter()
        self.path_stats = defaultdict(lambda: {'count': 0, 'total_bytes': 0})
        
    def parse_line(self, line: str) -> Dict:
        """
        Parse a single log line into structured data.
        
        Returns None if the line doesn't match the expected format,
        which is fine — some logs have junk in them.
        """
        match = self.LOG_PATTERN.match(line)
        if not match:
            return None
            
        data = match.groupdict()
        
        # Convert bytes to int, handle the "-" case for no body
        data['bytes'] = int(data['bytes']) if data['bytes'] != '-' else 0
        data['status'] = int(data['status'])
        
        return data
    
    def parse_file(self, filepath: str) -> None:
        """
        Parse an entire log file and populate internal stats.
        
        I decided to keep everything in memory because most log files
        I analyze are small enough (< 100MB). For huge files, I'd need
        to add streaming or sampling.
        """
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                entry = self.parse_line(line.strip())
                if entry:
                    self.entries.append(entry)
                    self._update_stats(entry)
    
    def _update_stats(self, entry: Dict) -> None:
        """Update running statistics with a new log entry."""
        self.status_counts[entry['status']] += 1
        self.method_counts[entry['method']] += 1
        
        # Track per-path metrics
        path = entry['path']
        self.path_stats[path]['count'] += 1
        self.path_stats[path]['total_bytes'] += entry['bytes']
    
    def get_status_summary(self) -> Dict[int, int]:
        """Get counts of each HTTP status code."""
        return dict(self.status_counts)
    
    def get_method_summary(self) -> Dict[str, int]:
        """Get counts of each HTTP method (GET, POST, etc.)."""
        return dict(self.method_counts)
    
    def get_top_paths(self, n: int = 10) -> List[Tuple[str, int]]:
        """
        Get the N most frequently requested paths.
        
        Useful for seeing what endpoints get hammered the most.
        """
        sorted_paths = sorted(
            self.path_stats.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )
        return [(path, stats['count']) for path, stats in sorted_paths[:n]]
    
    def get_bandwidth_hogs(self, n: int = 5) -> List[Tuple[str, int]]:
        """
        Find paths that serve the most bytes.
        
        I added this because I once had a single endpoint serving huge
        JSON blobs that was killing my server bandwidth.
        """
        sorted_paths = sorted(
            self.path_stats.items(),
            key=lambda x: x[1]['total_bytes'],
            reverse=True
        )
        return [(path, stats['total_bytes']) for path, stats in sorted_paths[:n]]
    
    def print_summary(self) -> None:
        """Print a nice human-readable summary of the parsed logs."""
        print(f"=== Nginx Log Analysis ===")
        print(f"Total requests parsed: {len(self.entries)}\n")
        
        print("Status Code Distribution:")
        for status, count in sorted(self.status_counts.items()):
            print(f"  {status}: {count}")
        
        print("\nHTTP Methods:")
        for method, count in sorted(self.method_counts.items()):
            print(f"  {method}: {count}")
        
        print("\nTop 10 Requested Paths:")
        for i, (path, count) in enumerate(self.get_top_paths(10), 1):
            print(f"  {i}. {path} ({count} requests)")
        
        print("\nTop 5 Bandwidth Consumers:")
        for i, (path, bytes_total) in enumerate(self.get_bandwidth_hogs(5), 1):
            mb = bytes_total / (1024 * 1024)
            print(f"  {i}. {path} ({mb:.2f} MB)")


def create_sample_log(filepath: str) -> None:
    """
    Create a sample nginx log file for testing.
    
    This generates fake but realistic-looking log entries so the demo
    actually works without needing a real log file.
    """
    sample_lines = [
        '192.168.1.100 - - [15/Mar/2024:10:23:45 +0000] "GET /api/users HTTP/1.1" 200 1543 "-" "Mozilla/5.0"',
        '192.168.1.101 - - [15/Mar/2024:10:23:46 +0000] "POST /api/login HTTP/1.1" 200 234 "-" "curl/7.68.0"',
        '192.168.1.102 - - [15/Mar/2024:10:23:47 +0000] "GET /api/users HTTP/1.1" 200 1543 "-" "Mozilla/5.0"',
        '192.168.1.103 - - [15/Mar/2024:10:23:48 +0000] "GET /static/app.js HTTP/1.1" 200 45234 "-" "Mozilla/5.0"',
        '192.168.1.104 - - [15/Mar/2024:10:23:49 +0000] "GET /api/posts HTTP/1.1" 200 8732 "-" "Mozilla/5.0"',
        '192.168.1.105 - - [15/Mar/2024:10:23:50 +0000] "GET /api/invalid HTTP/1.1" 404 178 "-" "curl/7.68.0"',
        '192.168.1.106 - - [15/Mar/2024:10:23:51 +0000] "POST /api/users HTTP/1.1" 201 423 "-" "Mozilla/5.0"',
        '192.168.1.107 - - [15/Mar/2024:10:23:52 +0000] "GET /api/users HTTP/1.1" 200 1543 "-" "Mozilla/5.0"',
        '192.168.1.108 - - [15/Mar/2024:10:23:53 +0000] "DELETE /api/users/42 HTTP/1.1" 204 - "-" "curl/7.68.0"',
        '192.168.1.109 - - [15/Mar/2024:10:23:54 +0000] "GET /static/app.js HTTP/1.1" 200 45234 "-" "Mozilla/5.0"',
        '192.168.1.110 - - [15/Mar/2024:10:23:55 +0000] "GET /api/posts HTTP/1.1" 500 89 "-" "Mozilla/5.0"',
    ]
    
    with open(filepath, 'w') as f:
        f.write('\n'.join(sample_lines))


if __name__ == "__main__":
    # Create a sample log file for demonstration
    sample_log_path = "sample_nginx.log"
    print("Creating sample log file...")
    create_sample_log(sample_log_path)
    
    # Parse the log file
    parser = NginxLogParser()
    print(f"Parsing {sample_log_path}...\n")
    parser.parse_file(sample_log_path)
    
    # Print the analysis
    parser.print_summary()
    
    print("\n(Sample log file created: sample_nginx.log)")