"""
Date: 2026-07-11
Created a command-line tool that analyzes text files for word frequency distribution, with configurable filtering and JSON/CSV export options because I got tired of doing this manually in data cleanup tasks.
"""

#!/usr/bin/env python3
"""
Word Frequency Analyzer CLI
Analyzes text files and outputs word frequency statistics with various filtering options.
"""

import argparse
import json
import csv
import sys
from collections import Counter
from pathlib import Path
import re


# Common English stop words - words I almost always want to filter out
STOP_WORDS = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'is',
    'was', 'are', 'been', 'has', 'had', 'were', 'can', 'said', 'so', 'if'
}


def load_and_tokenize(filepath, case_sensitive=False):
    """
    Load text from file and split into words.
    
    Uses regex to split on non-alphanumeric boundaries so contractions
    like "don't" stay intact but punctuation gets stripped.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    except UnicodeDecodeError:
        # Fallback for files with weird encoding
        with open(filepath, 'r', encoding='latin-1') as f:
            text = f.read()
    
    # Split on word boundaries, keep apostrophes for contractions
    words = re.findall(r"\b[\w']+\b", text)
    
    if not case_sensitive:
        words = [w.lower() for w in words]
    
    return words


def filter_words(words, min_length=1, exclude_stop_words=False, exclude_numbers=False):
    """
    Apply various filters to the word list based on user preferences.
    
    This is separate from tokenization because filtering criteria
    might change independently of how we split the text.
    """
    filtered = words
    
    if min_length > 1:
        filtered = [w for w in filtered if len(w) >= min_length]
    
    if exclude_stop_words:
        filtered = [w for w in filtered if w.lower() not in STOP_WORDS]
    
    if exclude_numbers:
        # Remove words that are purely numeric
        filtered = [w for w in filtered if not w.replace('.', '').replace(',', '').isdigit()]
    
    return filtered


def analyze_frequency(words, top_n=None):
    """
    Count word occurrences and optionally limit to top N results.
    
    Returns a list of (word, count) tuples sorted by frequency (descending).
    """
    counter = Counter(words)
    
    if top_n:
        return counter.most_common(top_n)
    
    return counter.most_common()


def output_results(results, output_format='text', output_file=None):
    """
    Format and output the frequency analysis results.
    
    Supports text (human-readable), JSON, and CSV formats.
    The text format is what I use most when just exploring data.
    """
    if output_format == 'json':
        data = [{'word': word, 'count': count} for word, count in results]
        output = json.dumps(data, indent=2)
    
    elif output_format == 'csv':
        # Using StringIO-like approach for in-memory CSV
        import io
        output_buffer = io.StringIO()
        writer = csv.writer(output_buffer)
        writer.writerow(['word', 'count'])
        writer.writerows(results)
        output = output_buffer.getvalue()
    
    else:  # text format
        lines = []
        max_word_len = max(len(word) for word, _ in results) if results else 10
        
        for word, count in results:
            # Visual bar chart using unicode blocks - makes patterns obvious at a glance
            bar = '█' * min(count, 50)  # Cap at 50 chars for readability
            lines.append(f"{word:<{max_word_len}} {count:>6}  {bar}")
        
        output = '\n'.join(lines)
    
    # Output to file or stdout
    if output_file:
        Path(output_file).write_text(output, encoding='utf-8')
        print(f"Results written to {output_file}")
    else:
        print(output)


def main():
    """Main CLI entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description='Analyze word frequency in text files',
        epilog='Example: %(prog)s document.txt -t 20 --exclude-stop-words'
    )
    
    parser.add_argument('file', help='Text file to analyze')
    parser.add_argument('-t', '--top', type=int, metavar='N',
                        help='Show only top N most frequent words')
    parser.add_argument('-m', '--min-length', type=int, default=1, metavar='N',
                        help='Minimum word length (default: 1)')
    parser.add_argument('-s', '--exclude-stop-words', action='store_true',
                        help='Filter out common English stop words')
    parser.add_argument('-n', '--exclude-numbers', action='store_true',
                        help='Exclude numeric values')
    parser.add_argument('-c', '--case-sensitive', action='store_true',
                        help='Treat words as case-sensitive')
    parser.add_argument('-f', '--format', choices=['text', 'json', 'csv'],
                        default='text', help='Output format (default: text)')
    parser.add_argument('-o', '--output', metavar='FILE',
                        help='Write output to file instead of stdout')
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not Path(args.file).exists():
        print(f"Error: File '{args.file}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Process the file through our pipeline
    words = load_and_tokenize(args.file, case_sensitive=args.case_sensitive)
    filtered_words = filter_words(
        words,
        min_length=args.min_length,
        exclude_stop_words=args.exclude_stop_words,
        exclude_numbers=args.exclude_numbers
    )
    
    if not filtered_words:
        print("No words found after applying filters", file=sys.stderr)
        sys.exit(1)
    
    results = analyze_frequency(filtered_words, top_n=args.top)
    output_results(results, output_format=args.format, output_file=args.output)


if __name__ == "__main__":
    # Demo mode when run directly without arguments
    if len(sys.argv) == 1:
        print("=== Word Frequency Analyzer Demo ===\n")
        
        # Create a sample text file for demonstration
        sample_text = """
        The quick brown fox jumps over the lazy dog. The dog was not amused.
        The fox, being quite clever, jumped over the fence and ran away.
        Dogs and foxes have been rivals for centuries, but this dog was particularly lazy.
        """
        
        demo_file = Path('_demo_sample.txt')
        demo_file.write_text(sample_text)
        
        print(f"Created demo file: {demo_file}\n")
        print("Analyzing word frequency (excluding stop words, min length 3)...\n")
        
        # Simulate CLI args for demo
        sys.argv = [
            'word_frequency_analyzer.py',
            str(demo_file),
            '--exclude-stop-words',
            '--min-length', '3',
            '--top', '10'
        ]
        
        main()
        
        # Cleanup
        demo_file.unlink()
        print(f"\nDemo complete! Removed {demo_file}")
        print("\nTry running with your own files:")
        print("  python word_frequency_analyzer.py yourfile.txt -t 20 -s")
    else:
        main()