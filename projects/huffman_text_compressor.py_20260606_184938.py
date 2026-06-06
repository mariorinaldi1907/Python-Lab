"""
Date: 2026-06-06
Implemented Huffman coding to see how much I could squeeze text files — includes encoding, decoding, and a frequency tree visualizer.
"""

#!/usr/bin/env python3
"""
Huffman Text Compressor
A from-scratch implementation of Huffman coding for text compression.
Builds a frequency tree, generates optimal bit codes, and can encode/decode.
"""

import heapq
from collections import Counter, defaultdict


class HuffmanNode:
    """
    Represents a node in the Huffman tree.
    Used for building the encoding tree via priority queue.
    """
    def __init__(self, char, freq, left=None, right=None):
        self.char = char  # None for internal nodes
        self.freq = freq
        self.left = left
        self.right = right
    
    # Priority queue needs comparison operators
    def __lt__(self, other):
        return self.freq < other.freq


def build_frequency_table(text):
    """
    Count character frequencies in the input text.
    Returns a Counter dict mapping char -> count.
    """
    return Counter(text)


def build_huffman_tree(freq_table):
    """
    Construct the Huffman tree using a min-heap.
    Repeatedly merge the two lowest-frequency nodes until one tree remains.
    """
    # Edge case: empty or single-character input
    if len(freq_table) == 0:
        return None
    if len(freq_table) == 1:
        char, freq = list(freq_table.items())[0]
        # Need at least one bit, so create a dummy parent
        return HuffmanNode(None, freq, HuffmanNode(char, freq), None)
    
    # Initialize heap with leaf nodes
    heap = [HuffmanNode(char, freq) for char, freq in freq_table.items()]
    heapq.heapify(heap)
    
    # Build tree by merging smallest nodes
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(None, left.freq + right.freq, left, right)
        heapq.heappush(heap, merged)
    
    return heap[0]


def generate_codes(root):
    """
    Traverse the Huffman tree to generate binary codes for each character.
    Left = 0, Right = 1. Returns a dict mapping char -> bitstring.
    """
    if root is None:
        return {}
    
    codes = {}
    
    def traverse(node, current_code):
        if node is None:
            return
        
        # Leaf node — assign code
        if node.char is not None:
            codes[node.char] = current_code if current_code else "0"
            return
        
        # Traverse left and right
        traverse(node.left, current_code + "0")
        traverse(node.right, current_code + "1")
    
    traverse(root, "")
    return codes


def encode_text(text, codes):
    """
    Encode the input text using the Huffman codes.
    Returns the encoded bitstring as a string of '0's and '1's.
    """
    return ''.join(codes[char] for char in text)


def decode_text(encoded, root):
    """
    Decode a Huffman-encoded bitstring back to original text.
    Walks the tree based on bits: 0 = left, 1 = right.
    """
    if root is None:
        return ""
    
    decoded = []
    current = root
    
    for bit in encoded:
        # Move left or right
        if bit == '0':
            current = current.left
        else:
            current = current.right
        
        # Reached a leaf — output character and reset
        if current.char is not None:
            decoded.append(current.char)
            current = root
    
    return ''.join(decoded)


def calculate_compression_ratio(original, encoded_bits):
    """
    Calculate how much we compressed.
    Original is in 8-bit ASCII, encoded is the bitstring length.
    """
    original_bits = len(original) * 8
    if original_bits == 0:
        return 0.0
    return (1 - len(encoded_bits) / original_bits) * 100


def print_code_table(codes):
    """
    Pretty-print the Huffman code table sorted by frequency.
    """
    print("\nHuffman Code Table:")
    print("-" * 40)
    sorted_codes = sorted(codes.items(), key=lambda x: len(x[1]))
    for char, code in sorted_codes:
        display_char = repr(char) if char in '\n\t ' else char
        print(f"  {display_char:5} -> {code}")
    print("-" * 40)


if __name__ == "__main__":
    # Demo text — something with repeating patterns to show compression
    sample_text = """The quick brown fox jumps over the lazy dog.
The quick brown fox jumps over the lazy dog.
Huffman coding is a lossless data compression algorithm.
It assigns variable-length codes to characters based on frequency."""

    print("=" * 60)
    print("HUFFMAN TEXT COMPRESSOR")
    print("=" * 60)
    print(f"\nOriginal text ({len(sample_text)} chars):")
    print(f'"{sample_text[:80]}..."' if len(sample_text) > 80 else f'"{sample_text}"')
    
    # Build frequency table
    freq_table = build_frequency_table(sample_text)
    print(f"\nUnique characters: {len(freq_table)}")
    
    # Build Huffman tree
    tree_root = build_huffman_tree(freq_table)
    
    # Generate codes
    huffman_codes = generate_codes(tree_root)
    print_code_table(huffman_codes)
    
    # Encode the text
    encoded_bits = encode_text(sample_text, huffman_codes)
    print(f"\nEncoded bitstring ({len(encoded_bits)} bits):")
    print(f"{encoded_bits[:80]}..." if len(encoded_bits) > 80 else encoded_bits)
    
    # Decode back to verify correctness
    decoded_text = decode_text(encoded_bits, tree_root)
    print(f"\nDecoded text matches original: {decoded_text == sample_text}")
    
    # Show compression stats
    ratio = calculate_compression_ratio(sample_text, encoded_bits)
    original_size = len(sample_text) * 8
    compressed_size = len(encoded_bits)
    
    print(f"\n{'Compression Statistics':^40}")
    print("-" * 40)
    print(f"  Original size:     {original_size:6} bits")
    print(f"  Compressed size:   {compressed_size:6} bits")
    print(f"  Compression ratio: {ratio:6.2f}%")
    print(f"  Space saved:       {original_size - compressed_size:6} bits")
    print("=" * 60)