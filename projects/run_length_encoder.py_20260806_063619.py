"""
Date: 2026-08-06
Created a run-length encoding utility that compresses repetitive data and shows you how much space you saved — works great for pixel data or logs with lots of repeating characters.
"""

#!/usr/bin/env python3
"""
Run-length encoding (RLE) utility for compressing repetitive data.

This is especially useful for data with long runs of identical values,
like pixel data, simple graphics, or logs with lots of repeated characters.
"""

import sys
from typing import List, Tuple


def encode_rle(data: bytes) -> List[Tuple[int, int]]:
    """
    Encode bytes using run-length encoding.
    
    Returns a list of (count, value) tuples where count is how many times
    the byte value appears consecutively. I'm capping runs at 255 to keep
    counts in a single byte when serialized.
    
    Args:
        data: Raw bytes to encode
        
    Returns:
        List of (count, byte_value) tuples
    """
    if not data:
        return []
    
    encoded = []
    current_byte = data[0]
    count = 1
    
    for byte in data[1:]:
        if byte == current_byte and count < 255:
            count += 1
        else:
            encoded.append((count, current_byte))
            current_byte = byte
            count = 1
    
    # Don't forget the last run
    encoded.append((count, current_byte))
    
    return encoded


def decode_rle(encoded: List[Tuple[int, int]]) -> bytes:
    """
    Decode run-length encoded data back to original bytes.
    
    Args:
        encoded: List of (count, value) tuples
        
    Returns:
        Original decompressed bytes
    """
    decoded = bytearray()
    
    for count, value in encoded:
        decoded.extend([value] * count)
    
    return bytes(decoded)


def serialize_rle(encoded: List[Tuple[int, int]]) -> bytes:
    """
    Convert encoded tuples into a byte stream for storage.
    
    Format is simple: alternating count and value bytes.
    This is why I limit counts to 255 — keeps everything clean.
    
    Args:
        encoded: List of (count, value) tuples
        
    Returns:
        Serialized bytes ready to write to a file
    """
    result = bytearray()
    
    for count, value in encoded:
        result.append(count)
        result.append(value)
    
    return bytes(result)


def deserialize_rle(data: bytes) -> List[Tuple[int, int]]:
    """
    Parse serialized RLE data back into tuples.
    
    Args:
        data: Serialized RLE bytes
        
    Returns:
        List of (count, value) tuples
    """
    if len(data) % 2 != 0:
        raise ValueError("Invalid RLE data: must have even number of bytes")
    
    encoded = []
    for i in range(0, len(data), 2):
        count = data[i]
        value = data[i + 1]
        encoded.append((count, value))
    
    return encoded


def compress_string(text: str) -> Tuple[bytes, float]:
    """
    Compress a string and return compressed data plus compression ratio.
    
    Args:
        text: String to compress
        
    Returns:
        Tuple of (compressed_bytes, compression_ratio)
    """
    original_bytes = text.encode('utf-8')
    encoded = encode_rle(original_bytes)
    compressed = serialize_rle(encoded)
    
    # Calculate how much we saved (or didn't save)
    ratio = len(compressed) / len(original_bytes) if original_bytes else 1.0
    
    return compressed, ratio


def decompress_to_string(compressed: bytes) -> str:
    """
    Decompress RLE data back to a string.
    
    Args:
        compressed: Serialized RLE bytes
        
    Returns:
        Original string
    """
    encoded = deserialize_rle(compressed)
    decoded_bytes = decode_rle(encoded)
    return decoded_bytes.decode('utf-8')


if __name__ == "__main__":
    print("=== Run-Length Encoding Demo ===\n")
    
    # Test 1: String with lots of repetition (RLE shines here)
    test1 = "aaaaaabbbbccccccccddddddddddeeee"
    print(f"Test 1 - Repetitive string:")
    print(f"Original: '{test1}' ({len(test1)} bytes)")
    
    compressed1, ratio1 = compress_string(test1)
    print(f"Compressed: {len(compressed1)} bytes")
    print(f"Compression ratio: {ratio1:.2%}")
    print(f"Space saved: {(1 - ratio1) * 100:.1f}%")
    
    decompressed1 = decompress_to_string(compressed1)
    print(f"Decompressed matches: {decompressed1 == test1}")
    print()
    
    # Test 2: Less repetitive data (RLE might not help much)
    test2 = "The quick brown fox jumps over the lazy dog"
    print(f"Test 2 - Normal text:")
    print(f"Original: '{test2}' ({len(test2)} bytes)")
    
    compressed2, ratio2 = compress_string(test2)
    print(f"Compressed: {len(compressed2)} bytes")
    print(f"Compression ratio: {ratio2:.2%}")
    
    if ratio2 > 1.0:
        print(f"Warning: Data expanded by {(ratio2 - 1) * 100:.1f}% (RLE not ideal here)")
    
    decompressed2 = decompress_to_string(compressed2)
    print(f"Decompressed matches: {decompressed2 == test2}")
    print()
    
    # Test 3: Extreme case - simulating pixel data
    test3 = "X" * 100 + "Y" * 100 + "Z" * 100
    print(f"Test 3 - Simulated pixel data (300 chars):")
    print(f"Original: {len(test3)} bytes")
    
    compressed3, ratio3 = compress_string(test3)
    print(f"Compressed: {len(compressed3)} bytes")
    print(f"Compression ratio: {ratio3:.2%}")
    print(f"Space saved: {(1 - ratio3) * 100:.1f}%")
    
    decompressed3 = decompress_to_string(compressed3)
    print(f"Decompressed matches: {decompressed3 == test3}")
    print()
    
    # Show the actual encoded representation for the first test
    print("=== Under the Hood (Test 1) ===")
    encoded_tuples = encode_rle(test1.encode('utf-8'))
    print("Encoded as (count, char) tuples:")
    for count, byte_val in encoded_tuples:
        print(f"  {count} × '{chr(byte_val)}' (byte {byte_val})")