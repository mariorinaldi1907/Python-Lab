"""
Date: 2026-07-13
Implemented a clean run-length encoding utility that compresses repetitive sequences — useful for simple text compression tasks.
"""

#!/usr/bin/env python3
"""
Run-Length Encoding (RLE) Compression Utility

This module provides encoding and decoding functionality for run-length encoding,
a simple lossless compression algorithm that replaces consecutive repeated characters
with a count and the character itself.
"""

import sys
from typing import Tuple


def encode_rle(data: str) -> str:
    """
    Encode a string using run-length encoding.
    
    Consecutive identical characters are replaced with the count followed by the character.
    Single characters are kept as-is to avoid unnecessary overhead (e.g., "a" stays "a" not "1a").
    
    Args:
        data: The input string to encode
        
    Returns:
        The run-length encoded string
        
    Example:
        >>> encode_rle("aaabbc")
        '3a2bc'
    """
    if not data:
        return ""
    
    encoded = []
    i = 0
    
    while i < len(data):
        current_char = data[i]
        count = 1
        
        # Count consecutive occurrences of the same character
        while i + count < len(data) and data[i + count] == current_char:
            count += 1
        
        # Only prepend count if there's more than one character
        # This saves space for non-repetitive data
        if count > 1:
            encoded.append(f"{count}{current_char}")
        else:
            encoded.append(current_char)
        
        i += count
    
    return "".join(encoded)


def decode_rle(data: str) -> str:
    """
    Decode a run-length encoded string back to its original form.
    
    Args:
        data: The run-length encoded string
        
    Returns:
        The decoded original string
        
    Raises:
        ValueError: If the encoded string is malformed
        
    Example:
        >>> decode_rle("3a2bc")
        'aaabbc'
    """
    if not data:
        return ""
    
    decoded = []
    i = 0
    
    while i < len(data):
        # Check if we're looking at a digit (start of a count)
        if data[i].isdigit():
            # Extract the full number (could be multi-digit like "12")
            num_str = ""
            while i < len(data) and data[i].isdigit():
                num_str += data[i]
                i += 1
            
            if i >= len(data):
                raise ValueError(f"Malformed RLE string: count '{num_str}' not followed by a character")
            
            count = int(num_str)
            char = data[i]
            decoded.append(char * count)
            i += 1
        else:
            # Single character without count
            decoded.append(data[i])
            i += 1
    
    return "".join(decoded)


def calculate_compression_ratio(original: str, encoded: str) -> float:
    """
    Calculate the compression ratio achieved.
    
    Args:
        original: The original uncompressed string
        encoded: The compressed string
        
    Returns:
        Compression ratio as a percentage (positive = compression, negative = expansion)
    """
    if not original:
        return 0.0
    
    original_size = len(original)
    encoded_size = len(encoded)
    ratio = ((original_size - encoded_size) / original_size) * 100
    
    return ratio


def demonstrate_encoding():
    """
    Run a demonstration of the RLE encoder with various test cases.
    
    Shows how the algorithm handles different types of input, including
    highly repetitive text, mixed content, and edge cases.
    """
    test_cases = [
        "aaabbbccc",
        "hello world",
        "aaaaaaaaaaaabbbbbbbbbbb",
        "abcdef",
        "aabbccddee",
        "xxxxxxxxxx",
        "",
        "a",
        "The quick brown fox jumps over the lazy dog",
        "WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWW"  # classic example
    ]
    
    print("=" * 70)
    print("RUN-LENGTH ENCODING DEMONSTRATION")
    print("=" * 70)
    
    for test in test_cases:
        encoded = encode_rle(test)
        decoded = decode_rle(encoded)
        ratio = calculate_compression_ratio(test, encoded)
        
        # Verify round-trip correctness
        assert decoded == test, f"Round-trip failed for: {test}"
        
        display_original = test if len(test) <= 50 else test[:47] + "..."
        display_encoded = encoded if len(encoded) <= 50 else encoded[:47] + "..."
        
        print(f"\nOriginal ({len(test)} chars): {display_original!r}")
        print(f"Encoded  ({len(encoded)} chars): {display_encoded!r}")
        print(f"Compression: {ratio:+.1f}%")
        
        if ratio < 0:
            print("  ⚠️  Warning: Data expanded (RLE not suitable for this input)")


if __name__ == "__main__":
    # If command-line arguments are provided, encode/decode them
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "encode" and len(sys.argv) > 2:
            input_text = " ".join(sys.argv[2:])
            result = encode_rle(input_text)
            print(f"Encoded: {result}")
        elif mode == "decode" and len(sys.argv) > 2:
            input_text = " ".join(sys.argv[2:])
            result = decode_rle(input_text)
            print(f"Decoded: {result}")
        else:
            print("Usage: python run_length_encoder.py [encode|decode] <text>")
            print("   Or: python run_length_encoder.py   (to run demo)")
    else:
        # No arguments, run the demo
        demonstrate_encoding()