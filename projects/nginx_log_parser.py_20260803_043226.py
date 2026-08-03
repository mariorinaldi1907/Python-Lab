"""
Date: 2026-08-03
Wrote a log parser that chews through nginx access logs and spits out traffic stats, error rates, and flags potential bot activity — been wanting to analyze my VPS logs for a while.
"""

#!/usr/bin/env python3
"""
nginx access log parser - analyzes traffic patterns and detects anomalies.
Parses standard nginx combined log format and generates useful statistics.
"""

import re
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Tuple


class NginxLogParser:
    """
    Parses nginx access logs in combined format and extracts meaningful insights.
    Focuses on traffic patterns, status codes, and suspicious activity detection.
    """
    
    # Regex for nginx combined log format - built this by hand, painful but worth it
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d\.]+) - (?P<user>\S+) \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\S+) (?P<path>\S+) (?P<protocol>\S+)" '
        r'(?P<status>\d+) (?P<bytes>\d+) "(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)"'
    )
    
    def __init__(self):
        self.entries = []
        self.ip_requests = Counter()
        self.status_codes = Counter()
        self.paths = Counter()
        self.user_agents = Counter()
        self.methods = Counter()
        
    def parse_line(self, line: str) -> Dict:
        """
        Parse a single log line into structured data.
        Returns None if line doesn't match expected format.
        """
        match = self.LOG_PATTERN.match(line)
        if not match:
            return None
        
        data = match.groupdict()
        # Convert numeric fields - keeping bytes as int is useful for bandwidth calc
        data['status'] = int(data['status'])
        data['bytes'] = int(data['bytes']) if data['bytes'] != '-' else 0
        
        return data
    
    def load_file(self, filepath: str):
        """
        Load and parse an entire log file.
        Silently skips malformed lines because real logs are messy.
        """
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                entry = self.parse_line(line.strip())
                if entry:
                    self.entries.append(entry)
                    self._update_stats(entry)
    
    def _update_stats(self, entry: Dict):
        """Update internal counters - doing this during parse for efficiency."""
        self.ip_requests[entry['ip']] += 1
        self.status_codes[entry['status']] += 1
        self.paths[entry['path']] += 1
        self.user_agents[entry['user_agent']] += 1
        self.methods[entry['method']] += 1
    
    def get_summary(self) -> Dict:
        """Generate overall traffic summary statistics."""
        total_requests = len(self.entries)
        total_bytes = sum(e['bytes'] for e in self.entries)
        
        return {
            'total_requests': total_requests,
            'total_bandwidth_mb': round(total_bytes / (1024 * 1024), 2),
            'unique_ips': len(self.ip_requests),
            'status_breakdown': dict(self.status_codes.most_common()),
            'top_paths': self.paths.most_common(5),
            'http_methods': dict(self.methods)
        }
    
    def detect_suspicious_ips(self, threshold: int = 100) -> List[Tuple[str, int]]:
        """
        Flag IPs with abnormally high request counts - classic bot/scraper behavior.
        Threshold is tunable based on your typical traffic patterns.
        """
        return [(ip, count) for ip, count in self.ip_requests.most_common() 
                if count > threshold]
    
    def find_error_paths(self) -> List[Tuple[str, int]]:
        """
        Find paths that frequently return errors (4xx/5xx).
        Helps identify broken links or application issues.
        """
        error_paths = Counter()
        for entry in self.entries:
            if entry['status'] >= 400:
                error_paths[entry['path']] += 1
        
        return error_paths.most_common(10)
    
    def get_crawler_activity(self) -> Dict[str, int]:
        """
        Identify known crawlers/bots by user agent string.
        Useful for understanding how much of your traffic is automated.
        """
        bot_keywords = ['bot', 'crawler', 'spider', 'scraper', 'curl', 'wget']
        bot_requests = Counter()
        
        for agent, count in self.user_agents.items():
            agent_lower = agent.lower()
            if any(keyword in agent_lower for keyword in bot_keywords):
                bot_requests[agent] = count
        
        return dict(bot_requests.most_common(10))


def print_section(title: str):
    """Helper to make output readable - because wall of text is awful."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


if __name__ == "__main__":
    # Demo with sample log data - this is what actual nginx logs look like
    sample_log = """192.168.1.100 - - [15/Jan/2024:10:23:45 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
192.168.1.101 - - [15/Jan/2024:10:23:46 +0000] "GET /api/users HTTP/1.1" 200 5678 "https://example.com" "curl/7.68.0"
192.168.1.100 - - [15/Jan/2024:10:23:47 +0000] "POST /login HTTP/1.1" 401 89 "-" "Mozilla/5.0"
192.168.1.102 - - [15/Jan/2024:10:23:48 +0000] "GET /admin HTTP/1.1" 403 234 "-" "Googlebot/2.1"
192.168.1.100 - - [15/Jan/2024:10:23:49 +0000] "GET /missing.html HTTP/1.1" 404 178 "-" "Mozilla/5.0"
192.168.1.103 - - [15/Jan/2024:10:23:50 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
192.168.1.100 - - [15/Jan/2024:10:23:51 +0000] "GET /about.html HTTP/1.1" 200 2345 "-" "Mozilla/5.0"
192.168.1.104 - - [15/Jan/2024:10:23:52 +0000] "GET /robots.txt HTTP/1.1" 200 45 "-" "Bingbot/2.0"
192.168.1.100 - - [15/Jan/2024:10:23:53 +0000] "GET /contact.html HTTP/1.1" 500 890 "-" "Mozilla/5.0"
"""
    
    # Write sample data to temp file
    with open('/tmp/sample_nginx.log', 'w') as f:
        f.write(sample_log)
    
    # Parse and analyze
    parser = NginxLogParser()
    parser.load_file('/tmp/sample_nginx.log')
    
    print_section("TRAFFIC SUMMARY")
    summary = parser.get_summary()
    print(f"Total Requests: {summary['total_requests']}")
    print(f"Bandwidth: {summary['total_bandwidth_mb']} MB")
    print(f"Unique IPs: {summary['unique_ips']}")
    print(f"\nHTTP Status Codes:")
    for status, count in sorted(summary['status_breakdown'].items()):
        print(f"  {status}: {count}")
    
    print_section("TOP REQUESTED PATHS")
    for path, count in summary['top_paths']:
        print(f"  {count:3d} - {path}")
    
    print_section("ERROR ANALYSIS")
    error_paths = parser.find_error_paths()
    if error_paths:
        print("Paths with errors:")
        for path, count in error_paths:
            print(f"  {count:3d} errors - {path}")
    else:
        print("No errors found - clean logs!")
    
    print_section("BOT/CRAWLER ACTIVITY")
    crawlers = parser.get_crawler_activity()
    if crawlers:
        for agent, count in crawlers.items():
            print(f"  {count:3d} - {agent[:60]}...")
    else:
        print("No bot activity detected")
    
    print_section("SUSPICIOUS IPs (>3 requests)")
    suspicious = parser.detect_suspicious_ips(threshold=3)
    if suspicious:
        for ip, count in suspicious:
            print(f"  {ip}: {count} requests")
    else:
        print("No suspicious activity detected")
    
    print("\n")