"""
Date: 2026-08-31
Implemented Huffman encoding to see how much I could compress text files — builds the tree, generates codes, and can decode back to original.
"""

#!/usr/bin/env python3
"""
Huffman coding implementation for text compression.
Builds a binary tree based on character frequency, then encodes text
using variable-length codes (common chars get shorter codes).
"""

import heapq
from collections import Counter, defaultdict


class HuffmanNode:
    """
    Node in the Huffman tree. Can be a leaf (with a character) or internal node.
    Using __lt__ for heap comparison since heapq needs to compare nodes.
    """
    def __init__(self, char, freq, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        # Heap should prioritize lower frequencies
        return self.freq < other.freq
    
    def is_leaf(self):
        """Check if this node is a leaf (has a character)."""
        return self.left is None and self.right is None


class HuffmanCompressor:
    """
    Encodes and decodes text using Huffman coding.
    The encoding table is built from character frequencies in the input.
    """
    
    def __init__(self):
        self.root = None
        self.encoding_table = {}
        self.decoding_table = {}
    
    def _build_tree(self, text):
        """
        Build the Huffman tree from character frequencies.
        Uses a min-heap to always combine the two least frequent nodes.
        """
        # Count character frequencies
        freq_map = Counter(text)
        
        # Edge case: single unique character
        if len(freq_map) == 1:
            char = list(freq_map.keys())[0]
            self.root = HuffmanNode(char, freq_map[char])
            return
        
        # Create a min-heap of nodes
        heap = [HuffmanNode(char, freq) for char, freq in freq_map.items()]
        heapq.heapify(heap)
        
        # Combine nodes until we have a single tree
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            
            # Create parent node with combined frequency
            merged = HuffmanNode(None, left.freq + right.freq, left, right)
            heapq.heappush(heap, merged)
        
        self.root = heap[0]
    
    def _generate_codes(self, node=None, current_code=""):
        """
        Recursively traverse the tree to generate binary codes for each character.
        Left = 0, Right = 1. This is why frequent chars end up with shorter codes.
        """
        if node is None:
            node = self.root
        
        # Special case: single character
        if node.is_leaf():
            # Give it a code of "0" to avoid empty codes
            self.encoding_table[node.char] = current_code if current_code else "0"
            self.decoding_table[current_code if current_code else "0"] = node.char
            return
        
        # Traverse left (add '0') and right (add '1')
        if node.left:
            self._generate_codes(node.left, current_code + "0")
        if node.right:
            self._generate_codes(node.right, current_code + "1")
    
    def encode(self, text):
        """
        Encode text to a binary string using Huffman codes.
        Returns the encoded binary string and the encoding table for reference.
        """
        if not text:
            return "", {}
        
        # Build tree and generate codes
        self._build_tree(text)
        self._generate_codes()
        
        # Encode the text
        encoded = "".join(self.encoding_table[char] for char in text)
        
        return encoded, self.encoding_table
    
    def decode(self, encoded_text):
        """
        Decode a binary string back to original text using the Huffman tree.
        Traverses the tree bit by bit until reaching a leaf node.
        """
        if not encoded_text or not self.root:
            return ""
        
        decoded = []
        current_node = self.root
        
        # Special case: single character tree
        if current_node.is_leaf():
            return current_node.char * len(encoded_text)
        
        # Traverse tree following the binary code
        for bit in encoded_text:
            if bit == "0":
                current_node = current_node.left
            else:
                current_node = current_node.right
            
            # Found a character
            if current_node.is_leaf():
                decoded.append(current_node.char)
                current_node = self.root  # Reset to root for next character
        
        return "".join(decoded)


def calculate_compression_ratio(original, encoded_bits):
    """Calculate how much space we saved (or didn't)."""
    # Original text in bits (assuming 8 bits per character)
    original_bits = len(original) * 8
    compression_ratio = (1 - encoded_bits / original_bits) * 100 if original_bits > 0 else 0
    return compression_ratio


if __name__ == "__main__":
    # Demo with a sample text that has varied character frequencies
    sample_text = "this is an example of huffman encoding in action! the letter 'e' appears often."
    
    print("=== Huffman Compression Demo ===\n")
    print(f"Original text ({len(sample_text)} chars):")
    print(f'"{sample_text}"\n')
    
    # Create compressor and encode
    compressor = HuffmanCompressor()
    encoded, code_table = compressor.encode(sample_text)
    
    print("Huffman Codes (sorted by code length):")
    sorted_codes = sorted(code_table.items(), key=lambda x: (len(x[1]), x[1]))
    for char, code in sorted_codes:
        display_char = repr(char) if char in [' ', '\n', '\t'] else char
        print(f"  {display_char}: {code}")
    
    print(f"\nEncoded binary ({len(encoded)} bits):")
    print(f"{encoded[:80]}..." if len(encoded) > 80 else encoded)
    
    # Decode it back
    decoded = compressor.decode(encoded)
    print(f"\nDecoded text ({len(decoded)} chars):")
    print(f'"{decoded}"')
    
    # Show compression stats
    original_bits = len(sample_text) * 8
    compression = calculate_compression_ratio(sample_text, len(encoded))
    
    print(f"\n=== Compression Stats ===")
    print(f"Original size: {original_bits} bits ({len(sample_text)} chars × 8)")
    print(f"Compressed size: {len(encoded)} bits")
    print(f"Compression ratio: {compression:.2f}% reduction")
    print(f"Matches original: {decoded == sample_text}")