"""
Date: 2026-08-31
Implemented Huffman coding to compress text files — wanted to see how much space I could actually save on repetitive data.
"""

#!/usr/bin/env python3
"""
Huffman coding implementation for text compression.
Uses a priority queue and binary tree to build optimal prefix codes.
"""

import heapq
from collections import Counter, defaultdict


class HuffmanNode:
    """
    Represents a node in the Huffman tree.
    Uses __lt__ for heap ordering since heapq needs to compare nodes.
    """
    def __init__(self, char, freq, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        # Priority queue needs this to compare nodes by frequency
        return self.freq < other.freq
    
    def is_leaf(self):
        """Check if this node is a leaf (contains an actual character)."""
        return self.left is None and self.right is None


def build_frequency_table(text):
    """
    Count character frequencies in the input text.
    Returns a Counter object mapping chars to their counts.
    """
    return Counter(text)


def build_huffman_tree(freq_table):
    """
    Construct the Huffman tree using a min-heap.
    Repeatedly merges the two lowest-frequency nodes until one tree remains.
    """
    if not freq_table:
        return None
    
    # Initialize heap with leaf nodes for each character
    heap = [HuffmanNode(char, freq) for char, freq in freq_table.items()]
    heapq.heapify(heap)
    
    # Edge case: single character input needs at least one bit
    if len(heap) == 1:
        single_node = heapq.heappop(heap)
        return HuffmanNode(None, single_node.freq, single_node, None)
    
    # Build tree by merging nodes
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        
        # Create internal node with combined frequency
        merged = HuffmanNode(None, left.freq + right.freq, left, right)
        heapq.heappush(heap, merged)
    
    return heap[0]


def generate_codes(root):
    """
    Traverse the Huffman tree to generate binary codes for each character.
    Left edges = '0', right edges = '1'.
    Returns a dict mapping characters to their binary code strings.
    """
    if root is None:
        return {}
    
    codes = {}
    
    def traverse(node, current_code):
        if node.is_leaf():
            # Leaf node: assign the accumulated code to this character
            codes[node.char] = current_code if current_code else '0'
            return
        
        if node.left:
            traverse(node.left, current_code + '0')
        if node.right:
            traverse(node.right, current_code + '1')
    
    traverse(root, '')
    return codes


def compress(text):
    """
    Compress text using Huffman coding.
    Returns a tuple of (encoded_bits, huffman_codes, original_length).
    """
    if not text:
        return '', {}, 0
    
    freq_table = build_frequency_table(text)
    tree = build_huffman_tree(freq_table)
    codes = generate_codes(tree)
    
    # Encode the text by replacing each char with its Huffman code
    encoded = ''.join(codes[char] for char in text)
    
    return encoded, codes, len(text)


def decompress(encoded_bits, codes):
    """
    Decompress Huffman-encoded bits back to original text.
    Builds a reverse lookup from codes to characters.
    """
    if not encoded_bits:
        return ''
    
    # Reverse the code table for decoding
    reverse_codes = {code: char for char, code in codes.items()}
    
    decoded = []
    current_code = ''
    
    for bit in encoded_bits:
        current_code += bit
        if current_code in reverse_codes:
            decoded.append(reverse_codes[current_code])
            current_code = ''
    
    return ''.join(decoded)


def calculate_compression_ratio(original_text, encoded_bits):
    """
    Calculate how much space we saved.
    ASCII uses 8 bits per character, Huffman uses variable length.
    """
    original_bits = len(original_text) * 8
    compressed_bits = len(encoded_bits)
    
    if original_bits == 0:
        return 0.0
    
    ratio = (1 - compressed_bits / original_bits) * 100
    return ratio


if __name__ == "__main__":
    # Demo with some sample text that has good repetition for compression
    sample_text = "hello huffman! huffman coding is really cool. " \
                  "compression works best with repeated patterns. " \
                  "huffman huffman huffman!"
    
    print("=" * 60)
    print("HUFFMAN CODING DEMO")
    print("=" * 60)
    print(f"\nOriginal text ({len(sample_text)} chars):")
    print(f'"{sample_text}"')
    
    # Compress the text
    encoded, codes, orig_len = compress(sample_text)
    
    print("\n" + "-" * 60)
    print("Huffman Codes Generated:")
    print("-" * 60)
    # Sort by frequency for nicer display
    freq = build_frequency_table(sample_text)
    for char, code in sorted(codes.items(), key=lambda x: freq[x[0]], reverse=True):
        display_char = repr(char) if char in [' ', '\n', '\t'] else char
        print(f"  {display_char:5} (×{freq[char]:2}) → {code}")
    
    print("\n" + "-" * 60)
    print("Compression Results:")
    print("-" * 60)
    print(f"Original size:    {len(sample_text) * 8} bits ({len(sample_text)} chars × 8 bits)")
    print(f"Compressed size:  {len(encoded)} bits")
    ratio = calculate_compression_ratio(sample_text, encoded)
    print(f"Compression ratio: {ratio:.2f}% reduction")
    
    print(f"\nEncoded (first 100 bits): {encoded[:100]}...")
    
    # Decompress to verify correctness
    decompressed = decompress(encoded, codes)
    
    print("\n" + "-" * 60)
    print("Verification:")
    print("-" * 60)
    print(f"Decompressed text matches original: {decompressed == sample_text}")
    print(f'Decompressed: "{decompressed}"')
    print("\n" + "=" * 60)