"""
Date: 2026-08-21
Implemented Huffman coding with a priority queue to compress text — wanted to see the algorithm work end-to-end with real compression stats.
"""

"""
Huffman coding implementation for text compression.

I built this to understand how Huffman trees work under the hood.
The algorithm builds a binary tree based on character frequencies,
then generates variable-length codes where common chars get shorter codes.
"""

import heapq
from collections import Counter, defaultdict


class HuffmanNode:
    """
    Node in the Huffman tree.
    
    Uses comparison methods so heapq can order nodes by frequency.
    I added a counter to break ties consistently — without it, Python
    complains when frequencies match and it tries to compare the actual chars.
    """
    _id_counter = 0
    
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None
        self.id = HuffmanNode._id_counter
        HuffmanNode._id_counter += 1
    
    def __lt__(self, other):
        if self.freq != other.freq:
            return self.freq < other.freq
        return self.id < other.id


def build_frequency_table(text):
    """Count how often each character appears in the text."""
    return Counter(text)


def build_huffman_tree(freq_table):
    """
    Construct the Huffman tree using a min-heap.
    
    The algorithm repeatedly pulls the two smallest nodes,
    combines them under a parent, and pushes back. Eventually
    you're left with one root node containing the whole tree.
    """
    if not freq_table:
        return None
    
    # Start with a leaf node for each character
    heap = [HuffmanNode(char, freq) for char, freq in freq_table.items()]
    heapq.heapify(heap)
    
    # Edge case: single character in text
    if len(heap) == 1:
        root = HuffmanNode(None, heap[0].freq)
        root.left = heap[0]
        return root
    
    # Build tree bottom-up
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        
        parent = HuffmanNode(None, left.freq + right.freq)
        parent.left = left
        parent.right = right
        
        heapq.heappush(heap, parent)
    
    return heap[0]


def generate_codes(root):
    """
    Traverse the tree to generate binary codes for each character.
    
    Left edges add '0', right edges add '1'. I'm using a dict because
    lookups during encoding need to be fast.
    """
    if root is None:
        return {}
    
    codes = {}
    
    def traverse(node, current_code):
        if node is None:
            return
        
        # Leaf node — we found a character
        if node.char is not None:
            codes[node.char] = current_code if current_code else '0'
            return
        
        traverse(node.left, current_code + '0')
        traverse(node.right, current_code + '1')
    
    traverse(root, '')
    return codes


def encode(text):
    """
    Compress text using Huffman coding.
    
    Returns the encoded bitstring and the tree (needed for decoding).
    In a real implementation, you'd serialize the tree too, but I'm
    keeping it separate here for clarity.
    """
    if not text:
        return '', None
    
    freq_table = build_frequency_table(text)
    tree = build_huffman_tree(freq_table)
    codes = generate_codes(tree)
    
    encoded = ''.join(codes[char] for char in text)
    return encoded, tree


def decode(encoded_bits, tree):
    """
    Decompress a Huffman-encoded bitstring.
    
    Walk the tree: '0' means go left, '1' means go right.
    When you hit a leaf, output that character and reset to root.
    """
    if not encoded_bits or tree is None:
        return ''
    
    decoded = []
    current = tree
    
    for bit in encoded_bits:
        # Traverse based on bit value
        if bit == '0':
            current = current.left
        else:
            current = current.right
        
        # Hit a leaf node — found a character
        if current.char is not None:
            decoded.append(current.char)
            current = tree  # Reset to root for next character
    
    return ''.join(decoded)


def compression_stats(original, encoded):
    """Calculate and display compression metrics."""
    original_bits = len(original) * 8  # ASCII is 8 bits per char
    encoded_bits = len(encoded)
    
    ratio = (1 - encoded_bits / original_bits) * 100 if original_bits > 0 else 0
    
    return {
        'original_bits': original_bits,
        'encoded_bits': encoded_bits,
        'compression_ratio': ratio
    }


if __name__ == "__main__":
    # Test with a few different strings to see how it performs
    
    print("=== Huffman Compression Demo ===\n")
    
    test_cases = [
        "hello world",
        "aaaaaabbbbcccd",
        "The quick brown fox jumps over the lazy dog",
        "aaaaaa"  # Edge case: single repeated character
    ]
    
    for text in test_cases:
        print(f"Original text: \"{text}\"")
        print(f"Length: {len(text)} characters\n")
        
        # Encode
        encoded, tree = encode(text)
        
        # Show the generated codes
        codes = generate_codes(tree)
        print("Huffman codes:")
        for char, code in sorted(codes.items(), key=lambda x: len(x[1])):
            print(f"  '{char}': {code}")
        
        print(f"\nEncoded: {encoded[:60]}{'...' if len(encoded) > 60 else ''}")
        
        # Decode to verify it works
        decoded = decode(encoded, tree)
        print(f"Decoded: \"{decoded[:60]}{'...' if len(decoded) > 60 else ''}\"")
        print(f"Match: {decoded == text}")
        
        # Stats
        stats = compression_stats(text, encoded)
        print(f"\nCompression: {stats['original_bits']} bits → {stats['encoded_bits']} bits")
        print(f"Ratio: {stats['compression_ratio']:.1f}% reduction")
        print("\n" + "="*50 + "\n")