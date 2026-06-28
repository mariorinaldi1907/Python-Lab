"""
Date: 2026-06-28
Made a parser for nginx access logs that groups requests by endpoint, tracks response codes, and flags potential bot traffic or attacks.
"""

#!/usr/bin/env python3
"""
Nginx access log parser and analyzer.
Parses standard nginx combined log format and extracts useful metrics.
"""

import re
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class NginxLogEntry:
    """Represents a single parsed line from an nginx access log."""
    
    def __init__(self, ip: str, timestamp: str, method: str, path: str, 
                 status: int, bytes_sent: int, user_agent: str):
        self.ip = ip
        self.timestamp = timestamp
        self.method = method
        self.path = path
        self.status = status
        self.bytes_sent = bytes_sent
        self.user_agent = user_agent
    
    def __repr__(self):
        return f"<LogEntry {self.method} {self.path} -> {self.status}>"


class NginxLogParser:
    """
    Parses and analyzes nginx access logs in combined format.
    
    Combined format looks like:
    127.0.0.1 - - [01/Jan/2024:12:00:00 +0000] "GET /api/users HTTP/1.1" 200 1234 "-" "Mozilla/5.0..."
    """
    
    # Regex pattern for nginx combined log format
    # I'm capturing: IP, timestamp, method, path, status, bytes, user agent
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d\.]+) - - \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\S+) (?P<path>\S+) HTTP/[\d\.]+" '
        r'(?P<status>\d+) (?P<bytes>\d+) '
        r'"[^"]*" "(?P<user_agent>[^"]*)"'
    )
    
    def __init__(self):
        self.entries: List[NginxLogEntry] = []
        self.parse_errors = 0
    
    def parse_line(self, line: str) -> Optional[NginxLogEntry]:
        """
        Parse a single log line and return an entry object.
        Returns None if the line doesn't match expected format.
        """
        match = self.LOG_PATTERN.match(line.strip())
        if not match:
            self.parse_errors += 1
            return None
        
        data = match.groupdict()
        
        return NginxLogEntry(
            ip=data['ip'],
            timestamp=data['timestamp'],
            method=data['method'],
            path=data['path'],
            status=int(data['status']),
            bytes_sent=int(data['bytes']),
            user_agent=data['user_agent']
        )
    
    def parse_file(self, filepath: str):
        """Read and parse an entire log file."""
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                entry = self.parse_line(line)
                if entry:
                    self.entries.append(entry)
    
    def get_status_distribution(self) -> Counter:
        """Count how many requests returned each status code."""
        return Counter(entry.status for entry in self.entries)
    
    def get_top_paths(self, n: int = 10) -> List[Tuple[str, int]]:
        """Return the N most frequently requested paths."""
        path_counts = Counter(entry.path for entry in self.entries)
        return path_counts.most_common(n)
    
    def get_top_ips(self, n: int = 10) -> List[Tuple[str, int]]:
        """Return the N IPs that made the most requests."""
        ip_counts = Counter(entry.ip for entry in self.entries)
        return ip_counts.most_common(n)
    
    def detect_suspicious_activity(self) -> Dict[str, List]:
        """
        Flag potentially suspicious patterns.
        This is pretty basic heuristics — real security analysis is way deeper.
        """
        suspicious = defaultdict(list)
        
        # Group requests by IP to analyze patterns
        ip_requests = defaultdict(list)
        for entry in self.entries:
            ip_requests[entry.ip].append(entry)
        
        for ip, requests in ip_requests.items():
            # Flag IPs with lots of 404s (scanning for vulnerabilities?)
            not_found_count = sum(1 for r in requests if r.status == 404)
            if not_found_count > 20:
                suspicious['high_404_count'].append((ip, not_found_count))
            
            # Flag IPs making tons of requests (potential DDoS or aggressive scraping)
            if len(requests) > 100:
                suspicious['high_request_volume'].append((ip, len(requests)))
            
            # Look for common bot user agents
            for req in requests:
                ua_lower = req.user_agent.lower()
                if any(bot in ua_lower for bot in ['bot', 'crawler', 'spider', 'scraper']):
                    suspicious['bot_traffic'].append((ip, req.user_agent))
                    break  # Only flag once per IP
        
        return suspicious
    
    def generate_report(self) -> str:
        """Generate a summary report of the parsed logs."""
        lines = []
        lines.append("=" * 60)
        lines.append("NGINX LOG ANALYSIS REPORT")
        lines.append("=" * 60)
        lines.append(f"\nTotal requests parsed: {len(self.entries)}")
        lines.append(f"Parse errors: {self.parse_errors}")
        
        lines.append("\n--- Status Code Distribution ---")
        for status, count in sorted(self.get_status_distribution().items()):
            lines.append(f"  {status}: {count}")
        
        lines.append("\n--- Top 5 Requested Paths ---")
        for path, count in self.get_top_paths(5):
            lines.append(f"  {count:4d}x  {path}")
        
        lines.append("\n--- Top 5 IPs by Request Count ---")
        for ip, count in self.get_top_ips(5):
            lines.append(f"  {count:4d}x  {ip}")
        
        suspicious = self.detect_suspicious_activity()
        if suspicious:
            lines.append("\n--- Suspicious Activity Detected ---")
            if 'high_404_count' in suspicious:
                lines.append(f"  High 404 errors: {len(suspicious['high_404_count'])} IPs")
            if 'high_request_volume' in suspicious:
                lines.append(f"  High request volume: {len(suspicious['high_request_volume'])} IPs")
            if 'bot_traffic' in suspicious:
                lines.append(f"  Bot traffic: {len(suspicious['bot_traffic'])} IPs")
        
        return "\n".join(lines)


if __name__ == "__main__":
    # Create a sample log file for demo purposes
    sample_log = """127.0.0.1 - - [15/Jan/2024:10:23:45 +0000] "GET /api/users HTTP/1.1" 200 1543 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
192.168.1.100 - - [15/Jan/2024:10:24:12 +0000] "POST /api/login HTTP/1.1" 200 234 "-" "curl/7.68.0"
10.0.0.5 - - [15/Jan/2024:10:24:45 +0000] "GET /admin HTTP/1.1" 404 162 "-" "Mozilla/5.0"
127.0.0.1 - - [15/Jan/2024:10:25:01 +0000] "GET /api/products HTTP/1.1" 200 8734 "-" "Mozilla/5.0"
10.0.0.5 - - [15/Jan/2024:10:25:10 +0000] "GET /wp-admin HTTP/1.1" 404 162 "-" "Googlebot/2.1"
192.168.1.100 - - [15/Jan/2024:10:25:33 +0000] "GET /api/users HTTP/1.1" 200 1543 "-" "PostmanRuntime/7.26.8"
10.0.0.5 - - [15/Jan/2024:10:25:55 +0000] "GET /.env HTTP/1.1" 404 162 "-" "Googlebot/2.1"
127.0.0.1 - - [15/Jan/2024:10:26:12 +0000] "GET /health HTTP/1.1" 200 15 "-" "curl/7.68.0"
10.0.0.5 - - [15/Jan/2024:10:26:30 +0000] "GET /config.php HTTP/1.1" 404 162 "-" "Googlebot/2.1"
192.168.1.100 - - [15/Jan/2024:10:26:45 +0000] "DELETE /api/users/123 HTTP/1.1" 204 0 "-" "axios/0.21.1"
"""
    
    # Write sample data to a temp file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        f.write(sample_log)
        temp_path = f.name
    
    print