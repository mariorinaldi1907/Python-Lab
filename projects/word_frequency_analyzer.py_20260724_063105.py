"""
Date: 2026-07-24
Created a CLI tool that analyzes text files for word frequencies with options to filter by min occurrences and sort by frequency or alphabetically.
"""

#!/usr/bin/env python3
"""
Word Frequency Analyzer
Counts word occurrences in text files with flexible output options.
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


def tokenize_text(text, case_sensitive=False):
    """
    Extract words from text using regex pattern matching.
    
    Args:
        text: String content to tokenize
        case_sensitive: Whether to preserve case (default: False)
    
    Returns:
        List of word tokens
    """
    # Match word characters, including contractions like "don't"
    pattern = r"\b[a-zA-Z]+(?:'[a-zA-Z]+)?\b"
    words = re.findall(pattern, text)
    
    if not case_sensitive:
        words = [word.lower() for word in words]
    
    return words


def analyze_file(filepath, case_sensitive=False):
    """
    Read a file and return word frequency counter.
    
    Args:
        filepath: Path to the text file
        case_sensitive: Preserve case during counting
    
    Returns:
        Counter object with word frequencies
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Fallback for files with different encoding
        with open(filepath, 'r', encoding='latin-1') as f:
            content = f.read()
    
    words = tokenize_text(content, case_sensitive)
    return Counter(words)


def format_output(word_counts, min_count=1, top_n=None, sort_alpha=False):
    """
    Format word frequencies for display.
    
    Args:
        word_counts: Counter object with frequencies
        min_count: Minimum frequency to include in output
        top_n: Limit to top N results (None for all)
        sort_alpha: Sort alphabetically instead of by frequency
    
    Returns:
        List of formatted strings
    """
    # Filter by minimum count
    filtered = {word: count for word, count in word_counts.items() 
                if count >= min_count}
    
    # Sort either alphabetically or by frequency (descending)
    if sort_alpha:
        sorted_items = sorted(filtered.items(), key=lambda x: x[0])
    else:
        sorted_items = sorted(filtered.items(), key=lambda x: x[1], reverse=True)
    
    # Limit results if requested
    if top_n:
        sorted_items = sorted_items[:top_n]
    
    # Find longest word for alignment
    max_word_len = max(len(word) for word, _ in sorted_items) if sorted_items else 0
    
    output_lines = []
    for word, count in sorted_items:
        output_lines.append(f"{word:<{max_word_len}}  {count:>6}")
    
    return output_lines


def main():
    """
    Main CLI entry point with argparse configuration.
    """
    parser = argparse.ArgumentParser(
        description="Analyze word frequencies in text files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.txt
  %(prog)s document.txt --top 20 --min-count 5
  %(prog)s document.txt --sort-alpha --case-sensitive
        """
    )
    
    parser.add_argument(
        'filepath',
        type=Path,
        help='Path to the text file to analyze'
    )
    
    parser.add_argument(
        '--min-count',
        type=int,
        default=1,
        metavar='N',
        help='Only show words appearing at least N times (default: 1)'
    )
    
    parser.add_argument(
        '--top',
        type=int,
        metavar='N',
        help='Show only the top N most frequent words'
    )
    
    parser.add_argument(
        '--sort-alpha',
        action='store_true',
        help='Sort alphabetically instead of by frequency'
    )
    
    parser.add_argument(
        '--case-sensitive',
        action='store_true',
        help='Treat words with different cases as distinct'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show summary statistics'
    )
    
    args = parser.parse_args()
    
    # Validate file exists
    if not args.filepath.exists():
        print(f"Error: File '{args.filepath}' not found", file=sys.stderr)
        sys.exit(1)
    
    if not args.filepath.is_file():
        print(f"Error: '{args.filepath}' is not a file", file=sys.stderr)
        sys.exit(1)
    
    # Analyze the file
    word_counts = analyze_file(args.filepath, args.case_sensitive)
    
    # Display statistics if requested
    if args.stats:
        total_words = sum(word_counts.values())
        unique_words = len(word_counts)
        print(f"\n{'=' * 50}")
        print(f"File: {args.filepath}")
        print(f"Total words: {total_words:,}")
        print(f"Unique words: {unique_words:,}")
        print(f"{'=' * 50}\n")
    
    # Format and print results
    output_lines = format_output(
        word_counts,
        min_count=args.min_count,
        top_n=args.top,
        sort_alpha=args.sort_alpha
    )
    
    for line in output_lines:
        print(line)
    
    # Print summary footer
    shown_count = len(output_lines)
    total_unique = len(word_counts)
    if shown_count < total_unique:
        print(f"\nShowing {shown_count} of {total_unique} unique words")


if __name__ == "__main__":
    # Demo mode: create a sample file and analyze it
    import tempfile
    import os
    
    # Check if being called with arguments
    if len(sys.argv) > 1:
        main()
    else:
        # Run a demo with sample text
        sample_text = """
        The quick brown fox jumps over the lazy dog.
        The dog was really lazy, and the fox was quick.
        But the lazy dog didn't care about the quick fox.
        """
        
        # Create temporary file for demo
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(sample_text)
            temp_path = f.name
        
        try:
            print("DEMO MODE: Analyzing sample text...")
            print("=" * 50)
            
            # Simulate command line args for demo
            sys.argv = ['word_frequency_analyzer.py', temp_path, '--stats', '--min-count', '2']
            main()
        finally:
            # Clean up temp file
            os.unlink(temp_path)