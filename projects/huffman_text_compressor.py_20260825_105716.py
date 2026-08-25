"""
Date: 2026-08-25
Implemented Huffman coding to compress text files — constructs the tree from character frequencies and packs encoded bits into bytes.
"""

#!/usr/bin/env python3
"""
Huffman text compressor - encodes text using variable-length prefix codes
based on character frequency. More frequent chars get shorter codes.
"""

import heapq
from collections import Counter, defaultdict
from typing import Dict, Optional, Tuple


class HuffmanNode:
    """Node in the Huffman tree. Leafs contain characters, internals just merge frequencies."""
    
    def __init__(self, char: Optional[str], freq: int, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        # For the priority queue - lower frequency = higher priority
        return self.freq < other.freq


class HuffmanCompressor:
    """Builds a Huffman tree and provides encode/decode methods."""
    
    def __init__(self, text: str):
        """Initialize with text and build the encoding tree."""
        self.text = text
        self.root = None
        self.codes: Dict[str, str] = {}
        self.reverse_codes: Dict[str, str] = {}
        
        if text:
            self._build_tree()
            self._generate_codes()
    
    def _build_tree(self):
        """Construct the Huffman tree using a min-heap (priority queue)."""
        # Count character frequencies
        freq_map = Counter(self.text)
        
        # Edge case: single unique character
        if len(freq_map) == 1:
            char = list(freq_map.keys())[0]
            self.root = HuffmanNode(char, freq_map[char])
            return
        
        # Build heap of leaf nodes
        heap = [HuffmanNode(char, freq) for char, freq in freq_map.items()]
        heapq.heapify(heap)
        
        # Merge nodes until we have one root
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            
            # Create internal node with combined frequency
            merged = HuffmanNode(None, left.freq + right.freq, left, right)
            heapq.heappush(heap, merged)
        
        self.root = heap[0]
    
    def _generate_codes(self):
        """Traverse tree to generate binary codes for each character."""
        if not self.root:
            return
        
        # Handle single-character edge case
        if self.root.char is not None:
            self.codes[self.root.char] = "0"
            self.reverse_codes["0"] = self.root.char
            return
        
        def traverse(node, code):
            if node.char is not None:
                # Leaf node - save the code
                self.codes[node.char] = code
                self.reverse_codes[code] = node.char
            else:
                # Internal node - keep traversing
                if node.left:
                    traverse(node.left, code + "0")
                if node.right:
                    traverse(node.right, code + "1")
        
        traverse(self.root, "")
    
    def encode(self) -> Tuple[str, Dict[str, str]]:
        """Encode the text into a binary string. Returns (encoded_bits, codebook)."""
        if not self.text:
            return "", {}
        
        encoded = "".join(self.codes[char] for char in self.text)
        return encoded, self.codes
    
    def decode(self, encoded_bits: str) -> str:
        """Decode a binary string back to text using the Huffman tree."""
        if not encoded_bits or not self.root:
            return ""
        
        # Handle single-character tree
        if self.root.char is not None:
            return self.root.char * len(encoded_bits)
        
        decoded = []
        current = self.root
        
        for bit in encoded_bits:
            # Traverse left on 0, right on 1
            current = current.left if bit == "0" else current.right
            
            if current.char is not None:
                # Hit a leaf - output character and reset to root
                decoded.append(current.char)
                current = self.root
        
        return "".join(decoded)
    
    def compression_ratio(self, encoded_bits: str) -> float:
        """Calculate compression ratio (original / compressed)."""
        original_bits = len(self.text) * 8  # ASCII = 8 bits per char
        compressed_bits = len(encoded_bits)
        return original_bits / compressed_bits if compressed_bits > 0 else 0.0


def pack_bits_to_bytes(bit_string: str) -> bytes:
    """Convert a string of '0' and '1' into actual bytes. Pads to byte boundary."""
    # Pad to multiple of 8
    padding = (8 - len(bit_string) % 8) % 8
    bit_string += "0" * padding
    
    byte_array = bytearray()
    for i in range(0, len(bit_string), 8):
        byte = bit_string[i:i+8]
        byte_array.append(int(byte, 2))
    
    return bytes(byte_array)


if __name__ == "__main__":
    # Demo with a sample text
    sample_text = "huffman coding is a cool compression algorithm that uses frequency analysis"
    
    print("=" * 70)
    print("HUFFMAN TEXT COMPRESSOR")
    print("=" * 70)
    print(f"\nOriginal text ({len(sample_text)} chars):")
    print(f'"{sample_text}"')
    
    # Build compressor
    compressor = HuffmanCompressor(sample_text)
    
    # Encode
    encoded_bits, codebook = compressor.encode()
    
    print(f"\n--- Huffman Codebook ---")
    # Sort by frequency for readability
    freq_map = Counter(sample_text)
    for char, code in sorted(codebook.items(), key=lambda x: freq_map[x[0]], reverse=True):
        print(f"  '{char}': {code} (appears {freq_map[char]} times)")
    
    print(f"\n--- Encoded Result ---")
    print(f"Bit string length: {len(encoded_bits)} bits")
    print(f"First 80 bits: {encoded_bits[:80]}...")
    
    # Pack into bytes
    packed = pack_bits_to_bytes(encoded_bits)
    print(f"Packed size: {len(packed)} bytes")
    
    # Compression stats
    ratio = compressor.compression_ratio(encoded_bits)
    print(f"\nCompression ratio: {ratio:.2f}x")
    print(f"Space saved: {(1 - 1/ratio) * 100:.1f}%")
    
    # Decode to verify
    decoded = compressor.decode(encoded_bits)
    print(f"\n--- Verification ---")
    print(f"Decoded matches original: {decoded == sample_text}")
    
    if decoded == sample_text:
        print("✓ Compression/decompression successful!")
    else:
        print("✗ Error in encoding/decoding")