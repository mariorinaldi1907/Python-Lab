"""
Date: 2026-07-05
Wrote a parser for nginx access logs because I got tired of grepping through thousands of lines to find 500 errors and slow requests on my VPS.
"""

#!/usr/bin/env python3
"""
Nginx access log parser that extracts useful stats from log files.
Parses the combined log format and provides filtering/analysis.
"""

import re
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class NginxLogEntry:
    """
    Represents a single nginx access log entry.
    Handles parsing of the combined log format.
    """
    
    # Regex pattern for nginx combined log format
    # Looks gnarly but it works — captures IP, timestamp, method, path, status, etc.
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d\.]+) - (?P<user>\S+) \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\w+) (?P<path>\S+) (?P<protocol>[^"]+)" '
        r'(?P<status>\d{3}) (?P<size>\d+) "(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)"'
    )
    
    def __init__(self, line: str):
        """Parse a single log line into structured data."""
        match = self.LOG_PATTERN.match(line)
        if not match:
            raise ValueError(f"Could not parse log line: {line[:50]}...")
        
        self.ip = match.group('ip')
        self.user = match.group('user')
        self.timestamp_str = match.group('timestamp')
        self.method = match.group('method')
        self.path = match.group('path')
        self.protocol = match.group('protocol')
        self.status = int(match.group('status'))
        self.size = int(match.group('size'))
        self.referer = match.group('referer')
        self.user_agent = match.group('user_agent')
        
        # Parse timestamp into datetime object for easier filtering
        self.timestamp = datetime.strptime(
            self.timestamp_str, '%d/%b/%Y:%H:%M:%S %z'
        )
    
    def __repr__(self):
        return f"<LogEntry {self.method} {self.path} -> {self.status}>"


class NginxLogAnalyzer:
    """
    Analyzes nginx access logs and produces useful insights.
    Built this because manual log analysis is tedious.
    """
    
    def __init__(self):
        """Initialize empty analyzer."""
        self.entries: List[NginxLogEntry] = []
    
    def parse_file(self, filepath: str) -> int:
        """
        Load and parse a log file.
        Returns the number of successfully parsed entries.
        """
        parsed_count = 0
        skipped_count = 0
        
        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    entry = NginxLogEntry(line)
                    self.entries.append(entry)
                    parsed_count += 1
                except ValueError as e:
                    skipped_count += 1
                    # In real usage I'd probably log this, but keeping it simple
        
        if skipped_count > 0:
            print(f"Warning: skipped {skipped_count} unparseable lines")
        
        return parsed_count
    
    def status_code_summary(self) -> Dict[int, int]:
        """Count occurrences of each HTTP status code."""
        return Counter(entry.status for entry in self.entries)
    
    def top_paths(self, n: int = 10) -> List[Tuple[str, int]]:
        """Get the N most frequently requested paths."""
        path_counts = Counter(entry.path for entry in self.entries)
        return path_counts.most_common(n)
    
    def error_requests(self, min_status: int = 400) -> List[NginxLogEntry]:
        """
        Filter for error responses (4xx and 5xx by default).
        Useful for debugging when things go wrong.
        """
        return [entry for entry in self.entries if entry.status >= min_status]
    
    def traffic_by_ip(self) -> List[Tuple[str, int]]:
        """
        Count requests per IP address.
        Helps identify potential bots or abusive clients.
        """
        ip_counts = Counter(entry.ip for entry in self.entries)
        return ip_counts.most_common()
    
    def size_stats(self) -> Dict[str, float]:
        """Calculate statistics about response sizes."""
        sizes = [entry.size for entry in self.entries]
        
        if not sizes:
            return {'total': 0, 'mean': 0, 'max': 0}
        
        return {
            'total_bytes': sum(sizes),
            'mean_bytes': sum(sizes) / len(sizes),
            'max_bytes': max(sizes),
            'total_mb': sum(sizes) / (1024 * 1024)
        }


def generate_sample_log() -> str:
    """
    Create a sample nginx log file for testing.
    Returns the filename of the generated log.
    """
    sample_data = [
        '192.168.1.100 - - [15/Jan/2024:10:23:45 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"',
        '192.168.1.101 - - [15/Jan/2024:10:24:12 +0000] "GET /api/users HTTP/1.1" 200 5678 "-" "curl/7.68.0"',
        '192.168.1.100 - - [15/Jan/2024:10:25:33 +0000] "POST /api/login HTTP/1.1" 401 89 "-" "Mozilla/5.0"',
        '192.168.1.102 - - [15/Jan/2024:10:26:01 +0000] "GET /missing.html HTTP/1.1" 404 162 "-" "Mozilla/5.0"',
        '192.168.1.101 - - [15/Jan/2024:10:27:45 +0000] "GET /api/data HTTP/1.1" 500 2345 "-" "curl/7.68.0"',
        '192.168.1.100 - - [15/Jan/2024:10:28:12 +0000] "GET /static/style.css HTTP/1.1" 200 8192 "-" "Mozilla/5.0"',
        '192.168.1.103 - - [15/Jan/2024:10:29:55 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "bot/1.0"',
    ]
    
    filename = 'sample_nginx.log'
    with open(filename, 'w') as f:
        f.write('\n'.join(sample_data))
    
    return filename


if __name__ == "__main__":
    # Generate a sample log file for demonstration
    print("Generating sample nginx log file...")
    log_file = generate_sample_log()
    print(f"Created {log_file}\n")
    
    # Parse and analyze the log
    analyzer = NginxLogAnalyzer()
    count = analyzer.parse_file(log_file)
    print(f"Parsed {count} log entries\n")
    
    # Show status code distribution
    print("=== Status Code Summary ===")
    for status, count in sorted(analyzer.status_code_summary().items()):
        print(f"  {status}: {count} requests")
    
    # Most requested paths
    print("\n=== Top Requested Paths ===")
    for path, count in analyzer.top_paths(5):
        print(f"  {path}: {count} requests")
    
    # Error analysis
    print("\n=== Error Requests (4xx/5xx) ===")
    errors = analyzer.error_requests()
    print(f"Found {len(errors)} errors:")
    for entry in errors:
        print(f"  {entry.status} {entry.method} {entry.path} from {entry.ip}")
    
    # Traffic by IP
    print("\n=== Traffic by IP ===")
    for ip, count in analyzer.traffic_by_ip():
        print(f"  {ip}: {count} requests")
    
    # Size statistics
    print("\n=== Response Size Stats ===")
    stats = analyzer.size_stats()
    print(f"  Total: {stats['total_mb']:.2f} MB")
    print(f"  Average: {stats['mean_bytes']:.0f} bytes")
    print(f"  Largest: {stats['max_bytes']} bytes")