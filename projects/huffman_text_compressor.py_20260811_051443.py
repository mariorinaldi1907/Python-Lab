"""
Date: 2026-08-11
Built a working Huffman encoder/decoder to see how compression works under the hood — generates variable-length codes based on character frequency.
"""

#!/usr/bin/env python3
"""
Huffman Coding Implementation
Compresses text by assigning shorter binary codes to more frequent characters.
"""

import heapq
from collections import Counter, defaultdict


class HuffmanNode:
    """
    Node in the Huffman tree. Needs custom comparison for heapq since
    we're comparing based on frequency, not the character itself.
    """
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None
    
    def __lt__(self, other):
        return self.freq < other.freq


class HuffmanCompressor:
    """
    Handles encoding and decoding using Huffman coding.
    The basic idea: build a binary tree where frequent chars are closer to root.
    """
    
    def __init__(self):
        self.root = None
        self.codes = {}
        self.reverse_codes = {}
    
    def _build_tree(self, text):
        """
        Build the Huffman tree using a min-heap.
        We merge the two least frequent nodes repeatedly.
        """
        if not text:
            return None
        
        # Count character frequencies
        freq_map = Counter(text)
        
        # Edge case: single unique character
        if len(freq_map) == 1:
            char = list(freq_map.keys())[0]
            root = HuffmanNode(char, freq_map[char])
            # Give it a simple code since there's only one char
            self.codes[char] = '0'
            self.reverse_codes['0'] = char
            return root
        
        # Build initial heap with all characters
        heap = [HuffmanNode(char, freq) for char, freq in freq_map.items()]
        heapq.heapify(heap)
        
        # Merge nodes until we have a single tree
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            
            # Create internal node with combined frequency
            merged = HuffmanNode(None, left.freq + right.freq)
            merged.left = left
            merged.right = right
            
            heapq.heappush(heap, merged)
        
        return heap[0]
    
    def _generate_codes(self, node, current_code=''):
        """
        Traverse the tree to generate binary codes for each character.
        Left = 0, Right = 1 (arbitrary but consistent).
        """
        if node is None:
            return
        
        # Leaf node = actual character
        if node.char is not None:
            self.codes[node.char] = current_code if current_code else '0'
            self.reverse_codes[current_code if current_code else '0'] = node.char
            return
        
        self._generate_codes(node.left, current_code + '0')
        self._generate_codes(node.right, current_code + '1')
    
    def compress(self, text):
        """
        Compress text and return (encoded_binary_string, tree_root).
        We need to keep the tree to decode later.
        """
        if not text:
            return '', None
        
        self.root = self._build_tree(text)
        self._generate_codes(self.root)
        
        # Encode the text using our generated codes
        encoded = ''.join(self.codes[char] for char in text)
        return encoded, self.root
    
    def decompress(self, encoded, root):
        """
        Decode the binary string back to original text using the tree.
        Walk the tree based on bits: 0 = left, 1 = right.
        """
        if not encoded or root is None:
            return ''
        
        # Edge case: single character tree
        if root.left is None and root.right is None:
            return root.char * len(encoded)
        
        decoded = []
        current = root
        
        for bit in encoded:
            # Traverse based on bit value
            current = current.left if bit == '0' else current.right
            
            # Reached a leaf node
            if current.char is not None:
                decoded.append(current.char)
                current = root  # Reset to root for next character
        
        return ''.join(decoded)
    
    def get_compression_stats(self, original, encoded):
        """
        Calculate compression ratio and other stats.
        """
        original_bits = len(original) * 8  # ASCII = 8 bits per char
        compressed_bits = len(encoded)
        ratio = (1 - compressed_bits / original_bits) * 100 if original_bits > 0 else 0
        
        return {
            'original_bits': original_bits,
            'compressed_bits': compressed_bits,
            'ratio': ratio,
            'codes': self.codes
        }


if __name__ == "__main__":
    # Demo with a sample text that has varying character frequencies
    sample_text = "huffman coding is a neat compression algorithm! it really works well with repeated characters."
    
    print("=" * 60)
    print("HUFFMAN COMPRESSION DEMO")
    print("=" * 60)
    print(f"\nOriginal text:\n{sample_text}")
    print(f"\nLength: {len(sample_text)} characters")
    
    # Compress
    compressor = HuffmanCompressor()
    encoded, tree = compressor.compress(sample_text)
    
    print(f"\nEncoded (first 100 bits):\n{encoded[:100]}...")
    print(f"\nTotal encoded length: {len(encoded)} bits")
    
    # Show the Huffman codes generated
    print("\nGenerated Huffman Codes:")
    sorted_codes = sorted(compressor.codes.items(), key=lambda x: len(x[1]))
    for char, code in sorted_codes[:10]:  # Show first 10
        display_char = repr(char) if char in '\n\t ' else char
        print(f"  {display_char:3} -> {code}")
    print(f"  ... and {len(sorted_codes) - 10} more\n")
    
    # Compression stats
    stats = compressor.get_compression_stats(sample_text, encoded)
    print(f"Original size:   {stats['original_bits']} bits ({len(sample_text)} chars × 8)")
    print(f"Compressed size: {stats['compressed_bits']} bits")
    print(f"Compression:     {stats['ratio']:.1f}% reduction\n")
    
    # Decompress to verify it works
    decoded = compressor.decompress(encoded, tree)
    print(f"Decoded text:\n{decoded}\n")
    
    # Verify correctness
    if decoded == sample_text:
        print("✓ Decompression successful! Text matches original.")
    else:
        print("✗ ERROR: Decoded text doesn't match!")
    
    print("=" * 60)