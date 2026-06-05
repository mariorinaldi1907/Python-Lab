"""
Date: 2026-06-05
Created a command-line tool to parse and analyze log files with regex patterns, giving me quick insights into error rates and time distributions.
"""

#!/usr/bin/env python3
"""
Log file analyzer - parses common log formats and gives you stats.
I kept running into situations where I needed quick insights from logs
without spinning up heavy monitoring tools, so I built this.
"""

import argparse
import re
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path


class LogEntry:
    """Represents a single log line with parsed fields."""
    
    def __init__(self, timestamp, level, message):
        self.timestamp = timestamp
        self.level = level
        self.message = message
    
    def __repr__(self):
        return f"LogEntry({self.timestamp}, {self.level}, {self.message[:30]}...)"


class LogAnalyzer:
    """
    Parses and analyzes log files with common formats.
    Currently supports formats like: "2024-01-15 10:23:45 ERROR Something broke"
    """
    
    # Regex to match timestamp, log level, and message
    # Handles formats like: 2024-01-15 10:23:45 INFO Started processing
    LOG_PATTERN = re.compile(
        r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+'  # timestamp
        r'(DEBUG|INFO|WARNING|ERROR|CRITICAL)\s+'       # log level
        r'(.*)'                                          # message
    )
    
    def __init__(self):
        self.entries = []
    
    def parse_file(self, filepath):
        """
        Read and parse a log file line by line.
        Skips lines that don't match the expected format.
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                match = self.LOG_PATTERN.match(line)
                if match:
                    timestamp_str, level, message = match.groups()
                    # Parse timestamp - format is YYYY-MM-DD HH:MM:SS
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    self.entries.append(LogEntry(timestamp, level, message))
    
    def filter_by_level(self, level):
        """Return only entries matching the specified log level."""
        return [e for e in self.entries if e.level == level]
    
    def get_level_counts(self):
        """Count occurrences of each log level."""
        return Counter(e.level for e in self.entries)
    
    def get_hourly_distribution(self):
        """
        Group log entries by hour of day.
        Useful for spotting when errors cluster.
        """
        hourly = defaultdict(int)
        for entry in self.entries:
            hour = entry.timestamp.hour
            hourly[hour] += 1
        return dict(sorted(hourly.items()))
    
    def search_messages(self, keyword):
        """Find all entries where the message contains a keyword (case-insensitive)."""
        keyword_lower = keyword.lower()
        return [e for e in self.entries if keyword_lower in e.message.lower()]


def print_stats(analyzer, args):
    """Display summary statistics based on parsed log data."""
    
    print(f"\n=== Log Analysis Results ===")
    print(f"Total entries parsed: {len(analyzer.entries)}")
    
    if not analyzer.entries:
        print("No log entries found!")
        return
    
    # Show breakdown by level
    print("\n--- Log Level Breakdown ---")
    level_counts = analyzer.get_level_counts()
    for level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
        count = level_counts.get(level, 0)
        if count > 0:
            print(f"  {level:8s}: {count:4d}")
    
    # If filtering by level, show those entries
    if args.level:
        filtered = analyzer.filter_by_level(args.level)
        print(f"\n--- {args.level} Entries ({len(filtered)} total) ---")
        for entry in filtered[:args.limit]:
            print(f"  [{entry.timestamp}] {entry.message}")
    
    # If searching for a keyword
    if args.search:
        results = analyzer.search_messages(args.search)
        print(f"\n--- Search Results for '{args.search}' ({len(results)} matches) ---")
        for entry in results[:args.limit]:
            print(f"  [{entry.timestamp}] [{entry.level}] {entry.message}")
    
    # Show hourly distribution if requested
    if args.hourly:
        print("\n--- Hourly Distribution ---")
        hourly = analyzer.get_hourly_distribution()
        for hour, count in hourly.items():
            bar = '█' * (count // max(1, len(analyzer.entries) // 50))
            print(f"  {hour:02d}:00 | {count:4d} {bar}")


def main():
    """Parse arguments and run the analyzer."""
    parser = argparse.ArgumentParser(
        description='Analyze log files and extract useful stats'
    )
    
    parser.add_argument(
        'logfile',
        type=Path,
        help='Path to the log file to analyze'
    )
    
    parser.add_argument(
        '--level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Filter by specific log level'
    )
    
    parser.add_argument(
        '--search',
        type=str,
        help='Search for keyword in log messages'
    )
    
    parser.add_argument(
        '--hourly',
        action='store_true',
        help='Show hourly distribution of log entries'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=10,
        help='Max number of entries to display (default: 10)'
    )
    
    args = parser.parse_args()
    
    # Make sure the file exists
    if not args.logfile.exists():
        print(f"Error: File '{args.logfile}' not found")
        return 1
    
    # Parse and analyze
    analyzer = LogAnalyzer()
    analyzer.parse_file(args.logfile)
    print_stats(analyzer, args)
    
    return 0


if __name__ == "__main__":
    # Create a sample log file for demo purposes
    sample_log = Path("sample_app.log")
    
    with open(sample_log, 'w') as f:
        f.write("""2024-01-15 08:15:23 INFO Application started
2024-01-15 08:15:24 DEBUG Loading configuration from config.json
2024-01-15 08:15:25 INFO Configuration loaded successfully
2024-01-15 09:23:11 WARNING Database connection slow (1.2s)
2024-01-15 09:23:45 ERROR Failed to process user request: timeout
2024-01-15 09:24:01 ERROR Database connection lost
2024-01-15 09:24:02 INFO Attempting reconnection
2024-01-15 09:24:05 INFO Database reconnected
2024-01-15 10:15:33 WARNING Cache miss rate above threshold (45%)
2024-01-15 10:45:12 INFO Processed 1000 requests
2024-01-15 11:23:55 ERROR Authentication failed for user john@example.com
2024-01-15 14:15:22 INFO Daily backup completed
2024-01-15 14:15:23 DEBUG Cleanup tasks running
2024-01-15 16:32:11 CRITICAL Out of memory - shutting down gracefully
2024-01-15 16:32:15 INFO Application stopped
""")
    
    print("Demo: Analyzing sample_app.log")
    print("=" * 50)
    
    # Simulate command-line args for demo
    import sys
    sys.argv = ['log_analyzer.py', 'sample_app.log', '--hourly', '--level', 'ERROR']
    
    main()
    
    # Cleanup demo file
    sample_log.unlink()