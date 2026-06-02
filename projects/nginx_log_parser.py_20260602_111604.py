"""
Date: 2026-06-02
Wrote a parser for nginx access logs that breaks down requests by status code, finds slow endpoints, and flags potential bot traffic.
"""

#!/usr/bin/env python3
"""
Nginx access log parser and analyzer.

Parses standard nginx combined log format and extracts useful metrics like
status code distribution, response times, and potentially suspicious traffic.
"""

import re
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class NginxLogEntry:
    """Represents a single parsed nginx log line."""
    
    def __init__(self, ip: str, timestamp: str, method: str, path: str,
                 status: int, bytes_sent: int, response_time: float,
                 user_agent: str):
        self.ip = ip
        self.timestamp = timestamp
        self.method = method
        self.path = path
        self.status = status
        self.bytes_sent = bytes_sent
        self.response_time = response_time
        self.user_agent = user_agent


class NginxLogParser:
    """
    Parses and analyzes nginx access logs.
    
    Handles the combined log format with an added response time field.
    I've tweaked this to work with my typical nginx config that includes $request_time.
    """
    
    # Regex for nginx combined log format + response time
    # Format: IP - - [timestamp] "METHOD path HTTP/x.x" status bytes "referer" "user-agent" response_time
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d\.]+) - - \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\w+) (?P<path>[^\s]+) HTTP/[\d\.]+" '
        r'(?P<status>\d{3}) (?P<bytes>\d+) '
        r'"[^"]*" "(?P<user_agent>[^"]*)"(?: (?P<response_time>[\d\.]+))?'
    )
    
    def __init__(self):
        self.entries: List[NginxLogEntry] = []
        self.parse_errors = 0
    
    def parse_line(self, line: str) -> Optional[NginxLogEntry]:
        """
        Parse a single log line into a structured entry.
        
        Returns None if the line doesn't match the expected format.
        """
        match = self.LOG_PATTERN.match(line)
        if not match:
            return None
        
        data = match.groupdict()
        
        # Default response time to 0 if not present in logs
        response_time = float(data['response_time']) if data['response_time'] else 0.0
        
        return NginxLogEntry(
            ip=data['ip'],
            timestamp=data['timestamp'],
            method=data['method'],
            path=data['path'],
            status=int(data['status']),
            bytes_sent=int(data['bytes']),
            response_time=response_time,
            user_agent=data['user_agent']
        )
    
    def parse_file(self, filepath: str) -> None:
        """Load and parse an entire log file."""
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                entry = self.parse_line(line.strip())
                if entry:
                    self.entries.append(entry)
                else:
                    self.parse_errors += 1
    
    def get_status_distribution(self) -> Dict[int, int]:
        """Count occurrences of each HTTP status code."""
        return dict(Counter(entry.status for entry in self.entries))
    
    def get_top_paths(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Return the most frequently requested paths."""
        path_counts = Counter(entry.path for entry in self.entries)
        return path_counts.most_common(limit)
    
    def get_slow_requests(self, threshold: float = 1.0) -> List[NginxLogEntry]:
        """
        Find requests that took longer than the threshold (in seconds).
        
        Useful for finding performance bottlenecks in the app.
        """
        return [e for e in self.entries if e.response_time > threshold]
    
    def detect_potential_bots(self, request_threshold: int = 100) -> Dict[str, int]:
        """
        Flag IPs that made an unusually high number of requests.
        
        Not foolproof, but catches obvious scrapers. I usually check these manually
        before adding them to the blocklist.
        """
        ip_counts = Counter(entry.ip for entry in self.entries)
        return {ip: count for ip, count in ip_counts.items() if count > request_threshold}
    
    def generate_report(self) -> str:
        """Create a human-readable summary of the log analysis."""
        total = len(self.entries)
        status_dist = self.get_status_distribution()
        top_paths = self.get_top_paths(5)
        slow_requests = self.get_slow_requests(1.0)
        bots = self.detect_potential_bots(50)
        
        report = [
            "=" * 60,
            "NGINX LOG ANALYSIS REPORT",
            "=" * 60,
            f"\nTotal requests parsed: {total}",
            f"Parse errors: {self.parse_errors}",
            "\n--- Status Code Distribution ---"
        ]
        
        for status in sorted(status_dist.keys()):
            count = status_dist[status]
            percentage = (count / total) * 100
            report.append(f"  {status}: {count} ({percentage:.1f}%)")
        
        report.append("\n--- Top 5 Requested Paths ---")
        for path, count in top_paths:
            report.append(f"  {count:4d} - {path}")
        
        report.append(f"\n--- Slow Requests (>1s) ---")
        report.append(f"  Found {len(slow_requests)} slow requests")
        if slow_requests:
            # Show top 3 slowest
            sorted_slow = sorted(slow_requests, key=lambda e: e.response_time, reverse=True)[:3]
            for entry in sorted_slow:
                report.append(f"  {entry.response_time:.2f}s - {entry.method} {entry.path}")
        
        report.append(f"\n--- Potential Bot Traffic ---")
        if bots:
            report.append(f"  {len(bots)} IPs with >50 requests:")
            for ip, count in sorted(bots.items(), key=lambda x: x[1], reverse=True)[:5]:
                report.append(f"  {ip}: {count} requests")
        else:
            report.append("  No suspicious activity detected")
        
        report.append("\n" + "=" * 60)
        return "\n".join(report)


if __name__ == "__main__":
    # Demo with sample log data that mimics real nginx logs
    sample_log = """192.168.1.100 - - [10/Jan/2024:08:15:23 +0000] "GET /api/users HTTP/1.1" 200 1234 "-" "Mozilla/5.0" 0.045
192.168.1.101 - - [10/Jan/2024:08:15:24 +0000] "GET /index.html HTTP/1.1" 200 5678 "-" "Mozilla/5.0" 0.023
192.168.1.102 - - [10/Jan/2024:08:15:25 +0000] "POST /api/login HTTP/1.1" 401 512 "-" "curl/7.68.0" 0.012
192.168.1.100 - - [10/Jan/2024:08:15:26 +0000] "GET /api/products HTTP/1.1" 200 9876 "-" "Mozilla/5.0" 1.234
192.168.1.103 - - [10/Jan/2024:08:15:27 +0000] "GET /favicon.ico HTTP/1.1" 404 0 "-" "Mozilla/5.0" 0.001
192.168.1.100 - - [10/Jan/2024:08:15:28 +0000] "GET /api/users HTTP/1.1" 200 1234 "-" "bot-scanner/1.0" 0.034
192.168.1.100 - - [10/Jan/2024:08:15:29 +0000] "GET /api/orders HTTP/1.1" 500 2048 "-" "Mozilla/5.0" 2.567"""
    
    # Write sample data to a temp file
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        f.write(sample_log)
        temp_path = f.name
    
    try:
        parser = NginxLogParser()
        parser.parse_file(temp_path)
        print(parser.generate_report())
    finally:
        os.unlink(temp_path)