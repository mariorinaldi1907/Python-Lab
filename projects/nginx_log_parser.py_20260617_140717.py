"""
Date: 2026-06-17
Wrote a parser for nginx access logs that gives me quick insights into traffic patterns, response codes, and potential bot activity on my server.
"""

#!/usr/bin/env python3
"""
Nginx access log parser — gives me quick stats on server traffic.
I got tired of grepping through logs manually, so I built this to parse
standard nginx access log format and spit out useful metrics.
"""

import re
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Optional


class NginxLogEntry:
    """
    Represents a single line from an nginx access log.
    Parses the common combined log format that nginx uses by default.
    """
    
    # Regex for nginx combined log format
    # Example: 192.168.1.1 - - [10/Oct/2023:13:55:36 +0000] "GET /api/data HTTP/1.1" 200 1234 "-" "Mozilla/5.0..."
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d\.]+) - - \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\S+) (?P<path>\S+) (?P<protocol>[^"]+)" '
        r'(?P<status>\d+) (?P<size>\d+) "(?P<referrer>[^"]*)" "(?P<user_agent>[^"]*)"'
    )
    
    def __init__(self, line: str):
        """Parse a single log line into structured fields."""
        match = self.LOG_PATTERN.match(line)
        if not match:
            raise ValueError(f"Line doesn't match expected format: {line[:50]}...")
        
        data = match.groupdict()
        self.ip = data['ip']
        self.timestamp = datetime.strptime(data['timestamp'], '%d/%b/%Y:%H:%M:%S %z')
        self.method = data['method']
        self.path = data['path']
        self.protocol = data['protocol']
        self.status = int(data['status'])
        self.size = int(data['size'])
        self.referrer = data['referrer'] if data['referrer'] != '-' else None
        self.user_agent = data['user_agent']


class NginxLogAnalyzer:
    """
    Analyzes a collection of nginx log entries to extract useful patterns.
    I mostly use this to check for suspicious traffic and track popular endpoints.
    """
    
    def __init__(self):
        """Initialize empty log storage."""
        self.entries: List[NginxLogEntry] = []
    
    def parse_file(self, filepath: str) -> int:
        """
        Read and parse a log file.
        Returns the number of successfully parsed lines.
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
                    # Some lines might be malformed, but don't crash the whole parse
                    skipped_count += 1
                    if skipped_count <= 5:  # Only print first few errors
                        print(f"Warning: Skipped line {line_num}: {e}")
        
        return parsed_count
    
    def status_code_distribution(self) -> Dict[int, int]:
        """Count occurrences of each HTTP status code."""
        return dict(Counter(entry.status for entry in self.entries))
    
    def top_paths(self, n: int = 10) -> List[tuple]:
        """Return the N most frequently accessed paths."""
        path_counts = Counter(entry.path for entry in self.entries)
        return path_counts.most_common(n)
    
    def top_ips(self, n: int = 10) -> List[tuple]:
        """
        Return the N most active IP addresses.
        Useful for spotting bots or scrapers hammering the server.
        """
        ip_counts = Counter(entry.ip for entry in self.entries)
        return ip_counts.most_common(n)
    
    def detect_suspicious_activity(self, threshold: int = 100) -> Dict[str, List[str]]:
        """
        Flag potentially suspicious patterns.
        This is a simple heuristic — if an IP makes too many 4xx requests,
        it might be scanning or probing the server.
        """
        ip_errors = defaultdict(int)
        ip_total = defaultdict(int)
        
        for entry in self.entries:
            ip_total[entry.ip] += 1
            if 400 <= entry.status < 500:
                ip_errors[entry.ip] += 1
        
        # Find IPs with high error rates and high request volumes
        suspicious = {
            'high_volume': [ip for ip, count in ip_total.items() if count > threshold],
            'high_error_rate': [
                ip for ip, errors in ip_errors.items()
                if ip_total[ip] > 20 and (errors / ip_total[ip]) > 0.5
            ]
        }
        
        return suspicious
    
    def get_summary(self) -> Dict:
        """
        Generate a complete summary of log analysis.
        This is what I actually look at when checking server health.
        """
        if not self.entries:
            return {'error': 'No entries parsed'}
        
        total_bytes = sum(entry.size for entry in self.entries)
        
        return {
            'total_requests': len(self.entries),
            'date_range': (
                min(e.timestamp for e in self.entries).isoformat(),
                max(e.timestamp for e in self.entries).isoformat()
            ),
            'total_bandwidth_mb': round(total_bytes / (1024 * 1024), 2),
            'avg_response_size_kb': round((total_bytes / len(self.entries)) / 1024, 2),
            'unique_ips': len(set(entry.ip for entry in self.entries)),
            'unique_paths': len(set(entry.path for entry in self.entries))
        }


def create_sample_log_file(filename: str = 'sample_nginx.log'):
    """
    Generate a sample nginx log file for testing.
    Mimics real log entries with various response codes and patterns.
    """
    sample_lines = [
        '192.168.1.100 - - [15/Dec/2023:10:15:30 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"',
        '192.168.1.101 - - [15/Dec/2023:10:16:45 +0000] "GET /api/users HTTP/1.1" 200 5678 "https://example.com" "curl/7.68.0"',
        '10.0.0.50 - - [15/Dec/2023:10:17:22 +0000] "POST /api/login HTTP/1.1" 401 89 "-" "Python-requests/2.28.0"',
        '192.168.1.100 - - [15/Dec/2023:10:18:01 +0000] "GET /static/style.css HTTP/1.1" 200 2048 "https://example.com/index.html" "Mozilla/5.0"',
        '203.0.113.42 - - [15/Dec/2023:10:19:15 +0000] "GET /admin/login HTTP/1.1" 404 162 "-" "Bot Scanner v2.0"',
        '203.0.113.42 - - [15/Dec/2023:10:19:16 +0000] "GET /wp-admin HTTP/1.1" 404 162 "-" "Bot Scanner v2.0"',
        '203.0.113.42 - - [15/Dec/2023:10:19:17 +0000] "GET /.env HTTP/1.1" 404 162 "-" "Bot Scanner v2.0"',
        '192.168.1.102 - - [15/Dec/2023:10:20:33 +0000] "GET /api/data?page=1 HTTP/1.1" 200 15000 "-" "Mozilla/5.0"',
        '192.168.1.101 - - [15/Dec/2023:10:21:10 +0000] "DELETE /api/users/123 HTTP/1.1" 204 0 "-" "curl/7.68.0"',
        '10.0.0.51 - - [15/Dec/2023:10:22:45 +0000] "GET /health HTTP/1.1" 200 45 "-" "KubernetesProbe/1.0"',
    ]
    
    with open(filename, 'w') as f:
        f.write('\n'.join(sample_lines))
    
    return filename


if __name__ == "__main__":
    # Create a sample log file for demo purposes
    print("Creating sample nginx log file...")
    log_file = create_sample_log_file()
    print(f"Sample log created: {log_file}\n")
    
    # Parse and analyze
    analyzer = NginxLogAnalyzer()
    parsed = analyzer.parse_file(log_file)
    print(f"Parsed {parsed} log entries\n")
    
    # Print summary stats
    print("=== Log Summary ===")
    summary =