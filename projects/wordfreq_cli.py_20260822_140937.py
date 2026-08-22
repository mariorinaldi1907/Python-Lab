"""
Date: 2026-08-22
Created a command-line tool to analyze text files and show word frequencies, with options to filter common words and sort by count or alphabetically.
"""

#!/usr/bin/env python3
"""
Word Frequency Analyzer CLI
Counts word occurrences in text files with customizable filters and sorting.
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


# Common English stopwords to filter out noise
STOPWORDS = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
    'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go',
    'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
    'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them',
    'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over',
    'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work',
    'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these',
    'give', 'day', 'most', 'us', 'is', 'was', 'are', 'been', 'has', 'had',
    'were', 'said', 'did', 'having', 'may', 'should', 'am'
}


def read_file(filepath):
    """
    Read and return file contents as a string.
    Handles common encoding issues gracefully.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Fallback for files with different encodings
        with open(filepath, 'r', encoding='latin-1') as f:
            return f.read()


def extract_words(text, case_sensitive=False):
    """
    Extract words from text using regex.
    Returns a list of words, optionally preserving case.
    """
    # Match sequences of word characters (letters, numbers, underscores)
    words = re.findall(r'\b\w+\b', text)
    
    if not case_sensitive:
        words = [word.lower() for word in words]
    
    return words


def filter_stopwords(words, remove_stopwords):
    """
    Remove common stopwords from the word list if requested.
    Only filters when words are lowercase (case-insensitive mode).
    """
    if not remove_stopwords:
        return words
    
    return [word for word in words if word.lower() not in STOPWORDS]


def analyze_frequency(words, top_n=None):
    """
    Count word frequencies and return as a Counter object.
    Optionally limit to top N most common words.
    """
    counter = Counter(words)
    
    if top_n:
        # most_common returns list of (word, count) tuples
        return dict(counter.most_common(top_n))
    
    return dict(counter)


def format_output(freq_dict, sort_by='count'):
    """
    Format the frequency dictionary for display.
    Sorts by count (descending) or alphabetically based on sort_by param.
    """
    if sort_by == 'alpha':
        items = sorted(freq_dict.items(), key=lambda x: x[0])
    else:  # sort by count
        items = sorted(freq_dict.items(), key=lambda x: x[1], reverse=True)
    
    # Find max word length for nice alignment
    max_word_len = max(len(word) for word, _ in items) if items else 0
    
    lines = []
    for word, count in items:
        lines.append(f"{word:<{max_word_len}} : {count}")
    
    return '\n'.join(lines)


def main():
    """
    Main entry point for the CLI tool.
    Parses arguments and orchestrates the analysis.
    """
    parser = argparse.ArgumentParser(
        description='Analyze word frequencies in text files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Example: python wordfreq_cli.py myfile.txt -t 20 --stopwords'
    )
    
    parser.add_argument('filepath', type=str, help='Path to the text file to analyze')
    parser.add_argument('-t', '--top', type=int, metavar='N',
                        help='Show only top N most frequent words')
    parser.add_argument('-s', '--stopwords', action='store_true',
                        help='Filter out common English stopwords')
    parser.add_argument('-c', '--case-sensitive', action='store_true',
                        help='Treat words as case-sensitive')
    parser.add_argument('--sort', choices=['count', 'alpha'], default='count',
                        help='Sort output by count or alphabetically (default: count)')
    
    args = parser.parse_args()
    
    # Validate file exists
    filepath = Path(args.filepath)
    if not filepath.exists():
        print(f"Error: File '{args.filepath}' not found.", file=sys.stderr)
        sys.exit(1)
    
    # Read and process the file
    text = read_file(filepath)
    words = extract_words(text, case_sensitive=args.case_sensitive)
    words = filter_stopwords(words, args.stopwords)
    
    if not words:
        print("No words found in file.", file=sys.stderr)
        sys.exit(0)
    
    # Analyze and display results
    freq_dict = analyze_frequency(words, top_n=args.top)
    output = format_output(freq_dict, sort_by=args.sort)
    
    print(f"\nWord Frequency Analysis: {filepath.name}")
    print(f"Total unique words: {len(freq_dict)}")
    print(f"Total words analyzed: {len(words)}")
    print("-" * 50)
    print(output)


if __name__ == "__main__":
    # Demo mode: create a sample file and analyze it
    if len(sys.argv) == 1:
        print("=== DEMO MODE ===\n")
        
        # Create a sample text file for demonstration
        demo_text = """
        The quick brown fox jumps over the lazy dog.
        The dog was not amused by the quick fox.
        Meanwhile, the brown fox continued to jump and play.
        The lazy dog decided to chase the fox, but the fox was too quick.
        In the end, both the fox and the dog became friends.
        """
        
        demo_file = Path('demo_sample.txt')
        demo_file.write_text(demo_text)
        
        print(f"Created demo file: {demo_file}\n")
        
        # Simulate command line args for demo
        sys.argv = ['wordfreq_cli.py', str(demo_file), '-t', '10', '--stopwords']
        
    main()