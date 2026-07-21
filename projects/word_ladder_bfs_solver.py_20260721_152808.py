"""
Date: 2026-07-21
Implemented a BFS-based word ladder puzzle solver that finds the shortest transformation sequence between two words, because I wanted to visualize how graph search works on something concrete.
"""

#!/usr/bin/env python3
"""
Word Ladder Solver using BFS

A word ladder puzzle asks you to transform one word into another by changing
exactly one letter at a time, with each intermediate step being a valid word.
This solver uses breadth-first search to find the shortest path.

Example: CAT -> DOG
CAT -> COT -> DOT -> DOG
"""

from collections import deque
from typing import List, Set, Dict, Optional


def load_dictionary(word_length: int) -> Set[str]:
    """
    Load a small built-in dictionary of common words.
    In a real implementation, you'd load from /usr/share/dict/words or similar.
    For demo purposes, I'm hardcoding some common 3-letter words.
    
    Args:
        word_length: Only return words of this length
        
    Returns:
        Set of valid words
    """
    # Small dictionary for demonstration - normally you'd read from a file
    words = {
        "cat", "cot", "dot", "dog", "bat", "hat", "hot", "lot", "log",
        "hog", "fog", "cog", "hit", "bit", "sit", "set", "get", "got",
        "rot", "pot", "pat", "rat", "mat", "sat", "fat", "fit", "pit",
        "pet", "met", "net", "wet", "let", "bet", "but", "cut", "gut",
        "hut", "nut", "not", "now", "how", "cow", "low", "bow", "row",
        "tow", "toy", "boy", "box", "fox", "fix", "six", "sin", "son",
        "sun", "bun", "bus", "bye", "dye", "eye", "ice", "ace", "age",
        "are", "art", "ate", "oak", "oar", "far", "fan", "can", "car"
    }
    
    return {w for w in words if len(w) == word_length}


def get_neighbors(word: str, dictionary: Set[str]) -> List[str]:
    """
    Find all valid words that differ by exactly one letter.
    
    This is the core of the graph construction — each word is a node,
    and edges exist between words that differ by one character.
    
    Args:
        word: Current word
        dictionary: Set of all valid words
        
    Returns:
        List of neighboring words
    """
    neighbors = []
    
    # Try changing each position to every letter
    for i in range(len(word)):
        for c in 'abcdefghijklmnopqrstuvwxyz':
            if c == word[i]:
                continue  # Skip the same letter
                
            # Build new word with one letter changed
            candidate = word[:i] + c + word[i+1:]
            
            if candidate in dictionary:
                neighbors.append(candidate)
    
    return neighbors


def find_word_ladder(start: str, end: str, dictionary: Set[str]) -> Optional[List[str]]:
    """
    Use BFS to find the shortest word ladder from start to end.
    
    BFS guarantees we find the shortest path because we explore all words
    at distance N before exploring any at distance N+1.
    
    Args:
        start: Starting word
        end: Target word
        dictionary: Set of valid words
        
    Returns:
        List representing the ladder path, or None if no path exists
    """
    if start == end:
        return [start]
    
    if start not in dictionary or end not in dictionary:
        return None
    
    # BFS queue: each element is (current_word, path_to_reach_it)
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        current_word, path = queue.popleft()
        
        # Check all neighbors (words that differ by one letter)
        for neighbor in get_neighbors(current_word, dictionary):
            if neighbor == end:
                # Found it! Return the complete path
                return path + [neighbor]
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    # No path exists
    return None


def print_ladder(ladder: Optional[List[str]]) -> None:
    """
    Pretty-print a word ladder with arrows and change highlighting.
    
    Args:
        ladder: The word ladder path to print
    """
    if ladder is None:
        print("No ladder found!")
        return
    
    print(f"\nFound ladder with {len(ladder)} words:")
    print("=" * 40)
    
    for i, word in enumerate(ladder):
        print(f"  {word.upper()}")
        
        if i < len(ladder) - 1:
            # Show which letter changed
            next_word = ladder[i + 1]
            changes = [j for j in range(len(word)) if word[j] != next_word[j]]
            if changes:
                print(f"    ↓ (change position {changes[0]}: {word[changes[0]]} → {next_word[changes[0]]})")


if __name__ == "__main__":
    print("Word Ladder Solver")
    print("=" * 40)
    
    # Demo 1: Classic CAT -> DOG
    print("\n[Demo 1] CAT -> DOG")
    dictionary = load_dictionary(3)
    ladder = find_word_ladder("cat", "dog", dictionary)
    print_ladder(ladder)
    
    # Demo 2: Longer path
    print("\n[Demo 2] HIT -> COG")
    ladder = find_word_ladder("hit", "cog", dictionary)
    print_ladder(ladder)
    
    # Demo 3: No path exists
    print("\n[Demo 3] CAT -> ICE (testing unreachable words)")
    ladder = find_word_ladder("cat", "ice", dictionary)
    print_ladder(ladder)
    
    # Show some stats
    print("\n" + "=" * 40)
    print(f"Dictionary size: {len(dictionary)} words")
    print(f"Sample words: {sorted(list(dictionary))[:20]}")