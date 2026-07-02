"""
Date: 2026-07-02
Built a Huffman encoder/decoder to explore how compression actually works under the hood — encodes text into variable-length bit strings based on character frequency.
"""

"""
Huffman coding implementation for text compression.
Uses frequency analysis to build optimal prefix-free codes.
"""

import heapq
from collections import Counter, defaultdict


class HuffmanNode:
    """
    Node for building the Huffman tree.
    Supports comparison for heap operations based on frequency.
    """
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None
    
    def __lt__(self, other):
        # Needed for heapq to compare nodes
        return self.freq < other.freq


def build_huffman_tree(text):
    """
    Builds a Huffman tree from input text based on character frequencies.
    Returns the root node of the tree.
    """
    if not text:
        return None
    
    # Count character frequencies
    freq_map = Counter(text)
    
    # Edge case: single unique character
    if len(freq_map) == 1:
        char = list(freq_map.keys())[0]
        root = HuffmanNode(char, freq_map[char])
        return root
    
    # Create a min heap of nodes
    heap = [HuffmanNode(char, freq) for char, freq in freq_map.items()]
    heapq.heapify(heap)
    
    # Build tree by merging two smallest nodes repeatedly
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        
        merged = HuffmanNode(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        
        heapq.heappush(heap, merged)
    
    return heap[0]


def build_codes(node, current_code="", codes=None):
    """
    Traverses the Huffman tree to generate binary codes for each character.
    Left = 0, Right = 1. Returns a dictionary mapping characters to their codes.
    """
    if codes is None:
        codes = {}
    
    if node is None:
        return codes
    
    # Leaf node contains a character
    if node.char is not None:
        codes[node.char] = current_code if current_code else "0"
        return codes
    
    # Traverse left and right
    build_codes(node.left, current_code + "0", codes)
    build_codes(node.right, current_code + "1", codes)
    
    return codes


def huffman_encode(text):
    """
    Encodes text using Huffman coding.
    Returns encoded binary string and the code mapping (needed for decoding).
    """
    if not text:
        return "", {}
    
    tree = build_huffman_tree(text)
    codes = build_codes(tree)
    
    # Encode the text
    encoded = "".join(codes[char] for char in text)
    
    return encoded, codes


def huffman_decode(encoded_text, codes):
    """
    Decodes a Huffman-encoded binary string using the code mapping.
    Reverses the codes dict to map binary strings back to characters.
    """
    if not encoded_text:
        return ""
    
    # Reverse the code mapping
    reverse_codes = {code: char for char, code in codes.items()}
    
    decoded = []
    current_code = ""
    
    for bit in encoded_text:
        current_code += bit
        if current_code in reverse_codes:
            decoded.append(reverse_codes[current_code])
            current_code = ""
    
    return "".join(decoded)


def calculate_compression_ratio(original, encoded):
    """
    Calculates compression ratio assuming 8 bits per character in original.
    Returns ratio as a percentage.
    """
    original_bits = len(original) * 8
    encoded_bits = len(encoded)
    
    if original_bits == 0:
        return 0.0
    
    ratio = (1 - encoded_bits / original_bits) * 100
    return ratio


if __name__ == "__main__":
    # Demo with a text sample that should compress well
    sample_text = "this is an example of huffman encoding. huffman encoding is cool!"
    
    print("=" * 60)
    print("HUFFMAN COMPRESSION DEMO")
    print("=" * 60)
    
    print(f"\nOriginal text ({len(sample_text)} chars):")
    print(f'"{sample_text}"')
    
    # Encode
    encoded, code_map = huffman_encode(sample_text)
    
    print(f"\nCharacter frequency and codes:")
    freq = Counter(sample_text)
    for char, count in sorted(freq.items(), key=lambda x: -x[1])[:10]:
        char_display = repr(char) if char != ' ' else "' '"
        print(f"  {char_display}: {count:2d} occurrences -> {code_map[char]}")
    
    print(f"\nEncoded binary string (first 100 bits):")
    print(f"{encoded[:100]}...")
    
    # Decode to verify
    decoded = huffman_decode(encoded, code_map)
    print(f"\nDecoded text matches original: {decoded == sample_text}")
    
    # Compression stats
    original_bits = len(sample_text) * 8
    encoded_bits = len(encoded)
    ratio = calculate_compression_ratio(sample_text, encoded)
    
    print(f"\nCompression statistics:")
    print(f"  Original: {original_bits} bits ({len(sample_text)} chars × 8)")
    print(f"  Encoded:  {encoded_bits} bits")
    print(f"  Ratio:    {ratio:.2f}% reduction")
    print(f"  Average:  {encoded_bits/len(sample_text):.2f} bits/char")