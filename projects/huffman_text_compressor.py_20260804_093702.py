"""
Date: 2026-08-04
Built a Huffman encoder/decoder to see how much I could compress text without external libraries — pretty satisfying to watch it build the tree.
"""

#!/usr/bin/env python3
"""
Huffman coding implementation for text compression.
Built this to understand how compression actually works under the hood.
"""

import heapq
from collections import Counter, defaultdict


class HuffmanNode:
    """
    Node for the Huffman tree. Uses __lt__ so heapq can compare nodes by frequency.
    """
    def __init__(self, char, freq):
        self.char = char  # None for internal nodes
        self.freq = freq
        self.left = None
        self.right = None
    
    def __lt__(self, other):
        return self.freq < other.freq


class HuffmanEncoder:
    """
    Encodes and decodes text using Huffman coding.
    Builds a frequency-based binary tree and generates variable-length codes.
    """
    
    def __init__(self):
        self.root = None
        self.codes = {}  # char -> binary string
        self.reverse_codes = {}  # binary string -> char
    
    def build_tree(self, text):
        """
        Construct the Huffman tree from character frequencies.
        Uses a min-heap to always merge the two least frequent nodes.
        """
        if not text:
            return None
        
        # Count character frequencies
        freq_map = Counter(text)
        
        # Edge case: single unique character
        if len(freq_map) == 1:
            char = list(freq_map.keys())[0]
            node = HuffmanNode(char, freq_map[char])
            self.root = node
            self.codes[char] = '0'
            self.reverse_codes['0'] = char
            return self.root
        
        # Build heap of leaf nodes
        heap = [HuffmanNode(char, freq) for char, freq in freq_map.items()]
        heapq.heapify(heap)
        
        # Merge nodes until we have a single tree
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            
            merged = HuffmanNode(None, left.freq + right.freq)
            merged.left = left
            merged.right = right
            
            heapq.heappush(heap, merged)
        
        self.root = heap[0]
        return self.root
    
    def generate_codes(self, node=None, current_code=''):
        """
        Recursively traverse the tree to generate binary codes for each character.
        Left = 0, Right = 1
        """
        if node is None:
            node = self.root
        
        if node is None:
            return
        
        # Leaf node - store the code
        if node.char is not None:
            self.codes[node.char] = current_code if current_code else '0'
            self.reverse_codes[current_code if current_code else '0'] = node.char
            return
        
        # Traverse left and right
        self.generate_codes(node.left, current_code + '0')
        self.generate_codes(node.right, current_code + '1')
    
    def encode(self, text):
        """
        Encode text into a binary string using the generated Huffman codes.
        """
        if not text:
            return ''
        
        self.build_tree(text)
        self.generate_codes()
        
        encoded = ''.join(self.codes[char] for char in text)
        return encoded
    
    def decode(self, encoded_text):
        """
        Decode a binary string back to the original text.
        Walks the tree bit by bit until hitting leaf nodes.
        """
        if not encoded_text or self.root is None:
            return ''
        
        decoded = []
        current_node = self.root
        
        # Handle single-character edge case
        if current_node.char is not None:
            return current_node.char * len(encoded_text)
        
        for bit in encoded_text:
            if bit == '0':
                current_node = current_node.left
            else:
                current_node = current_node.right
            
            # Reached a leaf
            if current_node.char is not None:
                decoded.append(current_node.char)
                current_node = self.root
        
        return ''.join(decoded)
    
    def get_compression_ratio(self, original_text, encoded_text):
        """
        Calculate how much space we saved (or didn't).
        Original uses 8 bits per character (ASCII), encoded uses variable length.
        """
        original_bits = len(original_text) * 8
        encoded_bits = len(encoded_text)
        ratio = (1 - encoded_bits / original_bits) * 100 if original_bits > 0 else 0
        return ratio


if __name__ == '__main__':
    # Demo with some actual text
    test_text = "hello world! this is a huffman coding demonstration. compression works best with repeated characters!!!"
    
    print("=== Huffman Coding Demo ===\n")
    print(f"Original text ({len(test_text)} chars):")
    print(f'"{test_text}"\n')
    
    encoder = HuffmanEncoder()
    encoded = encoder.encode(test_text)
    
    print(f"Encoded binary ({len(encoded)} bits):")
    print(f"{encoded[:80]}..." if len(encoded) > 80 else encoded)
    print()
    
    print("Huffman Codes (char -> binary):")
    for char, code in sorted(encoder.codes.items(), key=lambda x: len(x[1])):
        display_char = repr(char) if char in [' ', '\n', '\t'] else char
        print(f"  {display_char}: {code}")
    print()
    
    decoded = encoder.decode(encoded)
    print(f"Decoded text:")
    print(f'"{decoded}"\n')
    
    print(f"Verification: {'✓ PASSED' if decoded == test_text else '✗ FAILED'}")
    
    ratio = encoder.get_compression_ratio(test_text, encoded)
    original_bits = len(test_text) * 8
    print(f"\nCompression stats:")
    print(f"  Original: {original_bits} bits ({len(test_text)} chars × 8 bits)")
    print(f"  Encoded:  {len(encoded)} bits")
    print(f"  Savings:  {ratio:.1f}%")