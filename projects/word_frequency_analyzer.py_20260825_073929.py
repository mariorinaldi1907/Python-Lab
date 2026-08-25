"""
Date: 2026-08-25
Created a command-line word frequency counter that handles file input or stdin, filters stopwords, and outputs clean ranked results — useful for analyzing text dumps.
"""

#!/usr/bin/env python3
"""
Word Frequency Analyzer
Counts word occurrences in text files or stdin, with stopword filtering.
I built this because I was tired of piping text through awk/sort/uniq every time.
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


# Common English stopwords - keeping this minimal to avoid bloat
STOPWORDS = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'is',
}


def tokenize_text(text, case_sensitive=False):
    """
    Extract words from text using regex.
    
    Only keeps alphabetic sequences (sorry numbers, you're out).
    I'm using \w+ then filtering to avoid apostrophe weirdness.
    
    Args:
        text: Input string to tokenize
        case_sensitive: If False, lowercase everything
    
    Returns:
        List of word tokens
    """
    # Pull out word-like sequences
    tokens = re.findall(r'\b[a-zA-Z]+\b', text)
    
    if not case_sensitive:
        tokens = [t.lower() for t in tokens]
    
    return tokens


def count_words(tokens, filter_stopwords=False, min_length=1):
    """
    Count word frequencies with optional filtering.
    
    Args:
        tokens: List of word strings
        filter_stopwords: Remove common English words if True
        min_length: Ignore words shorter than this
    
    Returns:
        Counter object with word frequencies
    """
    # Apply filters before counting to save memory
    filtered = tokens
    
    if filter_stopwords:
        filtered = [w for w in filtered if w not in STOPWORDS]
    
    if min_length > 1:
        filtered = [w for w in filtered if len(w) >= min_length]
    
    return Counter(filtered)


def format_output(word_counts, top_n=None, show_percentages=False, total_words=None):
    """
    Pretty-print word frequency results.
    
    Args:
        word_counts: Counter object with frequencies
        top_n: Limit to top N words (None = show all)
        show_percentages: Include percentage of total
        total_words: Total word count for percentage calc
    
    Returns:
        Formatted string ready for printing
    """
    lines = []
    items = word_counts.most_common(top_n) if top_n else word_counts.most_common()
    
    if not items:
        return "No words found.\n"
    
    # Calculate column widths for alignment
    max_word_len = max(len(word) for word, _ in items)
    max_count_len = len(str(items[0][1]))  # Highest count
    
    for rank, (word, count) in enumerate(items, 1):
        line_parts = [f"{rank:3d}. {word:{max_word_len}} : {count:{max_count_len}d}"]
        
        if show_percentages and total_words:
            pct = (count / total_words) * 100
            line_parts.append(f" ({pct:5.2f}%)")
        
        lines.append(''.join(line_parts))
    
    return '\n'.join(lines) + '\n'


def process_file(filepath, args):
    """
    Read and analyze a single file.
    
    Args:
        filepath: Path object or string
        args: Parsed command-line arguments
    
    Returns:
        Counter object with word frequencies
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    except UnicodeDecodeError:
        # Fallback for non-UTF8 files
        with open(filepath, 'r', encoding='latin-1') as f:
            text = f.read()
    
    tokens = tokenize_text(text, case_sensitive=args.case_sensitive)
    return count_words(tokens, filter_stopwords=args.filter_stopwords, min_length=args.min_length)


def main():
    """
    Main CLI entry point with argument parsing.
    """
    parser = argparse.ArgumentParser(
        description='Analyze word frequencies in text files or stdin.',
        epilog='Example: python %(prog)s -n 20 --stopwords myfile.txt'
    )
    
    parser.add_argument(
        'files',
        nargs='*',
        help='Input text files (omit to read from stdin)'
    )
    parser.add_argument(
        '-n', '--top',
        type=int,
        metavar='N',
        help='Show only top N most frequent words'
    )
    parser.add_argument(
        '-s', '--filter-stopwords',
        action='store_true',
        help='Filter common English stopwords'
    )
    parser.add_argument(
        '-c', '--case-sensitive',
        action='store_true',
        help='Treat uppercase and lowercase as different words'
    )
    parser.add_argument(
        '-m', '--min-length',
        type=int,
        default=1,
        metavar='LEN',
        help='Ignore words shorter than LEN characters (default: 1)'
    )
    parser.add_argument(
        '-p', '--percentages',
        action='store_true',
        help='Show percentage of total words'
    )
    
    args = parser.parse_args()
    
    # Decide input source: files or stdin
    if args.files:
        combined_counts = Counter()
        for filepath in args.files:
            path = Path(filepath)
            if not path.exists():
                print(f"Error: File not found: {filepath}", file=sys.stderr)
                sys.exit(1)
            combined_counts.update(process_file(path, args))
    else:
        # Read from stdin
        text = sys.stdin.read()
        tokens = tokenize_text(text, case_sensitive=args.case_sensitive)
        combined_counts = count_words(tokens, filter_stopwords=args.filter_stopwords, 
                                     min_length=args.min_length)
    
    # Calculate total for percentages
    total_words = sum(combined_counts.values()) if args.percentages else None
    
    # Output results
    output = format_output(combined_counts, top_n=args.top, 
                          show_percentages=args.percentages, total_words=total_words)
    print(output)


if __name__ == "__main__":
    # Demo mode when run directly without args
    if len(sys.argv) == 1:
        print("=== Word Frequency Analyzer Demo ===\n")
        sample_text = """
        The quick brown fox jumps over the lazy dog. The dog was really lazy,
        but the fox was incredibly quick and brown. What a fantastic fox!
        The lazy dog didn't care much about the quick brown fox.
        """
        
        print("Sample text:")
        print(sample_text)
        print("\n--- Results (filtering stopwords, top 5) ---")
        
        tokens = tokenize_text(sample_text, case_sensitive=False)
        word_counts = count_words(tokens, filter_stopwords=True, min_length=1)
        total = sum(word_counts.values())
        
        output = format_output(word_counts, top_n=5, show_percentages=True, total_words=total)
        print(output)
        
        print("\nTry: python word_frequency_analyzer.py --help")
    else:
        main()