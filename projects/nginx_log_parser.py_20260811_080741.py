"""
Date: 2026-08-11
Wrote a parser for nginx access logs to analyze traffic patterns, spot slow requests, and generate a quick summary report — helps me debug my hobby projects faster.
"""

#!/usr/bin/env python3
"""
nginx access log parser
parses standard nginx combined log format and generates some useful stats
"""

import re
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Optional


class NginxLogEntry:
    """
    Represents a single nginx access log line.
    Parses the combined log format which is what I use for all my servers.
    """
    
    # regex for nginx combined log format
    # example: 192.168.1.1 - - [01/Jan/2024:12:00:00 +0000] "GET /api/users HTTP/1.1" 200 1234 "-" "Mozilla/5.0..."
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d\.]+) - - \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\w+) (?P<path>[^\s]+) HTTP/[\d\.]+" '
        r'(?P<status>\d+) (?P<size>\d+) "(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)"'
    )
    
    def __init__(self, line: str):
        """Parse a single log line into structured data."""
        match = self.LOG_PATTERN.match(line)
        if not match:
            raise ValueError(f"Could not parse log line: {line[:50]}...")
        
        data = match.groupdict()
        self.ip = data['ip']
        self.timestamp = datetime.strptime(data['timestamp'], '%d/%b/%Y:%H:%M:%S %z')
        self.method = data['method']
        self.path = data['path']
        self.status = int(data['status'])
        self.size = int(data['size'])
        self.referer = data['referer'] if data['referer'] != '-' else None
        self.user_agent = data['user_agent']
    
    def is_error(self) -> bool:
        """Check if this request resulted in an error (4xx or 5xx)."""
        return self.status >= 400
    
    def __repr__(self):
        return f"<LogEntry {self.method} {self.path} {self.status}>"


class NginxLogAnalyzer:
    """
    Analyzes a collection of nginx log entries and generates stats.
    I built this because I kept manually grepping logs to find slow endpoints.
    """
    
    def __init__(self):
        """Initialize empty analyzer."""
        self.entries: List[NginxLogEntry] = []
    
    def parse_file(self, filepath: str) -> None:
        """
        Read and parse a log file.
        Silently skips lines that don't match the expected format.
        """
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = NginxLogEntry(line)
                    self.entries.append(entry)
                except ValueError:
                    # skip malformed lines - sometimes logs get corrupted
                    continue
    
    def get_status_distribution(self) -> Counter:
        """Count how many requests returned each status code."""
        return Counter(entry.status for entry in self.entries)
    
    def get_top_paths(self, n: int = 10) -> List[tuple]:
        """
        Find the most frequently requested paths.
        Returns list of (path, count) tuples.
        """
        path_counts = Counter(entry.path for entry in self.entries)
        return path_counts.most_common(n)
    
    def get_error_paths(self) -> List[NginxLogEntry]:
        """Get all requests that resulted in 4xx or 5xx errors."""
        return [entry for entry in self.entries if entry.is_error()]
    
    def get_bandwidth_by_path(self) -> Dict[str, int]:
        """
        Calculate total bytes served per path.
        Useful for finding which endpoints consume the most bandwidth.
        """
        bandwidth = defaultdict(int)
        for entry in self.entries:
            bandwidth[entry.path] += entry.size
        return dict(sorted(bandwidth.items(), key=lambda x: x[1], reverse=True))
    
    def get_unique_ips(self) -> int:
        """Count unique IP addresses in the logs."""
        return len(set(entry.ip for entry in self.entries))
    
    def generate_report(self) -> str:
        """
        Create a human-readable summary report.
        This is what I actually wanted when I started building this tool.
        """
        if not self.entries:
            return "No log entries to analyze."
        
        report_lines = [
            "=" * 60,
            "nginx Access Log Analysis Report",
            "=" * 60,
            f"Total requests: {len(self.entries)}",
            f"Unique IPs: {self.get_unique_ips()}",
            "",
            "Status Code Distribution:",
        ]
        
        status_dist = self.get_status_distribution()
        for status, count in sorted(status_dist.items()):
            percentage = (count / len(self.entries)) * 100
            report_lines.append(f"  {status}: {count:6d} ({percentage:5.1f}%)")
        
        report_lines.extend([
            "",
            "Top 5 Most Requested Paths:",
        ])
        
        for path, count in self.get_top_paths(5):
            report_lines.append(f"  {count:6d} - {path}")
        
        error_entries = self.get_error_paths()
        if error_entries:
            report_lines.extend([
                "",
                f"Errors Found: {len(error_entries)} requests",
                "Sample error paths (first 5):",
            ])
            for entry in error_entries[:5]:
                report_lines.append(f"  [{entry.status}] {entry.method} {entry.path}")
        
        report_lines.append("=" * 60)
        return "\n".join(report_lines)


if __name__ == "__main__":
    # demo with sample log data
    # these are realistic log lines from one of my actual servers (IPs changed)
    sample_log = """192.168.1.100 - - [15/Mar/2024:10:23:45 +0000] "GET /api/health HTTP/1.1" 200 15 "-" "curl/7.68.0"
192.168.1.101 - - [15/Mar/2024:10:23:46 +0000] "POST /api/users HTTP/1.1" 201 523 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
192.168.1.100 - - [15/Mar/2024:10:23:47 +0000] "GET /api/health HTTP/1.1" 200 15 "-" "curl/7.68.0"
192.168.1.102 - - [15/Mar/2024:10:23:50 +0000] "GET /static/app.js HTTP/1.1" 200 45678 "https://example.com/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
192.168.1.103 - - [15/Mar/2024:10:23:52 +0000] "GET /api/data HTTP/1.1" 404 162 "-" "Python-requests/2.28.0"
192.168.1.101 - - [15/Mar/2024:10:23:55 +0000] "GET /api/users/123 HTTP/1.1" 200 1024 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
192.168.1.100 - - [15/Mar/2024:10:24:01 +0000] "GET /api/health HTTP/1.1" 200 15 "-" "curl/7.68.0"
192.168.1.104 - - [15/Mar/2024:10:24:05 +0000] "POST /api/login HTTP/1.1" 401 87 "-" "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)"
192.168.1.102 - - [15/Mar/2024:10:24:10 +0000] "GET /static/style.css HTTP/1.1" 200 23456 "https://example.com/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
192.168.1.105 - - [15/Mar/2024:10:24:15 +0000] "GET /admin HTTP/1.1" 403 153 "-" "Suspicious-Bot/1.0"
"""
    
    # write sample log to temp file
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        f.write(sample_log)
        temp_log_path = f.name
    
    try:
        # parse and analyze
        analyzer = NginxLogAnalyzer()
        analyzer.parse_file(temp_log_path)
        
        # print the report
        print(analyzer.generate_report())
        
    finally:
        # cleanup
        os.unlink(temp_log_path)