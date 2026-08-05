"""
Date: 2026-08-05
Created a command-line word frequency analyzer that processes text files and outputs stats in different formats — helpful for quick content analysis.
"""

#!/usr/bin/env python3
"""
Word Frequency Analyzer - CLI tool for analyzing word frequencies in text files.
Supports multiple output formats and common word filtering.
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


# Common English stopwords - kept minimal to avoid bloat
STOPWORDS = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'is'
}


def clean_word(word):
    """
    Remove punctuation and convert to lowercase.
    Returns None if the result is empty or non-alphabetic.
    """
    cleaned = re.sub(r'[^\w\s]', '', word.lower())
    # Only keep words with at least one letter
    if cleaned and any(c.isalpha() for c in cleaned):
        return cleaned
    return None


def extract_words(text, min_length=1, exclude_stopwords=False):
    """
    Extract and clean words from text.
    
    Args:
        text: Input text string
        min_length: Minimum word length to include
        exclude_stopwords: Whether to filter out common words
    
    Returns:
        List of cleaned words
    """
    words = []
    for word in text.split():
        cleaned = clean_word(word)
        if cleaned and len(cleaned) >= min_length:
            if exclude_stopwords and cleaned in STOPWORDS:
                continue
            words.append(cleaned)
    return words


def analyze_file(filepath, min_length=1, exclude_stopwords=False):
    """
    Read a file and return word frequency counter.
    
    Args:
        filepath: Path to the text file
        min_length: Minimum word length
        exclude_stopwords: Filter common words
    
    Returns:
        Counter object with word frequencies
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    words = extract_words(text, min_length, exclude_stopwords)
    return Counter(words)


def format_output(counter, top_n=None, sort_by='frequency'):
    """
    Format the word frequency data for display.
    
    Args:
        counter: Counter object with word frequencies
        top_n: Number of top words to show (None = all)
        sort_by: 'frequency' or 'alphabetical'
    
    Returns:
        Formatted string output
    """
    if not counter:
        return "No words found."
    
    # Sort based on preference
    if sort_by == 'alphabetical':
        items = sorted(counter.items(), key=lambda x: x[0])
    else:
        items = counter.most_common(top_n)
    
    if top_n and sort_by != 'alphabetical':
        items = items[:top_n]
    
    # Calculate padding for alignment
    max_word_len = max(len(word) for word, _ in items)
    max_count_len = len(str(max(count for _, count in items)))
    
    output = []
    output.append(f"Total unique words: {len(counter)}")
    output.append(f"Total word count: {sum(counter.values())}")
    output.append("-" * (max_word_len + max_count_len + 5))
    
    for word, count in items:
        output.append(f"{word:<{max_word_len}} : {count:>{max_count_len}}")
    
    return "\n".join(output)


def main():
    """
    Main CLI entry point - parses arguments and runs analysis.
    """
    parser = argparse.ArgumentParser(
        description="Analyze word frequencies in text files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example: python word_frequency_analyzer.py article.txt -t 20 -s"
    )
    
    parser.add_argument(
        'file',
        type=str,
        help='Path to the text file to analyze'
    )
    parser.add_argument(
        '-t', '--top',
        type=int,
        metavar='N',
        help='Show only top N words (default: show all)'
    )
    parser.add_argument(
        '-m', '--min-length',
        type=int,
        default=1,
        metavar='N',
        help='Minimum word length (default: 1)'
    )
    parser.add_argument(
        '-s', '--no-stopwords',
        action='store_true',
        help='Exclude common English stopwords'
    )
    parser.add_argument(
        '-a', '--alphabetical',
        action='store_true',
        help='Sort alphabetically instead of by frequency'
    )
    
    args = parser.parse_args()
    
    # Run the analysis
    counter = analyze_file(args.file, args.min_length, args.no_stopwords)
    
    sort_mode = 'alphabetical' if args.alphabetical else 'frequency'
    output = format_output(counter, args.top, sort_mode)
    
    print(output)


if __name__ == "__main__":
    # Demo mode - create a sample file and analyze it
    if len(sys.argv) == 1:
        print("=== DEMO MODE ===\n")
        
        # Create a sample text
        sample_text = """
        Python is an amazing programming language. Python makes it easy to write
        clean and readable code. Many developers love Python because Python is 
        versatile and powerful. The Python community is welcoming and helpful.
        Python, Python, Python - it's everywhere in modern software development!
        """
        
        # Write to temp file
        demo_file = Path("_demo_sample.txt")
        demo_file.write_text(sample_text)
        
        print(f"Created sample file: {demo_file}")
        print(f"Analyzing with stopword filtering and showing top 10 words...\n")
        
        # Analyze it
        counter = analyze_file(demo_file, min_length=2, exclude_stopwords=True)
        output = format_output(counter, top_n=10, sort_by='frequency')
        
        print(output)
        
        # Cleanup
        demo_file.unlink()
        print(f"\nCleaned up demo file. Run with --help to see usage options.")
    else:
        main()