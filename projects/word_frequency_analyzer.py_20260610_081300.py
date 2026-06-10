"""
Date: 2026-06-10
Created a word frequency counter that lets me quickly analyze text files with optional stopword filtering and flexible output formats.
"""

#!/usr/bin/env python3
"""
Word Frequency Analyzer
Analyzes text files and outputs word frequency statistics.
Useful for quick text analysis, finding common words, and preprocessing data.
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


# Common English stopwords - keeping this minimal for standard library only
DEFAULT_STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'as', 'by', 'with', 'from', 'is', 'was', 'are', 'were', 'be',
    'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
    'would', 'should', 'could', 'may', 'might', 'can', 'this', 'that',
    'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'them'
}


def read_text_file(filepath):
    """
    Read and return the contents of a text file.
    Tries multiple encodings because I've been burned by encoding issues before.
    """
    encodings = ['utf-8', 'latin-1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    
    # If all encodings fail, raise an error
    raise ValueError(f"Could not decode {filepath} with any common encoding")


def extract_words(text, case_sensitive=False):
    """
    Extract words from text using regex.
    Lowercases by default because most frequency analysis benefits from it.
    """
    # Match sequences of word characters (letters, numbers, underscores)
    words = re.findall(r'\b\w+\b', text)
    
    if not case_sensitive:
        words = [word.lower() for word in words]
    
    return words


def filter_stopwords(words, use_stopwords=True, custom_stopwords=None):
    """
    Remove common stopwords from the word list.
    Returns all words if use_stopwords is False.
    """
    if not use_stopwords:
        return words
    
    # Combine default and custom stopwords
    stopwords = DEFAULT_STOPWORDS.copy()
    if custom_stopwords:
        stopwords.update(custom_stopwords)
    
    return [word for word in words if word not in stopwords]


def analyze_frequency(words, top_n=None, min_length=1):
    """
    Count word frequencies and return sorted results.
    Uses Counter because it's perfect for this - I love Python's stdlib.
    """
    # Filter by minimum length if specified
    if min_length > 1:
        words = [word for word in words if len(word) >= min_length]
    
    counter = Counter(words)
    
    # Get most common words, limited to top_n if specified
    if top_n:
        return counter.most_common(top_n)
    
    return counter.most_common()


def format_output(frequency_data, total_words, unique_words, format_type='table'):
    """
    Format the frequency analysis results for display.
    Supports different output formats for different use cases.
    """
    if format_type == 'csv':
        print("word,count,percentage")
        for word, count in frequency_data:
            percentage = (count / total_words) * 100
            print(f"{word},{count},{percentage:.2f}")
    else:  # table format
        print(f"\nTotal words: {total_words}")
        print(f"Unique words: {unique_words}")
        print("\n{:<20} {:<10} {:<10}".format("Word", "Count", "Frequency"))
        print("-" * 40)
        
        for word, count in frequency_data:
            percentage = (count / total_words) * 100
            print(f"{word:<20} {count:<10} {percentage:>6.2f}%")


def main():
    """
    Main entry point - parses arguments and orchestrates the analysis.
    """
    parser = argparse.ArgumentParser(
        description="Analyze word frequency in text files. Built this for quick text stats.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('file', type=str, help='Path to the text file to analyze')
    parser.add_argument('-n', '--top', type=int, default=20, 
                       help='Number of top words to display (default: 20)')
    parser.add_argument('-m', '--min-length', type=int, default=1,
                       help='Minimum word length to include (default: 1)')
    parser.add_argument('-s', '--no-stopwords', action='store_true',
                       help='Include stopwords in analysis')
    parser.add_argument('-c', '--case-sensitive', action='store_true',
                       help='Make word matching case-sensitive')
    parser.add_argument('-f', '--format', choices=['table', 'csv'], default='table',
                       help='Output format (default: table)')
    
    args = parser.parse_args()
    
    # Validate file exists
    filepath = Path(args.file)
    if not filepath.exists():
        print(f"Error: File '{args.file}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Read and process the file
    try:
        text = read_text_file(filepath)
        words = extract_words(text, case_sensitive=args.case_sensitive)
        
        # Filter stopwords unless explicitly disabled
        filtered_words = filter_stopwords(words, use_stopwords=not args.no_stopwords)
        
        # Analyze frequency
        frequency_data = analyze_frequency(filtered_words, top_n=args.top, 
                                          min_length=args.min_length)
        
        # Display results
        total_words = len(filtered_words)
        unique_words = len(set(filtered_words))
        format_output(frequency_data, total_words, unique_words, format_type=args.format)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # Demo mode - analyze this script itself if no arguments provided
    if len(sys.argv) == 1:
        print("=== DEMO MODE: Analyzing this script's own source code ===\n")
        
        # Read this script
        current_file = Path(__file__)
        text = read_text_file(current_file)
        
        # Process words
        words = extract_words(text, case_sensitive=False)
        filtered_words = filter_stopwords(words, use_stopwords=True)
        
        # Get top 15 for demo
        frequency_data = analyze_frequency(filtered_words, top_n=15, min_length=3)
        
        # Display
        total_words = len(filtered_words)
        unique_words = len(set(filtered_words))
        format_output(frequency_data, total_words, unique_words, format_type='table')
        
        print("\n" + "="*50)
        print("Try: python word_frequency_analyzer.py <your_file.txt>")
        print("     python word_frequency_analyzer.py --help")
    else:
        main()