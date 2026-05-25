# parses log files and spits out a summary of errors grouped by their messages so you don't have to scroll through thousands of lines
# written: 2026-05-25

#!/usr/bin/env python3
"""
Simple log file summarizer that groups similar errors together.
Useful when you have massive log files and need to see what's actually breaking.
"""

import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path


class LogSummary:
    """Analyzes log files and groups similar entries together."""
    
    def __init__(self):
        self.entries = defaultdict(list)
        self.log_levels = defaultdict(int)
        
    def parse_line(self, line):
        """
        Extract timestamp, level, and message from a log line.
        Handles common log formats like: 2024-01-15 10:30:45 ERROR Something broke
        """
        # Try to match common log patterns
        pattern = r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}).*?(ERROR|WARN|INFO|DEBUG)\s+(.+)'
        match = re.search(pattern, line, re.IGNORECASE)
        
        if match:
            timestamp_str, level, message = match.groups()
            return {
                'timestamp': timestamp_str,
                'level': level.upper(),
                'message': message.strip()
            }
        return None
    
    def normalize_message(self, message):
        """
        Replace dynamic parts (IDs, numbers, paths) with placeholders
        so similar errors get grouped together. This is the tricky part.
        """
        # Replace things that look like IDs or numbers
        normalized = re.sub(r'\b\d+\b', '<NUM>', message)
        # Replace file paths
        normalized = re.sub(r'[/\\][\w/\\.-]+', '<PATH>', normalized)
        # Replace hex values
        normalized = re.sub(r'0x[0-9a-fA-F]+', '<HEX>', normalized)
        return normalized
    
    def add_entry(self, parsed):
        """Add a parsed log entry to our collection."""
        if not parsed:
            return
            
        level = parsed['level']
        message = parsed['message']
        normalized = self.normalize_message(message)
        
        self.log_levels[level] += 1
        self.entries[normalized].append({
            'timestamp': parsed['timestamp'],
            'original': message
        })
    
    def get_summary(self, top_n=10):
        """
        Returns the most common errors/warnings sorted by frequency.
        """
        sorted_entries = sorted(
            self.entries.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )
        return sorted_entries[:top_n]


def generate_sample_log():
    """Generate a sample log file for demo purposes."""
    sample_logs = [
        "2024-01-15 10:30:45 INFO Application started successfully",
        "2024-01-15 10:30:46 INFO Connected to database db_prod_001",
        "2024-01-15 10:31:12 ERROR Failed to process order 12345: Timeout",
        "2024-01-15 10:31:45 ERROR Failed to process order 12389: Timeout",
        "2024-01-15 10:32:01 WARN Cache miss for key user_session_abc123",
        "2024-01-15 10:32:03 ERROR Failed to process order 12401: Timeout",
        "2024-01-15 10:32:15 WARN Cache miss for key user_session_def456",
        "2024-01-15 10:32:30 ERROR Database connection lost at /var/lib/db.sock",
        "2024-01-15 10:32:45 ERROR Database connection lost at /var/lib/db.sock",
        "2024-01-15 10:33:01 INFO Attempting reconnection",
        "2024-01-15 10:33:15 ERROR Failed to process order 12450: Timeout",
        "2024-01-15 10:33:30 ERROR Invalid user token: 0x7f3a2b1c",
        "2024-01-15 10:33:45 ERROR Invalid user token: 0x8e4b3c2d",
        "2024-01-15 10:34:00 WARN Memory usage at 85%",
        "2024-01-15 10:34:15 ERROR Failed to process order 12478: Timeout",
    ]
    return "\n".join(sample_logs)


def main():
    """Main entry point for the log summarizer."""
    print("=== Log Summarizer ===\n")
    
    # For demo purposes, use generated sample logs
    sample_log_content = generate_sample_log()
    print("Analyzing sample log file...\n")
    
    summary = LogSummary()
    
    for line in sample_log_content.split('\n'):
        parsed = summary.parse_line(line)
        summary.add_entry(parsed)
    
    # Print log level counts
    print("Log Level Summary:")
    for level, count in sorted(summary.log_levels.items()):
        print(f"  {level:8s}: {count:3d}")
    
    print("\nTop Error Patterns (grouped by similarity):")
    print("-" * 60)
    
    top_errors = summary.get_summary(top_n=5)
    
    for i, (pattern, occurrences) in enumerate(top_errors, 1):
        print(f"\n{i}. [{len(occurrences)}x] {pattern}")
        # Show first and last occurrence
        if len(occurrences) > 0:
            first = occurrences[0]
            print(f"   First: {first['timestamp']} - {first['original'][:50]}...")
            if len(occurrences) > 1:
                last = occurrences[-1]
                print(f"   Last:  {last['timestamp']} - {last['original'][:50]}...")


if __name__ == "__main__":
    main()