"""
Date: 2026-06-14
Implemented Huffman coding to see how real compression algorithms work — encodes text into variable-length bit strings based on character frequency.
"""

#!/usr/bin/env python3
"""
Huffman Coding Text Compressor
Encodes and decodes text using Huffman's algorithm for optimal prefix-free codes.
Each character gets a binary code based on its frequency — more common chars get shorter codes.
"""

import heapq
from collections import Counter, defaultdict


class HuffmanNode:
    """
    Node in the Huffman tree. Can be a leaf (character) or internal (frequency combiner).
    """
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char  # None for internal nodes
        self.freq = freq
        self.left = left
        self.right = right
    
    # Heap needs to compare nodes by frequency
    def __lt__(self, other):
        return self.freq < other.freq


def build_frequency_table(text):
    """
    Count how many times each character appears.
    Returns a dict mapping char -> count.
    """
    return dict(Counter(text))


def build_huffman_tree(freq_table):
    """
    Construct the Huffman tree using a min-heap.
    We repeatedly merge the two least-frequent nodes until one tree remains.
    """
    if not freq_table:
        return None
    
    # Start with a heap of leaf nodes
    heap = [HuffmanNode(char=char, freq=freq) for char, freq in freq_table.items()]
    heapq.heapify(heap)
    
    # Edge case: only one unique character
    if len(heap) == 1:
        node = heapq.heappop(heap)
        return HuffmanNode(freq=node.freq, left=node)
    
    # Merge nodes until we have a single tree
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(freq=left.freq + right.freq, left=left, right=right)
        heapq.heappush(heap, merged)
    
    return heap[0]


def build_code_table(root):
    """
    Traverse the Huffman tree to generate binary codes for each character.
    Left edge = 0, right edge = 1.
    Returns a dict mapping char -> binary string.
    """
    if root is None:
        return {}
    
    codes = {}
    
    def traverse(node, current_code):
        if node.char is not None:  # Leaf node
            codes[node.char] = current_code if current_code else "0"
        else:
            if node.left:
                traverse(node.left, current_code + "0")
            if node.right:
                traverse(node.right, current_code + "1")
    
    traverse(root, "")
    return codes


def encode(text):
    """
    Compress text into a binary string using Huffman coding.
    Returns the encoded binary string and the Huffman tree (needed for decoding).
    """
    if not text:
        return "", None
    
    freq_table = build_frequency_table(text)
    tree = build_huffman_tree(freq_table)
    code_table = build_code_table(tree)
    
    # Encode each character using its Huffman code
    encoded = "".join(code_table[char] for char in text)
    return encoded, tree


def decode(encoded_binary, tree):
    """
    Decompress a binary string back to the original text using the Huffman tree.
    We traverse the tree based on each bit until we hit a leaf, then output that char.
    """
    if not encoded_binary or tree is None:
        return ""
    
    decoded = []
    current = tree
    
    for bit in encoded_binary:
        # Traverse left (0) or right (1)
        if bit == "0":
            current = current.left if current.left else current
        else:
            current = current.right if current.right else current
        
        # If we hit a leaf, output the character and reset to root
        if current.char is not None:
            decoded.append(current.char)
            current = tree
    
    return "".join(decoded)


def calculate_compression_ratio(original_text, encoded_binary):
    """
    Compare the sizes to see how much we saved.
    Original is measured in 8-bit ASCII, encoded in variable-length bits.
    """
    original_bits = len(original_text) * 8
    compressed_bits = len(encoded_binary)
    ratio = (1 - compressed_bits / original_bits) * 100 if original_bits > 0 else 0
    return ratio


def print_code_table(code_table):
    """
    Pretty-print the character -> code mapping for debugging.
    """
    print("\nHuffman Code Table:")
    print("-" * 40)
    for char, code in sorted(code_table.items(), key=lambda x: len(x[1])):
        display_char = repr(char) if char in '\n\t ' else char
        print(f"  {display_char:6} -> {code}")


if __name__ == "__main__":
    # Demo with a real-world-ish example
    test_text = "hello world! this is a huffman coding example. compression works best with repeated characters!!!"
    
    print("Original Text:")
    print(f"  '{test_text}'")
    print(f"  Length: {len(test_text)} characters ({len(test_text) * 8} bits in ASCII)\n")
    
    # Encode
    encoded, huffman_tree = encode(test_text)
    print(f"Encoded (binary string, first 100 chars):")
    print(f"  {encoded[:100]}...")
    print(f"  Total length: {len(encoded)} bits")
    
    # Show the code table we generated
    code_table = build_code_table(huffman_tree)
    print_code_table(code_table)
    
    # Calculate compression
    ratio = calculate_compression_ratio(test_text, encoded)
    print(f"\nCompression ratio: {ratio:.2f}%")
    
    # Decode to verify correctness
    decoded = decode(encoded, huffman_tree)
    print(f"\nDecoded Text:")
    print(f"  '{decoded}'")
    
    # Sanity check
    if decoded == test_text:
        print("\n✓ Success! Decoded text matches original.")
    else:
        print("\n✗ Error: Decoded text doesn't match!")