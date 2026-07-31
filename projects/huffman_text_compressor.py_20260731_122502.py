"""
Date: 2026-07-31
Built a Huffman encoder/decoder to play around with compression algorithms — actually gets decent ratios on repetitive text.
"""

#!/usr/bin/env python3
"""
Huffman coding implementation for text compression.
Uses a greedy algorithm to build optimal prefix codes based on character frequency.
"""

import heapq
from collections import Counter, defaultdict
from typing import Dict, Tuple, Optional


class HuffmanNode:
    """
    Node in the Huffman tree. Supports comparison for heap operations.
    """
    def __init__(self, char: Optional[str], freq: int, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        # Heap needs to compare nodes by frequency
        return self.freq < other.freq
    
    def is_leaf(self) -> bool:
        """Check if this node is a leaf (contains an actual character)."""
        return self.left is None and self.right is None


def build_huffman_tree(text: str) -> Optional[HuffmanNode]:
    """
    Build a Huffman tree from input text using character frequencies.
    Returns the root node of the tree, or None if text is empty.
    """
    if not text:
        return None
    
    # Count character frequencies
    freq_map = Counter(text)
    
    # Edge case: single unique character
    if len(freq_map) == 1:
        char, freq = list(freq_map.items())[0]
        return HuffmanNode(char, freq)
    
    # Build initial heap with leaf nodes
    heap = [HuffmanNode(char, freq) for char, freq in freq_map.items()]
    heapq.heapify(heap)
    
    # Merge nodes until we have a single tree
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        
        # Create parent node with combined frequency
        merged = HuffmanNode(None, left.freq + right.freq, left, right)
        heapq.heappush(heap, merged)
    
    return heap[0]


def build_code_table(root: Optional[HuffmanNode]) -> Dict[str, str]:
    """
    Generate the encoding table by traversing the Huffman tree.
    Returns a dict mapping each character to its binary code.
    """
    if root is None:
        return {}
    
    # Special case: only one unique character
    if root.is_leaf():
        return {root.char: '0'}
    
    code_table = {}
    
    def traverse(node: HuffmanNode, code: str):
        """Recursively build codes by traversing left (0) and right (1)."""
        if node.is_leaf():
            code_table[node.char] = code
            return
        
        if node.left:
            traverse(node.left, code + '0')
        if node.right:
            traverse(node.right, code + '1')
    
    traverse(root, '')
    return code_table


def encode(text: str) -> Tuple[str, HuffmanNode]:
    """
    Encode text using Huffman coding.
    Returns a tuple of (encoded_binary_string, tree_root).
    We need to keep the tree to decode later.
    """
    root = build_huffman_tree(text)
    
    if root is None:
        return '', None
    
    code_table = build_code_table(root)
    encoded = ''.join(code_table[char] for char in text)
    
    return encoded, root


def decode(encoded: str, root: Optional[HuffmanNode]) -> str:
    """
    Decode a binary string using the Huffman tree.
    Traverse the tree based on each bit until we hit a leaf.
    """
    if not encoded or root is None:
        return ''
    
    # Special case: single unique character
    if root.is_leaf():
        return root.char * len(encoded)
    
    decoded = []
    current = root
    
    for bit in encoded:
        # Traverse left for 0, right for 1
        current = current.left if bit == '0' else current.right
        
        if current.is_leaf():
            decoded.append(current.char)
            current = root  # Reset to root for next character
    
    return ''.join(decoded)


def compress_stats(original: str, encoded: str) -> None:
    """
    Print compression statistics to see how well Huffman did.
    """
    # Original size in bits (assuming 8-bit ASCII)
    original_bits = len(original) * 8
    compressed_bits = len(encoded)
    
    if original_bits == 0:
        print("No data to compress")
        return
    
    ratio = (1 - compressed_bits / original_bits) * 100
    
    print(f"\n{'='*50}")
    print(f"Original size: {original_bits} bits ({len(original)} chars)")
    print(f"Compressed size: {compressed_bits} bits")
    print(f"Compression ratio: {ratio:.2f}%")
    print(f"{'='*50}")


if __name__ == "__main__":
    # Demo with a text that has obvious repetition
    test_text = "mississippi river runs through mississippi state"
    
    print(f"Original text: '{test_text}'")
    
    # Encode
    encoded_data, tree = encode(test_text)
    print(f"\nEncoded (binary): {encoded_data[:80]}..." if len(encoded_data) > 80 else f"\nEncoded (binary): {encoded_data}")
    
    # Show the code table
    code_table = build_code_table(tree)
    print(f"\nHuffman codes generated:")
    for char, code in sorted(code_table.items(), key=lambda x: len(x[1])):
        display_char = repr(char) if char == ' ' else char
        print(f"  {display_char}: {code}")
    
    # Decode to verify
    decoded_text = decode(encoded_data, tree)
    print(f"\nDecoded text: '{decoded_text}'")
    print(f"Match: {decoded_text == test_text}")
    
    # Show compression stats
    compress_stats(test_text, encoded_data)
    
    # Try another example with less repetition
    print("\n" + "="*50)
    print("Testing with less repetitive text:")
    test_text2 = "abcdefghijklmnopqrstuvwxyz"
    print(f"Original: '{test_text2}'")
    encoded2, tree2 = encode(test_text2)
    decoded2 = decode(encoded2, tree2)
    print(f"Decoded: '{decoded2}'")
    print(f"Match: {decoded2 == test_text2}")
    compress_stats(test_text2, encoded2)