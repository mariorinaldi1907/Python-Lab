"""
Date: 2026-05-31
Created a word frequency counter that can process text files or stdin, filter common words, and output results as plain text, JSON, or CSV — helps me analyze writing patterns in my docs.
"""

#!/usr/bin/env python3
"""
Word Frequency Analyzer
Analyzes text files and counts word occurrences with various filtering options.
"""

import argparse
import json
import csv
import sys
import re
from collections import Counter
from pathlib import Path


# Common English stopwords - I keep this minimal but effective
STOPWORDS = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
    'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go',
    'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
    'take', 'into', 'year', 'your', 'some', 'could', 'them', 'see', 'other',
    'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think',
    'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first',
    'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give',
    'day', 'most', 'us', 'is', 'was', 'are', 'been', 'has', 'had', 'were',
    'said', 'did', 'having', 'may', 'should', 'am'
}


def read_text(file_path):
    """
    Read text from a file or stdin.
    
    Args:
        file_path: Path to file, or None for stdin
    
    Returns:
        String containing the full text
    """
    if file_path is None:
        return sys.stdin.read()
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def tokenize_text(text, min_length=1, case_sensitive=False):
    """
    Extract words from text using regex.
    
    I'm using \w+ which gets alphanumeric sequences - works well for most use cases.
    Could be more sophisticated with Unicode handling, but this covers 95% of my needs.
    
    Args:
        text: Input text string
        min_length: Minimum word length to include
        case_sensitive: Whether to preserve case
    
    Returns:
        List of word tokens
    """
    # Extract words (alphanumeric sequences)
    words = re.findall(r'\w+', text)
    
    if not case_sensitive:
        words = [w.lower() for w in words]
    
    # Filter by minimum length
    words = [w for w in words if len(w) >= min_length]
    
    return words


def count_frequencies(words, filter_stopwords=False, top_n=None):
    """
    Count word frequencies and optionally filter/limit results.
    
    Args:
        words: List of word tokens
        filter_stopwords: Remove common English stopwords
        top_n: Return only the N most common words (None = all)
    
    Returns:
        Counter object with word frequencies
    """
    if filter_stopwords:
        words = [w for w in words if w not in STOPWORDS]
    
    counter = Counter(words)
    
    if top_n is not None:
        # most_common returns list of tuples, convert back to Counter
        return Counter(dict(counter.most_common(top_n)))
    
    return counter


def output_plain(counter, show_percentages=False):
    """Print frequencies in plain text format."""
    total = sum(counter.values()) if show_percentages else None
    
    for word, count in counter.most_common():
        if show_percentages:
            pct = (count / total) * 100
            print(f"{word:20} {count:6} ({pct:5.2f}%)")
        else:
            print(f"{word:20} {count:6}")


def output_json(counter):
    """Print frequencies as JSON."""
    # Convert Counter to regular dict and sort by frequency
    data = dict(counter.most_common())
    print(json.dumps(data, indent=2))


def output_csv(counter):
    """Print frequencies as CSV to stdout."""
    writer = csv.writer(sys.stdout)
    writer.writerow(['word', 'count'])
    for word, count in counter.most_common():
        writer.writerow([word, count])


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description='Analyze word frequencies in text files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.txt
  %(prog)s -s -t 20 article.txt
  cat *.md | %(prog)s --format json
  %(prog)s -s -p README.md
        """
    )
    
    parser.add_argument('file', nargs='?', help='Input file (or stdin if not provided)')
    parser.add_argument('-s', '--stopwords', action='store_true',
                        help='Filter common English stopwords')
    parser.add_argument('-t', '--top', type=int, metavar='N',
                        help='Show only top N most frequent words')
    parser.add_argument('-m', '--min-length', type=int, default=1, metavar='N',
                        help='Minimum word length (default: 1)')
    parser.add_argument('-c', '--case-sensitive', action='store_true',
                        help='Preserve case (default: case-insensitive)')
    parser.add_argument('-f', '--format', choices=['plain', 'json', 'csv'],
                        default='plain', help='Output format (default: plain)')
    parser.add_argument('-p', '--percentages', action='store_true',
                        help='Show percentages in plain format')
    
    args = parser.parse_args()
    
    # Read input
    try:
        text = read_text(args.file)
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Process text
    words = tokenize_text(text, min_length=args.min_length, 
                          case_sensitive=args.case_sensitive)
    counter = count_frequencies(words, filter_stopwords=args.stopwords,
                                top_n=args.top)
    
    # Output results
    if args.format == 'json':
        output_json(counter)
    elif args.format == 'csv':
        output_csv(counter)
    else:
        output_plain(counter, show_percentages=args.percentages)


if __name__ == "__main__":
    # Demo with sample text
    if len(sys.argv) == 1:
        print("=== Word Frequency Analyzer Demo ===\n")
        
        sample_text = """
        Python is an amazing programming language. Python makes programming
        fun and accessible. Many developers love Python because Python is
        readable and powerful. Programming in Python feels natural.
        """
        
        print("Sample text:")
        print(sample_text)
        print("\n--- Without stopword filtering ---")
        words = tokenize_text(sample_text)
        counter = count_frequencies(words)
        output_plain(counter, show_percentages=True)
        
        print("\n--- With stopword filtering (top 5) ---")
        counter = count_frequencies(words, filter_stopwords=True, top_n=5)
        output_plain(counter, show_percentages=True)
        
        print("\n--- JSON format ---")
        output_json(counter)
        
        print("\nTry: python word_frequency_analyzer.py --help")
    else:
        main()