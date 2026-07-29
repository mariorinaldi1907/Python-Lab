"""
Date: 2026-07-29
Made a CLI tool that analyzes source files and gives me a detailed breakdown of code lines, comments, blanks, and calculates code density.
"""

#!/usr/bin/env python3
"""
Line Count Analyzer - breaks down source files into code, comments, and blank lines.

I built this because I wanted to see actual code density in my projects,
not just total line counts that include a ton of whitespace and documentation.
"""

import argparse
import os
import sys
from pathlib import Path
from collections import defaultdict


class LineStats:
    """Holds statistics for a single file's line breakdown."""
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.total = 0
        self.code = 0
        self.comments = 0
        self.blanks = 0
    
    def density(self):
        """Calculate code density as a percentage of non-blank lines."""
        non_blank = self.total - self.blanks
        if non_blank == 0:
            return 0.0
        return (self.code / non_blank) * 100
    
    def __repr__(self):
        return (f"LineStats({self.filepath}: {self.code} code, "
                f"{self.comments} comments, {self.blanks} blanks)")


def detect_comment_style(filepath):
    """
    Figure out comment syntax based on file extension.
    
    Returns tuple of (single_line_prefix, multi_start, multi_end).
    I'm only handling the languages I actually use regularly.
    """
    ext = Path(filepath).suffix.lower()
    
    # Python, shell, Ruby, YAML
    if ext in {'.py', '.sh', '.rb', '.yaml', '.yml'}:
        return ('#', '"""', '"""')
    
    # C-style: C, C++, Java, JavaScript, Go, Rust
    if ext in {'.c', '.cpp', '.cc', '.h', '.hpp', '.java', '.js', '.go', '.rs'}:
        return ('//', '/*', '*/')
    
    # HTML, XML
    if ext in {'.html', '.xml'}:
        return (None, '<!--', '-->')
    
    # Default to hash comments if unknown
    return ('#', None, None)


def analyze_file(filepath):
    """
    Parse a file and count code vs comments vs blank lines.
    
    This is the core logic. I'm tracking state for multi-line comments
    because they can span across many lines and I need to count them correctly.
    """
    stats = LineStats(filepath)
    single_prefix, multi_start, multi_end = detect_comment_style(filepath)
    
    in_multiline = False
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                stats.total += 1
                stripped = line.strip()
                
                # Blank line - easy case
                if not stripped:
                    stats.blanks += 1
                    continue
                
                # Check for multi-line comment toggles
                if multi_start and multi_start in stripped:
                    in_multiline = True
                    stats.comments += 1
                    # Handle single-line multi-comment like /* comment */
                    if multi_end and multi_end in stripped:
                        in_multiline = False
                    continue
                
                if in_multiline:
                    stats.comments += 1
                    if multi_end and multi_end in stripped:
                        in_multiline = False
                    continue
                
                # Single-line comment check
                if single_prefix and stripped.startswith(single_prefix):
                    stats.comments += 1
                    continue
                
                # If we got here, it's a code line
                stats.code += 1
    
    except Exception as e:
        print(f"Warning: couldn't read {filepath}: {e}", file=sys.stderr)
        return None
    
    return stats


def analyze_directory(dirpath, extensions=None):
    """
    Recursively scan a directory and analyze all matching files.
    
    If extensions is None, I'll analyze everything. Otherwise only
    files matching the given extensions (like ['.py', '.js']).
    """
    all_stats = []
    
    for root, dirs, files in os.walk(dirpath):
        # Skip hidden directories and common build/cache folders
        dirs[:] = [d for d in dirs if not d.startswith('.') 
                   and d not in {'node_modules', '__pycache__', 'venv', 'build'}]
        
        for filename in files:
            if filename.startswith('.'):
                continue
            
            filepath = os.path.join(root, filename)
            
            # Filter by extension if specified
            if extensions:
                if not any(filename.endswith(ext) for ext in extensions):
                    continue
            
            stats = analyze_file(filepath)
            if stats:
                all_stats.append(stats)
    
    return all_stats


def print_summary(stats_list):
    """Print a nice table summary of all analyzed files."""
    if not stats_list:
        print("No files analyzed.")
        return
    
    # Sort by code lines descending - I care most about the meatiest files
    stats_list.sort(key=lambda s: s.code, reverse=True)
    
    print(f"\n{'File':<40} {'Code':>8} {'Comments':>8} {'Blanks':>8} {'Density':>8}")
    print("-" * 80)
    
    total_code = 0
    total_comments = 0
    total_blanks = 0
    
    for stats in stats_list:
        print(f"{stats.filepath:<40} {stats.code:>8} {stats.comments:>8} "
              f"{stats.blanks:>8} {stats.density():>7.1f}%")
        total_code += stats.code
        total_comments += stats.comments
        total_blanks += stats.blanks
    
    print("-" * 80)
    total_all = total_code + total_comments + total_blanks
    overall_density = (total_code / (total_all - total_blanks) * 100) if total_all > total_blanks else 0
    
    print(f"{'TOTAL':<40} {total_code:>8} {total_comments:>8} "
          f"{total_blanks:>8} {overall_density:>7.1f}%")
    print()


def main():
    """CLI entry point with argparse setup."""
    parser = argparse.ArgumentParser(
        description="Analyze source files to count code vs comments vs blanks"
    )
    parser.add_argument(
        'path',
        help="File or directory to analyze"
    )
    parser.add_argument(
        '-e', '--extensions',
        nargs='+',
        help="Filter by file extensions (e.g., .py .js)"
    )
    
    args = parser.parse_args()
    
    path = args.path
    
    if not os.path.exists(path):
        print(f"Error: {path} doesn't exist", file=sys.stderr)
        sys.exit(1)
    
    # Analyze single file or directory
    if os.path.isfile(path):
        stats = analyze_file(path)
        if stats:
            print_summary([stats])
    else:
        stats_list = analyze_directory(path, args.extensions)
        print_summary(stats_list)


if __name__ == "__main__":
    # Quick demo showing what the tool does
    print("=== Line Count Analyzer Demo ===")
    print("Analyzing this script itself...\n")
    
    # Analyze this very file as a demo
    demo_stats = analyze_file(__file__)
    if demo_stats:
        print(f"This script has:")
        print(f"  - {demo_stats.code} lines of actual code")
        print(f"  - {demo_stats.comments} lines of comments")
        print(f"  - {demo_stats.blanks} blank lines")
        print(f"  - {demo_stats.density():.1f}% code density")
        print(f"\nTotal: {demo_stats.total} lines")
    
    print("\n" + "="*50)
    print("Run with a file or directory path to analyze your code!")
    print("Example: python line_count_analyzer.py /path/to/project")
    print("="*50 + "\n")