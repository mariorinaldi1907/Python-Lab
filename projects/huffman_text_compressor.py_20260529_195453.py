"""
Date: 2026-05-29
Implemented Huffman coding to compress text files by building frequency trees and generating variable-length bit codes for characters.
"""

#!/usr/bin/env python3
"""
Huffman coding compression utility.
Builds a frequency tree, generates optimal bit codes, and compresses text.
"""

import heapq
from collections import Counter, defaultdict
from typing import Dict, Tuple, Optional


class HuffmanNode:
    """
    Node in the Huffman tree. Can be a leaf (character) or internal (frequency sum).
    """
    def __init__(self, char: Optional[str], freq: int, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    
    # Heap needs comparison operators - we only care about frequency
    def __lt__(self, other):
        return self.freq < other.freq


def build_frequency_table(text: str) -> Dict[str, int]:
    """
    Count character occurrences in the text.
    """
    return dict(Counter(text))


def build_huffman_tree(freq_table: Dict[str, int]) -> HuffmanNode:
    """
    Construct the Huffman tree using a min-heap (priority queue).
    Start with leaf nodes for each character, then merge lowest frequency pairs.
    """
    # Edge case: single character
    if len(freq_table) == 1:
        char, freq = list(freq_table.items())[0]
        return HuffmanNode(None, freq, HuffmanNode(char, freq, None, None), None)
    
    # Initialize heap with leaf nodes
    heap = [HuffmanNode(char, freq) for char, freq in freq_table.items()]
    heapq.heapify(heap)
    
    # Build tree by repeatedly merging two smallest nodes
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        
        # Create internal node with combined frequency
        merged = HuffmanNode(None, left.freq + right.freq, left, right)
        heapq.heappush(heap, merged)
    
    return heap[0]


def generate_codes(root: HuffmanNode) -> Dict[str, str]:
    """
    Traverse the Huffman tree to generate bit codes for each character.
    Left = 0, Right = 1.
    """
    codes = {}
    
    def traverse(node: HuffmanNode, current_code: str):
        if node is None:
            return
        
        # Leaf node - we found a character
        if node.char is not None:
            codes[node.char] = current_code if current_code else "0"
            return
        
        # Traverse left (add '0') and right (add '1')
        traverse(node.left, current_code + "0")
        traverse(node.right, current_code + "1")
    
    traverse(root, "")
    return codes


def compress(text: str) -> Tuple[str, Dict[str, str]]:
    """
    Compress text using Huffman coding.
    Returns the encoded bit string and the codebook for decoding.
    """
    if not text:
        return "", {}
    
    freq_table = build_frequency_table(text)
    tree = build_huffman_tree(freq_table)
    codes = generate_codes(tree)
    
    # Encode the text
    encoded = "".join(codes[char] for char in text)
    
    return encoded, codes


def decompress(encoded: str, codes: Dict[str, str]) -> str:
    """
    Decode a Huffman-encoded bit string back to original text.
    We reverse the codebook for efficient lookup.
    """
    if not encoded or not codes:
        return ""
    
    # Reverse the codebook: bit_pattern -> character
    reverse_codes = {code: char for char, code in codes.items()}
    
    decoded = []
    current_code = ""
    
    for bit in encoded:
        current_code += bit
        if current_code in reverse_codes:
            decoded.append(reverse_codes[current_code])
            current_code = ""
    
    return "".join(decoded)


def calculate_compression_ratio(original: str, encoded: str) -> float:
    """
    Calculate how much space we saved.
    Original is in bytes (8 bits per char), encoded is in bits.
    """
    original_bits = len(original) * 8
    encoded_bits = len(encoded)
    
    if original_bits == 0:
        return 0.0
    
    return (1 - encoded_bits / original_bits) * 100


if __name__ == "__main__":
    # Test with a sample text that has varying character frequencies
    test_text = "hello huffman! this is a test of compression. compression is cool!"
    
    print("=" * 60)
    print("Huffman Compression Demo")
    print("=" * 60)
    print(f"\nOriginal text ({len(test_text)} chars):")
    print(f'"{test_text}"')
    
    # Compress
    encoded_bits, codebook = compress(test_text)
    
    print(f"\nCharacter frequencies:")
    freq_table = build_frequency_table(test_text)
    for char, freq in sorted(freq_table.items(), key=lambda x: -x[1])[:10]:
        code = codebook.get(char, "")
        print(f"  '{char}': {freq:2d} occurrences -> code: {code}")
    
    print(f"\nEncoded bit string ({len(encoded_bits)} bits):")
    print(f"{encoded_bits[:80]}..." if len(encoded_bits) > 80 else encoded_bits)
    
    # Decompress to verify
    decoded_text = decompress(encoded_bits, codebook)
    
    print(f"\nDecoded text ({len(decoded_text)} chars):")
    print(f'"{decoded_text}"')
    
    # Stats
    ratio = calculate_compression_ratio(test_text, encoded_bits)
    print(f"\nCompression ratio: {ratio:.2f}%")
    print(f"Original size: {len(test_text) * 8} bits")
    print(f"Compressed size: {len(encoded_bits)} bits")
    
    # Verify correctness
    assert test_text == decoded_text, "Decompression failed!"
    print("\n✓ Compression/decompression verified successfully!")