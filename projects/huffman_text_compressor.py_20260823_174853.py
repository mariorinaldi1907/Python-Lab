"""
Date: 2026-08-23
Implemented Huffman coding to actually see how much text compresses — builds the tree, encodes/decodes, and shows compression ratio.
"""

#!/usr/bin/env python3
"""
Huffman text compression utility.

This is a classic variable-length encoding where frequent characters get
shorter bit codes. I wanted to see the compression in action on real text.
"""

import heapq
from collections import Counter, defaultdict
from typing import Dict, Optional


class HuffmanNode:
    """
    Node in the Huffman tree.
    
    Using __lt__ so heapq can compare nodes by frequency without ties breaking
    on the actual character (which would fail for branch nodes).
    """
    def __init__(self, char: Optional[str], freq: int, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        return self.freq < other.freq


class HuffmanCoder:
    """
    Encodes and decodes text using Huffman coding.
    
    The encoding table maps characters to binary strings (as str of '0'/'1').
    The tree is used for decoding.
    """
    
    def __init__(self):
        self.root = None
        self.encoding_table: Dict[str, str] = {}
    
    def build_tree(self, text: str):
        """
        Build the Huffman tree from character frequencies.
        
        Standard greedy algorithm: repeatedly merge the two least-frequent nodes
        until we have a single root.
        """
        if not text:
            return
        
        # Count character frequencies
        freq_map = Counter(text)
        
        # Edge case: single unique character
        if len(freq_map) == 1:
            char = list(freq_map.keys())[0]
            # Give it a single-bit code to avoid empty encoding
            self.root = HuffmanNode(char, freq_map[char])
            self.encoding_table[char] = "0"
            return
        
        # Build priority queue of nodes
        heap = [HuffmanNode(char, freq) for char, freq in freq_map.items()]
        heapq.heapify(heap)
        
        # Merge nodes until one remains
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            merged = HuffmanNode(None, left.freq + right.freq, left, right)
            heapq.heappush(heap, merged)
        
        self.root = heap[0]
        self._build_encoding_table(self.root, "")
    
    def _build_encoding_table(self, node: HuffmanNode, code: str):
        """
        Recursively traverse tree to build character->code mapping.
        
        Left edges are '0', right edges are '1'.
        """
        if node is None:
            return
        
        # Leaf node - store the encoding
        if node.char is not None:
            self.encoding_table[node.char] = code if code else "0"
            return
        
        self._build_encoding_table(node.left, code + "0")
        self._build_encoding_table(node.right, code + "1")
    
    def encode(self, text: str) -> str:
        """
        Encode text into a binary string using the Huffman codes.
        
        Returns a string of '0' and '1' characters.
        """
        if not self.encoding_table:
            self.build_tree(text)
        
        return "".join(self.encoding_table[char] for char in text)
    
    def decode(self, encoded: str) -> str:
        """
        Decode a binary string back to original text.
        
        Walk the tree: '0' goes left, '1' goes right. When we hit a leaf,
        output that character and restart from root.
        """
        if not self.root or not encoded:
            return ""
        
        # Handle single-character edge case
        if self.root.char is not None:
            return self.root.char * len(encoded)
        
        result = []
        current = self.root
        
        for bit in encoded:
            # Navigate tree based on bit
            current = current.left if bit == "0" else current.right
            
            # Reached a leaf - output character and reset
            if current.char is not None:
                result.append(current.char)
                current = self.root
        
        return "".join(result)
    
    def get_compression_stats(self, original: str, encoded: str) -> dict:
        """
        Calculate compression metrics.
        
        Original size is chars * 8 (assuming ASCII). Encoded size is actual bits.
        """
        original_bits = len(original) * 8
        encoded_bits = len(encoded)
        
        return {
            "original_bits": original_bits,
            "encoded_bits": encoded_bits,
            "compression_ratio": original_bits / encoded_bits if encoded_bits else 0,
            "space_saved_percent": ((original_bits - encoded_bits) / original_bits * 100) if original_bits else 0
        }


if __name__ == "__main__":
    # Test with some sample text - a quote I like
    test_text = "this is an example of a huffman tree built to compress text efficiently"
    
    print("=" * 70)
    print("HUFFMAN CODING DEMONSTRATION")
    print("=" * 70)
    print(f"\nOriginal text ({len(test_text)} chars):")
    print(f'"{test_text}"')
    
    # Create coder and encode
    coder = HuffmanCoder()
    encoded = coder.encode(test_text)
    
    print(f"\nEncoded (binary string, {len(encoded)} bits):")
    print(encoded[:100] + "..." if len(encoded) > 100 else encoded)
    
    # Show the encoding table
    print("\nHuffman code table:")
    sorted_codes = sorted(coder.encoding_table.items(), key=lambda x: len(x[1]))
    for char, code in sorted_codes[:10]:  # Show first 10
        display_char = char if char != ' ' else '(space)'
        print(f"  '{display_char}': {code}")
    if len(sorted_codes) > 10:
        print(f"  ... and {len(sorted_codes) - 10} more")
    
    # Decode to verify
    decoded = coder.decode(encoded)
    print(f"\nDecoded text:")
    print(f'"{decoded}"')
    print(f"\nDecoding successful: {decoded == test_text}")
    
    # Show compression stats
    stats = coder.get_compression_stats(test_text, encoded)
    print(f"\nCompression stats:")
    print(f"  Original: {stats['original_bits']} bits ({len(test_text)} chars × 8)")
    print(f"  Encoded:  {stats['encoded_bits']} bits")
    print(f"  Ratio:    {stats['compression_ratio']:.2f}x")
    print(f"  Saved:    {stats['space_saved_percent']:.1f}%")
    
    print("\n" + "=" * 70)