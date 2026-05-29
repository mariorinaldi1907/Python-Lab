"""
Date: 2026-05-29
Implemented Huffman coding to compress text by building optimal prefix-free binary trees — included a visual tree printer because I wanted to see the structure.
"""

#!/usr/bin/env python3
"""
Huffman coding implementation for text compression.
Uses frequency-based binary tree construction to create optimal prefix codes.
"""

import heapq
from collections import Counter, defaultdict
from typing import Dict, Optional, Tuple


class HuffmanNode:
    """
    Node in the Huffman tree. Can be a leaf (with a character) or internal node.
    """
    def __init__(self, char: Optional[str], freq: int, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    
    # Heap comparison based on frequency
    def __lt__(self, other):
        return self.freq < other.freq


class HuffmanCompressor:
    """
    Compresses and decompresses text using Huffman coding.
    Builds a frequency-based binary tree and generates prefix-free codes.
    """
    
    def __init__(self):
        self.root = None
        self.codes = {}  # Maps char -> binary code string
        self.reverse_codes = {}  # Maps binary code -> char
    
    def _build_tree(self, text: str) -> HuffmanNode:
        """
        Build the Huffman tree from character frequencies.
        Uses a min-heap to always merge the two least frequent nodes.
        """
        if not text:
            return None
        
        # Count character frequencies
        freq_map = Counter(text)
        
        # Edge case: single unique character
        if len(freq_map) == 1:
            char, freq = list(freq_map.items())[0]
            return HuffmanNode(char, freq)
        
        # Create a min-heap of leaf nodes
        heap = [HuffmanNode(char, freq) for char, freq in freq_map.items()]
        heapq.heapify(heap)
        
        # Build tree by repeatedly merging two smallest nodes
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            
            # Create internal node with combined frequency
            merged = HuffmanNode(None, left.freq + right.freq, left, right)
            heapq.heappush(heap, merged)
        
        return heap[0]
    
    def _generate_codes(self, node: HuffmanNode, current_code: str = ""):
        """
        Traverse tree to generate binary codes for each character.
        Left = 0, Right = 1. Leaf nodes hold the actual characters.
        """
        if node is None:
            return
        
        # Leaf node - save the code
        if node.char is not None:
            # Handle single-character edge case
            self.codes[node.char] = current_code if current_code else "0"
            return
        
        # Traverse left and right
        self._generate_codes(node.left, current_code + "0")
        self._generate_codes(node.right, current_code + "1")
    
    def encode(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Encode text into binary string using Huffman coding.
        Returns the encoded binary string and the codebook for decoding.
        """
        if not text:
            return "", {}
        
        # Build tree and generate codes
        self.root = self._build_tree(text)
        self.codes = {}
        self._generate_codes(self.root)
        
        # Encode the text
        encoded = "".join(self.codes[char] for char in text)
        return encoded, self.codes
    
    def decode(self, encoded: str, codes: Dict[str, str]) -> str:
        """
        Decode binary string back to original text using the codebook.
        Builds reverse mapping and traverses bit by bit.
        """
        if not encoded or not codes:
            return ""
        
        # Build reverse lookup
        self.reverse_codes = {code: char for char, code in codes.items()}
        
        # Decode bit by bit
        decoded = []
        current_code = ""
        
        for bit in encoded:
            current_code += bit
            if current_code in self.reverse_codes:
                decoded.append(self.reverse_codes[current_code])
                current_code = ""
        
        return "".join(decoded)
    
    def print_tree(self, node: HuffmanNode = None, prefix: str = "", is_left: bool = True):
        """
        Pretty print the Huffman tree structure.
        Useful for visualizing how the encoding works.
        """
        if node is None:
            node = self.root
        
        if node is None:
            return
        
        print(prefix + ("|-- " if is_left else "`-- ") + 
              (f"'{node.char}' ({node.freq})" if node.char else f"* ({node.freq})"))
        
        if node.left or node.right:
            if node.left:
                self.print_tree(node.left, prefix + ("|   " if is_left else "    "), True)
            if node.right:
                self.print_tree(node.right, prefix + ("|   " if is_left else "    "), False)


def calculate_compression_ratio(original: str, encoded: str) -> float:
    """
    Calculate compression ratio. Original uses 8 bits per char (ASCII).
    """
    original_bits = len(original) * 8
    encoded_bits = len(encoded)
    return (1 - encoded_bits / original_bits) * 100 if original_bits > 0 else 0


if __name__ == "__main__":
    # Demo with a sample text
    sample_text = "hello world! this is a huffman coding example. compression works best with repeated characters!!!"
    
    print("=" * 70)
    print("HUFFMAN CODING COMPRESSION DEMO")
    print("=" * 70)
    print(f"\nOriginal text ({len(sample_text)} chars):")
    print(f'"{sample_text}"')
    
    # Compress
    compressor = HuffmanCompressor()
    encoded_bits, codebook = compressor.encode(sample_text)
    
    print(f"\n--- Codebook ---")
    # Sort by code length for readability
    for char, code in sorted(codebook.items(), key=lambda x: (len(x[1]), x[0])):
        print(f"  '{char}' -> {code}")
    
    print(f"\n--- Huffman Tree Structure ---")
    compressor.print_tree()
    
    print(f"\n--- Compression Stats ---")
    print(f"Original size: {len(sample_text) * 8} bits ({len(sample_text)} chars × 8 bits)")
    print(f"Compressed size: {len(encoded_bits)} bits")
    compression_ratio = calculate_compression_ratio(sample_text, encoded_bits)
    print(f"Compression ratio: {compression_ratio:.2f}% reduction")
    
    print(f"\nEncoded (first 100 bits): {encoded_bits[:100]}...")
    
    # Decompress
    decoded_text = compressor.decode(encoded_bits, codebook)
    
    print(f"\n--- Decompression ---")
    print(f'Decoded text: "{decoded_text}"')
    print(f"Match: {decoded_text == sample_text}")
    print("=" * 70)