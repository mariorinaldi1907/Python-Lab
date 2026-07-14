"""
Date: 2026-07-14
Created a command-line tool to analyze text files and show word frequency distributions — useful for quick content analysis when I'm curious about what terms dominate a document.
"""

#!/usr/bin/env python3
"""
Word Frequency Analyzer
Counts word occurrences in text files and displays results in various formats.
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


def load_stopwords(stopwords_file=None):
    """
    Load stopwords from a file or use a default minimal set.
    
    Args:
        stopwords_file: Optional path to a file with stopwords (one per line)
    
    Returns:
        set: A set of lowercase stopwords
    """
    # Basic stopwords I find useful for filtering noise
    default_stopwords = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'could', 'should', 'may', 'might', 'can', 'that', 'this',
        'it', 'its', 'i', 'you', 'he', 'she', 'we', 'they', 'my', 'your'
    }
    
    if stopwords_file:
        try:
            with open(stopwords_file, 'r', encoding='utf-8') as f:
                # Read stopwords, strip whitespace, convert to lowercase
                return {line.strip().lower() for line in f if line.strip()}
        except FileNotFoundError:
            print(f"Warning: stopwords file '{stopwords_file}' not found, using defaults", 
                  file=sys.stderr)
            return default_stopwords
    
    return default_stopwords


def extract_words(text, case_sensitive=False):
    """
    Extract words from text using regex.
    
    Args:
        text: Input text string
        case_sensitive: Whether to preserve case (default: False)
    
    Returns:
        list: List of words extracted from text
    """
    # Match sequences of word characters (letters, digits, underscores)
    # This approach handles contractions reasonably well
    words = re.findall(r"\b\w+\b", text)
    
    if not case_sensitive:
        words = [w.lower() for w in words]
    
    return words


def analyze_file(filepath, stopwords=None, case_sensitive=False, min_length=1):
    """
    Analyze word frequency in a given file.
    
    Args:
        filepath: Path to the text file
        stopwords: Set of words to exclude from counting
        case_sensitive: Whether to treat words case-sensitively
        min_length: Minimum word length to include
    
    Returns:
        Counter: Word frequency counter object
    """
    stopwords = stopwords or set()
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    except UnicodeDecodeError:
        # Fallback for files with different encoding
        with open(filepath, 'r', encoding='latin-1') as f:
            text = f.read()
    
    words = extract_words(text, case_sensitive)
    
    # Filter out stopwords and short words
    # I do this in one pass to avoid iterating multiple times
    filtered_words = [
        w for w in words 
        if len(w) >= min_length and (w.lower() not in stopwords)
    ]
    
    return Counter(filtered_words)


def display_results(counter, top_n=20, show_percentages=False):
    """
    Display word frequency results in a formatted table.
    
    Args:
        counter: Counter object with word frequencies
        top_n: Number of top words to display
        show_percentages: Whether to show percentage alongside count
    """
    if not counter:
        print("No words found matching criteria.")
        return
    
    total_words = sum(counter.values())
    print(f"\nTotal words analyzed: {total_words}")
    print(f"Unique words: {len(counter)}")
    print(f"\nTop {top_n} most frequent words:")
    print("-" * 50)
    
    for rank, (word, count) in enumerate(counter.most_common(top_n), 1):
        if show_percentages:
            percentage = (count / total_words) * 100
            print(f"{rank:3d}. {word:20s} {count:6d} ({percentage:5.2f}%)")
        else:
            print(f"{rank:3d}. {word:20s} {count:6d}")


def main():
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        description="Analyze word frequency in text files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.txt
  %(prog)s essay.txt --top 50 --min-length 4
  %(prog)s article.txt --no-stopwords --case-sensitive
  %(prog)s readme.md --stopwords custom_stopwords.txt --percentages
        """
    )
    
    parser.add_argument('file', type=Path, help='Text file to analyze')
    parser.add_argument('--top', type=int, default=20, metavar='N',
                        help='Show top N words (default: 20)')
    parser.add_argument('--min-length', type=int, default=1, metavar='LEN',
                        help='Minimum word length to include (default: 1)')
    parser.add_argument('--case-sensitive', action='store_true',
                        help='Treat words case-sensitively')
    parser.add_argument('--no-stopwords', action='store_true',
                        help='Disable stopword filtering')
    parser.add_argument('--stopwords', type=Path, metavar='FILE',
                        help='Custom stopwords file (one word per line)')
    parser.add_argument('--percentages', action='store_true',
                        help='Show percentages alongside counts')
    
    args = parser.parse_args()
    
    # Validate file exists
    if not args.file.exists():
        print(f"Error: File '{args.file}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Load stopwords unless disabled
    stopwords = None if args.no_stopwords else load_stopwords(args.stopwords)
    
    # Analyze the file
    word_counts = analyze_file(
        args.file,
        stopwords=stopwords,
        case_sensitive=args.case_sensitive,
        min_length=args.min_length
    )
    
    # Display results
    display_results(word_counts, top_n=args.top, show_percentages=args.percentages)


if __name__ == "__main__":
    # Demo mode: create a sample file and analyze it
    if len(sys.argv) == 1:
        print("=== DEMO MODE ===")
        print("Creating sample file for demonstration...\n")
        
        demo_text = """
        Python is an amazing programming language. Python makes development faster.
        Many developers choose Python for machine learning and data science projects.
        The Python community is large and supportive. Python's syntax is clean and readable.
        Learning Python opens many career opportunities in software development.
        """
        
        demo_file = Path("demo_sample.txt")
        demo_file.write_text(demo_text)
        
        print(f"Analyzing '{demo_file}'...")
        
        stopwords = load_stopwords()
        word_counts = analyze_file(demo_file, stopwords=stopwords, min_length=3)
        display_results(word_counts, top_n=10, show_percentages=True)
        
        print("\n" + "="*50)
        print("Demo complete! Try it with your own files:")
        print(f"  python {sys.argv[0]} your_file.txt --top 30")
        
        demo_file.unlink()  # Clean up demo file
    else:
        main()