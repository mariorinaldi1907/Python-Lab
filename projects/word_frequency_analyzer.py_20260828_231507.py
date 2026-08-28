"""
Date: 2026-08-28
Created a word frequency counter that handles multiple input sources and lets you filter by min occurrences or top N results — useful for quick text analysis.
"""

#!/usr/bin/env python3
"""
Word Frequency Analyzer
Counts word occurrences in text files or stdin, with options to filter results.
I built this because I kept needing to analyze log files and text dumps quickly.
"""

import argparse
import sys
import re
from collections import Counter
from typing import Iterator, TextIO


def normalize_word(word: str, case_sensitive: bool = False) -> str:
    """
    Strip punctuation and optionally lowercase a word.
    
    I'm keeping apostrophes for contractions like "don't" but removing
    everything else that isn't alphanumeric.
    """
    # Remove leading/trailing punctuation but keep internal apostrophes
    word = re.sub(r"^[^\w']+|[^\w']+$", '', word)
    
    if not case_sensitive:
        word = word.lower()
    
    return word


def extract_words(text: str, case_sensitive: bool = False) -> Iterator[str]:
    """
    Break text into words and normalize them.
    
    Yields each word after normalization. Empty strings are skipped because
    they'd just pollute the counts.
    """
    # Split on whitespace and common delimiters
    raw_words = re.split(r'\s+', text)
    
    for word in raw_words:
        normalized = normalize_word(word, case_sensitive)
        if normalized:  # Skip empty strings
            yield normalized


def count_words_from_file(file_handle: TextIO, case_sensitive: bool = False) -> Counter:
    """
    Read a file and return word frequency counts.
    
    Using Counter here because it's built exactly for this use case and
    handles the accumulation cleanly.
    """
    word_counter = Counter()
    
    for line in file_handle:
        words = extract_words(line, case_sensitive)
        word_counter.update(words)
    
    return word_counter


def format_output(word_counts: Counter, top_n: int = None, min_count: int = 1) -> str:
    """
    Format word counts into readable output.
    
    Returns a string with one word per line in the format: "word: count"
    Sorted by frequency (descending), then alphabetically for ties.
    """
    # Filter by minimum count first
    filtered = {word: count for word, count in word_counts.items() if count >= min_count}
    
    # Sort by count (desc) then by word (asc) for consistent ordering
    sorted_items = sorted(filtered.items(), key=lambda x: (-x[1], x[0]))
    
    # Limit to top N if specified
    if top_n:
        sorted_items = sorted_items[:top_n]
    
    # Build output string
    lines = []
    max_word_length = max((len(word) for word, _ in sorted_items), default=0)
    
    for word, count in sorted_items:
        # Right-align the counts for readability
        lines.append(f"{word.ljust(max_word_length)} : {count:>6}")
    
    return '\n'.join(lines)


def main():
    """
    Main entry point for the CLI.
    
    Handles argument parsing and orchestrates the word counting process.
    """
    parser = argparse.ArgumentParser(
        description='Count word frequencies in text files or stdin.',
        epilog='Example: python word_frequency_analyzer.py myfile.txt --top 10'
    )
    
    parser.add_argument(
        'files',
        nargs='*',
        type=argparse.FileType('r', encoding='utf-8'),
        default=[sys.stdin],
        help='Input files to analyze (default: stdin)'
    )
    
    parser.add_argument(
        '-t', '--top',
        type=int,
        metavar='N',
        help='Show only the top N most frequent words'
    )
    
    parser.add_argument(
        '-m', '--min-count',
        type=int,
        default=1,
        metavar='MIN',
        help='Show only words appearing at least MIN times (default: 1)'
    )
    
    parser.add_argument(
        '-c', '--case-sensitive',
        action='store_true',
        help='Treat words as case-sensitive (default: case-insensitive)'
    )
    
    args = parser.parse_args()
    
    # Aggregate counts from all input files
    total_counts = Counter()
    
    for file_handle in args.files:
        try:
            file_counts = count_words_from_file(file_handle, args.case_sensitive)
            total_counts.update(file_counts)
        except Exception as e:
            print(f"Error reading {file_handle.name}: {e}", file=sys.stderr)
            sys.exit(1)
        finally:
            if file_handle != sys.stdin:
                file_handle.close()
    
    # Output results
    if total_counts:
        output = format_output(total_counts, args.top, args.min_count)
        print(output)
        print(f"\nTotal unique words: {len(total_counts)}")
        print(f"Total word count: {sum(total_counts.values())}")
    else:
        print("No words found.", file=sys.stderr)


if __name__ == "__main__":
    # Demo mode: analyze a sample text if run directly without arguments
    if len(sys.argv) == 1 and sys.stdin.isatty():
        print("=== Word Frequency Analyzer Demo ===\n")
        
        # Sample text for demonstration
        sample_text = """
        The quick brown fox jumps over the lazy dog.
        The dog was really lazy, but the fox was quick!
        Quick movements and lazy afternoons define the fox and dog.
        """
        
        print("Analyzing sample text:")
        print(sample_text)
        print("\n--- Results ---\n")
        
        # Process the sample
        word_counter = Counter()
        for line in sample_text.strip().split('\n'):
            words = extract_words(line, case_sensitive=False)
            word_counter.update(words)
        
        output = format_output(word_counter, top_n=None, min_count=1)
        print(output)
        print(f"\nTotal unique words: {len(word_counter)}")
        print(f"Total word count: {sum(word_counter.values())}")
        
        print("\n\nRun with --help to see usage options for analyzing your own files!")
    else:
        main()