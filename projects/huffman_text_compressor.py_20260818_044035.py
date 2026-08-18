"""
Date: 2026-08-18
Built a Huffman encoder/decoder to compress text files — wanted to see actual compression ratios on real data.
"""

import heapq
from collections import Counter, defaultdict
from typing import Dict, Optional, Tuple


class HuffmanNode:
    """
    Node for building the Huffman tree.
    Uses __lt__ for heap comparison since heapq needs it.
    """
    def __init__(self, char: Optional[str], freq: int, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        # Heap will pop smallest frequency first
        return self.freq < other.freq


class HuffmanCompressor:
    """
    Compresses and decompresses text using Huffman coding.
    Builds a frequency-based binary tree and generates optimal prefix codes.
    """
    
    def __init__(self):
        self.codes: Dict[str, str] = {}
        self.reverse_codes: Dict[str, str] = {}
        self.root: Optional[HuffmanNode] = None
    
    def _build_tree(self, text: str) -> HuffmanNode:
        """
        Construct the Huffman tree from character frequencies.
        Returns the root node of the tree.
        """
        if not text:
            raise ValueError("Cannot compress empty text")
        
        # Count character frequencies
        freq_map = Counter(text)
        
        # Edge case: single unique character
        if len(freq_map) == 1:
            char = list(freq_map.keys())[0]
            return HuffmanNode(char, freq_map[char])
        
        # Build initial heap with leaf nodes
        heap = [HuffmanNode(char, freq) for char, freq in freq_map.items()]
        heapq.heapify(heap)
        
        # Merge nodes until we have one tree
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            
            # Create internal node with combined frequency
            merged = HuffmanNode(None, left.freq + right.freq, left, right)
            heapq.heappush(heap, merged)
        
        return heap[0]
    
    def _generate_codes(self, node: Optional[HuffmanNode], current_code: str = ""):
        """
        Recursively traverse the tree to generate binary codes for each character.
        Left branch = 0, right branch = 1.
        """
        if node is None:
            return
        
        # Leaf node — we found a character
        if node.char is not None:
            # Handle single-character edge case
            code = current_code if current_code else "0"
            self.codes[node.char] = code
            self.reverse_codes[code] = node.char
            return
        
        # Traverse left and right
        self._generate_codes(node.left, current_code + "0")
        self._generate_codes(node.right, current_code + "1")
    
    def compress(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Compress the input text using Huffman coding.
        Returns the encoded binary string and the code table.
        """
        self.root = self._build_tree(text)
        self._generate_codes(self.root)
        
        # Encode the text
        encoded = "".join(self.codes[char] for char in text)
        
        return encoded, self.codes
    
    def decompress(self, encoded: str, codes: Dict[str, str]) -> str:
        """
        Decompress a Huffman-encoded binary string back to original text.
        Uses the code table to decode.
        """
        # Build reverse mapping if not already built
        reverse = {code: char for char, code in codes.items()}
        
        decoded = []
        current_code = ""
        
        for bit in encoded:
            current_code += bit
            if current_code in reverse:
                decoded.append(reverse[current_code])
                current_code = ""
        
        return "".join(decoded)
    
    def get_compression_stats(self, original: str, encoded: str) -> dict:
        """
        Calculate compression statistics.
        Returns a dict with original size, compressed size, and ratio.
        """
        # Original size in bits (assuming 8-bit ASCII)
        original_bits = len(original) * 8
        compressed_bits = len(encoded)
        
        return {
            "original_bits": original_bits,
            "compressed_bits": compressed_bits,
            "compression_ratio": original_bits / compressed_bits if compressed_bits > 0 else 0,
            "space_saved_percent": ((original_bits - compressed_bits) / original_bits * 100) if original_bits > 0 else 0
        }


if __name__ == "__main__":
    # Demo with a sample text that should compress well (lots of repetition)
    sample_text = "hello world! this is a test of huffman coding. hello hello!"
    
    print("=" * 60)
    print("HUFFMAN COMPRESSION DEMO")
    print("=" * 60)
    print(f"\nOriginal text ({len(sample_text)} chars):")
    print(f'"{sample_text}"')
    
    # Compress
    compressor = HuffmanCompressor()
    encoded, code_table = compressor.compress(sample_text)
    
    print("\n" + "-" * 60)
    print("Huffman Code Table:")
    print("-" * 60)
    # Sort by frequency for readability
    char_freqs = Counter(sample_text)
    for char, code in sorted(code_table.items(), key=lambda x: char_freqs[x[0]], reverse=True):
        display_char = repr(char) if char in [' ', '\n', '\t'] else char
        print(f"  {display_char:>6} (freq: {char_freqs[char]:2d}) -> {code}")
    
    print("\n" + "-" * 60)
    print(f"Encoded binary ({len(encoded)} bits):")
    print("-" * 60)
    # Print in chunks for readability
    chunk_size = 64
    for i in range(0, len(encoded), chunk_size):
        print(f"  {encoded[i:i+chunk_size]}")
    
    # Decompress to verify
    decoded = compressor.decompress(encoded, code_table)
    
    print("\n" + "-" * 60)
    print("Decompressed text:")
    print("-" * 60)
    print(f'"{decoded}"')
    
    # Stats
    stats = compressor.get_compression_stats(sample_text, encoded)
    
    print("\n" + "=" * 60)
    print("COMPRESSION STATISTICS")
    print("=" * 60)
    print(f"Original size:     {stats['original_bits']:5d} bits ({len(sample_text)} chars × 8 bits)")
    print(f"Compressed size:   {stats['compressed_bits']:5d} bits")
    print(f"Compression ratio: {stats['compression_ratio']:.2f}x")
    print(f"Space saved:       {stats['space_saved_percent']:.1f}%")
    
    # Verify correctness
    print("\n" + "=" * 60)
    verification = "✓ PASS" if decoded == sample_text else "✗ FAIL"
    print(f"Decompression verification: {verification}")
    print("=" * 60)