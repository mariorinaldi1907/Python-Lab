"""
Date: 2026-06-24
Implemented a run-length encoder/decoder from scratch to compress repetitive text sequences — useful for simple data compression tasks.
"""

#!/usr/bin/env python3
"""
Run-Length Encoding (RLE) implementation.

This was a fun little exercise in string manipulation. RLE is one of the simplest
compression algorithms - it just counts consecutive identical characters.
Works great on data with long runs (like "AAAAAABBBB"), not so much on random data.
"""


def encode(data):
    """
    Compress a string using run-length encoding.
    
    Converts sequences of identical characters into count+character pairs.
    For example: "AAABBC" becomes "3A2B1C"
    
    Args:
        data: String to encode
        
    Returns:
        Encoded string with counts prefixed to each character run
    """
    if not data:
        return ""
    
    encoded = []
    current_char = data[0]
    count = 1
    
    # Walk through the string counting consecutive identical chars
    for i in range(1, len(data)):
        if data[i] == current_char:
            count += 1
        else:
            # Different char encountered, save what we've counted
            encoded.append(f"{count}{current_char}")
            current_char = data[i]
            count = 1
    
    # Don't forget the last run!
    encoded.append(f"{count}{current_char}")
    
    return "".join(encoded)


def decode(data):
    """
    Decompress a run-length encoded string back to original form.
    
    Takes encoded format like "3A2B1C" and expands to "AAABBC".
    Assumes the encoding format is valid (count followed by character).
    
    Args:
        data: RLE-encoded string
        
    Returns:
        Decoded original string
    """
    if not data:
        return ""
    
    decoded = []
    i = 0
    
    while i < len(data):
        # Extract the count (may be multiple digits)
        count_str = ""
        while i < len(data) and data[i].isdigit():
            count_str += data[i]
            i += 1
        
        if not count_str or i >= len(data):
            # Malformed input, but we'll handle it gracefully
            break
            
        count = int(count_str)
        char = data[i]
        
        # Expand the run
        decoded.append(char * count)
        i += 1
    
    return "".join(decoded)


def compression_ratio(original, encoded):
    """
    Calculate how much space we saved (or wasted) with encoding.
    
    Args:
        original: Original uncompressed string
        encoded: RLE-encoded string
        
    Returns:
        Ratio as a percentage. >100% means we made it worse (oops).
    """
    if not original:
        return 0.0
    
    return (len(encoded) / len(original)) * 100


def analyze_compression(text):
    """
    Encode text and report statistics about compression effectiveness.
    
    I added this because I wanted to see actual numbers on how well
    RLE performs on different types of input.
    
    Args:
        text: String to analyze
    """
    encoded = encode(text)
    ratio = compression_ratio(text, encoded)
    
    print(f"Original:  '{text}'")
    print(f"Encoded:   '{encoded}'")
    print(f"Original length: {len(text)} chars")
    print(f"Encoded length:  {len(encoded)} chars")
    print(f"Compression ratio: {ratio:.1f}%")
    
    if ratio < 100:
        savings = 100 - ratio
        print(f"✓ Saved {savings:.1f}% space!")
    else:
        waste = ratio - 100
        print(f"✗ Wasted {waste:.1f}% more space (RLE isn't good for this data)")
    
    # Verify round-trip works
    decoded = decode(encoded)
    if decoded == text:
        print("✓ Decode successful - data integrity verified")
    else:
        print("✗ ERROR: Decoded data doesn't match original!")
    
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("Run-Length Encoding Demo")
    print("=" * 60)
    print()
    
    # Test case 1: Lots of repetition (RLE shines here)
    print("Test 1: High repetition data")
    print("-" * 40)
    analyze_compression("AAAAABBBBBCCCCCDDDDDEEEEE")
    
    # Test case 2: Some repetition (still decent)
    print("Test 2: Moderate repetition")
    print("-" * 40)
    analyze_compression("WWWWWAAADEXXXXXXYWWW")
    
    # Test case 3: No repetition (RLE actually makes it worse!)
    print("Test 3: No repetition (worst case for RLE)")
    print("-" * 40)
    analyze_compression("ABCDEFGHIJK")
    
    # Test case 4: Real-world-ish scenario
    print("Test 4: Mixed content")
    print("-" * 40)
    analyze_compression("HELLO     WORLD!!!")
    
    # Test case 5: Edge cases
    print("Test 5: Edge cases")
    print("-" * 40)
    print(f"Empty string: '{encode('')}' (should be empty)")
    print(f"Single char: '{encode('A')}' (should be '1A')")
    print(f"All same: '{encode('ZZZZZZZZZZ')}' (should be '10Z')")
    print()
    
    print("=" * 60)
    print("Pro tip: RLE works best on data with long runs of")
    print("identical values - like bitmap images, simple graphics,")
    print("or data with lots of repeated whitespace.")
    print("=" * 60)