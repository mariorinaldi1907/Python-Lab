"""
Date: 2026-08-08
Implemented Huffman coding to compress text by building frequency-based binary trees — includes encode/decode with visual tree representation.
"""

#!/usr/bin/env python3
"""
Huffman Text Compressor
Builds a frequency tree and encodes text into variable-length bit strings.
Characters that appear more often get shorter codes.
"""

import heapq
from collections import Counter, defaultdict


class HuffmanNode:
    """
    Node in the Huffman tree.
    Leaf nodes store characters, internal nodes just hold combined frequencies.
    """
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    
    # heapq needs comparison operators for priority queue
    def __lt__(self, other):
        return self.freq < other.freq


def build_frequency_table(text):
    """
    Count how often each character appears in the text.
    Returns a Counter dict mapping char -> frequency.
    """
    return Counter(text)


def build_huffman_tree(freq_table):
    """
    Construct the Huffman tree using a min-heap.
    Repeatedly merge the two lowest-frequency nodes until one tree remains.
    """
    if not freq_table:
        return None
    
    # Start with a heap of leaf nodes
    heap = [HuffmanNode(char=char, freq=freq) for char, freq in freq_table.items()]
    heapq.heapify(heap)
    
    # Keep merging until we have a single root
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        
        # Create internal node with combined frequency
        merged = HuffmanNode(freq=left.freq + right.freq, left=left, right=right)
        heapq.heappush(heap, merged)
    
    return heap[0]


def generate_codes(node, prefix="", codebook=None):
    """
    Traverse the Huffman tree to assign binary codes to each character.
    Left edge = 0, right edge = 1.
    Returns a dict mapping char -> bit string.
    """
    if codebook is None:
        codebook = {}
    
    if node is None:
        return codebook
    
    # Leaf node: assign the current prefix as the code
    if node.char is not None:
        codebook[node.char] = prefix if prefix else "0"  # edge case: single char
        return codebook
    
    # Internal node: recurse left and right
    generate_codes(node.left, prefix + "0", codebook)
    generate_codes(node.right, prefix + "1", codebook)
    
    return codebook


def huffman_encode(text):
    """
    Encode text using Huffman coding.
    Returns the encoded bit string and the codebook for decoding.
    """
    if not text:
        return "", {}
    
    freq_table = build_frequency_table(text)
    tree = build_huffman_tree(freq_table)
    codebook = generate_codes(tree)
    
    # Convert text to bit string using the codebook
    encoded = "".join(codebook[char] for char in text)
    
    return encoded, codebook


def huffman_decode(encoded_bits, codebook):
    """
    Decode a bit string back to text using the codebook.
    We reverse the codebook so we can look up codes -> chars.
    """
    if not encoded_bits or not codebook:
        return ""
    
    # Reverse the codebook: bit string -> character
    reverse_codebook = {code: char for char, code in codebook.items()}
    
    decoded = []
    current_code = ""
    
    for bit in encoded_bits:
        current_code += bit
        if current_code in reverse_codebook:
            decoded.append(reverse_codebook[current_code])
            current_code = ""
    
    return "".join(decoded)


def print_tree(node, prefix="", is_tail=True):
    """
    Pretty-print the Huffman tree structure.
    Helps visualize how the tree is built.
    """
    if node is None:
        return
    
    connector = "└── " if is_tail else "├── "
    label = f"'{node.char}' ({node.freq})" if node.char else f"* ({node.freq})"
    print(prefix + connector + label)
    
    if node.left or node.right:
        extension = "    " if is_tail else "│   "
        if node.right:
            print_tree(node.right, prefix + extension, False)
        if node.left:
            print_tree(node.left, prefix + extension, True)


if __name__ == "__main__":
    # Real demo with a sample message
    original_text = "hello huffman! this is a compression test"
    
    print("=" * 60)
    print("HUFFMAN COMPRESSION DEMO")
    print("=" * 60)
    print(f"\nOriginal text: '{original_text}'")
    print(f"Length: {len(original_text)} characters")
    
    # Encode
    encoded, codebook = huffman_encode(original_text)
    
    print("\n--- Codebook ---")
    for char, code in sorted(codebook.items(), key=lambda x: len(x[1])):
        display_char = repr(char) if char in (' ', '\n', '\t') else char
        print(f"  {display_char:3} -> {code}")
    
    print(f"\n--- Encoded Bit String ---")
    print(f"{encoded[:80]}..." if len(encoded) > 80 else encoded)
    print(f"Total bits: {len(encoded)}")
    
    # Calculate compression ratio
    original_bits = len(original_text) * 8  # ASCII is 8 bits per char
    compression_ratio = (1 - len(encoded) / original_bits) * 100
    print(f"\nOriginal size: {original_bits} bits (8-bit ASCII)")
    print(f"Compressed size: {len(encoded)} bits")
    print(f"Compression ratio: {compression_ratio:.1f}%")
    
    # Decode
    decoded_text = huffman_decode(encoded, codebook)
    print(f"\n--- Decoded Text ---")
    print(f"'{decoded_text}'")
    
    # Verify
    match = "✓ MATCH" if decoded_text == original_text else "✗ MISMATCH"
    print(f"\nVerification: {match}")
    
    # Show tree structure
    print("\n--- Huffman Tree Structure ---")
    freq_table = build_frequency_table(original_text)
    tree = build_huffman_tree(freq_table)
    print_tree(tree)