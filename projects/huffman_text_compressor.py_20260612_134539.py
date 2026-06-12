"""
Date: 2026-06-12
Built a Huffman compression utility that encodes/decodes text using variable-length prefix codes — wanted to see real compression ratios on my own files.
"""

#!/usr/bin/env python3
"""
Huffman coding implementation for text compression.
Builds the tree from character frequencies, generates prefix codes,
and can encode/decode text. Not optimized for speed, but it works.
"""

import heapq
from collections import Counter, defaultdict


class HuffmanNode:
    """
    Node in the Huffman tree. Using __lt__ so heapq can compare nodes
    when frequencies are equal (otherwise it tries to compare the chars).
    """
    def __init__(self, char, freq, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        return self.freq < other.freq


class HuffmanCompressor:
    """
    Handles the full compression pipeline: building tree, generating codes,
    and encoding/decoding text using those codes.
    """
    
    def __init__(self):
        self.root = None
        self.codes = {}
        self.reverse_codes = {}
    
    def build_tree(self, text):
        """
        Constructs the Huffman tree from character frequencies.
        Uses a min-heap to always merge the two least frequent nodes.
        """
        if not text:
            return
        
        # Count frequencies
        freq_map = Counter(text)
        
        # Edge case: single unique character
        if len(freq_map) == 1:
            char = list(freq_map.keys())[0]
            self.root = HuffmanNode(char, freq_map[char])
            self.codes[char] = "0"
            self.reverse_codes["0"] = char
            return
        
        # Build heap of nodes
        heap = [HuffmanNode(char, freq) for char, freq in freq_map.items()]
        heapq.heapify(heap)
        
        # Merge nodes until we have a single tree
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            
            # Internal node has no character, just combined frequency
            merged = HuffmanNode(None, left.freq + right.freq, left, right)
            heapq.heappush(heap, merged)
        
        self.root = heap[0]
        self._generate_codes(self.root, "")
    
    def _generate_codes(self, node, current_code):
        """
        Recursively walks the tree to assign binary codes to each character.
        Left = 0, Right = 1. Only leaf nodes get codes.
        """
        if node is None:
            return
        
        # Leaf node - assign code
        if node.char is not None:
            self.codes[node.char] = current_code if current_code else "0"
            self.reverse_codes[current_code if current_code else "0"] = node.char
            return
        
        self._generate_codes(node.left, current_code + "0")
        self._generate_codes(node.right, current_code + "1")
    
    def encode(self, text):
        """
        Converts text to a binary string using the generated Huffman codes.
        Returns the encoded string and the codebook (needed for decoding).
        """
        if not self.codes:
            self.build_tree(text)
        
        encoded = "".join(self.codes[char] for char in text)
        return encoded
    
    def decode(self, encoded_text):
        """
        Converts binary string back to original text using the tree.
        Walks from root following 0s and 1s until hitting a leaf.
        """
        if not self.root:
            return ""
        
        decoded = []
        current = self.root
        
        for bit in encoded_text:
            # Single character edge case
            if current.char is not None:
                decoded.append(current.char)
                current = self.root
            
            # Traverse tree
            if bit == "0":
                current = current.left
            else:
                current = current.right
            
            # Reached a leaf
            if current.char is not None:
                decoded.append(current.char)
                current = self.root
        
        return "".join(decoded)
    
    def get_compression_stats(self, original_text, encoded_text):
        """
        Calculate how much space we saved (assuming 8 bits per char originally).
        In practice we'd need to store the tree too, but this gives a rough idea.
        """
        original_bits = len(original_text) * 8
        compressed_bits = len(encoded_text)
        ratio = (1 - compressed_bits / original_bits) * 100 if original_bits > 0 else 0
        
        return {
            "original_bits": original_bits,
            "compressed_bits": compressed_bits,
            "ratio": ratio
        }


if __name__ == "__main__":
    # Test with a sample text that has varied character frequencies
    sample_text = "hello world! this is a huffman coding demo. compression works best with repeated characters!!!"
    
    print("=== Huffman Compression Demo ===\n")
    print(f"Original text: {sample_text}")
    print(f"Length: {len(sample_text)} characters\n")
    
    # Compress
    compressor = HuffmanCompressor()
    encoded = compressor.encode(sample_text)
    
    print("Huffman Codes Generated:")
    # Sort by frequency for nicer display
    for char, code in sorted(compressor.codes.items(), key=lambda x: len(x[1])):
        display_char = char if char != " " else "SPACE"
        print(f"  '{display_char}': {code}")
    
    print(f"\nEncoded (first 100 bits): {encoded[:100]}...")
    print(f"Full encoded length: {len(encoded)} bits")
    
    # Decompress
    decoded = compressor.decode(encoded)
    print(f"\nDecoded text: {decoded}")
    print(f"Match: {decoded == sample_text}")
    
    # Stats
    stats = compressor.get_compression_stats(sample_text, encoded)
    print(f"\n--- Compression Stats ---")
    print(f"Original: {stats['original_bits']} bits")
    print(f"Compressed: {stats['compressed_bits']} bits")
    print(f"Reduction: {stats['ratio']:.2f}%")