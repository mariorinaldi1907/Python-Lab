"""
Date: 2026-08-21
Built a Huffman encoder/decoder to see how compression really works under the hood — handles arbitrary text and shows compression ratio.
"""

import heapq
from collections import Counter, defaultdict
from typing import Dict, Tuple, Optional


class HuffmanNode:
    """
    Node for building the Huffman tree.
    Uses frequency for priority queue ordering.
    """
    def __init__(self, char: Optional[str], freq: int, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    
    # Priority queue needs comparison - lower frequency = higher priority
    def __lt__(self, other):
        return self.freq < other.freq


def build_frequency_table(text: str) -> Dict[str, int]:
    """
    Count character occurrences in the input text.
    Returns a dict mapping each character to its frequency.
    """
    return dict(Counter(text))


def build_huffman_tree(freq_table: Dict[str, int]) -> HuffmanNode:
    """
    Construct the Huffman tree using a min-heap.
    Each character starts as a leaf node, then we merge the two
    lowest-frequency nodes until we have a single root.
    """
    # Edge case: single character
    if len(freq_table) == 1:
        char, freq = list(freq_table.items())[0]
        # Create a dummy parent so we have at least one bit
        return HuffmanNode(None, freq, HuffmanNode(char, freq), None)
    
    heap = [HuffmanNode(char, freq) for char, freq in freq_table.items()]
    heapq.heapify(heap)
    
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        # Internal nodes have no char, just combined frequency
        merged = HuffmanNode(None, left.freq + right.freq, left, right)
        heapq.heappush(heap, merged)
    
    return heap[0]


def build_codes(root: HuffmanNode) -> Dict[str, str]:
    """
    Traverse the Huffman tree to generate binary codes for each character.
    Left = '0', Right = '1'.
    """
    codes = {}
    
    def traverse(node, code):
        if node is None:
            return
        # Leaf node - this is an actual character
        if node.char is not None:
            codes[node.char] = code if code else '0'  # Handle single-char edge case
            return
        traverse(node.left, code + '0')
        traverse(node.right, code + '1')
    
    traverse(root, '')
    return codes


def encode(text: str) -> Tuple[str, Dict[str, str]]:
    """
    Encode text using Huffman coding.
    Returns the binary string and the codebook (for decoding later).
    """
    if not text:
        return '', {}
    
    freq_table = build_frequency_table(text)
    tree = build_huffman_tree(freq_table)
    codes = build_codes(tree)
    
    # Build the encoded bit string
    encoded = ''.join(codes[char] for char in text)
    return encoded, codes


def decode(encoded: str, codes: Dict[str, str]) -> str:
    """
    Decode a Huffman-encoded binary string back to original text.
    We reverse the codebook to map binary codes back to characters.
    """
    if not encoded:
        return ''
    
    # Reverse the code table for lookup
    reverse_codes = {code: char for char, code in codes.items()}
    
    decoded = []
    current_code = ''
    
    for bit in encoded:
        current_code += bit
        if current_code in reverse_codes:
            decoded.append(reverse_codes[current_code])
            current_code = ''
    
    return ''.join(decoded)


def calculate_compression_ratio(original: str, encoded: str) -> float:
    """
    Calculate how much space we saved.
    Original is 8 bits per char (ASCII assumption), encoded is len(bitstring).
    """
    original_bits = len(original) * 8
    encoded_bits = len(encoded)
    return (1 - encoded_bits / original_bits) * 100 if original_bits > 0 else 0


if __name__ == "__main__":
    # Test with a real-ish sentence that has varied character frequencies
    test_text = "hello world! this is a huffman coding test. compression works best with repeated characters."
    
    print("=" * 70)
    print("HUFFMAN CODING DEMO")
    print("=" * 70)
    print(f"\nOriginal text ({len(test_text)} chars):")
    print(f'"{test_text}"')
    
    # Encode
    encoded_bits, codebook = encode(test_text)
    
    print(f"\nCharacter frequency analysis:")
    freq_table = build_frequency_table(test_text)
    for char, freq in sorted(freq_table.items(), key=lambda x: -x[1])[:10]:
        code = codebook.get(char, '')
        print(f"  '{char}': {freq:2d} occurrences -> {code:>10s} ({len(code)} bits)")
    
    print(f"\nEncoded binary string (first 100 bits):")
    print(f"  {encoded_bits[:100]}...")
    
    # Decode to verify it works
    decoded_text = decode(encoded_bits, codebook)
    print(f"\nDecoded text matches original: {decoded_text == test_text}")
    
    # Compression stats
    original_bits = len(test_text) * 8
    compression_ratio = calculate_compression_ratio(test_text, encoded_bits)
    
    print(f"\nCompression stats:")
    print(f"  Original: {original_bits} bits ({len(test_text)} chars × 8 bits)")
    print(f"  Encoded:  {len(encoded_bits)} bits")
    print(f"  Saved:    {original_bits - len(encoded_bits)} bits ({compression_ratio:.1f}% reduction)")
    
    print("\n" + "=" * 70)