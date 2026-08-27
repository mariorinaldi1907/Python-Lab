"""
Date: 2026-08-27
Made a command-line tool to analyze text files and show word frequencies with optional stopword filtering — useful for quick content analysis.
"""

#!/usr/bin/env python3
"""
Word Frequency Analyzer
Analyzes text files and outputs word frequency statistics.
Supports stopword filtering, case sensitivity options, and multiple output formats.
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path


# Common English stopwords - didn't want to bring in NLTK for such a simple tool
DEFAULT_STOPWORDS = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'is'
}


def read_file(filepath):
    """
    Read and return the contents of a text file.
    
    Args:
        filepath: Path object or string pointing to the file
        
    Returns:
        String containing file contents
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        UnicodeDecodeError: If the file isn't valid text
    """
    path = Path(filepath)
    return path.read_text(encoding='utf-8')


def tokenize_text(text, case_sensitive=False):
    """
    Break text into individual words, stripping punctuation.
    
    Args:
        text: String to tokenize
        case_sensitive: Whether to preserve case (default: False)
        
    Returns:
        List of word tokens
    """
    # Using a regex to grab word characters only - ignores punctuation naturally
    words = re.findall(r'\b\w+\b', text)
    
    if not case_sensitive:
        words = [w.lower() for w in words]
    
    return words


def analyze_frequency(words, stopwords=None, top_n=None):
    """
    Count word frequencies and return sorted results.
    
    Args:
        words: List of word tokens
        stopwords: Set of words to exclude from analysis (optional)
        top_n: Return only top N most common words (optional)
        
    Returns:
        List of (word, count) tuples sorted by frequency descending
    """
    if stopwords:
        # Filter out stopwords before counting
        words = [w for w in words if w not in stopwords]
    
    counter = Counter(words)
    
    if top_n:
        return counter.most_common(top_n)
    
    # Return all words sorted by frequency, then alphabetically for ties
    return sorted(counter.items(), key=lambda x: (-x[1], x[0]))


def format_table(word_freq, total_words):
    """
    Format frequency results as a nice ASCII table.
    
    Args:
        word_freq: List of (word, count) tuples
        total_words: Total number of words analyzed
        
    Returns:
        Formatted string table
    """
    lines = []
    lines.append("=" * 50)
    lines.append(f"{'WORD':<20} {'COUNT':>10} {'PERCENT':>10}")
    lines.append("-" * 50)
    
    for word, count in word_freq:
        percent = (count / total_words * 100) if total_words > 0 else 0
        lines.append(f"{word:<20} {count:>10} {percent:>9.2f}%")
    
    lines.append("=" * 50)
    lines.append(f"Total words analyzed: {total_words}")
    
    return "\n".join(lines)


def main():
    """
    Main entry point - parse arguments and run the analysis.
    """
    parser = argparse.ArgumentParser(
        description='Analyze word frequency in text files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Example: %(prog)s document.txt -n 20 --no-stopwords'
    )
    
    parser.add_argument('file', help='Text file to analyze')
    parser.add_argument('-n', '--top', type=int, metavar='N',
                       help='Show only top N most frequent words')
    parser.add_argument('--case-sensitive', action='store_true',
                       help='Treat words with different cases as distinct')
    parser.add_argument('--no-stopwords', action='store_true',
                       help='Exclude common stopwords from analysis')
    parser.add_argument('--json', action='store_true',
                       help='Output results as JSON instead of table')
    
    args = parser.parse_args()
    
    try:
        # Read and tokenize the file
        text = read_file(args.file)
        words = tokenize_text(text, case_sensitive=args.case_sensitive)
        
        # Decide whether to use stopwords
        stopwords = DEFAULT_STOPWORDS if args.no_stopwords else None
        
        # Analyze frequency
        word_freq = analyze_frequency(words, stopwords=stopwords, top_n=args.top)
        
        # Output results
        if args.json:
            output = {
                'total_words': len(words),
                'unique_words': len(word_freq),
                'frequencies': [{'word': w, 'count': c} for w, c in word_freq]
            }
            print(json.dumps(output, indent=2))
        else:
            print(format_table(word_freq, len(words)))
    
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found", file=sys.stderr)
        sys.exit(1)
    except UnicodeDecodeError:
        print(f"Error: File '{args.file}' is not a valid text file", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # Quick demo with some sample text
    print("=== DEMO MODE ===\n")
    
    sample_text = """
    Python is an amazing programming language. Python makes programming fun.
    The Python community is welcoming and the ecosystem is vast.
    Learning Python opens many doors in software development.
    """
    
    print("Sample text:")
    print(sample_text)
    print("\n" + "="*50 + "\n")
    
    # Tokenize and analyze without stopwords
    words = tokenize_text(sample_text, case_sensitive=False)
    freq = analyze_frequency(words, stopwords=DEFAULT_STOPWORDS, top_n=10)
    
    print("Top 10 words (excluding stopwords):")
    print(format_table(freq, len(words)))
    
    print("\n\nRun with a real file: python word_frequency_analyzer.py <filename>")
    print("See --help for more options")