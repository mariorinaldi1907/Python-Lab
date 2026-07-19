"""
Date: 2026-07-19
Made a CLI tool that analyzes text files and shows word frequencies with optional filtering and ASCII histogram visualization.
"""

#!/usr/bin/env python3
"""
Word Frequency Analyzer
Analyzes text files and displays word frequency statistics with visual histograms.
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


# Basic English stopwords — I could've loaded from a file but keeping it simple
STOPWORDS = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'is'
}


def load_text(filepath):
    """
    Load text from a file, handling common encoding issues.
    
    Args:
        filepath: Path to the text file
        
    Returns:
        String containing the file contents
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Fallback to latin-1 if UTF-8 fails — sometimes happens with old files
        with open(filepath, 'r', encoding='latin-1') as f:
            return f.read()


def tokenize(text, min_length=1):
    """
    Extract words from text, converting to lowercase and filtering by length.
    
    Args:
        text: Input text string
        min_length: Minimum word length to include
        
    Returns:
        List of tokenized words
    """
    # Keep only alphabetic characters and apostrophes (for contractions)
    words = re.findall(r"[a-z']+", text.lower())
    return [w for w in words if len(w) >= min_length]


def filter_stopwords(words, remove_stopwords=True):
    """
    Optionally remove common stopwords from the word list.
    
    Args:
        words: List of words
        remove_stopwords: Whether to filter stopwords
        
    Returns:
        Filtered list of words
    """
    if not remove_stopwords:
        return words
    return [w for w in words if w not in STOPWORDS]


def create_histogram(word, count, max_count, bar_width=50):
    """
    Create an ASCII histogram bar for a word frequency.
    
    Args:
        word: The word to display
        count: Frequency count
        max_count: Maximum count (for scaling)
        bar_width: Maximum width of the bar in characters
        
    Returns:
        Formatted string with word and visual bar
    """
    # Scale the bar based on the maximum count
    bar_length = int((count / max_count) * bar_width)
    bar = '█' * bar_length
    return f"{word:20} {count:6} {bar}"


def analyze_frequency(filepath, top_n=20, min_length=3, remove_stopwords=True, show_histogram=True):
    """
    Analyze word frequencies in a text file and display results.
    
    Args:
        filepath: Path to text file
        top_n: Number of top words to display
        min_length: Minimum word length
        remove_stopwords: Whether to filter common stopwords
        show_histogram: Whether to show visual histogram
    """
    # Load and process the text
    text = load_text(filepath)
    words = tokenize(text, min_length=min_length)
    words = filter_stopwords(words, remove_stopwords=remove_stopwords)
    
    if not words:
        print("No words found matching the criteria.")
        return
    
    # Count frequencies
    counter = Counter(words)
    most_common = counter.most_common(top_n)
    
    # Display results
    print(f"\nAnalyzing: {filepath}")
    print(f"Total words (after filtering): {len(words)}")
    print(f"Unique words: {len(counter)}")
    print(f"\nTop {len(most_common)} words:\n")
    
    if show_histogram and most_common:
        max_count = most_common[0][1]
        print(f"{'Word':<20} {'Count':>6}   {'Frequency':>10}")
        print("-" * 80)
        for word, count in most_common:
            print(create_histogram(word, count, max_count))
    else:
        for rank, (word, count) in enumerate(most_common, 1):
            print(f"{rank:3}. {word:20} {count:6}")


def main():
    """Parse arguments and run the word frequency analyzer."""
    parser = argparse.ArgumentParser(
        description="Analyze word frequencies in text files with visual output",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'file',
        type=Path,
        help='Text file to analyze'
    )
    parser.add_argument(
        '-n', '--top',
        type=int,
        default=20,
        help='Number of top words to display (default: 20)'
    )
    parser.add_argument(
        '-m', '--min-length',
        type=int,
        default=3,
        help='Minimum word length to include (default: 3)'
    )
    parser.add_argument(
        '--keep-stopwords',
        action='store_true',
        help='Include common stopwords (the, and, etc.)'
    )
    parser.add_argument(
        '--no-histogram',
        action='store_true',
        help='Disable visual histogram output'
    )
    
    args = parser.parse_args()
    
    if not args.file.exists():
        print(f"Error: File '{args.file}' not found.", file=sys.stderr)
        sys.exit(1)
    
    analyze_frequency(
        args.file,
        top_n=args.top,
        min_length=args.min_length,
        remove_stopwords=not args.keep_stopwords,
        show_histogram=not args.no_histogram
    )


if __name__ == "__main__":
    # Demo mode — create a sample file and analyze it
    if len(sys.argv) == 1:
        print("=== DEMO MODE ===\n")
        
        # Create a sample text file with some content
        demo_file = Path("demo_sample.txt")
        demo_text = """
        Python is an amazing programming language. Python makes development easy.
        The simplicity of Python is why many developers love Python.
        Data science and machine learning often use Python because Python has
        great libraries. Python's readability and Python's community support
        make Python the perfect choice for beginners and experts alike.
        Whether you're building web applications, analyzing data, or creating
        automation scripts, Python provides the tools you need. Python continues
        to grow in popularity year after year.
        """
        
        demo_file.write_text(demo_text)
        print(f"Created sample file: {demo_file}\n")
        
        # Analyze it
        analyze_frequency(demo_file, top_n=10, min_length=3, remove_stopwords=True)
        
        print("\n" + "="*80)
        print("Run with --help to see all options")
        print(f"Example: python {sys.argv[0]} yourfile.txt -n 15 --min-length 4")
    else:
        main()