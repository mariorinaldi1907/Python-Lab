"""
Date: 2026-07-25
Built a Huffman encoder/decoder to mess around with lossless compression — shows actual compression ratios and bit savings.
"""

"""
Huffman Coding Implementation
Compresses text using variable-length prefix codes based on character frequency.
"""

import heapq
from collections import Counter, defaultdict
from typing import Optional, Dict, Tuple


class HuffmanNode:
    """
    Node in the Huffman tree. Supports comparison for heap operations.
    """
    
    def __init__(self, char: Optional[str], freq: int, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        # heapq needs this to compare nodes by frequency
        return self.freq < other.freq
    
    def is_leaf(self):
        return self.char is not None


def build_huffman_tree(text: str) -> Optional[HuffmanNode]:
    """
    Build a Huffman tree from character frequencies in the text.
    Returns the root node, or None if text is empty.
    """
    if not text:
        return None
    
    # Count character frequencies
    freq_map = Counter(text)
    
    # Edge case: single unique character
    if len(freq_map) == 1:
        char, freq = list(freq_map.items())[0]
        return HuffmanNode(char, freq)
    
    # Create a min-heap of leaf nodes
    heap = [HuffmanNode(char, freq) for char, freq in freq_map.items()]
    heapq.heapify(heap)
    
    # Build the tree by combining the two lowest-frequency nodes
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
    Returns a dict mapping characters to their binary codes.
    """
    if root is None:
        return {}
    
    # Special case for single character
    if root.is_leaf():
        return {root.char: '0'}
    
    code_table = {}
    
    def traverse(node, code):
        if node.is_leaf():
            code_table[node.char] = code
        else:
            if node.left:
                traverse(node.left, code + '0')
            if node.right:
                traverse(node.right, code + '1')
    
    traverse(root, '')
    return code_table


def huffman_encode(text: str) -> Tuple[str, HuffmanNode]:
    """
    Encode text using Huffman coding.
    Returns the encoded binary string and the tree (needed for decoding).
    """
    if not text:
        return '', None
    
    root = build_huffman_tree(text)
    code_table = build_code_table(root)
    
    # Encode each character using the code table
    encoded = ''.join(code_table[char] for char in text)
    
    return encoded, root


def huffman_decode(encoded: str, root: Optional[HuffmanNode]) -> str:
    """
    Decode a Huffman-encoded binary string using the tree.
    """
    if not encoded or root is None:
        return ''
    
    # Special case: single character
    if root.is_leaf():
        return root.char * len(encoded)
    
    decoded = []
    current = root
    
    # Traverse the tree based on each bit
    for bit in encoded:
        if bit == '0':
            current = current.left
        else:
            current = current.right
        
        # Found a leaf node, that's our character
        if current.is_leaf():
            decoded.append(current.char)
            current = root  # Reset to root for next character
    
    return ''.join(decoded)


def analyze_compression(original: str, encoded: str) -> None:
    """
    Print compression statistics comparing original and encoded sizes.
    """
    original_bits = len(original) * 8  # ASCII = 8 bits per char
    encoded_bits = len(encoded)
    
    if original_bits > 0:
        ratio = (1 - encoded_bits / original_bits) * 100
    else:
        ratio = 0
    
    print(f"\n{'='*50}")
    print("COMPRESSION STATS")
    print(f"{'='*50}")
    print(f"Original size:    {len(original)} chars ({original_bits} bits)")
    print(f"Encoded size:     {encoded_bits} bits")
    print(f"Compression:      {ratio:.2f}% savings")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    # Demo with a sample text that has varied character frequencies
    sample_text = "hello world! this is a huffman coding example. compression works best with repeated characters!!!"
    
    print("HUFFMAN CODING DEMO")
    print(f"\nOriginal text:\n{sample_text}")
    
    # Encode the text
    encoded_bits, tree = huffman_encode(sample_text)
    
    # Show the code table
    code_table = build_code_table(tree)
    print("\nGenerated Huffman Codes:")
    for char, code in sorted(code_table.items(), key=lambda x: len(x[1])):
        display_char = repr(char) if char in [' ', '\n', '\t'] else char
        print(f"  {display_char:>5} -> {code}")
    
    print(f"\nEncoded (first 80 bits): {encoded_bits[:80]}...")
    
    # Decode to verify correctness
    decoded_text = huffman_decode(encoded_bits, tree)
    
    print(f"\nDecoded text:\n{decoded_text}")
    print(f"\nDecoding {'SUCCESS' if decoded_text == sample_text else 'FAILED'}!")
    
    # Show compression statistics
    analyze_compression(sample_text, encoded_bits)