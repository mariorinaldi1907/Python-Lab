"""
Date: 2026-05-28
Implemented Huffman encoding to compress text by building frequency trees and generating variable-length codes — wanted to see real compression ratios on sample strings.
"""

#!/usr/bin/env python3
"""
Huffman coding implementation for text compression.
Builds a frequency tree, generates optimal variable-length codes,
and can encode/decode text strings.
"""

import heapq
from collections import Counter, defaultdict


class HuffmanNode:
    """
    Node for the Huffman tree. Can be a leaf (with a character) or internal node.
    """
    def __init__(self, char, freq, left=None, right=None):
        self.char = char  # None for internal nodes
        self.freq = freq
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        # Needed for heapq to compare nodes by frequency
        return self.freq < other.freq


class HuffmanCompressor:
    """
    Handles encoding and decoding of text using Huffman coding.
    Builds the tree once, then can compress/decompress multiple times.
    """
    
    def __init__(self, text):
        """
        Initialize with sample text to build the frequency tree.
        """
        self.text = text
        self.root = None
        self.codes = {}  # char -> binary code string
        self.reverse_codes = {}  # binary code string -> char
        
        # Build the tree immediately
        self._build_tree()
        self._generate_codes()
    
    def _build_tree(self):
        """
        Build the Huffman tree using a min-heap based on character frequencies.
        """
        if not self.text:
            return
        
        # Count character frequencies
        freq_map = Counter(self.text)
        
        # Edge case: single unique character
        if len(freq_map) == 1:
            char = list(freq_map.keys())[0]
            self.root = HuffmanNode(char, freq_map[char])
            return
        
        # Create a min-heap of nodes
        heap = [HuffmanNode(char, freq) for char, freq in freq_map.items()]
        heapq.heapify(heap)
        
        # Build tree by repeatedly combining two smallest nodes
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            
            # Create parent node with combined frequency
            parent = HuffmanNode(None, left.freq + right.freq, left, right)
            heapq.heappush(heap, parent)
        
        self.root = heap[0]
    
    def _generate_codes(self):
        """
        Traverse the tree to generate binary codes for each character.
        Left = 0, Right = 1 by convention.
        """
        if not self.root:
            return
        
        # Edge case: single character
        if self.root.char is not None:
            self.codes[self.root.char] = "0"
            self.reverse_codes["0"] = self.root.char
            return
        
        def traverse(node, code):
            if node.char is not None:
                # Leaf node
                self.codes[node.char] = code
                self.reverse_codes[code] = node.char
                return
            
            if node.left:
                traverse(node.left, code + "0")
            if node.right:
                traverse(node.right, code + "1")
        
        traverse(self.root, "")
    
    def encode(self, text):
        """
        Encode text into a binary string using the Huffman codes.
        Returns the compressed binary string.
        """
        if not self.codes:
            return ""
        
        encoded = "".join(self.codes[char] for char in text)
        return encoded
    
    def decode(self, binary_string):
        """
        Decode a binary string back to original text using the tree.
        """
        if not self.root or not binary_string:
            return ""
        
        # Edge case: single character tree
        if self.root.char is not None:
            return self.root.char * len(binary_string)
        
        decoded = []
        current = self.root
        
        for bit in binary_string:
            # Traverse tree based on bit value
            if bit == "0":
                current = current.left
            else:
                current = current.right
            
            # If we hit a leaf, record the character and reset
            if current.char is not None:
                decoded.append(current.char)
                current = self.root
        
        return "".join(decoded)
    
    def get_compression_stats(self, text):
        """
        Calculate compression statistics for given text.
        Returns original size, compressed size, and compression ratio.
        """
        encoded = self.encode(text)
        original_bits = len(text) * 8  # 8 bits per character (ASCII)
        compressed_bits = len(encoded)
        ratio = (1 - compressed_bits / original_bits) * 100 if original_bits > 0 else 0
        
        return original_bits, compressed_bits, ratio


if __name__ == "__main__":
    # Demo with a sample text that should compress well
    sample_text = "mississippi river flows through mississippi state"
    
    print("=== Huffman Coding Compression Demo ===\n")
    print(f"Original text: '{sample_text}'")
    print(f"Length: {len(sample_text)} characters\n")
    
    # Build compressor
    compressor = HuffmanCompressor(sample_text)
    
    # Show the generated codes
    print("Generated Huffman Codes:")
    for char, code in sorted(compressor.codes.items()):
        display_char = char if char != ' ' else '(space)'
        print(f"  '{display_char}': {code}")
    
    # Encode the text
    encoded = compressor.encode(sample_text)
    print(f"\nEncoded binary (first 80 chars): {encoded[:80]}...")
    
    # Decode it back
    decoded = compressor.decode(encoded)
    print(f"\nDecoded text: '{decoded}'")
    print(f"Match original: {decoded == sample_text}")
    
    # Show compression stats
    orig_bits, comp_bits, ratio = compressor.get_compression_stats(sample_text)
    print(f"\nCompression Stats:")
    print(f"  Original size: {orig_bits} bits ({orig_bits // 8} bytes)")
    print(f"  Compressed size: {comp_bits} bits ({comp_bits // 8} bytes)")
    print(f"  Compression ratio: {ratio:.2f}% reduction")
    
    # Try another string
    print("\n--- Testing with another string ---")
    test_text = "aaaaabbbbbcccccddddddeeeee"
    encoded2 = compressor.encode(test_text)
    decoded2 = compressor.decode(encoded2)
    orig2, comp2, ratio2 = compressor.get_compression_stats(test_text)
    print(f"Text: '{test_text}'")
    print(f"Compression: {ratio2:.2f}% reduction ({orig2} -> {comp2} bits)")
    print(f"Decode successful: {decoded2 == test_text}")