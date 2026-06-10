"""
Date: 2026-06-10
Implemented Huffman coding to compress text by building a frequency tree and generating optimal binary codes for each character.
"""

#!/usr/bin/env python3
"""
Huffman text compression utility.
Builds a frequency-based binary tree to encode common characters with shorter codes.
"""

import heapq
from collections import Counter, defaultdict


class HuffmanNode:
    """
    Node in the Huffman tree.
    Leaf nodes contain characters; internal nodes just aggregate frequencies.
    """
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    
    # Heap needs comparison operators; we only care about frequency
    def __lt__(self, other):
        return self.freq < other.freq


def build_huffman_tree(text):
    """
    Build a Huffman tree from input text based on character frequencies.
    Returns the root node of the tree.
    """
    if not text:
        return None
    
    # Count character frequencies
    frequency = Counter(text)
    
    # Edge case: single unique character
    if len(frequency) == 1:
        char = list(frequency.keys())[0]
        return HuffmanNode(char=char, freq=frequency[char])
    
    # Initialize a min-heap with leaf nodes for each character
    heap = [HuffmanNode(char=char, freq=freq) for char, freq in frequency.items()]
    heapq.heapify(heap)
    
    # Build the tree by combining the two lowest frequency nodes
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        
        # Create internal node with combined frequency
        merged = HuffmanNode(freq=left.freq + right.freq, left=left, right=right)
        heapq.heappush(heap, merged)
    
    return heap[0]


def generate_codes(root):
    """
    Generate Huffman codes by traversing the tree.
    Returns a dictionary mapping characters to their binary codes.
    """
    if root is None:
        return {}
    
    # Edge case: single character (give it a code of '0')
    if root.left is None and root.right is None:
        return {root.char: '0'}
    
    codes = {}
    
    def traverse(node, current_code):
        """Recursive DFS to build codes."""
        if node is None:
            return
        
        # Leaf node: store the code for this character
        if node.char is not None:
            codes[node.char] = current_code
            return
        
        # Traverse left (add '0') and right (add '1')
        traverse(node.left, current_code + '0')
        traverse(node.right, current_code + '1')
    
    traverse(root, '')
    return codes


def encode(text, codes):
    """
    Encode text using the provided Huffman codes.
    Returns the encoded binary string.
    """
    return ''.join(codes[char] for char in text)


def decode(encoded_text, root):
    """
    Decode a Huffman-encoded binary string using the tree.
    Returns the original text.
    """
    if not encoded_text or root is None:
        return ''
    
    # Edge case: single character tree
    if root.left is None and root.right is None:
        return root.char * len(encoded_text)
    
    decoded = []
    current = root
    
    for bit in encoded_text:
        # Traverse the tree based on bit value
        if bit == '0':
            current = current.left
        else:
            current = current.right
        
        # If we hit a leaf, we've decoded a character
        if current.char is not None:
            decoded.append(current.char)
            current = root  # Reset to root for next character
    
    return ''.join(decoded)


def print_codes(codes):
    """Pretty print the Huffman codes sorted by code length."""
    print("\nHuffman Codes:")
    print("-" * 40)
    for char, code in sorted(codes.items(), key=lambda x: (len(x[1]), x[0])):
        display_char = repr(char) if char in '\n\t ' else char
        print(f"  {display_char:>5} -> {code}")


def calculate_compression_ratio(original, encoded):
    """Calculate and return compression statistics."""
    original_bits = len(original) * 8  # ASCII is 8 bits per char
    encoded_bits = len(encoded)
    ratio = (1 - encoded_bits / original_bits) * 100 if original_bits > 0 else 0
    return original_bits, encoded_bits, ratio


if __name__ == "__main__":
    # Demo with a sample text that shows Huffman's power
    sample_text = "this is an example of a huffman tree encoding algorithm"
    
    print("=" * 50)
    print("HUFFMAN ENCODING DEMO")
    print("=" * 50)
    print(f"\nOriginal text:\n  '{sample_text}'")
    print(f"\nLength: {len(sample_text)} characters")
    
    # Build tree and generate codes
    tree = build_huffman_tree(sample_text)
    codes = generate_codes(tree)
    
    # Show the generated codes
    print_codes(codes)
    
    # Encode the text
    encoded = encode(sample_text, codes)
    print(f"\nEncoded (first 80 bits):\n  {encoded[:80]}...")
    
    # Calculate compression stats
    orig_bits, enc_bits, ratio = calculate_compression_ratio(sample_text, encoded)
    print(f"\nCompression Statistics:")
    print(f"  Original:  {orig_bits} bits ({orig_bits // 8} bytes)")
    print(f"  Encoded:   {enc_bits} bits ({enc_bits // 8} bytes)")
    print(f"  Saved:     {ratio:.1f}%")
    
    # Verify decoding works
    decoded = decode(encoded, tree)
    print(f"\nDecoded text:\n  '{decoded}'")
    print(f"\nVerification: {'✓ PASS' if decoded == sample_text else '✗ FAIL'}")