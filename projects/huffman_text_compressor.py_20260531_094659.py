"""
Date: 2026-05-31
Built a Huffman compression utility to see how much I could squeeze out of text files using variable-length prefix codes.
"""

#!/usr/bin/env python3
"""
Huffman coding implementation for text compression.
Builds a frequency tree, generates optimal prefix codes, and compresses/decompresses strings.
"""

import heapq
from collections import Counter, defaultdict
from typing import Dict, Optional, Tuple


class HuffmanNode:
    """
    Node in the Huffman tree. Uses frequency for priority queue ordering.
    Leaf nodes contain characters, internal nodes are just for structure.
    """
    def __init__(self, char: Optional[str], freq: int, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        # heapq needs this for comparison when frequencies are equal
        return self.freq < other.freq
    
    def is_leaf(self):
        return self.char is not None


def build_frequency_table(text: str) -> Dict[str, int]:
    """
    Count character occurrences in the input text.
    Using Counter because it's cleaner than manual dict updates.
    """
    return dict(Counter(text))


def build_huffman_tree(freq_table: Dict[str, int]) -> HuffmanNode:
    """
    Construct the Huffman tree using a min-heap priority queue.
    Repeatedly merge the two smallest frequency nodes until one tree remains.
    """
    if not freq_table:
        raise ValueError("Cannot build tree from empty frequency table")
    
    # Initialize heap with leaf nodes for each character
    heap = [HuffmanNode(char, freq) for char, freq in freq_table.items()]
    heapq.heapify(heap)
    
    # Edge case: single character input needs at least one bit
    if len(heap) == 1:
        node = heapq.heappop(heap)
        return HuffmanNode(None, node.freq, node, None)
    
    # Build tree bottom-up by combining smallest nodes
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(None, left.freq + right.freq, left, right)
        heapq.heappush(heap, merged)
    
    return heap[0]


def generate_codes(root: HuffmanNode) -> Dict[str, str]:
    """
    Traverse the tree to assign binary codes to each character.
    Left edge = 0, right edge = 1. This gives us prefix-free codes.
    """
    codes = {}
    
    def traverse(node: HuffmanNode, code: str):
        if node.is_leaf():
            # Use '0' for single-character edge case
            codes[node.char] = code if code else '0'
            return
        
        if node.left:
            traverse(node.left, code + '0')
        if node.right:
            traverse(node.right, code + '1')
    
    traverse(root, '')
    return codes


def compress(text: str) -> Tuple[str, HuffmanNode]:
    """
    Compress text using Huffman coding.
    Returns the binary string representation and the tree (needed for decompression).
    """
    if not text:
        raise ValueError("Cannot compress empty text")
    
    freq_table = build_frequency_table(text)
    tree = build_huffman_tree(freq_table)
    codes = generate_codes(tree)
    
    # Encode each character using its Huffman code
    compressed = ''.join(codes[char] for char in text)
    
    return compressed, tree


def decompress(compressed: str, tree: HuffmanNode) -> str:
    """
    Decompress a binary string using the Huffman tree.
    Walk the tree based on bits until we hit a leaf, then output that character.
    """
    if not compressed:
        return ''
    
    result = []
    current = tree
    
    for bit in compressed:
        # Navigate tree: 0 goes left, 1 goes right
        if bit == '0':
            current = current.left if current.left else current
        else:
            current = current.right if current.right else current
        
        # Found a character
        if current.is_leaf():
            result.append(current.char)
            current = tree  # Reset to root for next character
    
    return ''.join(result)


def calculate_compression_ratio(original: str, compressed: str) -> float:
    """
    Calculate how much space we saved.
    Original uses 8 bits per char (ASCII), compressed uses variable-length codes.
    """
    original_bits = len(original) * 8
    compressed_bits = len(compressed)
    return (1 - compressed_bits / original_bits) * 100 if original_bits > 0 else 0


if __name__ == "__main__":
    # Demo with a text sample that should compress well (repeated patterns)
    test_text = "hello world! this is a huffman coding example. huffman coding is pretty cool!"
    
    print("=" * 60)
    print("HUFFMAN COMPRESSION DEMO")
    print("=" * 60)
    print(f"\nOriginal text ({len(test_text)} chars):")
    print(f'"{test_text}"')
    
    # Compress
    compressed_bits, huffman_tree = compress(test_text)
    
    print(f"\nCompressed (binary string, {len(compressed_bits)} bits):")
    print(compressed_bits[:80] + "..." if len(compressed_bits) > 80 else compressed_bits)
    
    # Show the codes generated
    codes = generate_codes(huffman_tree)
    print("\nGenerated Huffman codes:")
    for char, code in sorted(codes.items(), key=lambda x: len(x[1]))[:10]:
        display_char = repr(char) if char in '\n\t ' else char
        print(f"  {display_char:6} -> {code}")
    if len(codes) > 10:
        print(f"  ... and {len(codes) - 10} more characters")
    
    # Decompress to verify
    decompressed_text = decompress(compressed_bits, huffman_tree)
    
    print(f"\nDecompressed text:")
    print(f'"{decompressed_text}"')
    
    # Stats
    ratio = calculate_compression_ratio(test_text, compressed_bits)
    print(f"\nCompression stats:")
    print(f"  Original:   {len(test_text) * 8} bits ({len(test_text)} chars × 8 bits)")
    print(f"  Compressed: {len(compressed_bits)} bits")
    print(f"  Savings:    {ratio:.2f}%")
    print(f"  Match:      {'✓ PASS' if test_text == decompressed_text else '✗ FAIL'}")