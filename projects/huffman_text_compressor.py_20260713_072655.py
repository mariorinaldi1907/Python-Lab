"""
Date: 2026-07-13
Implemented Huffman coding to compress text by building frequency trees and generating variable-length codes — wanted to see how much I could squeeze out of repetitive strings.
"""

#!/usr/bin/env python3
"""
Huffman Coding Implementation
Compresses text using variable-length prefix codes based on character frequency.
Characters that appear more often get shorter codes.
"""

import heapq
from collections import Counter, defaultdict


class HuffmanNode:
    """
    Node in the Huffman tree. Can be either a leaf (with a character)
    or an internal node (with two children).
    """
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    
    # Heap comparisons are based on frequency
    def __lt__(self, other):
        return self.freq < other.freq


def build_frequency_table(text):
    """
    Count how many times each character appears in the text.
    Returns a Counter object mapping char -> count.
    """
    return Counter(text)


def build_huffman_tree(freq_table):
    """
    Build the Huffman tree using a min-heap (priority queue).
    Start with all characters as leaf nodes, repeatedly merge the two
    nodes with smallest frequency until only one tree remains.
    """
    # Edge case: empty text
    if not freq_table:
        return None
    
    # Edge case: single unique character
    if len(freq_table) == 1:
        char, freq = list(freq_table.items())[0]
        # Create a tree with a dummy internal node so we can assign a code
        return HuffmanNode(freq=freq, left=HuffmanNode(char=char, freq=freq))
    
    # Initialize heap with leaf nodes for each character
    heap = [HuffmanNode(char=char, freq=freq) for char, freq in freq_table.items()]
    heapq.heapify(heap)
    
    # Build tree by repeatedly merging two smallest nodes
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        
        merged = HuffmanNode(
            freq=left.freq + right.freq,
            left=left,
            right=right
        )
        heapq.heappush(heap, merged)
    
    return heap[0]


def generate_codes(root):
    """
    Traverse the Huffman tree to generate binary codes for each character.
    Left edge = 0, right edge = 1.
    Returns a dict mapping char -> binary string (e.g., 'a' -> '101').
    """
    if root is None:
        return {}
    
    codes = {}
    
    def traverse(node, current_code):
        if node is None:
            return
        
        # Leaf node: assign the code
        if node.char is not None:
            codes[node.char] = current_code if current_code else '0'
            return
        
        # Internal node: go left (0) and right (1)
        traverse(node.left, current_code + '0')
        traverse(node.right, current_code + '1')
    
    traverse(root, '')
    return codes


def encode(text, codes):
    """
    Encode the text using the generated Huffman codes.
    Returns a binary string (as a str of '0' and '1' characters).
    """
    return ''.join(codes[char] for char in text)


def decode(encoded_bits, root):
    """
    Decode a binary string back to the original text using the Huffman tree.
    Walk down the tree: '0' goes left, '1' goes right.
    """
    if root is None:
        return ""
    
    decoded = []
    current = root
    
    for bit in encoded_bits:
        # Navigate the tree
        if bit == '0':
            current = current.left
        else:
            current = current.right
        
        # If we hit a leaf, output the character and reset to root
        if current.char is not None:
            decoded.append(current.char)
            current = root
    
    return ''.join(decoded)


def compress_text(text):
    """
    Full compression pipeline: build tree, generate codes, encode.
    Returns the encoded bits and the Huffman tree (needed for decoding).
    """
    freq_table = build_frequency_table(text)
    tree = build_huffman_tree(freq_table)
    codes = generate_codes(tree)
    encoded = encode(text, codes)
    return encoded, tree, codes


def calculate_compression_ratio(original, encoded_bits):
    """
    Calculate how much we saved. Original is measured in 8-bit ASCII,
    encoded is measured in bits (length of the binary string).
    """
    original_bits = len(original) * 8
    compressed_bits = len(encoded_bits)
    ratio = (1 - compressed_bits / original_bits) * 100 if original_bits > 0 else 0
    return original_bits, compressed_bits, ratio


if __name__ == "__main__":
    # Demo with a text that has obvious repetition
    sample_text = "huffman coding is a compression algorithm that assigns variable length codes"
    
    print("=" * 60)
    print("HUFFMAN CODING COMPRESSION DEMO")
    print("=" * 60)
    print(f"\nOriginal text:\n\"{sample_text}\"\n")
    print(f"Length: {len(sample_text)} characters")
    
    # Compress
    encoded_bits, tree, codes = compress_text(sample_text)
    
    print("\nGenerated Huffman Codes:")
    # Sort by code length for nicer display
    for char, code in sorted(codes.items(), key=lambda x: (len(x[1]), x[0])):
        display_char = repr(char) if char in ' \n\t' else char
        print(f"  {display_char:5} -> {code}")
    
    print(f"\nEncoded binary string (first 80 chars):\n{encoded_bits[:80]}...")
    
    # Calculate compression
    orig_bits, comp_bits, ratio = calculate_compression_ratio(sample_text, encoded_bits)
    print(f"\nCompression Statistics:")
    print(f"  Original:   {orig_bits} bits ({len(sample_text)} chars × 8 bits)")
    print(f"  Compressed: {comp_bits} bits")
    print(f"  Saved:      {ratio:.1f}%")
    
    # Decompress to verify
    decoded_text = decode(encoded_bits, tree)
    print(f"\nDecoded text:\n\"{decoded_text}\"\n")
    
    # Verify correctness
    if decoded_text == sample_text:
        print("✓ Decompression successful! Original text perfectly restored.")
    else:
        print("✗ Error: Decoded text doesn't match original!")