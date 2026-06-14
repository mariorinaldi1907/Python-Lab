"""
Date: 2026-06-14
Created a CLI tool to analyze word frequency in text files with sorting options and export formats — something I needed for analyzing my writing patterns.
"""

#!/usr/bin/env python3
"""
Word Frequency Analyzer
Analyzes text files and outputs word frequency statistics with various filtering options.
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


class WordFrequencyAnalyzer:
    """
    Analyzes word frequencies in text, with options for case sensitivity,
    minimum word length, and stop word filtering.
    """
    
    def __init__(self, case_sensitive=False, min_length=1, stop_words=None):
        """
        Initialize the analyzer with configuration options.
        
        Args:
            case_sensitive: Whether to treat words as case-sensitive
            min_length: Minimum word length to include in analysis
            stop_words: Set of words to exclude from analysis
        """
        self.case_sensitive = case_sensitive
        self.min_length = min_length
        self.stop_words = stop_words or set()
        
    def extract_words(self, text):
        """
        Extract words from text using regex, applying filters.
        
        I'm using \w+ to match word characters, which handles most cases well.
        Could be more sophisticated with Unicode, but this works for my use cases.
        """
        # Extract all word sequences
        words = re.findall(r'\w+', text)
        
        # Apply transformations and filters
        processed_words = []
        for word in words:
            if not self.case_sensitive:
                word = word.lower()
            
            # Skip if below minimum length or in stop words
            if len(word) >= self.min_length and word not in self.stop_words:
                processed_words.append(word)
        
        return processed_words
    
    def analyze(self, text):
        """
        Analyze text and return a Counter object with word frequencies.
        """
        words = self.extract_words(text)
        return Counter(words)


def load_stop_words(stop_words_file):
    """
    Load stop words from a file, one per line.
    Returns an empty set if file doesn't exist or can't be read.
    """
    try:
        with open(stop_words_file, 'r', encoding='utf-8') as f:
            return {line.strip().lower() for line in f if line.strip()}
    except (FileNotFoundError, IOError) as e:
        print(f"Warning: Could not load stop words file: {e}", file=sys.stderr)
        return set()


def format_output(counter, top_n, format_type):
    """
    Format the frequency counter for output.
    
    I added multiple formats because sometimes I want to pipe this into
    other tools or just quickly scan the results.
    """
    results = counter.most_common(top_n) if top_n else counter.most_common()
    
    if format_type == 'simple':
        for word, count in results:
            print(f"{word}: {count}")
    
    elif format_type == 'csv':
        print("word,count")
        for word, count in results:
            print(f"{word},{count}")
    
    elif format_type == 'detailed':
        if not results:
            print("No words found.")
            return
        
        total_words = sum(counter.values())
        unique_words = len(counter)
        
        print(f"Total words: {total_words}")
        print(f"Unique words: {unique_words}")
        print("-" * 50)
        
        for word, count in results:
            percentage = (count / total_words) * 100
            print(f"{word:20} {count:8} ({percentage:5.2f}%)")


def main():
    """
    Main entry point for the CLI tool.
    """
    parser = argparse.ArgumentParser(
        description="Analyze word frequency in text files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.txt
  %(prog)s -n 20 --case-sensitive article.txt
  %(prog)s --format csv --min-length 4 novel.txt
  cat file.txt | %(prog)s -
        """
    )
    
    parser.add_argument('input', 
                       help='Input file path (use "-" for stdin)')
    parser.add_argument('-n', '--top', 
                       type=int, 
                       metavar='N',
                       help='Show only top N words')
    parser.add_argument('-c', '--case-sensitive', 
                       action='store_true',
                       help='Treat words as case-sensitive')
    parser.add_argument('-m', '--min-length', 
                       type=int, 
                       default=1,
                       metavar='LENGTH',
                       help='Minimum word length (default: 1)')
    parser.add_argument('-s', '--stop-words', 
                       metavar='FILE',
                       help='File containing stop words (one per line)')
    parser.add_argument('-f', '--format', 
                       choices=['simple', 'detailed', 'csv'],
                       default='detailed',
                       help='Output format (default: detailed)')
    
    args = parser.parse_args()
    
    # Load stop words if specified
    stop_words = set()
    if args.stop_words:
        stop_words = load_stop_words(args.stop_words)
    
    # Read input
    try:
        if args.input == '-':
            text = sys.stdin.read()
        else:
            with open(args.input, 'r', encoding='utf-8') as f:
                text = f.read()
    except IOError as e:
        print(f"Error reading input: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Analyze and display results
    analyzer = WordFrequencyAnalyzer(
        case_sensitive=args.case_sensitive,
        min_length=args.min_length,
        stop_words=stop_words
    )
    
    word_counts = analyzer.analyze(text)
    format_output(word_counts, args.top, args.format)


if __name__ == "__main__":
    # Demo mode: analyze this script itself
    if len(sys.argv) == 1:
        print("=== DEMO: Analyzing this Python script ===\n")
        
        script_path = Path(__file__)
        with open(script_path, 'r', encoding='utf-8') as f:
            demo_text = f.read()
        
        analyzer = WordFrequencyAnalyzer(
            case_sensitive=False,
            min_length=3,
            stop_words={'the', 'and', 'for', 'with', 'this', 'from'}
        )
        
        word_counts = analyzer.analyze(demo_text)
        format_output(word_counts, top_n=15, format_type='detailed')
    else:
        main()