"""
Date: 2026-07-23
Implemented Huffman encoding/decoding to actually compress text data — wanted to see how much space I could save on repetitive strings.
"""

#!/usr/bin/env env python3
"""
Huffman coding implementation for text compression.
Built this to understand how variable-length encoding actually works under the hood.
"""

import heapq
from collections import Counter, defaultdict
from typing import Dict, Optional


class HuffmanNode:
    """
    Node for building the Huffman tree.
    Using __lt__ so heapq can compare nodes by frequency.
    """
    def __init__(self, char: Optional[str], freq: int, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        return self.freq < other.freq


class HuffmanCompressor:
    """
    Compresses and decompresses text using Huffman coding.
    Builds a frequency-based binary tree and generates variable-length codes.
    """
    
    def __init__(self):
        self.codes: Dict[str, str] = {}
        self.reverse_codes: Dict[str, str] = {}
        self.root: Optional[HuffmanNode] = None
    
    def _build_frequency_table(self, text: str) -> Dict[str, int]:
        """Count how often each character appears — basis for the tree."""
        return dict(Counter(text))
    
    def _build_huffman_tree(self, freq_table: Dict[str, int]) -> HuffmanNode:
        """
        Build the tree bottom-up using a min-heap.
        Characters with lower frequency get pushed deeper (longer codes).
        """
        heap = [HuffmanNode(char, freq) for char, freq in freq_table.items()]
        heapq.heapify(heap)
        
        # Keep merging the two smallest nodes until we have one root
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            merged = HuffmanNode(None, left.freq + right.freq, left, right)
            heapq.heappush(heap, merged)
        
        return heap[0]
    
    def _generate_codes(self, node: Optional[HuffmanNode], current_code: str = ""):
        """
        Traverse the tree to assign binary codes.
        Left = 0, Right = 1. Leaf nodes get the final code.
        """
        if node is None:
            return
        
        # Leaf node — this is an actual character
        if node.char is not None:
            self.codes[node.char] = current_code or "0"  # Handle single-char edge case
            self.reverse_codes[current_code or "0"] = node.char
            return
        
        self._generate_codes(node.left, current_code + "0")
        self._generate_codes(node.right, current_code + "1")
    
    def compress(self, text: str) -> str:
        """
        Compress text into a binary string representation.
        Returns the encoded binary string (as a string of 0s and 1s).
        """
        if not text:
            return ""
        
        freq_table = self._build_frequency_table(text)
        self.root = self._build_huffman_tree(freq_table)
        self._generate_codes(self.root)
        
        # Encode each character using its Huffman code
        compressed = "".join(self.codes[char] for char in text)
        return compressed
    
    def decompress(self, compressed: str) -> str:
        """
        Decode the binary string back to original text.
        Walk the tree bit by bit until we hit a leaf node.
        """
        if not compressed or self.root is None:
            return ""
        
        decoded = []
        current_node = self.root
        
        # Handle edge case where tree is just a single node
        if current_node.char is not None:
            return current_node.char * len(compressed)
        
        for bit in compressed:
            # Navigate the tree based on bit value
            if bit == "0":
                current_node = current_node.left
            else:
                current_node = current_node.right
            
            # Found a character
            if current_node.char is not None:
                decoded.append(current_node.char)
                current_node = self.root  # Reset to root for next character
        
        return "".join(decoded)
    
    def get_compression_ratio(self, original: str, compressed: str) -> float:
        """
        Calculate compression ratio.
        Assuming original is 8 bits per char (ASCII), compressed is actual bit count.
        """
        original_bits = len(original) * 8
        compressed_bits = len(compressed)
        return (1 - compressed_bits / original_bits) * 100 if original_bits > 0 else 0


def demo_compression():
    """Show how the compressor works with a real example."""
    compressor = HuffmanCompressor()
    
    # Using a repetitive string to show decent compression
    test_text = "hello world! this is a test of huffman encoding. hello hello!"
    
    print("=" * 60)
    print("Huffman Compression Demo")
    print("=" * 60)
    print(f"\nOriginal text:\n  '{test_text}'")
    print(f"  Length: {len(test_text)} characters")
    print(f"  Size: {len(test_text) * 8} bits (8 bits/char)")
    
    # Compress
    compressed = compressor.compress(test_text)
    print(f"\nCompressed binary (first 80 chars):\n  {compressed[:80]}...")
    print(f"  Total bits: {len(compressed)}")
    
    # Show the generated codes
    print(f"\nGenerated Huffman codes:")
    sorted_codes = sorted(compressor.codes.items(), key=lambda x: len(x[1]))
    for char, code in sorted_codes[:10]:  # Show first 10 to keep output readable
        display_char = repr(char) if char in '\n\t ' else char
        print(f"    {display_char}: {code}")
    if len(sorted_codes) > 10:
        print(f"    ... ({len(sorted_codes) - 10} more)")
    
    # Decompress to verify
    decompressed = compressor.decompress(compressed)
    print(f"\nDecompressed text:\n  '{decompressed}'")
    
    # Stats
    ratio = compressor.get_compression_ratio(test_text, compressed)
    print(f"\nCompression ratio: {ratio:.2f}% reduction")
    print(f"Match: {decompressed == test_text}")
    print("=" * 60)


if __name__ == "__main__":
    demo_compression()