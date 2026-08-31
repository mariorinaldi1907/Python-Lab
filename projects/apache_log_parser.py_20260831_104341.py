"""
Date: 2026-08-31
Wrote a quick log parser to analyze web server access logs — counts status codes, finds slow requests, and flags potential bot traffic.
"""

#!/usr/bin/env python3
"""
Apache/Nginx access log parser and analyzer.
Parses combined log format and generates basic metrics.
"""

import re
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Optional


class LogEntry:
    """Represents a single parsed log line from Apache/Nginx."""
    
    def __init__(self, ip: str, timestamp: str, method: str, path: str, 
                 status: int, size: int, referrer: str, user_agent: str):
        self.ip = ip
        self.timestamp = timestamp
        self.method = method
        self.path = path
        self.status = status
        self.size = size
        self.referrer = referrer
        self.user_agent = user_agent
    
    def __repr__(self):
        return f"<LogEntry {self.method} {self.path} -> {self.status}>"


class AccessLogParser:
    """
    Parses and analyzes Apache/Nginx access logs in combined format.
    Combined format: IP - - [timestamp] "METHOD path HTTP/x.x" status size "referrer" "user-agent"
    """
    
    # Regex pattern for combined log format
    # I'm using named groups here to make extraction cleaner than positional matching
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d\.]+) - - \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\S+) (?P<path>\S+) HTTP/[\d\.]+" '
        r'(?P<status>\d+) (?P<size>\d+) '
        r'"(?P<referrer>[^"]*)" "(?P<user_agent>[^"]*)"'
    )
    
    def __init__(self):
        self.entries: List[LogEntry] = []
        self.parse_errors = 0
    
    def parse_line(self, line: str) -> Optional[LogEntry]:
        """
        Parse a single log line into a LogEntry object.
        Returns None if the line doesn't match expected format.
        """
        match = self.LOG_PATTERN.match(line.strip())
        if not match:
            return None
        
        data = match.groupdict()
        
        # Convert numeric fields, handling potential errors gracefully
        try:
            status = int(data['status'])
            size = int(data['size']) if data['size'] != '-' else 0
        except ValueError:
            return None
        
        return LogEntry(
            ip=data['ip'],
            timestamp=data['timestamp'],
            method=data['method'],
            path=data['path'],
            status=status,
            size=size,
            referrer=data['referrer'],
            user_agent=data['user_agent']
        )
    
    def parse_file(self, filepath: str) -> None:
        """Read and parse an entire log file."""
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                entry = self.parse_line(line)
                if entry:
                    self.entries.append(entry)
                else:
                    self.parse_errors += 1
    
    def get_status_summary(self) -> Dict[int, int]:
        """Count occurrences of each HTTP status code."""
        return Counter(entry.status for entry in self.entries)
    
    def get_top_paths(self, n: int = 10) -> List[tuple]:
        """Return the top N most requested paths."""
        path_counts = Counter(entry.path for entry in self.entries)
        return path_counts.most_common(n)
    
    def get_top_ips(self, n: int = 10) -> List[tuple]:
        """Return the top N most active IP addresses."""
        ip_counts = Counter(entry.ip for entry in self.entries)
        return ip_counts.most_common(n)
    
    def get_bot_traffic(self) -> List[LogEntry]:
        """
        Identify potential bot traffic based on user-agent strings.
        This is a simple heuristic — real bot detection is way more complex.
        """
        bot_keywords = ['bot', 'crawler', 'spider', 'scraper', 'curl', 'wget']
        bots = []
        
        for entry in self.entries:
            ua_lower = entry.user_agent.lower()
            if any(keyword in ua_lower for keyword in bot_keywords):
                bots.append(entry)
        
        return bots
    
    def get_error_requests(self) -> List[LogEntry]:
        """Return all requests that resulted in 4xx or 5xx errors."""
        return [entry for entry in self.entries if entry.status >= 400]
    
    def print_summary(self) -> None:
        """Print a comprehensive analysis summary."""
        print(f"\n{'='*60}")
        print(f"ACCESS LOG ANALYSIS")
        print(f"{'='*60}")
        print(f"Total requests parsed: {len(self.entries)}")
        print(f"Parse errors: {self.parse_errors}")
        
        print(f"\n{'─'*60}")
        print("STATUS CODE DISTRIBUTION:")
        status_summary = self.get_status_summary()
        for status in sorted(status_summary.keys()):
            count = status_summary[status]
            percentage = (count / len(self.entries)) * 100
            print(f"  {status}: {count:>6} ({percentage:>5.1f}%)")
        
        print(f"\n{'─'*60}")
        print("TOP 5 REQUESTED PATHS:")
        for path, count in self.get_top_paths(5):
            print(f"  {count:>6}x  {path}")
        
        print(f"\n{'─'*60}")
        print("TOP 5 ACTIVE IPs:")
        for ip, count in self.get_top_ips(5):
            print(f"  {count:>6}x  {ip}")
        
        bot_count = len(self.get_bot_traffic())
        bot_percentage = (bot_count / len(self.entries)) * 100 if self.entries else 0
        print(f"\n{'─'*60}")
        print(f"BOT TRAFFIC: {bot_count} requests ({bot_percentage:.1f}%)")
        
        error_count = len(self.get_error_requests())
        error_percentage = (error_count / len(self.entries)) * 100 if self.entries else 0
        print(f"ERROR REQUESTS (4xx/5xx): {error_count} ({error_percentage:.1f}%)")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    # Create a sample log file for demonstration
    sample_log = """192.168.1.100 - - [15/Jan/2024:10:23:45 +0000] "GET /index.html HTTP/1.1" 200 2326 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
192.168.1.101 - - [15/Jan/2024:10:23:46 +0000] "GET /api/users HTTP/1.1" 200 1543 "https://example.com/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
192.168.1.102 - - [15/Jan/2024:10:23:47 +0000] "POST /api/login HTTP/1.1" 401 89 "-" "curl/7.68.0"
192.168.1.100 - - [15/Jan/2024:10:23:48 +0000] "GET /images/logo.png HTTP/1.1" 304 0 "https://example.com/index.html" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
192.168.1.103 - - [15/Jan/2024:10:23:49 +0000] "GET /admin HTTP/1.1" 403 178 "-" "Googlebot/2.1"
192.168.1.100 - - [15/Jan/2024:10:23:50 +0000] "GET /api/posts HTTP/1.1" 200 8934 "https://example.com/" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
192.168.1.104 - - [15/Jan/2024:10:23:51 +0000] "GET /nonexistent HTTP/1.1" 404 196 "-" "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)"
192.168.1.101 - - [15/Jan/2024:10:23:52 +0000] "GET /api/posts/123 HTTP/1.1" 200 1234 "https://example.com/api/posts" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
192.168.1.105 - - [15/Jan/2024:10:23:53 +0000] "GET /robots.txt HTTP/1.1" 200 67 "-" "Bingbot/2.0"
192.168.1.100 - - [15/Jan/2024:10:23:54 +0000] "GET /contact HTTP/1.1" 500 543 "https://example.com/index.html" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
"""
    
    # Write sample data to