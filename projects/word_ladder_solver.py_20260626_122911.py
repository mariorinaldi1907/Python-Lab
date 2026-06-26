"""
Date: 2026-06-26
Implemented a BFS-based word ladder solver that transforms one word into another through valid dictionary words, changing only one letter at a time.
"""

#!/usr/bin/env python3
"""
Word Ladder Solver - finds the shortest transformation sequence between two words.

A word ladder is a sequence where each word differs from the previous by exactly one letter.
For example: CAT -> COT -> DOT -> DOG transforms "CAT" into "DOG" in 4 steps.

I wrote this because word ladders are a fun puzzle and BFS is the perfect algorithm for 
finding the shortest path. The trick is generating neighbors efficiently without checking
every possible single-letter mutation.
"""

from collections import deque
from typing import List, Set, Optional, Dict


def load_word_list() -> Set[str]:
    """
    Load a basic word list for demonstration purposes.
    
    In a real implementation, you'd load from /usr/share/dict/words or a file.
    For this demo, I'm using a small hardcoded set that creates interesting ladders.
    """
    words = {
        'cat', 'cot', 'dot', 'dog', 'dig', 'dug', 'bug', 'bag', 'bat',
        'hat', 'hot', 'hog', 'log', 'lag', 'rag', 'tag', 'tan', 'can',
        'cog', 'fog', 'fig', 'pig', 'pit', 'sit', 'set', 'let', 'lot',
        'got', 'gat', 'rat', 'mat', 'map', 'tap', 'top', 'pot', 'pat',
        'hit', 'bit', 'big', 'wig', 'wag', 'way', 'say', 'day', 'dam',
        'dim', 'din', 'pin', 'pan', 'van', 'ban', 'bad', 'bed', 'bid',
        'did', 'dad', 'mad', 'sad', 'had', 'has', 'was', 'war', 'car',
        'far', 'fat', 'eat', 'oat', 'out', 'our', 'sour', 'four', 'pour'
    }
    return words


def get_neighbors(word: str, word_set: Set[str]) -> List[str]:
    """
    Find all valid words that differ by exactly one letter.
    
    Instead of trying every letter at every position (26 * len(word) checks),
    I generate all possible mutations and check if they exist in the word set.
    This is O(26 * len(word)) but with an O(1) lookup, so it's fast.
    """
    neighbors = []
    for i in range(len(word)):
        for c in 'abcdefghijklmnopqrstuvwxyz':
            if c != word[i]:
                candidate = word[:i] + c + word[i+1:]
                if candidate in word_set:
                    neighbors.append(candidate)
    return neighbors


def find_word_ladder(start: str, end: str, word_set: Set[str]) -> Optional[List[str]]:
    """
    Find the shortest word ladder from start to end using BFS.
    
    BFS guarantees we find the shortest path because it explores all words
    at distance k before exploring any at distance k+1. I'm keeping track
    of the full path in the queue rather than reconstructing it at the end,
    which uses more memory but simplifies the code.
    
    Returns the path as a list, or None if no ladder exists.
    """
    if start == end:
        return [start]
    
    if start not in word_set or end not in word_set:
        return None
    
    # Queue stores tuples of (current_word, path_to_current_word)
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        current_word, path = queue.popleft()
        
        for neighbor in get_neighbors(current_word, word_set):
            if neighbor == end:
                return path + [neighbor]
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    # No path found
    return None


def print_ladder(ladder: Optional[List[str]], start: str, end: str) -> None:
    """
    Pretty-print the word ladder result.
    
    Shows the transformation step-by-step with arrows, or a message if no path exists.
    """
    if ladder is None:
        print(f"No word ladder found from '{start}' to '{end}'")
    else:
        print(f"Found ladder from '{start}' to '{end}' in {len(ladder)} steps:")
        print(" -> ".join(ladder))
        print()


if __name__ == "__main__":
    # Load our word dictionary
    words = load_word_list()
    
    print("=== Word Ladder Solver ===\n")
    print(f"Dictionary size: {len(words)} words\n")
    
    # Test cases that showcase different scenarios
    test_cases = [
        ("cat", "dog"),  # Classic example
        ("hit", "cog"),  # Another common one
        ("pig", "bat"),  # Slightly longer path
        ("cat", "car"),  # Very short path
        ("hot", "cold"), # Impossible with our small dictionary
    ]
    
    for start, end in test_cases:
        ladder = find_word_ladder(start, end, words)
        print_ladder(ladder, start, end)
    
    # Interactive mode example (commented out for clean demo output)
    # Uncomment this block to try your own word pairs:
    """
    print("\n=== Try your own (Ctrl+C to exit) ===")
    while True:
        try:
            start = input("\nStart word: ").strip().lower()
            end = input("End word: ").strip().lower()
            ladder = find_word_ladder(start, end, words)
            print_ladder(ladder, start, end)
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            break
    """