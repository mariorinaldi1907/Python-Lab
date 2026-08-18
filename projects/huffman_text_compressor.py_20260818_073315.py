"""
Date: 2026-08-18
Implemented Huffman coding to compress text files — encodes character frequencies into variable-length bit patterns and can decode back to original.
"""

"""
Huffman Text Compressor
Simple implementation of Huffman coding for text compression.
I wanted to see how much I could actually compress english text
without using any libraries - just pure Python and bit manipulation.
"""

import heapq
from collections import Counter, namedtuple
import pickle


class HuffmanNode:
    """
    Node in the Huffman tree.
    Using __lt__ so heapq can compare nodes by frequency.
    """
    def __init__(self, char, freq, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        return self.freq < other.freq
    
    def is_leaf(self):
        return self.left is None and self.right is None


def build_frequency_table(text):
    """
    Count character frequencies in the input text.
    Returns a Counter object with char -> count mapping.
    """
    return Counter(text)


def build_huffman_tree(freq_table):
    """
    Build the Huffman tree from character frequencies.
    Uses a min-heap to always merge the two least frequent nodes.
    Returns the root of the tree.
    """
    if not freq_table:
        return None
    
    # Edge case: single character text
    if len(freq_table) == 1:
        char, freq = list(freq_table.items())[0]
        # Create a dummy parent so we have at least one bit for encoding
        return HuffmanNode(None, freq, HuffmanNode(char, freq), None)
    
    # Initialize heap with leaf nodes
    heap = [HuffmanNode(char, freq) for char, freq in freq_table.items()]
    heapq.heapify(heap)
    
    # Keep merging until we have one tree
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(None, left.freq + right.freq, left, right)
        heapq.heappush(heap, merged)
    
    return heap[0]


def build_codes(root):
    """
    Traverse the Huffman tree to build the character -> bitstring mapping.
    Left edges are '0', right edges are '1'.
    """
    if root is None:
        return {}
    
    codes = {}
    
    def traverse(node, current_code):
        if node.is_leaf():
            # Found a character - store its code
            codes[node.char] = current_code if current_code else '0'
            return
        
        if node.left:
            traverse(node.left, current_code + '0')
        if node.right:
            traverse(node.right, current_code + '1')
    
    traverse(root, '')
    return codes


def encode(text, codes):
    """
    Encode text using the Huffman codes.
    Returns a string of '0' and '1' characters.
    """
    return ''.join(codes[char] for char in text)


def decode(encoded_bits, root):
    """
    Decode a bitstring back to text using the Huffman tree.
    Walk the tree based on bits: 0 = left, 1 = right.
    """
    if not encoded_bits or root is None:
        return ''
    
    decoded = []
    current = root
    
    for bit in encoded_bits:
        # Navigate tree
        if bit == '0':
            current = current.left
        else:
            current = current.right
        
        # Reached a leaf - found a character
        if current.is_leaf():
            decoded.append(current.char)
            current = root  # Reset to root for next character
    
    return ''.join(decoded)


def compress(text):
    """
    Complete compression pipeline.
    Returns encoded bitstring and the Huffman tree (needed for decoding).
    """
    freq_table = build_frequency_table(text)
    tree = build_huffman_tree(freq_table)
    codes = build_codes(tree)
    encoded = encode(text, codes)
    return encoded, tree


def calculate_compression_ratio(original_text, encoded_bits):
    """
    Calculate how much space we saved.
    Original is in 8-bit ASCII, encoded is variable-length bits.
    """
    original_bits = len(original_text) * 8
    compressed_bits = len(encoded_bits)
    ratio = (1 - compressed_bits / original_bits) * 100 if original_bits > 0 else 0
    return ratio


if __name__ == "__main__":
    # Demo with some sample text
    sample_text = """
    The Huffman coding algorithm is a greedy algorithm that builds an optimal
    prefix-free binary code. It works by repeatedly merging the two least
    frequent symbols until only one symbol remains. This implementation uses
    a min-heap to efficiently find the minimum frequency nodes at each step.
    """
    
    print("=" * 70)
    print("HUFFMAN TEXT COMPRESSOR")
    print("=" * 70)
    print(f"\nOriginal text ({len(sample_text)} chars):")
    print(sample_text[:100] + "..." if len(sample_text) > 100 else sample_text)
    
    # Compress
    encoded_bits, huffman_tree = compress(sample_text)
    
    print(f"\nEncoded bits ({len(encoded_bits)} bits):")
    print(encoded_bits[:100] + "..." if len(encoded_bits) > 100 else encoded_bits)
    
    # Show some codes
    codes = build_codes(huffman_tree)
    print("\nSample character codes:")
    for char in sorted(set(sample_text))[:10]:
        if char == '\n':
            print(f"  '\\n' -> {codes[char]}")
        elif char == ' ':
            print(f"  ' '  -> {codes[char]}")
        else:
            print(f"  '{char}'  -> {codes[char]}")
    
    # Decode to verify
    decoded_text = decode(encoded_bits, huffman_tree)
    
    print(f"\nDecoded successfully: {decoded_text == sample_text}")
    
    # Stats
    ratio = calculate_compression_ratio(sample_text, encoded_bits)
    print(f"\nCompression ratio: {ratio:.2f}%")
    print(f"Original size: {len(sample_text) * 8} bits")
    print(f"Compressed size: {len(encoded_bits)} bits")
    print("=" * 70)