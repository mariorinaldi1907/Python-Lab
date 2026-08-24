"""
Date: 2026-08-24
Implemented Huffman coding with a priority queue to compress text files — wanted to see how much I could squeeze out of natural language patterns.
"""

#!/usr/bin/env python3
"""
Huffman coding implementation for text compression.
Uses a min-heap to build the optimal prefix-free code tree.
"""

import heapq
from collections import Counter, defaultdict
from typing import Dict, Tuple, Optional


class HuffmanNode:
    """
    Node in the Huffman tree. Can be either a leaf (with a character)
    or an internal node (with two children).
    """
    def __init__(self, char: Optional[str], freq: int, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        # For heapq comparison — we only care about frequency
        return self.freq < other.freq
    
    def is_leaf(self) -> bool:
        """Check if this is a leaf node (has a character)."""
        return self.char is not None


def build_frequency_table(text: str) -> Dict[str, int]:
    """
    Count character frequencies in the input text.
    Returns a dict mapping each character to its count.
    """
    return dict(Counter(text))


def build_huffman_tree(freq_table: Dict[str, int]) -> HuffmanNode:
    """
    Build the Huffman tree using a min-heap (priority queue).
    Repeatedly merge the two least-frequent nodes until one tree remains.
    """
    # Start with a heap of leaf nodes
    heap = [HuffmanNode(char, freq) for char, freq in freq_table.items()]
    heapq.heapify(heap)
    
    # Edge case: single character text
    if len(heap) == 1:
        # Create a dummy parent so we still have a tree structure
        single = heapq.heappop(heap)
        return HuffmanNode(None, single.freq, single, None)
    
    # Build tree by merging smallest nodes
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        
        merged = HuffmanNode(
            char=None,
            freq=left.freq + right.freq,
            left=left,
            right=right
        )
        heapq.heappush(heap, merged)
    
    return heap[0]


def build_codes(root: HuffmanNode) -> Dict[str, str]:
    """
    Traverse the Huffman tree to generate binary codes for each character.
    Left edges = '0', right edges = '1'.
    """
    codes = {}
    
    def traverse(node: HuffmanNode, code: str):
        if node.is_leaf():
            # For single-char texts, ensure we have at least one bit
            codes[node.char] = code if code else '0'
            return
        
        if node.left:
            traverse(node.left, code + '0')
        if node.right:
            traverse(node.right, code + '1')
    
    traverse(root, '')
    return codes


def huffman_encode(text: str) -> Tuple[str, Dict[str, str]]:
    """
    Encode text using Huffman coding.
    Returns the encoded bit string and the code table (for decoding).
    """
    if not text:
        return '', {}
    
    freq_table = build_frequency_table(text)
    tree = build_huffman_tree(freq_table)
    codes = build_codes(tree)
    
    # Encode the text by replacing each char with its code
    encoded = ''.join(codes[char] for char in text)
    
    return encoded, codes


def huffman_decode(encoded: str, codes: Dict[str, str]) -> str:
    """
    Decode a Huffman-encoded bit string back to the original text.
    We build a reverse lookup (code -> char) for efficiency.
    """
    if not encoded:
        return ''
    
    # Reverse the code table
    reverse_codes = {code: char for char, code in codes.items()}
    
    decoded = []
    current_code = ''
    
    for bit in encoded:
        current_code += bit
        if current_code in reverse_codes:
            decoded.append(reverse_codes[current_code])
            current_code = ''
    
    return ''.join(decoded)


def calculate_compression_ratio(original: str, encoded: str) -> float:
    """
    Calculate how much space we saved.
    Original is measured in 8-bit ASCII, encoded in bits.
    """
    original_bits = len(original) * 8
    encoded_bits = len(encoded)
    
    if original_bits == 0:
        return 0.0
    
    return (1 - encoded_bits / original_bits) * 100


if __name__ == "__main__":
    # Demo with a real text sample that should compress well
    sample_text = "hello hello world world world compression compression compression test test"
    
    print("=== Huffman Coding Demo ===\n")
    print(f"Original text ({len(sample_text)} chars):")
    print(f'"{sample_text}"\n')
    
    # Encode
    encoded_bits, code_table = huffman_encode(sample_text)
    
    print("Huffman Code Table:")
    # Sort by frequency (most common first) for readability
    char_freq = Counter(sample_text)
    for char, code in sorted(code_table.items(), key=lambda x: char_freq[x[0]], reverse=True):
        display_char = repr(char) if char != ' ' else "' '"
        print(f"  {display_char}: {code} (freq: {char_freq[char]})")
    
    print(f"\nEncoded bitstring ({len(encoded_bits)} bits):")
    # Show first 80 bits to keep output readable
    preview = encoded_bits[:80] + ('...' if len(encoded_bits) > 80 else '')
    print(f"{preview}\n")
    
    # Decode to verify
    decoded_text = huffman_decode(encoded_bits, code_table)
    print(f"Decoded text matches original: {decoded_text == sample_text}")
    
    # Compression stats
    ratio = calculate_compression_ratio(sample_text, encoded_bits)
    original_size = len(sample_text) * 8
    compressed_size = len(encoded_bits)
    
    print(f"\nCompression Stats:")
    print(f"  Original size: {original_size} bits ({len(sample_text)} bytes)")
    print(f"  Compressed size: {compressed_size} bits")
    print(f"  Compression ratio: {ratio:.2f}%")
    print(f"  Space saved: {original_size - compressed_size} bits")