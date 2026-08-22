"""
Date: 2026-08-22
Made a command-line tool to analyze text files and find the most common words, with customizable filters because I got tired of counting manually in log files.
"""

#!/usr/bin/env python3
"""
Word Frequency Analyzer - counts word occurrences in text files.

I wrote this because I kept needing to analyze logs and documents to find
patterns, and opening them in editors or using grep was getting tedious.
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


# Common English stopwords - I built this list from the ones I saw cluttering
# my actual analysis results. Feel free to expand it.
DEFAULT_STOPWORDS = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'is'
}


def load_stopwords(filepath):
    """
    Load custom stopwords from a file (one word per line).
    
    Returns a set of lowercase words. I added this so I could maintain
    domain-specific stopword lists for different projects.
    """
    stopwords = set()
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            word = line.strip().lower()
            if word:
                stopwords.add(word)
    return stopwords


def analyze_text(text, min_length=1, case_sensitive=False, stopwords=None):
    """
    Count word frequencies in the given text.
    
    Args:
        text: String to analyze
        min_length: Minimum word length to count (helps filter noise)
        case_sensitive: Whether to treat 'Word' and 'word' differently
        stopwords: Set of words to ignore (e.g., 'the', 'and')
    
    Returns:
        Counter object with word frequencies
    """
    # Extract words using regex - I'm keeping alphanumeric and hyphens
    # because words like 'self-aware' should stay together
    words = re.findall(r'\b[\w\-]+\b', text)
    
    # Process each word based on our filters
    processed_words = []
    for word in words:
        if not case_sensitive:
            word = word.lower()
        
        # Skip if below minimum length
        if len(word) < min_length:
            continue
        
        # Skip stopwords if we're filtering them
        if stopwords and word.lower() in stopwords:
            continue
        
        processed_words.append(word)
    
    return Counter(processed_words)


def format_results(counter, top_n, show_percentages=False):
    """
    Format the word frequency results for display.
    
    I added percentage display because sometimes raw counts don't give
    enough context about distribution.
    """
    if not counter:
        return "No words found matching the criteria."
    
    total_words = sum(counter.values())
    lines = []
    
    # Get the top N most common words
    for rank, (word, count) in enumerate(counter.most_common(top_n), 1):
        if show_percentages:
            percentage = (count / total_words) * 100
            lines.append(f"{rank:3d}. {word:20s} {count:6d} ({percentage:5.2f}%)")
        else:
            lines.append(f"{rank:3d}. {word:20s} {count:6d}")
    
    return '\n'.join(lines)


def main():
    """
    Main entry point - sets up argument parsing and runs the analysis.
    """
    parser = argparse.ArgumentParser(
        description='Analyze word frequencies in text files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Example: %(prog)s document.txt -n 20 --min-length 4 --no-stopwords'
    )
    
    parser.add_argument('file', type=Path, help='Text file to analyze')
    parser.add_argument('-n', '--top', type=int, default=10,
                        help='Number of top words to display (default: 10)')
    parser.add_argument('-m', '--min-length', type=int, default=1,
                        help='Minimum word length to count (default: 1)')
    parser.add_argument('-c', '--case-sensitive', action='store_true',
                        help='Treat uppercase and lowercase as different words')
    parser.add_argument('--no-stopwords', action='store_true',
                        help='Don\'t filter common stopwords')
    parser.add_argument('--stopwords-file', type=Path,
                        help='Custom stopwords file (one word per line)')
    parser.add_argument('-p', '--percentages', action='store_true',
                        help='Show percentages alongside counts')
    
    args = parser.parse_args()
    
    # Validate input file
    if not args.file.exists():
        print(f"Error: File '{args.file}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Read the file - using utf-8 because I've been burned by encoding issues
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Set up stopwords based on arguments
    stopwords = None
    if not args.no_stopwords:
        if args.stopwords_file:
            stopwords = load_stopwords(args.stopwords_file)
        else:
            stopwords = DEFAULT_STOPWORDS
    
    # Run the analysis
    word_counts = analyze_text(
        text,
        min_length=args.min_length,
        case_sensitive=args.case_sensitive,
        stopwords=stopwords
    )
    
    # Display results
    print(f"\nAnalysis of: {args.file}")
    print(f"Total unique words: {len(word_counts)}")
    print(f"Total word count: {sum(word_counts.values())}")
    print(f"\nTop {args.top} most frequent words:\n")
    print(format_results(word_counts, args.top, args.percentages))


if __name__ == "__main__":
    # Demo mode - if no args provided, analyze this script itself
    if len(sys.argv) == 1:
        print("=== DEMO MODE: Analyzing this script's source code ===\n")
        
        # Read our own source code
        script_path = Path(__file__)
        with open(script_path, 'r', encoding='utf-8') as f:
            demo_text = f.read()
        
        # Analyze with some sensible defaults
        word_counts = analyze_text(
            demo_text,
            min_length=3,
            case_sensitive=False,
            stopwords=DEFAULT_STOPWORDS
        )
        
        print(f"File: {script_path.name}")
        print(f"Total unique words (3+ chars): {len(word_counts)}")
        print(f"Total words analyzed: {sum(word_counts.values())}")
        print("\nTop 15 most common words:\n")
        print(format_results(word_counts, 15, show_percentages=True))
        print("\n--- Run with --help to see all options ---")
    else:
        main()