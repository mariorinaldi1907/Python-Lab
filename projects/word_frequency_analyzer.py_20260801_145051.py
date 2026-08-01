"""
Date: 2026-08-01
Created a command-line tool to analyze word frequencies in text files with optional stopword filtering and configurable output limits.
"""

#!/usr/bin/env python3
"""
Word Frequency Analyzer
Analyzes text files and outputs word frequency statistics.
Supports stopword filtering and various output formats.
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


# Common English stopwords - keeping this minimal to avoid bloat
DEFAULT_STOPWORDS = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what'
}


def load_stopwords(stopwords_file):
    """
    Load stopwords from a file (one word per line).
    Returns a set of lowercase stopwords.
    """
    stopwords = set()
    try:
        with open(stopwords_file, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip().lower()
                if word:
                    stopwords.add(word)
        return stopwords
    except FileNotFoundError:
        print(f"Warning: stopwords file '{stopwords_file}' not found, using defaults", file=sys.stderr)
        return DEFAULT_STOPWORDS


def extract_words(text, min_length=1):
    """
    Extract words from text using regex.
    Only keeps alphabetic words of at least min_length characters.
    Returns a list of lowercase words.
    """
    # This pattern splits on non-alphabetic characters
    words = re.findall(r'[a-zA-Z]+', text.lower())
    return [w for w in words if len(w) >= min_length]


def analyze_file(filepath, stopwords=None, min_length=1):
    """
    Read a file and return word frequency counter.
    Filters out stopwords if provided.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    except UnicodeDecodeError:
        # Try with different encoding if UTF-8 fails
        with open(filepath, 'r', encoding='latin-1') as f:
            text = f.read()
    
    words = extract_words(text, min_length)
    
    # Filter stopwords if provided
    if stopwords:
        words = [w for w in words if w not in stopwords]
    
    return Counter(words)


def format_output(counter, top_n=None, show_percentage=False, total_words=None):
    """
    Format the word frequency counter for display.
    Returns a list of formatted strings.
    """
    if total_words is None:
        total_words = sum(counter.values())
    
    # Get the most common words
    items = counter.most_common(top_n)
    
    lines = []
    for word, count in items:
        if show_percentage:
            percentage = (count / total_words) * 100
            lines.append(f"{word:20} {count:6} ({percentage:5.2f}%)")
        else:
            lines.append(f"{word:20} {count:6}")
    
    return lines


def main():
    """
    Main entry point for the CLI tool.
    """
    parser = argparse.ArgumentParser(
        description='Analyze word frequencies in text files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.txt
  %(prog)s document.txt --top 20 --min-length 4
  %(prog)s document.txt --no-stopwords --percentage
  %(prog)s document.txt --stopwords custom_stopwords.txt
        """
    )
    
    parser.add_argument('file', type=Path, help='Text file to analyze')
    parser.add_argument('-t', '--top', type=int, default=25,
                        help='Show top N words (default: 25)')
    parser.add_argument('-m', '--min-length', type=int, default=1,
                        help='Minimum word length to consider (default: 1)')
    parser.add_argument('--no-stopwords', action='store_true',
                        help='Do not filter common stopwords')
    parser.add_argument('-s', '--stopwords', type=Path,
                        help='Custom stopwords file (one word per line)')
    parser.add_argument('-p', '--percentage', action='store_true',
                        help='Show percentages alongside counts')
    
    args = parser.parse_args()
    
    # Validate file exists
    if not args.file.exists():
        print(f"Error: file '{args.file}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Determine stopwords to use
    stopwords = None
    if not args.no_stopwords:
        if args.stopwords:
            stopwords = load_stopwords(args.stopwords)
        else:
            stopwords = DEFAULT_STOPWORDS
    
    # Analyze the file
    print(f"Analyzing: {args.file}")
    counter = analyze_file(args.file, stopwords, args.min_length)
    total_words = sum(counter.values())
    unique_words = len(counter)
    
    print(f"Total words: {total_words}")
    print(f"Unique words: {unique_words}")
    print()
    
    # Display results
    header = "Word                 Count"
    if args.percentage:
        header += "  Percentage"
    print(header)
    print("-" * len(header))
    
    output_lines = format_output(counter, args.top, args.percentage, total_words)
    for line in output_lines:
        print(line)


if __name__ == "__main__":
    # Demo mode - create a sample text and analyze it
    if len(sys.argv) == 1:
        print("=== DEMO MODE ===")
        print("Creating sample text file for demonstration...\n")
        
        sample_text = """
        Python is an amazing programming language. Python makes programming fun.
        The beauty of Python lies in its simplicity. Many developers love Python
        because Python is easy to learn and powerful. Programming in Python feels
        natural and intuitive. Python's syntax is clean and readable.
        """
        
        demo_file = Path("demo_sample.txt")
        demo_file.write_text(sample_text)
        
        print(f"Sample text:\n{sample_text}\n")
        print("=" * 60)
        print()
        
        # Analyze the demo file
        sys.argv = ['word_frequency_analyzer.py', str(demo_file), '--top', '10']
        main()
        
        # Clean up
        demo_file.unlink()
    else:
        main()