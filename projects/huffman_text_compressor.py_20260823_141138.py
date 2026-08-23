"""
Date: 2026-08-23
Built a Huffman encoder to understand how lossless compression works — generates variable-length codes based on character frequency.
"""

"""
Huffman coding implementation for text compression.
I wanted to see how much I could compress text files using frequency-based encoding.
The tree-building process is pretty elegant once you get the heap logic right.
"""

import heapq
from collections import Counter, defaultdict


class HuffmanNode:
    """
    Node for the Huffman tree. I made this comparable so heapq works nicely.
    Each node either has two children (internal) or represents a character (leaf).
    """
    def __init__(self, char, freq, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        # Needed for heap comparison - lower frequency = higher priority
        return self.freq < other.freq
    
    def is_leaf(self):
        """Check if this is a leaf node (actual character)."""
        return self.left is None and self.right is None


class HuffmanEncoder:
    """
    Main encoder class. Builds the tree, generates codes, and handles compression.
    I keep the tree around so we can decode later with the same instance.
    """
    
    def __init__(self):
        self.root = None
        self.codes = {}  # char -> binary string
        self.reverse_codes = {}  # binary string -> char
    
    def build_tree(self, text):
        """
        Build the Huffman tree from character frequencies.
        Uses a min-heap to always merge the two least-frequent nodes.
        """
        if not text:
            return
        
        # Count character frequencies
        freq_map = Counter(text)
        
        # Edge case: single unique character
        if len(freq_map) == 1:
            char = list(freq_map.keys())[0]
            self.root = HuffmanNode(char, freq_map[char])
            self.codes[char] = '0'
            self.reverse_codes['0'] = char
            return
        
        # Build initial heap of leaf nodes
        heap = [HuffmanNode(char, freq) for char, freq in freq_map.items()]
        heapq.heapify(heap)
        
        # Merge nodes until we have a single tree
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            
            # Create parent node with combined frequency
            merged = HuffmanNode(None, left.freq + right.freq, left, right)
            heapq.heappush(heap, merged)
        
        self.root = heap[0]
        self._generate_codes(self.root, '')
    
    def _generate_codes(self, node, current_code):
        """
        Recursively traverse the tree to generate binary codes.
        Left = 0, Right = 1. Only leaf nodes get codes assigned.
        """
        if node is None:
            return
        
        if node.is_leaf():
            self.codes[node.char] = current_code
            self.reverse_codes[current_code] = node.char
            return
        
        self._generate_codes(node.left, current_code + '0')
        self._generate_codes(node.right, current_code + '1')
    
    def encode(self, text):
        """
        Encode text into a binary string using the generated Huffman codes.
        Returns the encoded binary string.
        """
        if not self.codes:
            self.build_tree(text)
        
        return ''.join(self.codes[char] for char in text)
    
    def decode(self, binary_string):
        """
        Decode a binary string back to text using the Huffman tree.
        Traverses the tree bit by bit until hitting a leaf node.
        """
        if not self.root:
            return ''
        
        # Edge case: single character tree
        if self.root.is_leaf():
            return self.root.char * len(binary_string)
        
        decoded = []
        current_node = self.root
        
        for bit in binary_string:
            # Traverse left or right based on bit
            current_node = current_node.left if bit == '0' else current_node.right
            
            # If we hit a leaf, output the character and reset
            if current_node.is_leaf():
                decoded.append(current_node.char)
                current_node = self.root
        
        return ''.join(decoded)
    
    def get_compression_stats(self, text):
        """
        Calculate compression ratio and other stats.
        Useful for seeing how well the encoding worked.
        """
        encoded = self.encode(text)
        original_bits = len(text) * 8  # ASCII = 8 bits per char
        compressed_bits = len(encoded)
        
        return {
            'original_size': original_bits,
            'compressed_size': compressed_bits,
            'ratio': compressed_bits / original_bits if original_bits > 0 else 0,
            'savings_percent': (1 - compressed_bits / original_bits) * 100 if original_bits > 0 else 0
        }


if __name__ == "__main__":
    # Demo with a sample text that has varying character frequencies
    sample_text = "hello world! this is a huffman coding example. compression works best with repeated characters!!!"
    
    print("=" * 70)
    print("HUFFMAN CODING DEMO")
    print("=" * 70)
    print(f"\nOriginal text:\n{sample_text}")
    print(f"\nLength: {len(sample_text)} characters")
    
    # Create encoder and compress
    encoder = HuffmanEncoder()
    encoded = encoder.encode(sample_text)
    
    print(f"\n{'Char':<8} {'Frequency':<12} {'Huffman Code'}")
    print("-" * 40)
    freq_map = Counter(sample_text)
    for char, code in sorted(encoder.codes.items(), key=lambda x: len(x[1])):
        display_char = repr(char) if char in [' ', '\n', '\t'] else char
        print(f"{display_char:<8} {freq_map[char]:<12} {code}")
    
    print(f"\nEncoded binary (first 100 bits):\n{encoded[:100]}...")
    
    # Decode to verify correctness
    decoded = encoder.decode(encoded)
    print(f"\nDecoded text:\n{decoded}")
    print(f"\nDecoding successful: {decoded == sample_text}")
    
    # Show compression stats
    stats = encoder.get_compression_stats(sample_text)
    print(f"\n{'COMPRESSION STATISTICS':-^70}")
    print(f"Original size:    {stats['original_size']} bits ({stats['original_size']//8} bytes)")
    print(f"Compressed size:  {stats['compressed_size']} bits")
    print(f"Compression ratio: {stats['ratio']:.2%}")
    print(f"Space savings:    {stats['savings_percent']:.1f}%")