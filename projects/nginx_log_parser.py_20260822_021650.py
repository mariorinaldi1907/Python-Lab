"""
Date: 2026-08-22
Wrote a parser for nginx/apache-style access logs that extracts request patterns, computes response time statistics, and identifies slow endpoints — helps me debug my side projects.
"""

#!/usr/bin/env python3
"""
Nginx/Apache access log parser with response time analytics.

Parses common log format lines and computes statistics like request counts,
response time percentiles, and status code distributions per endpoint.
"""

import re
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple


class LogEntry:
    """Represents a single parsed log entry."""
    
    def __init__(self, ip: str, timestamp: str, method: str, path: str, 
                 status: int, size: int, response_time: float):
        """
        Initialize a log entry with parsed fields.
        
        Args:
            ip: Client IP address
            timestamp: Request timestamp string
            method: HTTP method (GET, POST, etc.)
            path: Request path/endpoint
            status: HTTP status code
            size: Response size in bytes
            response_time: Response time in milliseconds
        """
        self.ip = ip
        self.timestamp = timestamp
        self.method = method
        self.path = path
        self.status = status
        self.size = size
        self.response_time = response_time


class NginxLogParser:
    """Parses nginx access logs and computes endpoint statistics."""
    
    # Regex for combined log format with response time appended
    # Example: 192.168.1.1 - - [10/Oct/2023:13:55:36 +0000] "GET /api/users HTTP/1.1" 200 1234 0.042
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d.]+) - - \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\w+) (?P<path>[^\s]+) HTTP/[\d.]+" '
        r'(?P<status>\d+) (?P<size>\d+)(?: (?P<response_time>[\d.]+))?'
    )
    
    def __init__(self):
        """Initialize the parser with empty data structures."""
        self.entries: List[LogEntry] = []
        # Using defaultdict because it's cleaner than checking if key exists
        self.endpoint_stats: Dict[str, List[float]] = defaultdict(list)
        self.status_counts: Dict[int, int] = defaultdict(int)
    
    def parse_line(self, line: str) -> LogEntry | None:
        """
        Parse a single log line into a LogEntry object.
        
        Args:
            line: Raw log line string
            
        Returns:
            LogEntry if parsing succeeds, None otherwise
        """
        match = self.LOG_PATTERN.match(line.strip())
        if not match:
            return None
        
        data = match.groupdict()
        
        # Some logs might not have response time; default to 0
        response_time = float(data.get('response_time') or 0)
        
        return LogEntry(
            ip=data['ip'],
            timestamp=data['timestamp'],
            method=data['method'],
            path=data['path'],
            status=int(data['status']),
            size=int(data['size']),
            response_time=response_time
        )
    
    def parse_file(self, filepath: str) -> None:
        """
        Parse an entire log file and populate internal stats.
        
        Args:
            filepath: Path to the log file
        """
        with open(filepath, 'r') as f:
            for line in f:
                entry = self.parse_line(line)
                if entry:
                    self.entries.append(entry)
                    self.endpoint_stats[entry.path].append(entry.response_time)
                    self.status_counts[entry.status] += 1
    
    def percentile(self, values: List[float], p: int) -> float:
        """
        Calculate the p-th percentile of a list of values.
        
        Args:
            values: List of numeric values
            p: Percentile (0-100)
            
        Returns:
            The value at the p-th percentile
        """
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int(len(sorted_values) * p / 100)
        # Clamp to valid index range
        index = min(index, len(sorted_values) - 1)
        return sorted_values[index]
    
    def endpoint_summary(self) -> List[Tuple[str, Dict[str, float]]]:
        """
        Generate summary statistics for each endpoint.
        
        Returns:
            List of tuples: (endpoint, stats_dict)
            Stats include count, p50, p95, p99, and max response times
        """
        summary = []
        
        for endpoint, times in self.endpoint_stats.items():
            stats = {
                'count': len(times),
                'p50': self.percentile(times, 50),
                'p95': self.percentile(times, 95),
                'p99': self.percentile(times, 99),
                'max': max(times) if times else 0
            }
            summary.append((endpoint, stats))
        
        # Sort by request count descending — most hit endpoints first
        summary.sort(key=lambda x: x[1]['count'], reverse=True)
        return summary
    
    def print_report(self) -> None:
        """Print a formatted report of log analysis."""
        print(f"=== Log Analysis Report ===")
        print(f"Total requests: {len(self.entries)}\n")
        
        print("Status Code Distribution:")
        for status, count in sorted(self.status_counts.items()):
            print(f"  {status}: {count}")
        
        print("\nTop Endpoints (by request count):")
        print(f"{'Endpoint':<40} {'Count':>8} {'P50':>8} {'P95':>8} {'P99':>8} {'Max':>8}")
        print("-" * 88)
        
        for endpoint, stats in self.endpoint_summary()[:10]:  # Top 10
            print(f"{endpoint:<40} {stats['count']:>8} "
                  f"{stats['p50']:>8.3f} {stats['p95']:>8.3f} "
                  f"{stats['p99']:>8.3f} {stats['max']:>8.3f}")


if __name__ == "__main__":
    # Create a sample log file for demonstration
    sample_log = """192.168.1.10 - - [15/Jan/2024:14:23:45 +0000] "GET /api/users HTTP/1.1" 200 1523 0.032
192.168.1.11 - - [15/Jan/2024:14:23:46 +0000] "POST /api/login HTTP/1.1" 200 456 0.089
192.168.1.10 - - [15/Jan/2024:14:23:47 +0000] "GET /api/users HTTP/1.1" 200 1498 0.028
192.168.1.12 - - [15/Jan/2024:14:23:48 +0000] "GET /api/posts HTTP/1.1" 200 8734 0.156
192.168.1.11 - - [15/Jan/2024:14:23:49 +0000] "GET /api/users HTTP/1.1" 200 1501 0.045
192.168.1.13 - - [15/Jan/2024:14:23:50 +0000] "GET /api/posts HTTP/1.1" 200 8821 0.201
192.168.1.10 - - [15/Jan/2024:14:23:51 +0000] "DELETE /api/posts/123 HTTP/1.1" 204 0 0.067
192.168.1.14 - - [15/Jan/2024:14:23:52 +0000] "GET /health HTTP/1.1" 200 15 0.003
192.168.1.11 - - [15/Jan/2024:14:23:53 +0000] "GET /api/users HTTP/1.1" 200 1489 0.031
192.168.1.15 - - [15/Jan/2024:14:23:54 +0000] "GET /api/posts HTTP/1.1" 500 234 0.521"""
    
    # Write sample log to temp file
    with open('/tmp/sample_access.log', 'w') as f:
        f.write(sample_log)
    
    # Parse and analyze
    parser = NginxLogParser()
    parser.parse_file('/tmp/sample_access.log')
    parser.print_report()