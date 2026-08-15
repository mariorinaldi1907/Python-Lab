"""
Date: 2026-08-15
Implemented run-length encoding to compress repetitive sequences — included both encoding and decoding with visual compression ratio feedback.
"""

#!/usr/bin/env python3
"""
Run-Length Encoding (RLE) utility.

Compresses sequences by replacing consecutive identical characters
with a count+character pair. Works best on data with long runs of
repeated characters (like bitmap data or simple graphics).
"""


def encode(data):
    """
    Encode a string using run-length encoding.
    
    Takes consecutive runs of identical characters and replaces them
    with the count followed by the character. For single characters,
    just outputs the character (no count prefix) to avoid expansion.
    
    Args:
        data: String to encode
        
    Returns:
        Encoded string with runs compressed to count+char format
        
    Example:
        "aaabbc" -> "3a2bc"
        "abc" -> "abc" (no compression since no runs)
    """
    if not data:
        return ""
    
    encoded = []
    i = 0
    
    while i < len(data):
        current_char = data[i]
        count = 1
        
        # Count consecutive identical characters
        while i + count < len(data) and data[i + count] == current_char:
            count += 1
        
        # Only include count if there's more than one character
        # Otherwise we'd be expanding single chars (e.g., "a" -> "1a")
        if count > 1:
            encoded.append(f"{count}{current_char}")
        else:
            encoded.append(current_char)
        
        i += count
    
    return "".join(encoded)


def decode(data):
    """
    Decode a run-length encoded string back to original form.
    
    Reads digit sequences as counts and expands the following character
    that many times. Non-digit characters are treated as single chars.
    
    Args:
        data: RLE-encoded string
        
    Returns:
        Decoded original string
        
    Example:
        "3a2bc" -> "aaabbc"
    """
    if not data:
        return ""
    
    decoded = []
    i = 0
    
    while i < len(data):
        # Check if we're at the start of a number
        if data[i].isdigit():
            # Extract the full number (could be multi-digit like "12a")
            num_str = ""
            while i < len(data) and data[i].isdigit():
                num_str += data[i]
                i += 1
            
            count = int(num_str)
            
            # The character to repeat should follow the number
            if i < len(data):
                char = data[i]
                decoded.append(char * count)
                i += 1
        else:
            # Single character, no count prefix
            decoded.append(data[i])
            i += 1
    
    return "".join(decoded)


def compression_ratio(original, compressed):
    """
    Calculate the compression ratio as a percentage.
    
    Args:
        original: Original string
        compressed: Compressed string
        
    Returns:
        Float representing compression ratio (negative means expansion)
    """
    if not original:
        return 0.0
    
    original_size = len(original)
    compressed_size = len(compressed)
    
    # Positive ratio means compression, negative means expansion
    ratio = ((original_size - compressed_size) / original_size) * 100
    return ratio


def visualize_encoding(data, encoded):
    """
    Print a side-by-side comparison of original and encoded data.
    
    Args:
        data: Original string
        encoded: Encoded string
    """
    print(f"Original:  '{data}'")
    print(f"Encoded:   '{encoded}'")
    print(f"Size:      {len(data)} -> {len(encoded)} bytes")
    
    ratio = compression_ratio(data, encoded)
    if ratio > 0:
        print(f"Compressed {ratio:.1f}%")
    elif ratio < 0:
        print(f"Expanded {abs(ratio):.1f}% (RLE not suitable for this data)")
    else:
        print("No change in size")


if __name__ == "__main__":
    print("=== Run-Length Encoding Demo ===\n")
    
    # Test case 1: Great compression scenario (repetitive data)
    test1 = "aaaaaabbbbccccccccdddd"
    encoded1 = encode(test1)
    print("Test 1: Highly repetitive string")
    visualize_encoding(test1, encoded1)
    decoded1 = decode(encoded1)
    assert decoded1 == test1, "Decode failed for test1!"
    print()
    
    # Test case 2: Poor compression scenario (no repetition)
    test2 = "abcdefghij"
    encoded2 = encode(test2)
    print("Test 2: No repetition (worst case for RLE)")
    visualize_encoding(test2, encoded2)
    decoded2 = decode(encoded2)
    assert decoded2 == test2, "Decode failed for test2!"
    print()
    
    # Test case 3: Mixed scenario
    test3 = "aaabccddddeeee"
    encoded3 = encode(test3)
    print("Test 3: Mixed repetition")
    visualize_encoding(test3, encoded3)
    decoded3 = decode(encoded3)
    assert decoded3 == test3, "Decode failed for test3!"
    print()
    
    # Test case 4: Long run (multi-digit count)
    test4 = "x" * 123 + "y" * 45
    encoded4 = encode(test4)
    print("Test 4: Very long runs")
    visualize_encoding(test4, encoded4)
    decoded4 = decode(encoded4)
    assert decoded4 == test4, "Decode failed for test4!"
    print()
    
    # Test case 5: Edge case - empty string
    test5 = ""
    encoded5 = encode(test5)
    decoded5 = decode(encoded5)
    assert decoded5 == test5, "Decode failed for test5!"
    print("Test 5: Empty string - ✓ Passed")
    print()
    
    # Test case 6: Real-world-ish example (simulated bitmap row)
    test6 = "000000001111110000000000111111111100000"
    encoded6 = encode(test6)
    print("Test 6: Simulated bitmap data")
    visualize_encoding(test6, encoded6)
    decoded6 = decode(encoded6)
    assert decoded6 == test6, "Decode failed for test6!"
    print()
    
    print("✓ All tests passed! Encoding/decoding works correctly.")