"""
Date: 2026-08-07
Implemented a word ladder puzzle solver that uses breadth-first search to find the shortest transformation sequence between two words, where each step changes exactly one letter.
"""

#!/usr/bin/env python3
"""
Word Ladder Solver using BFS
Finds the shortest transformation sequence between two words where each
intermediate step is a valid word and differs by exactly one letter.
"""

from collections import deque
from typing import List, Set, Optional


def load_word_list() -> Set[str]:
    """
    Load a basic word list for demo purposes.
    In a real scenario, I'd load from /usr/share/dict/words or a file.
    For now, using a curated list that makes interesting ladders.
    """
    words = {
        "hit", "hot", "dot", "dog", "log", "cog",
        "lot", "lit", "sit", "set", "sat", "mat",
        "cat", "can", "man", "men", "pen", "hen",
        "hat", "bat", "bad", "bed", "bid", "did",
        "dad", "mad", "sad", "say", "bay", "day",
        "way", "war", "car", "bar", "far", "tar",
        "tan", "ten", "tea", "sea", "see", "bee",
        "bet", "but", "put", "pot", "cot", "cut",
        "gut", "get", "wet", "net", "not", "now",
        "cow", "how", "low", "law", "paw", "pay",
        "ply", "fly", "try", "cry", "dry", "dye"
    }
    return words


def get_neighbors(word: str, word_set: Set[str]) -> List[str]:
    """
    Generate all valid neighbors of a word by changing one letter.
    Only returns words that exist in the word_set.
    
    This is the key function — I iterate through each position and try
    all 26 letters to see what's valid. Could optimize with preprocessing
    but this is clear and works well for reasonable word sets.
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
    Use BFS to find the shortest word ladder from start to end.
    
    Returns the complete path as a list, or None if no path exists.
    BFS guarantees we find the shortest path because we explore level by level.
    """
    if start == end:
        return [start]
    
    if start not in word_set or end not in word_set:
        return None
    
    # BFS setup: queue stores (current_word, path_so_far)
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        current_word, path = queue.popleft()
        
        # Try all single-letter transformations
        for neighbor in get_neighbors(current_word, word_set):
            if neighbor == end:
                # Found it! Return the complete path
                return path + [neighbor]
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    # No path exists
    return None


def print_ladder(ladder: Optional[List[str]], start: str, end: str) -> None:
    """
    Pretty-print the word ladder result.
    Highlights which letter changed at each step — useful for visualization.
    """
    if ladder is None:
        print(f"No word ladder found from '{start}' to '{end}'")
        return
    
    print(f"Word ladder from '{start}' to '{end}' ({len(ladder)} steps):")
    for i, word in enumerate(ladder):
        if i == 0:
            print(f"  {i+1}. {word} (start)")
        elif i == len(ladder) - 1:
            print(f"  {i+1}. {word} (goal!)")
        else:
            # Find which letter changed from previous word
            prev = ladder[i-1]
            changed_pos = next((j for j in range(len(word)) if word[j] != prev[j]), -1)
            if changed_pos >= 0:
                print(f"  {i+1}. {word} (changed position {changed_pos}: {prev[changed_pos]} → {word[changed_pos]})")
            else:
                print(f"  {i+1}. {word}")


if __name__ == "__main__":
    # Load our word dictionary
    word_set = load_word_list()
    
    print("=== Word Ladder Solver (BFS) ===\n")
    
    # Test case 1: Classic example
    print("Example 1:")
    ladder1 = find_word_ladder("hit", "cog", word_set)
    print_ladder(ladder1, "hit", "cog")
    
    print("\n" + "="*40 + "\n")
    
    # Test case 2: Longer path
    print("Example 2:")
    ladder2 = find_word_ladder("cat", "dog", word_set)
    print_ladder(ladder2, "cat", "dog")
    
    print("\n" + "="*40 + "\n")
    
    # Test case 3: Impossible transformation
    print("Example 3 (impossible):")
    ladder3 = find_word_ladder("hit", "fly", word_set)
    print_ladder(ladder3, "hit", "fly")
    
    print("\n" + "="*40 + "\n")
    
    # Test case 4: Short path
    print("Example 4 (short path):")
    ladder4 = find_word_ladder("bat", "cat", word_set)
    print_ladder(ladder4, "bat", "cat")