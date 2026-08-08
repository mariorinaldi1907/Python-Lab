"""
Date: 2026-08-08
Wrote a parser for nginx access logs that extracts stats like top IPs, status codes, and request patterns — helps me spot weird traffic on my server.
"""

#!/usr/bin/env python3
"""
Nginx access log parser and analyzer.
Parses standard nginx combined log format and generates useful statistics.
"""

import re
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Optional


class NginxLogEntry:
    """Represents a single parsed nginx log line."""
    
    # Regex for nginx combined log format
    # Example: 192.168.1.1 - - [10/Oct/2023:13:55:36 +0000] "GET /api/users HTTP/1.1" 200 1234 "https://example.com" "Mozilla/5.0..."
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d\.]+) - - \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\w+) (?P<path>[^\s]+) HTTP/[\d\.]+" '
        r'(?P<status>\d{3}) (?P<size>\d+) '
        r'"(?P<referrer>[^"]*)" "(?P<user_agent>[^"]*)"'
    )
    
    def __init__(self, line: str):
        """
        Parse a single log line.
        
        Args:
            line: Raw log line from nginx access log
        """
        self.raw = line.strip()
        self.parsed = self._parse()
    
    def _parse(self) -> Optional[Dict]:
        """Extract fields from log line using regex."""
        match = self.LOG_PATTERN.match(self.raw)
        if not match:
            return None
        
        data = match.groupdict()
        # Convert status and size to integers for easier analysis
        data['status'] = int(data['status'])
        data['size'] = int(data['size'])
        
        # Parse timestamp into datetime object
        # Format: 10/Oct/2023:13:55:36 +0000
        try:
            data['datetime'] = datetime.strptime(
                data['timestamp'].split()[0], 
                '%d/%b/%Y:%H:%M:%S'
            )
        except ValueError:
            data['datetime'] = None
        
        return data
    
    def is_valid(self) -> bool:
        """Check if the log line was successfully parsed."""
        return self.parsed is not None


class NginxLogAnalyzer:
    """Analyzes nginx access logs and generates statistics."""
    
    def __init__(self):
        """Initialize empty analyzer."""
        self.entries: List[NginxLogEntry] = []
        self.ip_counter = Counter()
        self.status_counter = Counter()
        self.path_counter = Counter()
        self.method_counter = Counter()
        self.total_bytes = 0
        self.hourly_requests = defaultdict(int)
    
    def parse_file(self, filepath: str) -> None:
        """
        Read and parse an nginx log file.
        
        Args:
            filepath: Path to the nginx access log file
        """
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                entry = NginxLogEntry(line)
                if entry.is_valid():
                    self.entries.append(entry)
                    self._update_stats(entry)
    
    def parse_lines(self, lines: List[str]) -> None:
        """
        Parse a list of log lines directly.
        
        Args:
            lines: List of raw log line strings
        """
        for line in lines:
            entry = NginxLogEntry(line)
            if entry.is_valid():
                self.entries.append(entry)
                self._update_stats(entry)
    
    def _update_stats(self, entry: NginxLogEntry) -> None:
        """Update internal counters with data from a parsed entry."""
        data = entry.parsed
        self.ip_counter[data['ip']] += 1
        self.status_counter[data['status']] += 1
        self.path_counter[data['path']] += 1
        self.method_counter[data['method']] += 1
        self.total_bytes += data['size']
        
        # Track requests by hour if we have a valid datetime
        if data['datetime']:
            hour = data['datetime'].hour
            self.hourly_requests[hour] += 1
    
    def get_summary(self) -> str:
        """Generate a human-readable summary of the log analysis."""
        lines = []
        lines.append("=" * 60)
        lines.append("NGINX LOG ANALYSIS SUMMARY")
        lines.append("=" * 60)
        lines.append(f"Total requests parsed: {len(self.entries)}")
        lines.append(f"Total bandwidth: {self.total_bytes / (1024**2):.2f} MB")
        lines.append("")
        
        lines.append("Top 5 IP addresses:")
        for ip, count in self.ip_counter.most_common(5):
            lines.append(f"  {ip:15s} - {count:4d} requests")
        lines.append("")
        
        lines.append("Status code distribution:")
        for status in sorted(self.status_counter.keys()):
            count = self.status_counter[status]
            lines.append(f"  {status} - {count:4d} requests")
        lines.append("")
        
        lines.append("Top 5 requested paths:")
        for path, count in self.path_counter.most_common(5):
            # Truncate long paths for readability
            display_path = path[:45] + "..." if len(path) > 45 else path
            lines.append(f"  {display_path:48s} - {count:4d}")
        lines.append("")
        
        lines.append("HTTP methods:")
        for method, count in self.method_counter.most_common():
            lines.append(f"  {method:6s} - {count:4d} requests")
        
        return "\n".join(lines)


if __name__ == "__main__":
    # Demo with some realistic fake log data
    sample_logs = [
        '192.168.1.100 - - [15/Dec/2023:10:23:45 +0000] "GET /index.html HTTP/1.1" 200 2345 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"',
        '192.168.1.101 - - [15/Dec/2023:10:24:12 +0000] "POST /api/login HTTP/1.1" 200 156 "https://example.com/login" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"',
        '10.0.0.5 - - [15/Dec/2023:10:25:33 +0000] "GET /static/style.css HTTP/1.1" 304 0 "https://example.com/" "Mozilla/5.0"',
        '192.168.1.100 - - [15/Dec/2023:10:26:01 +0000] "GET /api/users/123 HTTP/1.1" 200 8192 "-" "curl/7.68.0"',
        '203.0.113.42 - - [15/Dec/2023:10:27:15 +0000] "GET /admin HTTP/1.1" 403 278 "-" "BadBot/1.0"',
        '192.168.1.102 - - [15/Dec/2023:10:28:45 +0000] "GET /favicon.ico HTTP/1.1" 404 153 "https://example.com/" "Mozilla/5.0"',
        '192.168.1.100 - - [15/Dec/2023:10:29:22 +0000] "DELETE /api/users/456 HTTP/1.1" 204 0 "-" "PostmanRuntime/7.32.1"',
        '10.0.0.5 - - [15/Dec/2023:10:30:01 +0000] "GET /api/health HTTP/1.1" 200 45 "-" "kube-probe/1.24"',
        '192.168.1.101 - - [15/Dec/2023:10:31:18 +0000] "POST /api/data HTTP/1.1" 201 512 "https://example.com/dashboard" "Mozilla/5.0"',
        '203.0.113.42 - - [15/Dec/2023:10:32:05 +0000] "GET /../../../etc/passwd HTTP/1.1" 400 166 "-" "BadBot/1.0"',
    ]
    
    print("Analyzing nginx access logs...\n")
    
    analyzer = NginxLogAnalyzer()
    analyzer.parse_lines(sample_logs)
    
    print(analyzer.get_summary())