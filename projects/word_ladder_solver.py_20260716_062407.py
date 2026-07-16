"""
Date: 2026-07-16
Built a word ladder puzzle solver that finds the shortest transformation sequence between two words using breadth-first search — handles arbitrary dictionary sizes and validates paths.
"""

#!/usr/bin/env python3
"""
Word Ladder Solver - finds shortest path between two words by changing one letter at a time.

I wanted to tackle this classic problem because it's a nice application of BFS and
demonstrates how graph algorithms can solve word puzzles. The idea is simple:
each word is a node, and two words are connected if they differ by exactly one letter.
"""

from collections import deque
from typing import List, Set, Optional, Tuple


def get_neighbors(word: str, word_set: Set[str]) -> List[str]:
    """
    Find all valid words that differ from the input word by exactly one letter.
    
    This is the core of building our graph — we try replacing each position
    with every letter a-z and check if it's in our dictionary. I'm using a set
    for O(1) lookups instead of iterating through the whole word list.
    """
    neighbors = []
    for i in range(len(word)):
        for c in 'abcdefghijklmnopqrstuvwxyz':
            if c != word[i]:
                candidate = word[:i] + c + word[i+1:]
                if candidate in word_set:
                    neighbors.append(candidate)
    return neighbors


def word_ladder(start: str, end: str, word_list: List[str]) -> Optional[List[str]]:
    """
    Find the shortest transformation sequence from start to end word.
    
    Uses BFS because we want the *shortest* path. DFS would find *a* path but
    not necessarily the optimal one. Returns None if no path exists.
    """
    # Edge cases that would waste computation time
    if start == end:
        return [start]
    
    if len(start) != len(end):
        return None
    
    # Convert to set for faster lookups and ensure both words are available
    word_set = set(word_list)
    if end not in word_set:
        return None
    
    # BFS setup: queue stores (current_word, path_to_reach_it)
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        current_word, path = queue.popleft()
        
        # Try all one-letter transformations
        for neighbor in get_neighbors(current_word, word_set):
            if neighbor == end:
                return path + [neighbor]
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    # No path found
    return None


def find_all_ladders(start: str, end: str, word_list: List[str]) -> List[List[str]]:
    """
    Find ALL shortest transformation sequences (there might be multiple).
    
    This is trickier than finding just one path. We need to track all paths
    at each level and only move to the next level when we've exhausted the current one.
    """
    if start == end:
        return [[start]]
    
    if len(start) != len(end):
        return []
    
    word_set = set(word_list)
    if end not in word_set:
        return []
    
    # Track all paths that reach each word
    level = {start: [[start]]}
    visited = {start}
    
    while level:
        next_level = {}
        
        # Process all words at current distance
        for word in level:
            for neighbor in get_neighbors(word, word_set):
                if neighbor == end:
                    # Found the target! Return all paths that reach it
                    return [path + [end] for path in level[word]]
                
                if neighbor not in visited:
                    if neighbor not in next_level:
                        next_level[neighbor] = []
                    # Extend all paths to this word
                    for path in level[word]:
                        next_level[neighbor].append(path + [neighbor])
        
        # Mark this level as visited (prevents cycles)
        visited.update(next_level.keys())
        level = next_level
    
    return []


def print_ladder(ladder: Optional[List[str]]) -> None:
    """Pretty print a word ladder with arrows showing the transformation."""
    if ladder is None:
        print("No valid transformation found!")
        return
    
    print(f"Found ladder with {len(ladder)} steps:")
    for i, word in enumerate(ladder):
        if i < len(ladder) - 1:
            print(f"  {word} → ", end="")
        else:
            print(f"{word}")


if __name__ == "__main__":
    # Test with a small dictionary - in production you'd load from a file
    # I'm using common 4-letter words here to make the demo interesting
    test_dictionary = [
        "cold", "cord", "card", "ward", "warm", "harm", "farm", "form",
        "word", "work", "pork", "port", "part", "hart", "hard", "hare",
        "care", "case", "cast", "cost", "host", "post", "pose", "pore",
        "core", "come", "home", "hole", "hold", "bold", "told", "toll",
        "tall", "tale", "talk", "walk", "wall", "will", "well", "sell"
    ]
    
    print("=" * 60)
    print("WORD LADDER SOLVER")
    print("=" * 60)
    
    # Test case 1: Simple transformation
    print("\n[Test 1] Transform 'cold' to 'warm'")
    ladder1 = word_ladder("cold", "warm", test_dictionary)
    print_ladder(ladder1)
    
    # Test case 2: Longer path
    print("\n[Test 2] Transform 'cold' to 'tall'")
    ladder2 = word_ladder("cold", "tall", test_dictionary)
    print_ladder(ladder2)
    
    # Test case 3: Multiple shortest paths
    print("\n[Test 3] All shortest paths from 'care' to 'cost'")
    all_ladders = find_all_ladders("care", "cost", test_dictionary)
    if all_ladders:
        print(f"Found {len(all_ladders)} shortest path(s):")
        for i, ladder in enumerate(all_ladders, 1):
            print(f"  Path {i}: {' → '.join(ladder)}")
    else:
        print("No paths found!")
    
    # Test case 4: Impossible transformation
    print("\n[Test 4] Impossible: 'cold' to 'cats' (not in dictionary)")
    ladder3 = word_ladder("cold", "cats", test_dictionary)
    print_ladder(ladder3)
    
    print("\n" + "=" * 60)