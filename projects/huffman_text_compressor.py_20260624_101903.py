"""
Date: 2026-06-24
Implemented Huffman coding to compress text files — builds the tree, encodes to binary strings, and can decode back to original.
"""

"""
Huffman text compression utility.

This module implements Huffman coding for text compression. I wanted to see
how much I could actually compress repeated text patterns, and Huffman seemed
like the classic approach worth understanding from the ground up.
"""

import heapq
from collections import Counter, defaultdict
from typing import Dict, Optional


class HuffmanNode:
    """
    Represents a node in the Huffman tree.
    
    Using a class here because nodes need to be comparable for the heap,
    and we need to track both leaves (characters) and internal nodes.
    """
    
    def __init__(self, char: Optional[str], freq: int, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        # Needed for heapq to compare nodes by frequency
        return self.freq < other.freq
    
    def is_leaf(self):
        """Check if this node is a leaf (represents an actual character)."""
        return self.left is None and self.right is None


def build_huffman_tree(text: str) -> Optional[HuffmanNode]:
    """
    Build a Huffman tree from character frequencies.
    
    Returns the root node of the tree, or None if text is empty.
    I'm using a min-heap to always merge the two lowest-frequency nodes.
    """
    if not text:
        return None
    
    # Count character frequencies
    freq_map = Counter(text)
    
    # Edge case: single unique character
    if len(freq_map) == 1:
        char, freq = list(freq_map.items())[0]
        return HuffmanNode(char, freq)
    
    # Build initial heap of leaf nodes
    heap = [HuffmanNode(char, freq) for char, freq in freq_map.items()]
    heapq.heapify(heap)
    
    # Merge nodes until we have a single tree
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        
        # Create internal node with combined frequency
        merged = HuffmanNode(None, left.freq + right.freq, left, right)
        heapq.heappush(heap, merged)
    
    return heap[0]


def build_code_table(root: Optional[HuffmanNode]) -> Dict[str, str]:
    """
    Generate the encoding table by traversing the Huffman tree.
    
    Returns a dict mapping each character to its binary code string.
    Left = 0, Right = 1 in the tree traversal.
    """
    if root is None:
        return {}
    
    # Handle single character case
    if root.is_leaf():
        return {root.char: "0"}
    
    code_table = {}
    
    def traverse(node, code):
        if node.is_leaf():
            code_table[node.char] = code
            return
        
        if node.left:
            traverse(node.left, code + "0")
        if node.right:
            traverse(node.right, code + "1")
    
    traverse(root, "")
    return code_table


def huffman_encode(text: str) -> tuple[str, HuffmanNode]:
    """
    Encode text using Huffman coding.
    
    Returns the encoded binary string and the tree (needed for decoding).
    """
    if not text:
        return "", None
    
    root = build_huffman_tree(text)
    code_table = build_code_table(root)
    
    # Encode the text by replacing each character with its code
    encoded = "".join(code_table[char] for char in text)
    
    return encoded, root


def huffman_decode(encoded: str, root: Optional[HuffmanNode]) -> str:
    """
    Decode a Huffman-encoded binary string back to original text.
    
    Walk the tree for each bit: 0 = left, 1 = right, until we hit a leaf.
    """
    if not encoded or root is None:
        return ""
    
    # Handle single character case
    if root.is_leaf():
        return root.char * len(encoded)
    
    decoded = []
    current = root
    
    for bit in encoded:
        # Navigate the tree based on the bit
        if bit == "0":
            current = current.left
        else:
            current = current.right
        
        # If we hit a leaf, we found a character
        if current.is_leaf():
            decoded.append(current.char)
            current = root  # Reset to root for next character
    
    return "".join(decoded)


if __name__ == "__main__":
    # Demo with a test string that has clear repetition patterns
    original_text = "hello huffman! huffman coding is cool. huffman huffman huffman!"
    
    print("=" * 60)
    print("HUFFMAN COMPRESSION DEMO")
    print("=" * 60)
    print(f"\nOriginal text ({len(original_text)} chars):")
    print(f'"{original_text}"')
    
    # Encode
    encoded_bits, tree = huffman_encode(original_text)
    
    print(f"\nEncoded to {len(encoded_bits)} bits:")
    print(f"{encoded_bits[:80]}..." if len(encoded_bits) > 80 else encoded_bits)
    
    # Show the code table
    code_table = build_code_table(tree)
    print(f"\nHuffman codes (sorted by frequency):")
    freq_map = Counter(original_text)
    sorted_chars = sorted(code_table.items(), key=lambda x: freq_map[x[0]], reverse=True)
    for char, code in sorted_chars[:10]:  # Show top 10
        display_char = repr(char) if char in ' \n\t' else char
        print(f"  {display_char}: {code} (appears {freq_map[char]} times)")
    
    # Calculate compression ratio
    original_bits = len(original_text) * 8  # ASCII is 8 bits per char
    compression_ratio = (1 - len(encoded_bits) / original_bits) * 100
    
    print(f"\nCompression stats:")
    print(f"  Original: {original_bits} bits ({len(original_text)} chars × 8 bits)")
    print(f"  Encoded:  {len(encoded_bits)} bits")
    print(f"  Saved:    {compression_ratio:.1f}%")
    
    # Decode to verify it works
    decoded_text = huffman_decode(encoded_bits, tree)
    
    print(f"\nDecoded text:")
    print(f'"{decoded_text}"')
    
    print(f"\nVerification: {'✓ PASS' if decoded_text == original_text else '✗ FAIL'}")
    print("=" * 60)