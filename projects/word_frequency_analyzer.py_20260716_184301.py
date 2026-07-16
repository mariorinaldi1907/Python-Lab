"""
Date: 2026-07-16
Created a command-line tool to analyze word frequencies in text files with configurable stopword filtering and visual percentage output.
"""

#!/usr/bin/env python3
"""
Word Frequency Analyzer
Counts word occurrences in text files and displays results with visual bars.
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


# Common English stopwords to filter out noise
DEFAULT_STOPWORDS = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
    'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me',
    'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take',
    'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other',
    'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also',
    'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way',
    'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us'
}


def read_text_file(filepath):
    """
    Read and return the contents of a text file.
    Tries multiple encodings because you never know what you'll get.
    """
    encodings = ['utf-8', 'latin-1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    
    # If all encodings fail, just give up
    print(f"Error: Could not decode {filepath} with any common encoding", file=sys.stderr)
    sys.exit(1)


def extract_words(text, case_sensitive=False):
    """
    Extract words from text using regex.
    By default converts to lowercase for case-insensitive counting.
    """
    # Match sequences of word characters (letters, digits, underscores)
    words = re.findall(r'\b\w+\b', text)
    
    if not case_sensitive:
        words = [word.lower() for word in words]
    
    return words


def filter_stopwords(words, use_stopwords, custom_stopwords=None):
    """
    Remove common stopwords from the word list.
    Optionally accepts custom stopwords to add to the default set.
    """
    if not use_stopwords:
        return words
    
    stopwords = DEFAULT_STOPWORDS.copy()
    
    if custom_stopwords:
        stopwords.update(word.lower() for word in custom_stopwords)
    
    return [word for word in words if word.lower() not in stopwords]


def calculate_frequencies(words):
    """
    Count word frequencies and return as a Counter object.
    Counter is basically a dict but with convenient most_common() method.
    """
    return Counter(words)


def format_bar(percentage, max_width=40):
    """
    Create a visual bar representation of a percentage.
    Makes the output way more readable than just numbers.
    """
    filled = int(percentage * max_width / 100)
    bar = '█' * filled + '░' * (max_width - filled)
    return bar


def display_results(counter, top_n, show_percentage=True):
    """
    Display word frequency results in a nice formatted table.
    Shows count, percentage, and a visual bar for each word.
    """
    if not counter:
        print("No words found.")
        return
    
    total_words = sum(counter.values())
    most_common = counter.most_common(top_n)
    
    # Calculate column widths for nice alignment
    max_word_len = max(len(word) for word, _ in most_common)
    max_count_len = len(str(most_common[0][1]))
    
    print(f"\nTotal words analyzed: {total_words}")
    print(f"Unique words: {len(counter)}")
    print(f"\nTop {min(top_n, len(counter))} most frequent words:\n")
    
    for word, count in most_common:
        percentage = (count / total_words) * 100
        bar = format_bar(percentage)
        
        if show_percentage:
            print(f"{word:<{max_word_len}}  {count:>{max_count_len}}  "
                  f"{percentage:5.2f}%  {bar}")
        else:
            print(f"{word:<{max_word_len}}  {count:>{max_count_len}}  {bar}")


def main():
    """
    Main entry point. Sets up argparse and orchestrates the analysis.
    """
    parser = argparse.ArgumentParser(
        description='Analyze word frequencies in text files',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('file', type=Path, help='Text file to analyze')
    parser.add_argument('-n', '--top', type=int, default=20,
                        help='Number of top words to display (default: 20)')
    parser.add_argument('-s', '--no-stopwords', action='store_true',
                        help='Disable stopword filtering')
    parser.add_argument('-c', '--case-sensitive', action='store_true',
                        help='Enable case-sensitive counting')
    parser.add_argument('--min-length', type=int, default=1,
                        help='Minimum word length to include (default: 1)')
    
    args = parser.parse_args()
    
    # Validate file exists
    if not args.file.exists():
        print(f"Error: File '{args.file}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Read and process the file
    text = read_text_file(args.file)
    words = extract_words(text, case_sensitive=args.case_sensitive)
    
    # Filter by minimum length (helps remove noise like 'a', 'i', etc.)
    words = [w for w in words if len(w) >= args.min_length]
    
    # Apply stopword filtering
    use_stopwords = not args.no_stopwords
    words = filter_stopwords(words, use_stopwords)
    
    # Calculate and display frequencies
    frequencies = calculate_frequencies(words)
    display_results(frequencies, args.top)


if __name__ == "__main__":
    # Demo mode: create a sample file and analyze it
    if len(sys.argv) == 1:
        print("=== DEMO MODE ===\n")
        
        # Create a sample text file for demonstration
        demo_file = Path("demo_sample.txt")
        sample_text = """
        Python is an amazing programming language. Python makes programming fun.
        Many developers love Python because Python is simple and powerful.
        Learning Python opens many doors in software development.
        Python, Python, Python - it's everywhere in modern development!
        Data science uses Python extensively for analysis and visualization.
        """
        
        demo_file.write_text(sample_text)
        print(f"Created demo file: {demo_file}")
        
        # Override sys.argv to run the demo
        sys.argv = ['word_frequency_analyzer.py', str(demo_file), '-n', '10']
        
    main()