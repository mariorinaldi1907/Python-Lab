"""
Date: 2026-06-23
Created a CLI tool to analyze word frequencies in text files with stopword filtering and multiple output formats because I got tired of manually counting words in my writing.
"""

#!/usr/bin/env python3
"""
Word Frequency Analyzer
Analyzes word frequencies in text files with filtering and formatting options.
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


# Common English stopwords to filter out
DEFAULT_STOPWORDS = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
    'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me',
    'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take',
    'into', 'year', 'your', 'some', 'could', 'them', 'see', 'other', 'than',
    'then', 'now', 'look', 'only', 'come', 'its', 'over', 'also', 'back',
    'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way',
    'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us'
}


def read_and_tokenize(filepath, case_sensitive=False):
    """
    Read a file and tokenize it into words.
    
    Uses regex to extract only alphabetic sequences, which handles
    punctuation and numbers gracefully.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Extract words (alphabetic sequences only)
    words = re.findall(r'[a-zA-Z]+', text)
    
    if not case_sensitive:
        words = [w.lower() for w in words]
    
    return words


def filter_stopwords(words, use_stopwords):
    """
    Remove common stopwords from the word list.
    
    Only filters if use_stopwords is True — sometimes you want
    to see ALL words including common ones.
    """
    if not use_stopwords:
        return words
    
    return [w for w in words if w.lower() not in DEFAULT_STOPWORDS]


def analyze_frequencies(words, top_n=None, min_length=1):
    """
    Count word frequencies and return sorted results.
    
    Args:
        words: List of words to analyze
        top_n: Limit results to top N most frequent (None = all)
        min_length: Filter out words shorter than this
    
    Returns:
        List of (word, count) tuples sorted by frequency
    """
    # Filter by minimum length
    words = [w for w in words if len(w) >= min_length]
    
    counter = Counter(words)
    
    # Sort by frequency (descending), then alphabetically for ties
    sorted_words = sorted(counter.items(), key=lambda x: (-x[1], x[0]))
    
    if top_n:
        sorted_words = sorted_words[:top_n]
    
    return sorted_words


def format_output(word_freq, total_words, output_format='table'):
    """
    Format the frequency analysis results for display.
    
    Supports table and simple formats — table is prettier but
    simple is easier to pipe into other tools.
    """
    if output_format == 'simple':
        for word, count in word_freq:
            percentage = (count / total_words * 100) if total_words > 0 else 0
            print(f"{word}: {count} ({percentage:.2f}%)")
    else:  # table format
        if not word_freq:
            print("No words found.")
            return
        
        # Calculate column widths for nice alignment
        max_word_len = max(len(word) for word, _ in word_freq)
        max_count_len = len(str(word_freq[0][1]))
        
        # Header
        print(f"{'Word':<{max_word_len}}  {'Count':>{max_count_len}}  Percentage")
        print("-" * (max_word_len + max_count_len + 15))
        
        # Data rows
        for word, count in word_freq:
            percentage = (count / total_words * 100) if total_words > 0 else 0
            print(f"{word:<{max_word_len}}  {count:>{max_count_len}}  {percentage:>6.2f}%")
        
        # Summary
        print("-" * (max_word_len + max_count_len + 15))
        print(f"Total unique words: {len(word_freq)}")
        print(f"Total word count: {total_words}")


def main():
    """Parse arguments and run the word frequency analysis."""
    parser = argparse.ArgumentParser(
        description='Analyze word frequencies in text files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Example: %(prog)s document.txt -t 20 --filter-stopwords'
    )
    
    parser.add_argument('file', type=str, help='Text file to analyze')
    parser.add_argument('-t', '--top', type=int, metavar='N',
                        help='Show only top N most frequent words')
    parser.add_argument('-m', '--min-length', type=int, default=1, metavar='LEN',
                        help='Minimum word length to include (default: 1)')
    parser.add_argument('-f', '--filter-stopwords', action='store_true',
                        help='Filter out common English stopwords')
    parser.add_argument('-c', '--case-sensitive', action='store_true',
                        help='Treat words as case-sensitive')
    parser.add_argument('-o', '--output', choices=['table', 'simple'],
                        default='table', help='Output format (default: table)')
    
    args = parser.parse_args()
    
    # Process the file
    words = read_and_tokenize(args.file, case_sensitive=args.case_sensitive)
    words = filter_stopwords(words, args.filter_stopwords)
    
    if not words:
        print("No words found in file after filtering.", file=sys.stderr)
        sys.exit(1)
    
    word_freq = analyze_frequencies(words, top_n=args.top, min_length=args.min_length)
    
    # Display results
    format_output(word_freq, len(words), output_format=args.output)


if __name__ == "__main__":
    # Demo mode: analyze this script itself if no args provided
    if len(sys.argv) == 1:
        print("=== DEMO MODE: Analyzing this script's word frequencies ===\n")
        
        # Create a temporary demo by analyzing our own source
        sys.argv = [sys.argv[0], __file__, '--top', '15', '--filter-stopwords', '--min-length', '3']
        main()