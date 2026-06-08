"""
Date: 2026-06-08
Wrote a parser for nginx access logs that breaks down request patterns, status codes, and can flag suspicious activity — helped me analyze traffic on my VPS.
"""

#!/usr/bin/env python3
"""
Nginx access log parser and analyzer.

Parses standard nginx combined log format and extracts useful metrics.
I built this because I kept manually grepping through logs on my server
and wanted something that could give me a quick overview of what's happening.
"""

import re
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class NginxLogEntry:
    """Represents a single parsed line from an nginx access log."""
    
    # Regex for nginx combined log format
    # I spent way too long getting this pattern right, but it handles quoted strings properly
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d\.]+) - (?P<user>\S+) \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\S+) (?P<path>\S+) (?P<protocol>[^"]+)" '
        r'(?P<status>\d+) (?P<size>\d+) "(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)"'
    )
    
    def __init__(self, line: str):
        """
        Parse a single log line.
        
        Args:
            line: Raw log line from nginx access.log
        
        Raises:
            ValueError: If the line doesn't match expected format
        """
        match = self.LOG_PATTERN.match(line)
        if not match:
            raise ValueError(f"Line doesn't match nginx log format: {line[:50]}...")
        
        self.ip = match.group('ip')
        self.user = match.group('user')
        self.timestamp = datetime.strptime(match.group('timestamp'), '%d/%b/%Y:%H:%M:%S %z')
        self.method = match.group('method')
        self.path = match.group('path')
        self.protocol = match.group('protocol')
        self.status = int(match.group('status'))
        self.size = int(match.group('size'))
        self.referer = match.group('referer')
        self.user_agent = match.group('user_agent')


class NginxLogAnalyzer:
    """Analyzes parsed nginx log entries and generates useful statistics."""
    
    def __init__(self):
        """Initialize counters and storage for log analysis."""
        self.entries: List[NginxLogEntry] = []
        self.parse_errors = 0
    
    def parse_file(self, filepath: str) -> None:
        """
        Read and parse an nginx log file.
        
        I'm catching parse errors individually so one bad line doesn't kill
        the whole analysis — useful when logs get corrupted or truncated.
        
        Args:
            filepath: Path to the nginx access.log file
        """
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = NginxLogEntry(line)
                    self.entries.append(entry)
                except ValueError as e:
                    self.parse_errors += 1
                    # In a real scenario I'd log this properly, but print works for now
                    if self.parse_errors <= 5:  # Don't spam if there are tons of errors
                        print(f"Warning: Couldn't parse line {line_num}: {str(e)}")
    
    def get_status_code_distribution(self) -> Counter:
        """Return count of each HTTP status code."""
        return Counter(entry.status for entry in self.entries)
    
    def get_top_paths(self, n: int = 10) -> List[Tuple[str, int]]:
        """
        Get the most frequently requested paths.
        
        Args:
            n: Number of top paths to return
        
        Returns:
            List of (path, count) tuples sorted by frequency
        """
        path_counter = Counter(entry.path for entry in self.entries)
        return path_counter.most_common(n)
    
    def get_ip_request_counts(self) -> Counter:
        """Count requests per IP address — useful for spotting scrapers or attacks."""
        return Counter(entry.ip for entry in self.entries)
    
    def find_suspicious_activity(self, threshold: int = 100) -> List[Tuple[str, int]]:
        """
        Flag IPs that made an unusual number of requests.
        
        This is a naive implementation but catches obvious automated traffic.
        Real rate limiting would be more sophisticated, but this helps me spot
        when someone is hammering my server.
        
        Args:
            threshold: Number of requests to consider suspicious
        
        Returns:
            List of (ip, count) tuples exceeding threshold
        """
        ip_counts = self.get_ip_request_counts()
        return [(ip, count) for ip, count in ip_counts.items() if count > threshold]
    
    def get_error_requests(self) -> List[NginxLogEntry]:
        """Return all requests that resulted in 4xx or 5xx errors."""
        return [entry for entry in self.entries if entry.status >= 400]
    
    def generate_report(self) -> str:
        """
        Generate a human-readable summary report.
        
        Returns:
            Formatted string with analysis results
        """
        if not self.entries:
            return "No log entries parsed."
        
        report_lines = [
            "=== Nginx Log Analysis Report ===",
            f"Total requests parsed: {len(self.entries)}",
            f"Parse errors: {self.parse_errors}",
            "",
            "Status Code Distribution:",
        ]
        
        for status, count in sorted(self.get_status_code_distribution().items()):
            percentage = (count / len(self.entries)) * 100
            report_lines.append(f"  {status}: {count} ({percentage:.1f}%)")
        
        report_lines.extend([
            "",
            "Top 5 Requested Paths:",
        ])
        
        for path, count in self.get_top_paths(5):
            report_lines.append(f"  {path}: {count} requests")
        
        suspicious = self.find_suspicious_activity(threshold=50)
        if suspicious:
            report_lines.extend([
                "",
                f"Suspicious Activity (>{50} requests):",
            ])
            for ip, count in sorted(suspicious, key=lambda x: x[1], reverse=True)[:5]:
                report_lines.append(f"  {ip}: {count} requests")
        
        errors = self.get_error_requests()
        if errors:
            report_lines.extend([
                "",
                f"Error Summary: {len(errors)} failed requests",
                "  Most common errors:",
            ])
            error_paths = Counter(e.path for e in errors)
            for path, count in error_paths.most_common(3):
                report_lines.append(f"    {path}: {count} errors")
        
        return "\n".join(report_lines)


def create_sample_log(filepath: str) -> None:
    """Generate a sample nginx log file for testing purposes."""
    sample_logs = [
        '192.168.1.100 - - [15/Jan/2024:10:15:23 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"',
        '192.168.1.101 - - [15/Jan/2024:10:15:24 +0000] "GET /api/users HTTP/1.1" 200 5678 "https://example.com" "curl/7.68.0"',
        '192.168.1.100 - - [15/Jan/2024:10:15:25 +0000] "POST /api/login HTTP/1.1" 401 89 "-" "Mozilla/5.0"',
        '10.0.0.50 - - [15/Jan/2024:10:15:26 +0000] "GET /admin HTTP/1.1" 403 162 "-" "Scrapy/2.5.0"',
        '10.0.0.50 - - [15/Jan/2024:10:15:27 +0000] "GET /admin/users HTTP/1.1" 403 162 "-" "Scrapy/2.5.0"',
        '192.168.1.102 - - [15/Jan/2024:10:15:28 +0000] "GET /about.html HTTP/1.1" 200 3421 "https://google.com" "Mozilla/5.0"',
        '192.168.1.100 - - [15/Jan/2024:10:15:29 +0000] "GET /assets/style.css HTTP/1.1" 200 9876 "https://example.com/index.html" "Mozilla/5.0"',
        '192.168.1.103 - - [15/Jan/2024:10:15:30 +0000] "GET /nonexistent HTTP/1.1" 404 153 "-" "Mozilla/5.0"',
        '10.0.0.50 - - [15/Jan/2024:10:15:31 +0000] "GET /wp-admin HTTP/1.1" 404 153 "-" "Scrapy/2.5.0"',
        '192.168.1.100 - - [15/Jan/2024:10:15:32 +0000] "GET /contact.html HTTP/1.1" 200 2341 "https://example.com" "