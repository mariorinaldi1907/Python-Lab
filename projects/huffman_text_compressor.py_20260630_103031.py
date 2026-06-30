"""
Date: 2026-06-30
Implemented Huffman coding with tree visualization to see how compression actually works on different text inputs.
"""

#!/usr/bin/env python3
"""
Huffman encoding/decoding implementation.
I wanted to understand how text compression actually works under the hood,
so I built this from scratch using heaps and binary trees.
"""

import heapq
from collections import Counter, defaultdict


class HuffmanNode:
    """
    A node in the Huffman tree. We need to track frequency for building
    the tree, and left/right children for traversing it during encoding.
    """
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None
    
    # heapq needs these to compare nodes by frequency
    def __lt__(self, other):
        return self.freq < other.freq
    
    def __eq__(self, other):
        return self.freq == other.freq


def build_huffman_tree(text):
    """
    Build a Huffman tree from text by counting character frequencies
    and merging the two least frequent nodes repeatedly.
    
    Returns the root node of the tree, or None if text is empty.
    """
    if not text:
        return None
    
    # Count how often each character appears
    freq_map = Counter(text)
    
    # Edge case: single unique character
    if len(freq_map) == 1:
        char, freq = list(freq_map.items())[0]
        root = HuffmanNode(None, freq)
        root.left = HuffmanNode(char, freq)
        return root
    
    # Initialize heap with leaf nodes for each character
    heap = [HuffmanNode(char, freq) for char, freq in freq_map.items()]
    heapq.heapify(heap)
    
    # Keep merging the two smallest nodes until we have one tree
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        
        # Create parent node with combined frequency
        parent = HuffmanNode(None, left.freq + right.freq)
        parent.left = left
        parent.right = right
        
        heapq.heappush(heap, parent)
    
    return heap[0]


def build_codes(root):
    """
    Traverse the Huffman tree to generate binary codes for each character.
    Left edges = 0, right edges = 1.
    
    Returns a dictionary mapping characters to their binary code strings.
    """
    if root is None:
        return {}
    
    codes = {}
    
    def traverse(node, code):
        if node.char is not None:
            # Leaf node - store the code
            codes[node.char] = code if code else "0"
            return
        
        if node.left:
            traverse(node.left, code + "0")
        if node.right:
            traverse(node.right, code + "1")
    
    traverse(root, "")
    return codes


def huffman_encode(text):
    """
    Encode text using Huffman coding.
    
    Returns a tuple of (encoded_binary_string, huffman_tree_root)
    We need to return the tree so we can decode later.
    """
    if not text:
        return "", None
    
    root = build_huffman_tree(text)
    codes = build_codes(root)
    
    # Encode the text using our generated codes
    encoded = "".join(codes[char] for char in text)
    
    return encoded, root


def huffman_decode(encoded, root):
    """
    Decode a binary string using the Huffman tree.
    Walk down the tree based on each bit until we hit a leaf.
    """
    if not encoded or root is None:
        return ""
    
    decoded = []
    current = root
    
    for bit in encoded:
        # Traverse left or right based on the bit
        current = current.left if bit == "0" else current.right
        
        # If we hit a leaf, we found a character
        if current.char is not None:
            decoded.append(current.char)
            current = root  # Reset to root for next character
    
    return "".join(decoded)


def visualize_tree(root, prefix="", is_left=None):
    """
    Print the Huffman tree structure in a readable way.
    Just helps to see what the tree actually looks like.
    """
    if root is None:
        return
    
    # Print current node
    if is_left is None:
        print(f"{prefix}ROOT [{root.freq}]")
    else:
        connector = "└── " if not is_left else "├── "
        char_display = repr(root.char) if root.char else "•"
        print(f"{prefix}{connector}{char_display} [{root.freq}]")
    
    # Print children
    if root.left or root.right:
        new_prefix = prefix + ("    " if is_left is False else "│   " if is_left else "")
        if root.left:
            visualize_tree(root.left, new_prefix, True)
        if root.right:
            visualize_tree(root.right, new_prefix, False)


if __name__ == "__main__":
    # Test with a sample text that has varied character frequencies
    test_text = "hello world! this is a test of huffman encoding."
    
    print(f"Original text: {test_text}")
    print(f"Original length: {len(test_text)} characters\n")
    
    # Encode
    encoded, tree = huffman_encode(test_text)
    print(f"Encoded (binary): {encoded}")
    print(f"Encoded length: {len(encoded)} bits")
    
    # Calculate compression ratio
    original_bits = len(test_text) * 8  # assuming ASCII
    compression_ratio = (1 - len(encoded) / original_bits) * 100
    print(f"Compression: {compression_ratio:.1f}% reduction\n")
    
    # Show the codes
    codes = build_codes(tree)
    print("Huffman codes:")
    for char, code in sorted(codes.items(), key=lambda x: len(x[1])):
        print(f"  {repr(char)}: {code}")
    
    print("\nHuffman tree structure:")
    visualize_tree(tree)
    
    # Decode to verify it works
    decoded = huffman_decode(encoded, tree)
    print(f"\nDecoded text: {decoded}")
    print(f"Decoding successful: {decoded == test_text}")