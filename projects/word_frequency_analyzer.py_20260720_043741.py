"""
Date: 2026-07-20
Created a CLI tool to analyze word frequencies across text files with options for case sensitivity, minimum occurrence filtering, and top-N results display.
"""

#!/usr/bin/env python3
"""
Word Frequency Analyzer
Analyzes word frequencies in text files with various filtering options.
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


class WordFrequencyAnalyzer:
    """
    Analyzes word frequencies from text files.
    Handles multiple files, case sensitivity, and filtering options.
    """
    
    def __init__(self, case_sensitive=False):
        """
        Initialize the analyzer.
        
        Args:
            case_sensitive: Whether to treat words with different cases as distinct
        """
        self.case_sensitive = case_sensitive
        self.word_counter = Counter()
    
    def add_file(self, filepath):
        """
        Read a file and add its words to the frequency counter.
        
        Args:
            filepath: Path to the text file to analyze
            
        Returns:
            Number of words added from this file
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                words = self._extract_words(content)
                self.word_counter.update(words)
                return len(words)
        except FileNotFoundError:
            print(f"Warning: File '{filepath}' not found, skipping.", file=sys.stderr)
            return 0
        except Exception as e:
            print(f"Warning: Error reading '{filepath}': {e}", file=sys.stderr)
            return 0
    
    def _extract_words(self, text):
        """
        Extract words from text using regex.
        Keeps only alphabetic characters and handles case sensitivity.
        
        Args:
            text: String to extract words from
            
        Returns:
            List of words
        """
        # Match sequences of word characters (letters, numbers, underscores)
        # but we'll filter to mostly alphabetic in practice
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        
        if not self.case_sensitive:
            words = [w.lower() for w in words]
        
        return words
    
    def get_frequencies(self, min_count=1, top_n=None):
        """
        Get word frequencies with optional filtering.
        
        Args:
            min_count: Minimum occurrence count to include
            top_n: If set, return only top N most common words
            
        Returns:
            List of (word, count) tuples sorted by frequency
        """
        filtered = [(word, count) for word, count in self.word_counter.items() 
                    if count >= min_count]
        
        # Sort by count (descending), then alphabetically for ties
        filtered.sort(key=lambda x: (-x[1], x[0]))
        
        if top_n:
            filtered = filtered[:top_n]
        
        return filtered
    
    def total_words(self):
        """Return total number of words processed."""
        return sum(self.word_counter.values())
    
    def unique_words(self):
        """Return number of unique words."""
        return len(self.word_counter)


def print_results(analyzer, args):
    """
    Print analysis results in a formatted table.
    
    Args:
        analyzer: WordFrequencyAnalyzer instance
        args: Command line arguments namespace
    """
    frequencies = analyzer.get_frequencies(
        min_count=args.min_count,
        top_n=args.top
    )
    
    print(f"\n{'='*60}")
    print(f"Word Frequency Analysis")
    print(f"{'='*60}")
    print(f"Total words: {analyzer.total_words():,}")
    print(f"Unique words: {analyzer.unique_words():,}")
    print(f"{'='*60}\n")
    
    if frequencies:
        # Calculate column widths for nice formatting
        max_word_len = max(len(word) for word, _ in frequencies)
        max_count_len = len(str(frequencies[0][1]))
        
        print(f"{'Word':<{max_word_len}}  {'Count':>{max_count_len}}  Percentage")
        print(f"{'-'*max_word_len}  {'-'*max_count_len}  ----------")
        
        total = analyzer.total_words()
        for word, count in frequencies:
            percentage = (count / total) * 100
            print(f"{word:<{max_word_len}}  {count:>{max_count_len}}  {percentage:>6.2f}%")
    else:
        print("No words found matching criteria.")


def main():
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        description="Analyze word frequencies in text files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example: %(prog)s document.txt --top 10 --min-count 5"
    )
    
    parser.add_argument(
        'files',
        nargs='+',
        help='Text file(s) to analyze'
    )
    
    parser.add_argument(
        '-c', '--case-sensitive',
        action='store_true',
        help='Treat words with different cases as distinct'
    )
    
    parser.add_argument(
        '-m', '--min-count',
        type=int,
        default=1,
        help='Minimum occurrence count to display (default: 1)'
    )
    
    parser.add_argument(
        '-t', '--top',
        type=int,
        help='Show only top N most frequent words'
    )
    
    args = parser.parse_args()
    
    # Create analyzer and process files
    analyzer = WordFrequencyAnalyzer(case_sensitive=args.case_sensitive)
    
    for filepath in args.files:
        word_count = analyzer.add_file(filepath)
        if word_count > 0:
            print(f"Processed '{filepath}': {word_count:,} words")
    
    # Display results
    print_results(analyzer, args)


if __name__ == "__main__":
    # Demo mode: create a sample file and analyze it
    if len(sys.argv) == 1:
        print("Running demo with sample text...\n")
        
        # Create a temporary demo file
        demo_text = """
        The quick brown fox jumps over the lazy dog.
        The dog was not amused by the fox.
        The fox thought the dog was being lazy.
        Meanwhile, the brown fox continued jumping.
        """
        
        demo_file = Path("demo_sample.txt")
        demo_file.write_text(demo_text)
        
        # Simulate command line args for demo
        sys.argv = ['word_frequency_analyzer.py', str(demo_file), '--top', '10']
        
        try:
            main()
        finally:
            # Clean up demo file
            demo_file.unlink()
    else:
        main()