"""
Date: 2026-07-01
Created a parser that analyzes nginx access logs to pull out stats like top IPs, most hit endpoints, status code distribution, and flags potential bot traffic.
"""

#!/usr/bin/env python3
"""
Nginx access log parser with basic traffic analysis.

I wrote this to quickly analyze nginx logs when debugging traffic issues.
Parses the standard combined log format and generates useful stats.
"""

import re
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class NginxLogEntry:
    """
    Represents a single parsed nginx log line.
    
    I'm storing the raw line too in case I need to debug parsing issues later.
    """
    
    def __init__(self, ip: str, timestamp: str, method: str, path: str, 
                 status: int, size: int, user_agent: str, raw_line: str):
        self.ip = ip
        self.timestamp = timestamp
        self.method = method
        self.path = path
        self.status = status
        self.size = size
        self.user_agent = user_agent
        self.raw_line = raw_line


class NginxLogParser:
    """
    Parses nginx access logs in combined format.
    
    The regex is ugly but it handles all the edge cases I've seen in real logs.
    """
    
    # Standard nginx combined log format regex
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d\.]+) - - \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\w+) (?P<path>[^\s]+) HTTP/[^"]*" '
        r'(?P<status>\d+) (?P<size>\d+) '
        r'"[^"]*" "(?P<user_agent>[^"]*)"'
    )
    
    def __init__(self):
        self.entries: List[NginxLogEntry] = []
        self.parse_errors: List[str] = []
    
    def parse_line(self, line: str) -> Optional[NginxLogEntry]:
        """
        Parse a single log line into a structured entry.
        
        Returns None if the line doesn't match the expected format.
        I'm keeping track of parse errors so I know if my regex needs fixing.
        """
        match = self.LOG_PATTERN.match(line.strip())
        if not match:
            return None
        
        data = match.groupdict()
        try:
            return NginxLogEntry(
                ip=data['ip'],
                timestamp=data['timestamp'],
                method=data['method'],
                path=data['path'],
                status=int(data['status']),
                size=int(data['size']),
                user_agent=data['user_agent'],
                raw_line=line
            )
        except (ValueError, KeyError) as e:
            self.parse_errors.append(f"Error parsing: {line[:50]}... ({e})")
            return None
    
    def parse_file(self, filepath: str) -> None:
        """
        Read and parse an entire log file.
        
        I'm reading line by line instead of loading everything into memory
        because production logs can get huge.
        """
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue
                
                entry = self.parse_line(line)
                if entry:
                    self.entries.append(entry)
                else:
                    self.parse_errors.append(f"Line {line_num}: {line[:50]}...")
    
    def get_top_ips(self, n: int = 10) -> List[Tuple[str, int]]:
        """Return the top N IPs by request count."""
        ip_counts = Counter(entry.ip for entry in self.entries)
        return ip_counts.most_common(n)
    
    def get_status_distribution(self) -> Dict[int, int]:
        """Get the distribution of HTTP status codes."""
        return dict(Counter(entry.status for entry in self.entries))
    
    def get_top_paths(self, n: int = 10) -> List[Tuple[str, int]]:
        """Return the most frequently accessed paths."""
        path_counts = Counter(entry.path for entry in self.entries)
        return path_counts.most_common(n)
    
    def detect_suspicious_activity(self) -> Dict[str, List[str]]:
        """
        Flag potentially suspicious patterns.
        
        This is basic heuristic stuff - looking for common bot/scanner behavior.
        In real life I'd make these thresholds configurable.
        """
        suspicious = defaultdict(list)
        
        # Check for IPs with unusually high 404 rates
        ip_404_counts = defaultdict(int)
        ip_total_counts = defaultdict(int)
        
        for entry in self.entries:
            ip_total_counts[entry.ip] += 1
            if entry.status == 404:
                ip_404_counts[entry.ip] += 1
        
        for ip, total in ip_total_counts.items():
            if total >= 10:  # Only flag IPs with significant activity
                rate_404 = ip_404_counts[ip] / total
                if rate_404 > 0.5:  # More than 50% 404s is weird
                    suspicious['high_404_rate'].append(
                        f"{ip} ({ip_404_counts[ip]}/{total} = {rate_404:.1%})"
                    )
        
        # Look for scanner-like user agents
        scanner_keywords = ['bot', 'crawler', 'spider', 'scan']
        for entry in self.entries:
            ua_lower = entry.user_agent.lower()
            if any(keyword in ua_lower for keyword in scanner_keywords):
                if entry.ip not in suspicious['scanner_agents']:
                    suspicious['scanner_agents'].append(entry.ip)
        
        return dict(suspicious)
    
    def print_summary(self) -> None:
        """Print a nice summary of the parsed logs."""
        print(f"\n{'='*60}")
        print(f"Nginx Log Analysis Summary")
        print(f"{'='*60}\n")
        
        print(f"Total entries parsed: {len(self.entries)}")
        print(f"Parse errors: {len(self.parse_errors)}\n")
        
        print("Top 5 IP Addresses:")
        for ip, count in self.get_top_ips(5):
            print(f"  {ip:15} - {count:4} requests")
        
        print("\nStatus Code Distribution:")
        for status, count in sorted(self.get_status_distribution().items()):
            print(f"  {status}: {count:4} requests")
        
        print("\nTop 5 Paths:")
        for path, count in self.get_top_paths(5):
            display_path = path if len(path) <= 50 else path[:47] + "..."
            print(f"  {count:4}x - {display_path}")
        
        suspicious = self.detect_suspicious_activity()
        if suspicious:
            print("\n⚠️  Suspicious Activity Detected:")
            for category, items in suspicious.items():
                print(f"\n  {category.replace('_', ' ').title()}:")
                for item in items[:5]:  # Limit output
                    print(f"    - {item}")


if __name__ == "__main__":
    # Demo with sample nginx log data
    sample_log = """192.168.1.100 - - [10/Jan/2024:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 1043 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
192.168.1.101 - - [10/Jan/2024:13:55:37 +0000] "GET /api/users HTTP/1.1" 200 532 "-" "curl/7.68.0"
192.168.1.100 - - [10/Jan/2024:13:55:38 +0000] "GET /style.css HTTP/1.1" 200 2341 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
192.168.1.102 - - [10/Jan/2024:13:55:39 +0000] "GET /admin HTTP/1.1" 404 162 "-" "python-requests/2.28.1"
192.168.1.102 - - [10/Jan/2024:13:55:40 +0000] "GET /wp-admin HTTP/1.1" 404 162 "-" "python-requests/2.28.1"
192.168.1.102 - - [10/Jan/2024:13:55:41 +0000] "GET /.env HTTP/1.1" 404 162 "-" "python-requests/2.28.1"
192.168.1.100 - - [10/Jan/2024:13:55:42 +0000] "GET /about.html HTTP/1.1" 200 845 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
192.168.1.103 - - [10/Jan/2024:13:55:43 +0000] "POST /api/login HTTP/1.1" 200 89 "-" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
192.168.1.101 - - [10/Jan/2024:13:55:44 +0000] "GET /api/products HTTP/1.1" 200 1876 "-"