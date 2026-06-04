"""
Date: 2026-06-04
Built a Huffman encoder/decoder to see how compression really works under the hood — frequency analysis, tree building, and binary encoding all in standard lib.
"""

#!/usr/bin/env python3
"""
Huffman Coding Implementation
Compresses text by assigning shorter codes to more frequent characters.
"""

import heapq
from collections import Counter, defaultdict
from typing import Dict, Optional, Tuple


class HuffmanNode:
    """
    Node in the Huffman tree. I'm using comparison operators for the heap.
    """
    def __init__(self, char: Optional[str], freq: int, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        # Needed for heapq to compare nodes by frequency
        return self.freq < other.freq


class HuffmanCompressor:
    """
    Encodes and decodes text using Huffman coding.
    Builds a frequency-based binary tree and generates optimal prefix codes.
    """
    
    def __init__(self):
        self.codes: Dict[str, str] = {}
        self.reverse_codes: Dict[str, str] = {}
        self.root: Optional[HuffmanNode] = None
    
    def _build_frequency_table(self, text: str) -> Dict[str, int]:
        """Count character occurrences in the text."""
        return dict(Counter(text))
    
    def _build_huffman_tree(self, freq_table: Dict[str, int]) -> HuffmanNode:
        """
        Build the tree bottom-up using a min-heap.
        Characters with lower frequency end up deeper in the tree.
        """
        heap = []
        
        # Start with leaf nodes for each character
        for char, freq in freq_table.items():
            node = HuffmanNode(char, freq)
            heapq.heappush(heap, node)
        
        # Merge nodes until we have a single root
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            
            # Internal node has no character, just combined frequency
            merged = HuffmanNode(None, left.freq + right.freq, left, right)
            heapq.heappush(heap, merged)
        
        return heap[0]
    
    def _generate_codes(self, node: Optional[HuffmanNode], current_code: str = ""):
        """
        Traverse the tree to generate binary codes for each character.
        Left = 0, Right = 1. This is a recursive DFS.
        """
        if node is None:
            return
        
        # Leaf node - we found a character
        if node.char is not None:
            # Edge case: single character input gets code "0"
            self.codes[node.char] = current_code if current_code else "0"
            self.reverse_codes[current_code if current_code else "0"] = node.char
            return
        
        # Traverse left and right subtrees
        self._generate_codes(node.left, current_code + "0")
        self._generate_codes(node.right, current_code + "1")
    
    def compress(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Compress the input text and return the encoded bitstring and code table.
        Returns both so we can decode later (need the tree/codes to decompress).
        """
        if not text:
            return "", {}
        
        # Build the tree and generate codes
        freq_table = self._build_frequency_table(text)
        self.root = self._build_huffman_tree(freq_table)
        self._generate_codes(self.root)
        
        # Encode the text using the generated codes
        encoded = "".join(self.codes[char] for char in text)
        
        return encoded, self.codes
    
    def decompress(self, encoded: str, codes: Dict[str, str]) -> str:
        """
        Decode a bitstring back to original text using the code table.
        I'm rebuilding the reverse mapping for decoding.
        """
        if not encoded:
            return ""
        
        # Build reverse lookup
        reverse = {code: char for char, code in codes.items()}
        
        decoded = []
        current_code = ""
        
        # Read bits one at a time until we match a code
        for bit in encoded:
            current_code += bit
            if current_code in reverse:
                decoded.append(reverse[current_code])
                current_code = ""
        
        return "".join(decoded)


def calculate_compression_ratio(original: str, encoded: str) -> float:
    """
    Calculate how much space we saved.
    Original is in ASCII (8 bits/char), encoded is actual bit length.
    """
    original_bits = len(original) * 8
    encoded_bits = len(encoded)
    
    if original_bits == 0:
        return 0.0
    
    return (1 - encoded_bits / original_bits) * 100


if __name__ == "__main__":
    # Demo with a sentence that has clear frequency patterns
    sample_text = "hello huffman! huffman coding is really cool and efficient."
    
    print("=" * 60)
    print("HUFFMAN CODING DEMO")
    print("=" * 60)
    print(f"\nOriginal text ({len(sample_text)} chars):")
    print(f'"{sample_text}"')
    
    # Compress
    compressor = HuffmanCompressor()
    encoded_bits, code_table = compressor.compress(sample_text)
    
    print(f"\nCharacter codes generated:")
    # Sort by frequency (code length) for readability
    for char, code in sorted(code_table.items(), key=lambda x: len(x[1])):
        display_char = char if char != ' ' else '<space>'
        print(f"  '{display_char}' -> {code}")
    
    print(f"\nEncoded bitstring ({len(encoded_bits)} bits):")
    print(f"{encoded_bits[:80]}..." if len(encoded_bits) > 80 else encoded_bits)
    
    # Calculate savings
    compression_pct = calculate_compression_ratio(sample_text, encoded_bits)
    print(f"\nCompression: {compression_pct:.1f}% reduction")
    print(f"  Original: {len(sample_text) * 8} bits (8 bits/char)")
    print(f"  Encoded:  {len(encoded_bits)} bits")
    
    # Decompress to verify it works
    decoded_text = compressor.decompress(encoded_bits, code_table)
    print(f"\nDecoded text:")
    print(f'"{decoded_text}"')
    
    print(f"\nVerification: {'✓ PASS' if decoded_text == sample_text else '✗ FAIL'}")