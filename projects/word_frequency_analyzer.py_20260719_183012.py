"""
Date: 2026-07-19
Created a command-line tool to analyze word frequencies in text files with optional stopword filtering and configurable output formats.
"""

#!/usr/bin/env python3
"""
Word Frequency Analyzer
Analyzes text files and outputs word frequency statistics.
Supports filtering common stopwords and multiple output formats.
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


# Common English stopwords — could be extended but keeping it reasonable
DEFAULT_STOPWORDS = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'is',
    'was', 'are', 'been', 'has', 'had', 'were', 'can', 'said'
}


def read_text_file(filepath):
    """
    Read and return the contents of a text file.
    
    Args:
        filepath: Path to the text file
        
    Returns:
        String containing file contents
        
    Raises:
        FileNotFoundError: If file doesn't exist
        UnicodeDecodeError: If file isn't valid text
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def extract_words(text, case_sensitive=False):
    """
    Extract words from text using regex pattern.
    
    I'm using \b\w+\b to capture word boundaries — this handles
    contractions and hyphenated words reasonably well while
    filtering out punctuation.
    
    Args:
        text: Input text string
        case_sensitive: Whether to preserve case (default: False)
        
    Returns:
        List of words
    """
    words = re.findall(r'\b\w+\b', text)
    if not case_sensitive:
        words = [word.lower() for word in words]
    return words


def calculate_frequencies(words, exclude_stopwords=False, min_length=1):
    """
    Calculate word frequencies with optional filtering.
    
    Args:
        words: List of words
        exclude_stopwords: Whether to filter common stopwords
        min_length: Minimum word length to include
        
    Returns:
        Counter object with word frequencies
    """
    # Filter based on criteria
    filtered_words = words
    
    if exclude_stopwords:
        filtered_words = [w for w in filtered_words if w not in DEFAULT_STOPWORDS]
    
    if min_length > 1:
        filtered_words = [w for w in filtered_words if len(w) >= min_length]
    
    return Counter(filtered_words)


def format_output(frequency_counter, top_n=None, format_type='text'):
    """
    Format frequency results for display.
    
    Args:
        frequency_counter: Counter object with frequencies
        top_n: Number of top results to show (None = all)
        format_type: Output format ('text' or 'csv')
        
    Returns:
        Formatted string ready for printing
    """
    items = frequency_counter.most_common(top_n)
    
    if format_type == 'csv':
        lines = ['word,count']
        lines.extend([f'{word},{count}' for word, count in items])
        return '\n'.join(lines)
    else:
        # Text format with nice alignment
        if not items:
            return "No words found."
        
        max_word_len = max(len(word) for word, _ in items)
        lines = []
        for word, count in items:
            lines.append(f'{word:<{max_word_len}}  {count:>6}')
        return '\n'.join(lines)


def main():
    """
    Main CLI entry point with argparse configuration.
    """
    parser = argparse.ArgumentParser(
        description='Analyze word frequencies in text files',
        epilog='Example: %(prog)s document.txt -n 20 --no-stopwords'
    )
    
    parser.add_argument(
        'file',
        type=Path,
        help='Text file to analyze'
    )
    
    parser.add_argument(
        '-n', '--top',
        type=int,
        metavar='N',
        help='Show only top N most frequent words'
    )
    
    parser.add_argument(
        '--no-stopwords',
        action='store_true',
        help='Exclude common English stopwords'
    )
    
    parser.add_argument(
        '--min-length',
        type=int,
        default=1,
        metavar='N',
        help='Minimum word length to include (default: 1)'
    )
    
    parser.add_argument(
        '--case-sensitive',
        action='store_true',
        help='Treat uppercase and lowercase as different words'
    )
    
    parser.add_argument(
        '--format',
        choices=['text', 'csv'],
        default='text',
        help='Output format (default: text)'
    )
    
    args = parser.parse_args()
    
    # Validate file exists
    if not args.file.exists():
        print(f"Error: File '{args.file}' not found", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Process the file
        text = read_text_file(args.file)
        words = extract_words(text, case_sensitive=args.case_sensitive)
        frequencies = calculate_frequencies(
            words,
            exclude_stopwords=args.no_stopwords,
            min_length=args.min_length
        )
        
        # Output results
        output = format_output(frequencies, top_n=args.top, format_type=args.format)
        print(output)
        
        # Print summary stats to stderr so it doesn't interfere with CSV output
        total_words = sum(frequencies.values())
        unique_words = len(frequencies)
        print(f'\n[Total: {total_words} words, Unique: {unique_words}]', file=sys.stderr)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    # Demo mode if no arguments provided
    if len(sys.argv) == 1:
        print("=== Word Frequency Analyzer Demo ===\n")
        
        # Create a sample text for demonstration
        sample_text = """
        The quick brown fox jumps over the lazy dog.
        The dog was not amused by the fox.
        Meanwhile, the brown fox continued jumping.
        """
        
        print("Sample text:")
        print(sample_text)
        print("\n--- Analysis (excluding stopwords) ---")
        
        words = extract_words(sample_text, case_sensitive=False)
        frequencies = calculate_frequencies(words, exclude_stopwords=True, min_length=2)
        output = format_output(frequencies, top_n=10, format_type='text')
        
        print(output)
        print(f"\nTotal words: {sum(frequencies.values())}")
        print(f"Unique words: {len(frequencies)}")
        print("\nTry: python word_frequency_analyzer.py --help")
    else:
        main()