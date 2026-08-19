"""
Date: 2026-08-19
Implemented Huffman coding for text compression with a priority queue-based tree builder — actually compresses strings into binary and decodes them back.
"""

#!/usr/bin/env python3
"""
Huffman coding implementation for text compression.
Uses frequency analysis to build optimal prefix-free codes.
"""

import heapq
from collections import defaultdict, Counter


class HuffmanNode:
    """
    Node in the Huffman tree. Can be a leaf (with a character) or internal (children only).
    Using __lt__ because heapq needs to compare nodes when frequencies are equal.
    """
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        return self.freq < other.freq
    
    def is_leaf(self):
        """Check if this node is a leaf (has a character)."""
        return self.char is not None


def build_frequency_table(text):
    """
    Count character frequencies in the input text.
    Returns a Counter object mapping chars to their counts.
    """
    return Counter(text)


def build_huffman_tree(freq_table):
    """
    Build the Huffman tree using a min-heap (priority queue).
    Repeatedly merges the two lowest-frequency nodes until one tree remains.
    """
    # Edge case: empty input
    if not freq_table:
        return None
    
    # Edge case: single character - need at least one bit per char
    if len(freq_table) == 1:
        char = list(freq_table.keys())[0]
        freq = freq_table[char]
        return HuffmanNode(left=HuffmanNode(char=char, freq=freq))
    
    # Initialize heap with leaf nodes
    heap = [HuffmanNode(char=char, freq=freq) for char, freq in freq_table.items()]
    heapq.heapify(heap)
    
    # Build tree bottom-up
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        
        # Create parent node with combined frequency
        parent = HuffmanNode(
            freq=left.freq + right.freq,
            left=left,
            right=right
        )
        heapq.heappush(heap, parent)
    
    return heap[0]


def build_codes(root):
    """
    Traverse the Huffman tree to generate binary codes for each character.
    Left edges = 0, right edges = 1.
    Returns a dict mapping characters to their binary string codes.
    """
    if root is None:
        return {}
    
    codes = {}
    
    def traverse(node, current_code):
        if node.is_leaf():
            # Found a character - save its code
            codes[node.char] = current_code if current_code else "0"
            return
        
        if node.left:
            traverse(node.left, current_code + "0")
        if node.right:
            traverse(node.right, current_code + "1")
    
    traverse(root, "")
    return codes


def huffman_encode(text):
    """
    Encode text using Huffman coding.
    Returns a tuple: (encoded_binary_string, huffman_tree_root)
    The tree is needed for decoding.
    """
    if not text:
        return "", None
    
    freq_table = build_frequency_table(text)
    tree = build_huffman_tree(freq_table)
    codes = build_codes(tree)
    
    # Encode the text using the generated codes
    encoded = "".join(codes[char] for char in text)
    
    return encoded, tree


def huffman_decode(encoded_bits, tree):
    """
    Decode a binary string using the Huffman tree.
    Traverses the tree following the bits: 0=left, 1=right.
    """
    if not encoded_bits or tree is None:
        return ""
    
    decoded = []
    current = tree
    
    for bit in encoded_bits:
        # Navigate tree based on bit
        if bit == "0":
            current = current.left
        else:
            current = current.right
        
        # If we hit a leaf, we've found a character
        if current.is_leaf():
            decoded.append(current.char)
            current = tree  # Reset to root for next character
    
    return "".join(decoded)


def calculate_compression_ratio(original, encoded):
    """
    Calculate how much compression we achieved.
    Original uses 8 bits per char (ASCII), encoded uses variable bits.
    """
    original_bits = len(original) * 8
    encoded_bits = len(encoded)
    
    if original_bits == 0:
        return 0.0
    
    ratio = (1 - encoded_bits / original_bits) * 100
    return ratio


if __name__ == "__main__":
    # Test with a sample string that has varied character frequencies
    # 'e' and 's' appear more often, should get shorter codes
    test_text = "huffman compression is pretty neat! it uses trees and stuff."
    
    print("=" * 60)
    print("Huffman Coding Demo")
    print("=" * 60)
    print(f"\nOriginal text ({len(test_text)} chars):")
    print(f'"{test_text}"')
    
    # Encode
    encoded, tree = huffman_encode(test_text)
    print(f"\nEncoded binary ({len(encoded)} bits):")
    print(encoded[:80] + "..." if len(encoded) > 80 else encoded)
    
    # Show the codes for each character
    codes = build_codes(tree)
    print("\nHuffman codes (sorted by frequency):")
    freq_table = build_frequency_table(test_text)
    sorted_chars = sorted(freq_table.items(), key=lambda x: x[1], reverse=True)
    for char, freq in sorted_chars[:10]:  # Show top 10
        display_char = repr(char) if char in ' \n\t' else char
        print(f"  {display_char:4} (freq={freq:2}): {codes[char]}")
    
    # Decode to verify
    decoded = huffman_decode(encoded, tree)
    print(f"\nDecoded text:")
    print(f'"{decoded}"')
    
    # Stats
    compression = calculate_compression_ratio(test_text, encoded)
    print(f"\nCompression ratio: {compression:.1f}%")
    print(f"Original: {len(test_text) * 8} bits")
    print(f"Encoded:  {len(encoded)} bits")
    
    # Verify correctness
    assert test_text == decoded, "Decoding failed!"
    print("\n✓ Encoding/decoding successful!")