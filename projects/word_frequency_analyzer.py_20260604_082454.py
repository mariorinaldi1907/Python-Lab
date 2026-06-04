"""
Date: 2026-06-04
Created a word frequency counter that processes text files with optional stopword filtering and configurable output limits — helps me analyze writing patterns in my markdown notes.
"""

#!/usr/bin/env python3
"""
Word Frequency Analyzer
Counts word occurrences in text files with optional stopword filtering.
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


class WordFrequencyAnalyzer:
    """Analyzes word frequencies in text with optional stopword filtering."""
    
    # Common English stopwords - could expand this but keeping it practical
    DEFAULT_STOPWORDS = {
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
        'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
        'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
        'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'is',
        'was', 'are', 'been', 'has', 'had', 'were', 'said', 'can', 'me', 'so'
    }
    
    def __init__(self, case_sensitive=False, use_stopwords=False):
        """
        Initialize the analyzer with configuration options.
        
        Args:
            case_sensitive: Whether to treat 'Word' and 'word' as different
            use_stopwords: Whether to filter out common words
        """
        self.case_sensitive = case_sensitive
        self.stopwords = self.DEFAULT_STOPWORDS if use_stopwords else set()
    
    def tokenize(self, text):
        """
        Extract words from text, handling punctuation and whitespace.
        
        Args:
            text: Input string to tokenize
            
        Returns:
            List of word tokens
        """
        # Match sequences of word characters (letters, numbers, underscores)
        # This keeps contractions together which I think makes sense
        words = re.findall(r'\b\w+\b', text)
        
        if not self.case_sensitive:
            words = [w.lower() for w in words]
        
        # Filter stopwords if enabled
        if self.stopwords:
            words = [w for w in words if w.lower() not in self.stopwords]
        
        return words
    
    def analyze_file(self, filepath):
        """
        Read a file and count word frequencies.
        
        Args:
            filepath: Path to text file
            
        Returns:
            Counter object with word frequencies
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
        except UnicodeDecodeError:
            # Fallback for files with different encoding
            with open(filepath, 'r', encoding='latin-1') as f:
                text = f.read()
        
        words = self.tokenize(text)
        return Counter(words)
    
    def format_results(self, counter, top_n=None, min_count=1):
        """
        Format word frequency results for display.
        
        Args:
            counter: Counter object with frequencies
            top_n: Limit to top N results (None for all)
            min_count: Minimum frequency to include
            
        Returns:
            Formatted string with results
        """
        # Filter by minimum count first
        filtered = {word: count for word, count in counter.items() if count >= min_count}
        
        # Sort by frequency (descending), then alphabetically for ties
        sorted_items = sorted(filtered.items(), key=lambda x: (-x[1], x[0]))
        
        if top_n:
            sorted_items = sorted_items[:top_n]
        
        if not sorted_items:
            return "No words found matching criteria."
        
        # Calculate padding for alignment
        max_word_len = max(len(word) for word, _ in sorted_items)
        max_count_len = len(str(sorted_items[0][1]))
        
        lines = []
        total_words = sum(counter.values())
        
        for word, count in sorted_items:
            percentage = (count / total_words) * 100
            line = f"{word:<{max_word_len}}  {count:>{max_count_len}}  ({percentage:5.2f}%)"
            lines.append(line)
        
        return '\n'.join(lines)


def main():
    """Parse arguments and run the word frequency analyzer."""
    parser = argparse.ArgumentParser(
        description='Analyze word frequencies in text files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Example: %(prog)s document.txt -t 20 -s'
    )
    
    parser.add_argument(
        'file',
        type=Path,
        help='Path to text file to analyze'
    )
    
    parser.add_argument(
        '-t', '--top',
        type=int,
        metavar='N',
        help='Show only top N most frequent words'
    )
    
    parser.add_argument(
        '-m', '--min-count',
        type=int,
        default=1,
        metavar='COUNT',
        help='Minimum word frequency to display (default: 1)'
    )
    
    parser.add_argument(
        '-s', '--stopwords',
        action='store_true',
        help='Filter out common English stopwords'
    )
    
    parser.add_argument(
        '-c', '--case-sensitive',
        action='store_true',
        help='Treat words with different cases as distinct'
    )
    
    args = parser.parse_args()
    
    # Validate file exists
    if not args.file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    
    if not args.file.is_file():
        print(f"Error: Not a file: {args.file}", file=sys.stderr)
        sys.exit(1)
    
    # Run analysis
    analyzer = WordFrequencyAnalyzer(
        case_sensitive=args.case_sensitive,
        use_stopwords=args.stopwords
    )
    
    counter = analyzer.analyze_file(args.file)
    results = analyzer.format_results(counter, top_n=args.top, min_count=args.min_count)
    
    print(f"\nWord Frequency Analysis: {args.file.name}")
    print(f"Total unique words: {len(counter)}")
    print(f"Total word count: {sum(counter.values())}")
    print("-" * 50)
    print(results)


if __name__ == "__main__":
    # Demo with sample text if no args provided
    if len(sys.argv) == 1:
        print("=== Demo Mode: Analyzing sample text ===\n")
        
        # Create a temp sample file
        sample_text = """
        The quick brown fox jumps over the lazy dog.
        The dog was not amused by the fox.
        Meanwhile, the fox was quite proud of the jump.
        The quick fox and the lazy dog met again later that day.
        """
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(sample_text)
            temp_path = f.name
        
        # Demo without stopwords
        print("1. Basic analysis:")
        analyzer = WordFrequencyAnalyzer()
        counter = analyzer.analyze_file(temp_path)
        print(analyzer.format_results(counter, top_n=10))
        
        print("\n" + "="*50 + "\n")
        
        # Demo with stopwords
        print("2. Analysis with stopwords filtered:")
        analyzer = WordFrequencyAnalyzer(use_stopwords=True)
        counter = analyzer.analyze_file(temp_path)
        print(analyzer.format_results(counter, top_n=10))
        
        # Cleanup
        Path(temp_path).unlink()
        
        print("\n" + "="*50)
        print("\nTo analyze your own file, run:")
        print(f"  python {sys.argv[0]} yourfile.txt -t 20 -s")
    else:
        main()