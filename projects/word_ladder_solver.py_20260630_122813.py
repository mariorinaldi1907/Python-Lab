"""
Date: 2026-06-30
Built a word ladder puzzle solver using BFS to find the shortest transformation sequence between two words, like turning "cold" into "warm".
"""

#!/usr/bin/env python3
"""
Word Ladder Solver using BFS

Finds the shortest transformation sequence from a start word to an end word,
where each step changes exactly one letter and every intermediate word must be valid.
Classic BFS problem that I wanted to implement cleanly with a custom word list filter.
"""

from collections import deque
from typing import List, Set, Optional


def generate_neighbors(word: str, word_set: Set[str]) -> List[str]:
    """
    Generate all valid one-letter transformations of a word.
    
    Only returns words that exist in the provided word set.
    I'm iterating through each position and trying all 26 letters because
    it's more efficient than checking edit distance against every word.
    """
    neighbors = []
    for i in range(len(word)):
        for char in 'abcdefghijklmnopqrstuvwxyz':
            if char != word[i]:
                candidate = word[:i] + char + word[i+1:]
                if candidate in word_set:
                    neighbors.append(candidate)
    return neighbors


def find_word_ladder(start: str, end: str, word_list: List[str]) -> Optional[List[str]]:
    """
    Find shortest word ladder from start to end using BFS.
    
    Returns the transformation path if one exists, None otherwise.
    BFS guarantees we find the shortest path first, which is exactly what we want.
    """
    if start == end:
        return [start]
    
    # Convert to set for O(1) lookups
    word_set = set(word_list)
    
    if end not in word_set:
        return None
    
    # Add start word if it's not in the set (sometimes test cases do this)
    word_set.add(start)
    
    # BFS queue: each element is (current_word, path_to_current)
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        current_word, path = queue.popleft()
        
        # Try all one-letter transformations
        for neighbor in generate_neighbors(current_word, word_set):
            if neighbor == end:
                return path + [neighbor]
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    # No path found
    return None


def build_sample_dictionary() -> List[str]:
    """
    Create a small word list for demo purposes.
    
    In a real scenario I'd load from /usr/share/dict/words or similar,
    but keeping it self-contained for this demo.
    """
    return [
        "cold", "cord", "card", "ward", "warm",
        "gold", "fold", "food", "good", "wood",
        "hot", "dot", "dog", "cog", "log",
        "hit", "hot", "lot", "hat",
        "cat", "bat", "rat", "mat",
        "cape", "care", "card", "cart", "cars", "mars",
        "park", "part", "port", "post", "cost",
        "lost", "list", "last", "past", "fast",
        "cast", "case", "base", "bass", "pass",
        "pale", "sale", "tale", "tile", "file",
        "fill", "fall", "fail", "tail", "mail",
        "main", "pain", "gain", "rain", "ruin",
        "spin", "spit", "spot", "slot", "plot"
    ]


def print_ladder(ladder: Optional[List[str]], start: str, end: str):
    """
    Pretty print the word ladder result.
    
    Shows the transformation step by step with which letter changed.
    """
    if ladder is None:
        print(f"No path found from '{start}' to '{end}'")
        return
    
    print(f"Found ladder from '{start}' to '{end}' in {len(ladder)} steps:")
    print()
    for i, word in enumerate(ladder):
        if i == 0:
            print(f"  {i+1}. {word} (start)")
        elif i == len(ladder) - 1:
            print(f"  {i+1}. {word} (end)")
        else:
            # Find which letter changed from previous word
            prev = ladder[i-1]
            changed_pos = next(j for j in range(len(word)) if word[j] != prev[j])
            print(f"  {i+1}. {word} (changed position {changed_pos}: {prev[changed_pos]} → {word[changed_pos]})")


if __name__ == "__main__":
    print("=== Word Ladder Solver ===")
    print("Finding shortest paths between words by changing one letter at a time\n")
    
    dictionary = build_sample_dictionary()
    print(f"Dictionary size: {len(set(dictionary))} unique words\n")
    
    # Test case 1: Classic example
    test_cases = [
        ("cold", "warm"),
        ("hit", "cog"),
        ("cat", "dog"),
        ("pale", "rain"),
        ("cost", "pass"),
    ]
    
    for start, end in test_cases:
        print("-" * 50)
        result = find_word_ladder(start, end, dictionary)
        print_ladder(result, start, end)
        print()
    
    # Show an impossible case
    print("-" * 50)
    impossible = find_word_ladder("cold", "zzzzz", dictionary)
    print_ladder(impossible, "cold", "zzzzz")