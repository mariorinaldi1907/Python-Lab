"""
Date: 2026-06-06
Created a BFS-based word ladder solver that transforms one word into another by changing a single letter per step, using only valid English words from a dictionary.
"""

"""
Word Ladder Solver - finds the shortest transformation sequence between two words.

A word ladder is a sequence where each word differs by exactly one letter from
the previous word. This uses BFS to guarantee the shortest path.
"""

from collections import deque
from typing import List, Set, Optional, Tuple


def get_word_neighbors(word: str, word_set: Set[str]) -> List[str]:
    """
    Generate all valid one-letter variations of a word that exist in the dictionary.
    
    Args:
        word: The source word to generate neighbors for
        word_set: Set of valid dictionary words
        
    Returns:
        List of valid neighboring words
    """
    neighbors = []
    # Try replacing each position with every letter a-z
    for i in range(len(word)):
        for char in 'abcdefghijklmnopqrstuvwxyz':
            if char != word[i]:  # Skip if it's the same letter
                neighbor = word[:i] + char + word[i+1:]
                if neighbor in word_set:
                    neighbors.append(neighbor)
    return neighbors


def word_ladder(start: str, end: str, word_list: List[str]) -> Optional[List[str]]:
    """
    Find the shortest word ladder from start to end using BFS.
    
    I chose BFS because it guarantees finding the shortest path in an unweighted graph.
    Each word is a node, and edges exist between words that differ by one letter.
    
    Args:
        start: Starting word
        end: Target word
        word_list: List of valid dictionary words
        
    Returns:
        List representing the ladder path, or None if no path exists
    """
    # Quick validation
    if start == end:
        return [start]
    
    word_set = set(word_list)
    if end not in word_set:
        return None
    
    # BFS setup: queue stores (current_word, path_to_current_word)
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        current_word, path = queue.popleft()
        
        # Check all valid one-letter transformations
        for neighbor in get_word_neighbors(current_word, word_set):
            if neighbor == end:
                return path + [neighbor]
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    # No path found
    return None


def build_sample_dictionary() -> List[str]:
    """
    Build a small dictionary for demonstration.
    
    In a real implementation, I'd load from /usr/share/dict/words or similar,
    but keeping it self-contained for portability.
    
    Returns:
        List of valid words
    """
    # Handpicked words that create interesting ladder paths
    return [
        "hit", "hot", "dot", "dog", "lot", "log", "cog",
        "cat", "hat", "bat", "mat", "rat", "sat", "fat",
        "bit", "fit", "pit", "pot", "pat", "pal", "gal",
        "gel", "get", "set", "net", "met", "let", "led",
        "red", "ted", "bed", "bad", "bag", "big", "pig",
        "fig", "fog", "fag", "far", "bar", "car", "tar",
        "tan", "ten", "pen", "hen", "den", "men", "man",
        "mad", "may", "day", "bay", "way", "say", "pay"
    ]


def print_ladder(ladder: Optional[List[str]], start: str, end: str) -> None:
    """
    Pretty-print the word ladder result.
    
    Args:
        ladder: The word ladder path or None
        start: Starting word
        end: Ending word
    """
    print(f"\n{'='*50}")
    print(f"Word Ladder: {start.upper()} → {end.upper()}")
    print('='*50)
    
    if ladder is None:
        print("❌ No valid ladder found!")
    else:
        print(f"✓ Found ladder with {len(ladder)} steps:\n")
        for i, word in enumerate(ladder, 1):
            arrow = "   ↓" if i < len(ladder) else ""
            print(f"  {i}. {word}{arrow}")
        print(f"\nTotal transformations: {len(ladder) - 1}")


if __name__ == "__main__":
    # Build our working dictionary
    dictionary = build_sample_dictionary()
    print(f"Loaded dictionary with {len(dictionary)} words")
    
    # Test case 1: Classic hit → cog transformation
    result = word_ladder("hit", "cog", dictionary)
    print_ladder(result, "hit", "cog")
    
    # Test case 2: cat → dog (should exist in our dict)
    result = word_ladder("cat", "dog", dictionary)
    print_ladder(result, "cat", "dog")
    
    # Test case 3: Impossible transformation
    result = word_ladder("hit", "man", dictionary)
    print_ladder(result, "hit", "man")
    
    # Test case 4: Same word edge case
    result = word_ladder("cat", "cat", dictionary)
    print_ladder(result, "cat", "cat")