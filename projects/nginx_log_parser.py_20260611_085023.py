"""
Date: 2026-06-11
Built a parser for nginx access logs that pulls out useful metrics like status code distribution, top IPs, and can flag potential bot traffic or attacks.
"""

#!/usr/bin/env python3
"""
Nginx access log parser with basic analytics and anomaly detection.

Parses standard nginx combined log format and extracts metrics like:
- Request distribution by status code
- Top requesting IPs
- Most accessed endpoints
- Potential suspicious activity (high error rates, rapid requests)
"""

import re
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class NginxLogEntry:
    """Represents a single parsed nginx log line."""
    
    # Regex for nginx combined log format
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d\.]+) - - \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\w+) (?P<path>[^\s]+) HTTP/[\d\.]+" '
        r'(?P<status>\d+) (?P<size>\d+) '
        r'"(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)"'
    )
    
    def __init__(self, log_line: str):
        """
        Parse a single nginx log line.
        
        Args:
            log_line: Raw log line string
        """
        match = self.LOG_PATTERN.match(log_line)
        if not match:
            raise ValueError(f"Invalid log format: {log_line[:50]}")
        
        self.ip = match.group('ip')
        self.timestamp = datetime.strptime(
            match.group('timestamp'), 
            '%d/%b/%Y:%H:%M:%S %z'
        )
        self.method = match.group('method')
        self.path = match.group('path')
        self.status = int(match.group('status'))
        self.size = int(match.group('size'))
        self.referer = match.group('referer')
        self.user_agent = match.group('user_agent')


class NginxLogAnalyzer:
    """Analyzes nginx logs and provides metrics and anomaly detection."""
    
    def __init__(self):
        """Initialize the analyzer with empty tracking structures."""
        self.entries: List[NginxLogEntry] = []
        self.ip_requests: Counter = Counter()
        self.status_codes: Counter = Counter()
        self.paths: Counter = Counter()
        self.errors_by_ip: Dict[str, int] = defaultdict(int)
    
    def parse_file(self, filepath: str) -> None:
        """
        Parse an entire nginx log file.
        
        Args:
            filepath: Path to the nginx access log file
        """
        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    entry = NginxLogEntry(line)
                    self.entries.append(entry)
                    
                    # Track metrics as we parse
                    self.ip_requests[entry.ip] += 1
                    self.status_codes[entry.status] += 1
                    self.paths[entry.path] += 1
                    
                    if entry.status >= 400:
                        self.errors_by_ip[entry.ip] += 1
                        
                except ValueError as e:
                    print(f"Warning: Skipping line {line_num}: {e}")
    
    def get_top_ips(self, n: int = 10) -> List[Tuple[str, int]]:
        """Return top N requesting IP addresses."""
        return self.ip_requests.most_common(n)
    
    def get_status_distribution(self) -> Dict[str, int]:
        """
        Group status codes into categories.
        
        Returns:
            Dictionary with status categories and their counts
        """
        distribution = {
            '2xx_success': 0,
            '3xx_redirect': 0,
            '4xx_client_error': 0,
            '5xx_server_error': 0
        }
        
        for status, count in self.status_codes.items():
            if 200 <= status < 300:
                distribution['2xx_success'] += count
            elif 300 <= status < 400:
                distribution['3xx_redirect'] += count
            elif 400 <= status < 500:
                distribution['4xx_client_error'] += count
            elif 500 <= status < 600:
                distribution['5xx_server_error'] += count
        
        return distribution
    
    def detect_suspicious_ips(self, error_threshold: int = 10) -> List[Tuple[str, int, float]]:
        """
        Find IPs with unusually high error rates.
        
        Args:
            error_threshold: Minimum errors to consider suspicious
            
        Returns:
            List of (ip, error_count, error_rate) tuples
        """
        suspicious = []
        
        for ip, error_count in self.errors_by_ip.items():
            if error_count >= error_threshold:
                total_requests = self.ip_requests[ip]
                error_rate = (error_count / total_requests) * 100
                suspicious.append((ip, error_count, error_rate))
        
        # Sort by error rate descending
        return sorted(suspicious, key=lambda x: x[2], reverse=True)
    
    def print_summary(self) -> None:
        """Print a formatted summary of the analysis."""
        print(f"\n{'='*60}")
        print(f"Nginx Log Analysis Summary")
        print(f"{'='*60}")
        print(f"Total requests parsed: {len(self.entries)}")
        print(f"Unique IPs: {len(self.ip_requests)}")
        
        print(f"\n--- Status Code Distribution ---")
        dist = self.get_status_distribution()
        for category, count in sorted(dist.items()):
            print(f"  {category}: {count}")
        
        print(f"\n--- Top 5 Requesting IPs ---")
        for ip, count in self.get_top_ips(5):
            print(f"  {ip}: {count} requests")
        
        print(f"\n--- Top 5 Accessed Paths ---")
        for path, count in self.paths.most_common(5):
            print(f"  {path}: {count} hits")
        
        print(f"\n--- Suspicious Activity ---")
        suspicious = self.detect_suspicious_ips()
        if suspicious:
            for ip, errors, rate in suspicious[:5]:
                print(f"  {ip}: {errors} errors ({rate:.1f}% error rate)")
        else:
            print("  No suspicious activity detected")
        
        print(f"{'='*60}\n")


if __name__ == "__main__":
    # Demo with a synthetic log file
    # In real usage, you'd point this at an actual nginx access.log
    
    import tempfile
    import os
    
    # Create a sample log file for demonstration
    sample_logs = [
        '192.168.1.100 - - [15/Jan/2024:10:15:32 +0000] "GET /index.html HTTP/1.1" 200 1024 "-" "Mozilla/5.0"',
        '192.168.1.101 - - [15/Jan/2024:10:15:33 +0000] "POST /api/login HTTP/1.1" 401 512 "-" "curl/7.68.0"',
        '192.168.1.100 - - [15/Jan/2024:10:15:34 +0000] "GET /static/style.css HTTP/1.1" 200 2048 "-" "Mozilla/5.0"',
        '10.0.0.50 - - [15/Jan/2024:10:15:35 +0000] "GET /admin HTTP/1.1" 404 256 "-" "Python-requests/2.28"',
        '10.0.0.50 - - [15/Jan/2024:10:15:36 +0000] "GET /wp-admin HTTP/1.1" 404 256 "-" "Python-requests/2.28"',
        '10.0.0.50 - - [15/Jan/2024:10:15:37 +0000] "GET /.env HTTP/1.1" 404 256 "-" "Python-requests/2.28"',
        '192.168.1.100 - - [15/Jan/2024:10:15:38 +0000] "GET /about.html HTTP/1.1" 200 1536 "-" "Mozilla/5.0"',
        '192.168.1.102 - - [15/Jan/2024:10:15:39 +0000] "GET /api/data HTTP/1.1" 500 128 "-" "Mozilla/5.0"',
    ]
    
    # Write sample logs to temp file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        for log in sample_logs:
            f.write(log + '\n')
        temp_path = f.name
    
    try:
        # Run the analyzer
        analyzer = NginxLogAnalyzer()
        analyzer.parse_file(temp_path)
        analyzer.print_summary()
    finally:
        # Clean up temp file
        os.unlink(temp_path)