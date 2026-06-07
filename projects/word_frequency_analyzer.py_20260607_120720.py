"""
Date: 2026-06-07
Made a CLI tool to analyze word frequencies in text files because I got curious about word distributions in my markdown notes.
"""

#!/usr/bin/env python3
"""
Word Frequency Analyzer
Counts word occurrences in text files and displays them ranked by frequency.
Useful for analyzing writing patterns, finding overused words, or just exploring text data.
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


def load_text_from_file(filepath):
    """
    Load text content from a file, handling encoding gracefully.
    
    Args:
        filepath: Path object or string path to the file
        
    Returns:
        String containing file contents
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        PermissionError: If we can't read the file
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Fallback to latin-1 if utf-8 fails — covers most edge cases
        with open(filepath, 'r', encoding='latin-1') as f:
            return f.read()


def tokenize_text(text, case_sensitive=False):
    """
    Break text into words, stripping punctuation and handling case.
    
    I'm using a simple regex that splits on non-alphanumeric characters.
    This means contractions like "don't" become "don" and "t", which is
    fine for basic frequency analysis but could be improved with NLTK.
    
    Args:
        text: String to tokenize
        case_sensitive: If False, normalize all words to lowercase
        
    Returns:
        List of word tokens
    """
    # Split on anything that's not a letter, number, or apostrophe
    words = re.findall(r"[a-zA-Z0-9']+", text)
    
    if not case_sensitive:
        words = [w.lower() for w in words]
    
    return words


def count_word_frequencies(words):
    """
    Count how many times each word appears.
    
    Args:
        words: List of word strings
        
    Returns:
        Counter object mapping words to their frequencies
    """
    return Counter(words)


def filter_by_min_count(counter, min_count):
    """
    Remove words that appear fewer than min_count times.
    
    This is useful for filtering out rare words when analyzing large texts.
    
    Args:
        counter: Counter object of word frequencies
        min_count: Minimum number of occurrences to keep a word
        
    Returns:
        New Counter with filtered words
    """
    return Counter({word: count for word, count in counter.items() if count >= min_count})


def display_results(counter, top_n=None):
    """
    Print word frequencies in a nice tabular format.
    
    Args:
        counter: Counter object of word frequencies
        top_n: If set, only show the top N most common words
    """
    if not counter:
        print("No words found matching criteria.")
        return
    
    # Get sorted list of (word, count) tuples
    items = counter.most_common(top_n) if top_n else counter.most_common()
    
    # Calculate column widths for pretty alignment
    max_word_len = max(len(word) for word, _ in items)
    max_count_len = max(len(str(count)) for _, count in items)
    
    # Print header
    print(f"\n{'Word':<{max_word_len}}  {'Count':>{max_count_len}}  Percentage")
    print("-" * (max_word_len + max_count_len + 15))
    
    total = sum(counter.values())
    
    # Print each word with its stats
    for word, count in items:
        percentage = (count / total) * 100
        print(f"{word:<{max_word_len}}  {count:>{max_count_len}}  {percentage:>6.2f}%")
    
    print(f"\nTotal unique words: {len(counter)}")
    print(f"Total word count: {total}")


def main():
    """
    Parse arguments and orchestrate the word frequency analysis.
    """
    parser = argparse.ArgumentParser(
        description="Analyze word frequencies in text files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example: %(prog)s my_essay.txt --top 20 --min-count 3"
    )
    
    parser.add_argument(
        'filepath',
        type=Path,
        help='Path to the text file to analyze'
    )
    
    parser.add_argument(
        '--top', '-t',
        type=int,
        metavar='N',
        help='Show only the top N most frequent words'
    )
    
    parser.add_argument(
        '--min-count', '-m',
        type=int,
        default=1,
        metavar='MIN',
        help='Only show words that appear at least MIN times (default: 1)'
    )
    
    parser.add_argument(
        '--case-sensitive', '-c',
        action='store_true',
        help='Treat uppercase and lowercase as different words'
    )
    
    args = parser.parse_args()
    
    # Validate the file exists before doing anything else
    if not args.filepath.exists():
        print(f"Error: File '{args.filepath}' not found.", file=sys.stderr)
        sys.exit(1)
    
    if not args.filepath.is_file():
        print(f"Error: '{args.filepath}' is not a file.", file=sys.stderr)
        sys.exit(1)
    
    # Do the actual work
    print(f"Analyzing: {args.filepath}")
    text = load_text_from_file(args.filepath)
    words = tokenize_text(text, case_sensitive=args.case_sensitive)
    frequencies = count_word_frequencies(words)
    
    # Apply minimum count filter if requested
    if args.min_count > 1:
        frequencies = filter_by_min_count(frequencies, args.min_count)
    
    display_results(frequencies, top_n=args.top)


if __name__ == "__main__":
    # Demo mode: create a sample file and analyze it
    if len(sys.argv) == 1:
        print("=== DEMO MODE ===")
        print("Creating a sample text file for demonstration...\n")
        
        demo_file = Path("demo_text.txt")
        demo_content = """
        The quick brown fox jumps over the lazy dog.
        The dog was not amused by the fox.
        The fox thought the dog was too lazy to care.
        Meanwhile, the brown fox continued jumping.
        """
        
        demo_file.write_text(demo_content)
        print(f"Created: {demo_file}")
        
        # Simulate running with arguments
        sys.argv = ['word_frequency_analyzer.py', str(demo_file), '--top', '10']
        main()
        
        # Clean up
        demo_file.unlink()
        print(f"\nCleaned up: {demo_file}")
    else:
        main()