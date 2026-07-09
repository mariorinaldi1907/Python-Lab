"""
Date: 2026-07-09
Created a command-line tool to analyze word frequencies in text files with stopword filtering and multiple output formats, because I got tired of manually counting words in my writing.
"""

#!/usr/bin/env python3
"""
Word Frequency Analyzer
Analyzes word frequency in text files with stopword filtering and customizable output.
"""

import argparse
import sys
from collections import Counter
from pathlib import Path
import re


# Basic stopwords list - common English words that don't add much meaning
STOPWORDS = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
    'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me',
    'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take',
    'into', 'your', 'some', 'could', 'them', 'than', 'then', 'now', 'only',
    'come', 'its', 'over', 'also', 'back', 'after', 'use', 'how', 'our', 'way'
}


def read_file(filepath):
    """
    Read and return the contents of a file.
    
    Args:
        filepath: Path to the file to read
        
    Returns:
        String containing file contents
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)


def tokenize_text(text, min_length=1):
    """
    Convert text into a list of lowercase words.
    
    Strips punctuation and filters out words shorter than min_length.
    This uses a simple regex approach that works well for English text.
    
    Args:
        text: Input text string
        min_length: Minimum word length to include
        
    Returns:
        List of cleaned, lowercase words
    """
    # Extract words (alphanumeric sequences), convert to lowercase
    words = re.findall(r'\b[a-z]+\b', text.lower())
    
    # Filter by minimum length
    return [w for w in words if len(w) >= min_length]


def analyze_frequency(words, exclude_stopwords=False, top_n=None):
    """
    Analyze word frequency and return sorted results.
    
    Args:
        words: List of words to analyze
        exclude_stopwords: If True, filter out common stopwords
        top_n: If specified, return only the top N most common words
        
    Returns:
        List of (word, count) tuples sorted by frequency (descending)
    """
    # Filter stopwords if requested - I do this before counting for efficiency
    if exclude_stopwords:
        words = [w for w in words if w not in STOPWORDS]
    
    # Count occurrences and sort
    counter = Counter(words)
    
    # Get most common (all or top N)
    if top_n:
        return counter.most_common(top_n)
    else:
        return counter.most_common()


def format_output(freq_data, format_type='table', show_percentage=False, total_words=None):
    """
    Format frequency data for display.
    
    Args:
        freq_data: List of (word, count) tuples
        format_type: 'table', 'csv', or 'simple'
        show_percentage: Include percentage of total
        total_words: Total word count (needed for percentage)
        
    Returns:
        Formatted string ready to print
    """
    if not freq_data:
        return "No words found."
    
    lines = []
    
    if format_type == 'csv':
        lines.append("Word,Count" + (",Percentage" if show_percentage else ""))
        for word, count in freq_data:
            line = f"{word},{count}"
            if show_percentage and total_words:
                percentage = (count / total_words) * 100
                line += f",{percentage:.2f}%"
            lines.append(line)
    
    elif format_type == 'table':
        # Calculate column widths based on data
        max_word_len = max(len(word) for word, _ in freq_data)
        max_count_len = max(len(str(count)) for _, count in freq_data)
        
        header = f"{'Word':<{max_word_len}}  {'Count':>{max_count_len}}"
        if show_percentage:
            header += "  Percentage"
        
        lines.append(header)
        lines.append("-" * len(header))
        
        for word, count in freq_data:
            line = f"{word:<{max_word_len}}  {count:>{max_count_len}}"
            if show_percentage and total_words:
                percentage = (count / total_words) * 100
                line += f"  {percentage:>6.2f}%"
            lines.append(line)
    
    else:  # simple format
        for word, count in freq_data:
            line = f"{word}: {count}"
            if show_percentage and total_words:
                percentage = (count / total_words) * 100
                line += f" ({percentage:.2f}%)"
            lines.append(line)
    
    return "\n".join(lines)


def main():
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        description="Analyze word frequency in text files.",
        epilog="Example: %(prog)s document.txt -n 20 --no-stopwords"
    )
    
    parser.add_argument('file', help="Path to the text file to analyze")
    parser.add_argument('-n', '--top', type=int, metavar='N',
                        help="Show only the top N most frequent words")
    parser.add_argument('--no-stopwords', action='store_true',
                        help="Exclude common stopwords from analysis")
    parser.add_argument('--min-length', type=int, default=1, metavar='L',
                        help="Minimum word length to include (default: 1)")
    parser.add_argument('--format', choices=['table', 'csv', 'simple'],
                        default='table', help="Output format (default: table)")
    parser.add_argument('--percentage', action='store_true',
                        help="Show percentage of total words")
    
    args = parser.parse_args()
    
    # Process the file
    text = read_file(args.file)
    words = tokenize_text(text, min_length=args.min_length)
    
    if not words:
        print("No words found in file.", file=sys.stderr)
        sys.exit(1)
    
    total_words = len(words)
    freq_data = analyze_frequency(words, exclude_stopwords=args.no_stopwords, top_n=args.top)
    
    # Display results
    print(format_output(freq_data, format_type=args.format, 
                       show_percentage=args.percentage, total_words=total_words))
    
    # Summary stats
    print(f"\nTotal words: {total_words}")
    print(f"Unique words: {len(freq_data)}")


if __name__ == "__main__":
    # Demo mode - create a sample file and analyze it
    if len(sys.argv) == 1:
        print("=== DEMO MODE ===\n")
        
        # Create a temporary sample file
        sample_text = """
        The quick brown fox jumps over the lazy dog. The dog was really lazy,
        and the fox was incredibly quick. This is a sample text for demonstrating
        word frequency analysis. The word 'the' appears many times in this text.
        Python makes text analysis easy and fun. This tool helps analyze word
        patterns and frequency distributions in any text file.
        """
        
        demo_file = Path("demo_sample.txt")
        demo_file.write_text(sample_text)
        
        print(f"Created sample file: {demo_file}\n")
        print("Running analysis with stopword filtering...\n")
        
        # Simulate command-line args for demo
        sys.argv = ['word_freq_analyzer.py', str(demo_file), '-n', '10', '--no-stopwords', '--percentage']
        
        main()
        
        # Cleanup
        demo_file.unlink()
        print(f"\n(Cleaned up {demo_file})")
    else:
        main()