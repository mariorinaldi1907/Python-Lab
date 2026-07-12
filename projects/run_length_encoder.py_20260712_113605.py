"""
Date: 2026-07-12
Built a simple but solid run-length encoder/decoder to compress repetitive text — useful for basic data compression experiments.
"""

#!/usr/bin/env python3
"""
Run-length encoding utility for compressing repetitive sequences.

RLE is great for simple text with lots of repeated characters, but
honestly terrible for natural text. Still fun to implement though.
"""


def encode(data):
    """
    Encode a string using run-length encoding.
    
    Takes consecutive repeated characters and represents them as:
    character + count (only if count > 1, otherwise just the char).
    
    Args:
        data: String to encode
        
    Returns:
        Encoded string where runs are represented as char+count
        
    Example:
        "aaabbc" -> "a3b2c"
        "abc" -> "abc" (no compression needed)
    """
    if not data:
        return ""
    
    encoded = []
    current_char = data[0]
    count = 1
    
    for char in data[1:]:
        if char == current_char:
            count += 1
        else:
            # Write out the previous run
            if count > 1:
                encoded.append(f"{current_char}{count}")
            else:
                # Single character, just append it
                encoded.append(current_char)
            
            # Start tracking the new character
            current_char = char
            count = 1
    
    # Don't forget the last run!
    if count > 1:
        encoded.append(f"{current_char}{count}")
    else:
        encoded.append(current_char)
    
    return "".join(encoded)


def decode(data):
    """
    Decode a run-length encoded string back to original form.
    
    Parses character+number pairs and expands them. Handles both
    single characters and runs (char followed by digits).
    
    Args:
        data: RLE-encoded string
        
    Returns:
        Decoded original string
        
    Example:
        "a3b2c" -> "aaabbc"
        "abc" -> "abc"
    """
    if not data:
        return ""
    
    decoded = []
    i = 0
    
    while i < len(data):
        char = data[i]
        i += 1
        
        # Check if there's a number following this character
        num_str = ""
        while i < len(data) and data[i].isdigit():
            num_str += data[i]
            i += 1
        
        # If we found digits, that's the count; otherwise it's just 1
        count = int(num_str) if num_str else 1
        decoded.append(char * count)
    
    return "".join(decoded)


def compression_ratio(original, encoded):
    """
    Calculate how much space we saved (or lost) with encoding.
    
    Args:
        original: Original uncompressed string
        encoded: RLE-encoded string
        
    Returns:
        Ratio as a percentage. >100% means we made it worse.
    """
    if not original:
        return 0.0
    
    return (len(encoded) / len(original)) * 100


def analyze_compression(original):
    """
    Encode a string and print stats about the compression.
    
    This is mostly just for the demo, shows whether RLE actually
    helps or makes things worse for a given input.
    
    Args:
        original: String to analyze
    """
    encoded = encode(original)
    ratio = compression_ratio(original, encoded)
    
    print(f"\nOriginal: '{original}'")
    print(f"Encoded:  '{encoded}'")
    print(f"Original length: {len(original)}")
    print(f"Encoded length:  {len(encoded)}")
    print(f"Compression ratio: {ratio:.1f}%", end="")
    
    if ratio < 100:
        print(f" (saved {100 - ratio:.1f}%)")
    elif ratio > 100:
        print(f" (WORSE by {ratio - 100:.1f}%)")
    else:
        print(" (no change)")
    
    # Verify round-trip works
    decoded = decode(encoded)
    if decoded == original:
        print("✓ Decode successful")
    else:
        print(f"✗ Decode FAILED: got '{decoded}'")


if __name__ == "__main__":
    print("Run-Length Encoding Demo")
    print("=" * 50)
    
    # Test cases showing when RLE works well
    test_cases = [
        "aaaaaabbbbcccc",  # Great for RLE
        "aabbccddee",       # Okay for RLE
        "abcdefgh",         # Terrible for RLE
        "aaabbbaaabbb",     # Multiple runs
        "a",                # Edge case: single char
        "",                 # Edge case: empty
        "aaaaaaaaaaaaaaaaaaaaaaaa",  # Extreme repetition
        "The    quick    brown    fox",  # Realistic-ish with spaces
    ]
    
    for test in test_cases:
        analyze_compression(test)
    
    print("\n" + "=" * 50)
    print("Manual encode/decode test:")
    
    # Show the actual functions work independently
    original = "wwwwwwhhhhhoooooaaaaa"
    encoded = encode(original)
    decoded = decode(encoded)
    
    print(f"Original:  {original}")
    print(f"Encoded:   {encoded}")
    print(f"Decoded:   {decoded}")
    print(f"Match: {original == decoded}")