"""
Date: 2026-05-30
Implemented Huffman coding with binary tree construction and bit-level encoding — wanted to see how much I could squeeze out of plain text files.
"""

"""
Huffman Coding Implementation
Compresses text by building a binary tree based on character frequency.
More frequent characters get shorter bit codes.
"""

import heapq
from collections import Counter, defaultdict


class HuffmanNode:
    """
    Node in the Huffman tree. Can be a leaf (with a character) or internal node.
    """
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    
    # Heap comparison is based on frequency
    def __lt__(self, other):
        return self.freq < other.freq


class HuffmanEncoder:
    """
    Builds a Huffman tree and generates variable-length codes for characters.
    """
    
    def __init__(self, text):
        """Initialize encoder with input text and build the tree."""
        self.text = text
        self.root = None
        self.codes = {}  # char -> binary string
        self.reverse_codes = {}  # binary string -> char
        
        if text:
            self._build_tree()
            self._generate_codes()
    
    def _build_tree(self):
        """
        Build the Huffman tree using a min-heap.
        Each step combines the two lowest-frequency nodes.
        """
        frequency = Counter(self.text)
        
        # Edge case: single unique character
        if len(frequency) == 1:
            char = list(frequency.keys())[0]
            self.root = HuffmanNode(char=char, freq=frequency[char])
            return
        
        # Initialize heap with leaf nodes
        heap = [HuffmanNode(char=char, freq=freq) for char, freq in frequency.items()]
        heapq.heapify(heap)
        
        # Build tree by combining smallest nodes
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            
            # Create parent node with combined frequency
            parent = HuffmanNode(
                freq=left.freq + right.freq,
                left=left,
                right=right
            )
            heapq.heappush(heap, parent)
        
        self.root = heap[0]
    
    def _generate_codes(self, node=None, current_code=""):
        """
        Recursively traverse tree to generate binary codes.
        Left = 0, Right = 1
        """
        if node is None:
            node = self.root
        
        # Leaf node contains a character
        if node.char is not None:
            # Handle single-character text edge case
            code = current_code if current_code else "0"
            self.codes[node.char] = code
            self.reverse_codes[code] = node.char
            return
        
        # Traverse left and right
        if node.left:
            self._generate_codes(node.left, current_code + "0")
        if node.right:
            self._generate_codes(node.right, current_code + "1")
    
    def encode(self):
        """
        Encode the original text using generated Huffman codes.
        Returns the binary string representation.
        """
        if not self.text:
            return ""
        
        return "".join(self.codes[char] for char in self.text)
    
    def decode(self, encoded_text):
        """
        Decode a binary string back to original text.
        Uses the reverse lookup table for efficiency.
        """
        if not encoded_text:
            return ""
        
        decoded = []
        current_code = ""
        
        for bit in encoded_text:
            current_code += bit
            if current_code in self.reverse_codes:
                decoded.append(self.reverse_codes[current_code])
                current_code = ""
        
        return "".join(decoded)
    
    def get_compression_stats(self):
        """
        Calculate and return compression statistics.
        """
        original_bits = len(self.text) * 8  # ASCII = 8 bits per char
        encoded = self.encode()
        compressed_bits = len(encoded)
        
        ratio = (1 - compressed_bits / original_bits) * 100 if original_bits > 0 else 0
        
        return {
            "original_size": original_bits,
            "compressed_size": compressed_bits,
            "compression_ratio": f"{ratio:.2f}%",
            "codes": self.codes
        }


if __name__ == "__main__":
    # Demo with a sample text
    sample_text = "hello world! this is a huffman coding demo. compression works best with repeated characters!!!"
    
    print("=" * 60)
    print("HUFFMAN CODING DEMO")
    print("=" * 60)
    print(f"\nOriginal text ({len(sample_text)} chars):")
    print(f'"{sample_text}"')
    
    # Encode
    encoder = HuffmanEncoder(sample_text)
    encoded = encoder.encode()
    
    print(f"\nEncoded (binary string, {len(encoded)} bits):")
    print(encoded[:100] + "..." if len(encoded) > 100 else encoded)
    
    # Show the code table
    print("\nHuffman Codes (character -> binary):")
    for char, code in sorted(encoder.codes.items(), key=lambda x: len(x[1])):
        display_char = repr(char) if char in [' ', '\n', '\t'] else char
        print(f"  {display_char:6} -> {code}")
    
    # Decode back
    decoded = encoder.decode(encoded)
    print(f"\nDecoded text:")
    print(f'"{decoded}"')
    
    # Verify correctness
    print(f"\nDecoding successful: {decoded == sample_text}")
    
    # Compression stats
    stats = encoder.get_compression_stats()
    print(f"\n--- Compression Statistics ---")
    print(f"Original size:    {stats['original_size']} bits")
    print(f"Compressed size:  {stats['compressed_size']} bits")
    print(f"Reduction:        {stats['compression_ratio']}")
    
    print("\n" + "=" * 60)