"""
Date: 2026-08-22
Created a parser for nginx access logs that breaks down traffic patterns, identifies problematic requests, and shows me who's hitting my server the hardest.
"""

#!/usr/bin/env python3
"""
Nginx access log parser for analyzing web traffic patterns.

I got tired of grepping through logs manually, so I built this to quickly
spot traffic anomalies, identify bot patterns, and see which endpoints are
getting hammered. Parses the standard nginx combined log format.
"""

import re
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Optional


class NginxLogEntry:
    """Represents a single nginx access log entry."""
    
    # Regex for nginx combined log format
    # Example: 192.168.1.1 - - [10/Oct/2023:13:55:36 +0000] "GET /api/users HTTP/1.1" 200 1234 "https://example.com" "Mozilla/5.0..."
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d\.]+) - - \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\w+) (?P<path>[^\s]+) HTTP/[\d\.]+" '
        r'(?P<status>\d+) (?P<size>\d+) "(?P<referrer>[^"]*)" "(?P<user_agent>[^"]*)"'
    )
    
    def __init__(self, line: str):
        """
        Parse a single log line into structured fields.
        
        Args:
            line: Raw log line from nginx access log
        """
        match = self.LOG_PATTERN.match(line)
        if not match:
            raise ValueError(f"Unable to parse log line: {line[:50]}...")
        
        self.ip = match.group('ip')
        self.timestamp = datetime.strptime(match.group('timestamp'), '%d/%b/%Y:%H:%M:%S %z')
        self.method = match.group('method')
        self.path = match.group('path')
        self.status = int(match.group('status'))
        self.size = int(match.group('size'))
        self.referrer = match.group('referrer') if match.group('referrer') != '-' else None
        self.user_agent = match.group('user_agent')
    
    def is_bot(self) -> bool:
        """Check if the request likely came from a bot based on user agent."""
        bot_indicators = ['bot', 'crawler', 'spider', 'scraper', 'curl', 'wget']
        ua_lower = self.user_agent.lower()
        return any(indicator in ua_lower for indicator in bot_indicators)


class NginxLogAnalyzer:
    """Analyzes nginx access logs and generates traffic insights."""
    
    def __init__(self):
        """Initialize the analyzer with empty tracking structures."""
        self.entries: List[NginxLogEntry] = []
        self.ip_counter = Counter()
        self.status_counter = Counter()
        self.path_counter = Counter()
        self.bot_ips = set()
    
    def parse_file(self, filepath: str) -> None:
        """
        Parse an nginx log file and extract all valid entries.
        
        Args:
            filepath: Path to the nginx access log file
        """
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    entry = NginxLogEntry(line)
                    self.entries.append(entry)
                    self.ip_counter[entry.ip] += 1
                    self.status_counter[entry.status] += 1
                    self.path_counter[entry.path] += 1
                    
                    if entry.is_bot():
                        self.bot_ips.add(entry.ip)
                
                except ValueError as e:
                    # Skip malformed lines — sometimes logs get corrupted
                    print(f"Warning: Skipped line {line_num}: {e}")
    
    def get_top_ips(self, n: int = 10) -> List[tuple]:
        """Return the top N IP addresses by request count."""
        return self.ip_counter.most_common(n)
    
    def get_status_distribution(self) -> Dict[int, int]:
        """Return the distribution of HTTP status codes."""
        return dict(self.status_counter)
    
    def get_error_rate(self) -> float:
        """Calculate percentage of requests that resulted in 4xx or 5xx errors."""
        total = len(self.entries)
        if total == 0:
            return 0.0
        
        errors = sum(count for status, count in self.status_counter.items() if status >= 400)
        return (errors / total) * 100
    
    def get_top_paths(self, n: int = 10) -> List[tuple]:
        """Return the top N most requested paths."""
        return self.path_counter.most_common(n)
    
    def get_bot_traffic_percentage(self) -> float:
        """Calculate what percentage of traffic came from bots."""
        if not self.entries:
            return 0.0
        
        bot_requests = sum(1 for entry in self.entries if entry.is_bot())
        return (bot_requests / len(self.entries)) * 100
    
    def print_summary(self) -> None:
        """Print a human-readable summary of the log analysis."""
        print(f"\n{'='*60}")
        print(f"NGINX LOG ANALYSIS SUMMARY")
        print(f"{'='*60}\n")
        
        print(f"Total Requests: {len(self.entries):,}")
        print(f"Unique IPs: {len(self.ip_counter):,}")
        print(f"Error Rate: {self.get_error_rate():.2f}%")
        print(f"Bot Traffic: {self.get_bot_traffic_percentage():.2f}%")
        
        print(f"\n{'─'*60}")
        print("TOP 5 IP ADDRESSES:")
        print(f"{'─'*60}")
        for ip, count in self.get_top_ips(5):
            bot_marker = " [BOT]" if ip in self.bot_ips else ""
            print(f"  {ip:15s} → {count:6,} requests{bot_marker}")
        
        print(f"\n{'─'*60}")
        print("STATUS CODE DISTRIBUTION:")
        print(f"{'─'*60}")
        for status in sorted(self.status_counter.keys()):
            count = self.status_counter[status]
            print(f"  {status} → {count:6,} requests")
        
        print(f"\n{'─'*60}")
        print("TOP 5 REQUESTED PATHS:")
        print(f"{'─'*60}")
        for path, count in self.get_top_paths(5):
            # Truncate long paths for readability
            display_path = path if len(path) <= 50 else path[:47] + "..."
            print(f"  {count:6,} → {display_path}")
        
        print(f"\n{'='*60}\n")


if __name__ == "__main__":
    # Demo with a sample log — in real usage, you'd pass a file path
    import tempfile
    import os
    
    # Create a sample nginx log file for demonstration
    sample_log = """192.168.1.100 - - [15/Jan/2024:10:23:45 +0000] "GET /api/users HTTP/1.1" 200 1234 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
192.168.1.101 - - [15/Jan/2024:10:23:46 +0000] "POST /api/login HTTP/1.1" 200 567 "https://example.com" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
192.168.1.100 - - [15/Jan/2024:10:23:47 +0000] "GET /api/posts HTTP/1.1" 200 8901 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
66.249.64.1 - - [15/Jan/2024:10:23:48 +0000] "GET /robots.txt HTTP/1.1" 200 234 "-" "Googlebot/2.1"
192.168.1.102 - - [15/Jan/2024:10:23:49 +0000] "GET /missing HTTP/1.1" 404 153 "-" "curl/7.68.0"
192.168.1.100 - - [15/Jan/2024:10:23:50 +0000] "GET /api/users/123 HTTP/1.1" 200 456 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
192.168.1.103 - - [15/Jan/2024:10:23:51 +0000] "GET /admin HTTP/1.1" 403 78 "-" "Mozilla/5.0"
66.249.64.1 - - [15/Jan/2024:10:23:52 +0000] "GET /sitemap.xml HTTP/1.1" 200 3456 "-" "Googlebot/2.1"
192.168.1.100 - - [15/Jan/2024:10:23:53 +0000] "DELETE /api/posts/5 HTTP/1