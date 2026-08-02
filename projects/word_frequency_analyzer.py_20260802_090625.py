"""
Date: 2026-08-02
Created a CLI tool to analyze text files and show word frequency distributions — includes basic stemming and common word filtering to get more meaningful results.
"""

#!/usr/bin/env python3
"""
Word Frequency Analyzer
Analyzes text files to find the most common words, with optional stopword filtering
and basic stemming to group similar words together.
"""

import argparse
import re
from collections import Counter
from pathlib import Path


# Basic stopwords - common English words that don't add much meaning
STOPWORDS = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
    'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go',
    'me', 'when', 'make', 'can', 'like', 'no', 'just', 'him', 'know',
    'take', 'into', 'your', 'some', 'could', 'them', 'than', 'then',
    'now', 'only', 'come', 'its', 'over', 'also', 'back', 'after',
    'use', 'how', 'our', 'work', 'first', 'well', 'way', 'even', 'new',
    'want', 'because', 'any', 'these', 'give', 'most', 'us', 'is', 'was',
    'are', 'been', 'has', 'had', 'were', 'said', 'did', 'am'
}


def simple_stem(word):
    """
    Apply very basic stemming rules to normalize word forms.
    This isn't Porter or Snowball, just enough to catch common plurals and verb forms.
    """
    # Remove common suffixes to group related words
    if len(word) > 4:
        if word.endswith('ing'):
            return word[:-3]
        if word.endswith('ed'):
            return word[:-2]
        if word.endswith('s') and not word.endswith('ss'):
            return word[:-1]
    return word


def extract_words(text, use_stemming=False, filter_stopwords=False, min_length=1):
    """
    Extract and normalize words from text.
    Returns a list of words after applying various filters and transformations.
    """
    # Convert to lowercase and extract alphabetic sequences
    # I'm using a simple regex here because it's fast and handles most cases
    words = re.findall(r'[a-z]+', text.lower())
    
    # Apply length filter first to reduce processing
    words = [w for w in words if len(w) >= min_length]
    
    # Filter out stopwords if requested
    if filter_stopwords:
        words = [w for w in words if w not in STOPWORDS]
    
    # Apply stemming to group similar words
    if use_stemming:
        words = [simple_stem(w) for w in words]
    
    return words


def analyze_file(filepath, top_n=20, use_stemming=False, filter_stopwords=False, min_length=1):
    """
    Analyze a text file and return the most common words.
    Returns a list of (word, count) tuples sorted by frequency.
    """
    try:
        # Read the entire file - this is fine for reasonably sized text files
        # For gigantic files, you'd want to process in chunks
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
    except FileNotFoundError:
        raise ValueError(f"File not found: {filepath}")
    except PermissionError:
        raise ValueError(f"Permission denied reading: {filepath}")
    
    words = extract_words(text, use_stemming, filter_stopwords, min_length)
    
    if not words:
        return []
    
    # Counter is perfect for this - handles the frequency counting efficiently
    word_counts = Counter(words)
    return word_counts.most_common(top_n)


def print_results(results, filepath, total_words):
    """
    Pretty-print the analysis results in a readable table format.
    """
    print(f"\n{'='*60}")
    print(f"Word Frequency Analysis: {Path(filepath).name}")
    print(f"{'='*60}")
    print(f"Total words analyzed: {total_words:,}")
    print(f"{'='*60}\n")
    
    if not results:
        print("No words found matching the criteria.")
        return
    
    # Calculate column widths for nice alignment
    max_word_len = max(len(word) for word, _ in results)
    max_count_len = len(str(results[0][1]))
    
    print(f"{'Rank':<6} {'Word':<{max_word_len}} {'Count':>{max_count_len}}  {'Frequency'}")
    print(f"{'-'*6} {'-'*max_word_len} {'-'*max_count_len}  {'-'*10}")
    
    for rank, (word, count) in enumerate(results, 1):
        percentage = (count / total_words) * 100
        print(f"{rank:<6} {word:<{max_word_len}} {count:>{max_count_len}}  {percentage:6.2f}%")


def main():
    """
    Main entry point - handles CLI argument parsing and orchestrates the analysis.
    """
    parser = argparse.ArgumentParser(
        description='Analyze word frequency in text files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Example: %(prog)s document.txt -n 10 -s -f'
    )
    
    parser.add_argument('file', help='Text file to analyze')
    parser.add_argument('-n', '--top', type=int, default=20,
                       help='Number of top words to display (default: 20)')
    parser.add_argument('-s', '--stem', action='store_true',
                       help='Apply basic stemming to group similar words')
    parser.add_argument('-f', '--filter-stopwords', action='store_true',
                       help='Filter out common English stopwords')
    parser.add_argument('-m', '--min-length', type=int, default=1,
                       help='Minimum word length to include (default: 1)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.top < 1:
        parser.error("--top must be at least 1")
    if args.min_length < 1:
        parser.error("--min-length must be at least 1")
    
    try:
        # Run the analysis
        results = analyze_file(
            args.file,
            top_n=args.top,
            use_stemming=args.stem,
            filter_stopwords=args.filter_stopwords,
            min_length=args.min_length
        )
        
        # Calculate total for percentage display
        total = sum(count for _, count in results) if results else 0
        
        print_results(results, args.file, total)
        
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user")
        return 130
    
    return 0


if __name__ == "__main__":
    # Demo mode - create a sample file and analyze it
    import tempfile
    import sys
    
    # If no arguments provided, run a demo
    if len(sys.argv) == 1:
        print("Running demo mode...\n")
        
        # Create a temporary file with sample text
        sample_text = """
        The quick brown fox jumps over the lazy dog. The dog was very lazy indeed.
        Foxes are quick and clever animals. The brown fox is quicker than most foxes.
        Dogs can be lazy, but they are also loyal companions. The quick movements of
        the fox amazed everyone watching. Brown is a common color for foxes in the wild.
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(sample_text)
            temp_path = f.name
        
        try:
            # Simulate command line arguments for demo
            sys.argv = ['word_frequency_analyzer.py', temp_path, '-n', '10', '-s', '-f']
            exit(main())
        finally:
            # Clean up temp file
            Path(temp_path).unlink()
    else:
        exit(main())