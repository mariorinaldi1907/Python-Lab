"""
Date: 2026-08-01
Built a word ladder puzzle solver that finds the shortest chain of single-letter transformations between two words using breadth-first search.
"""

#!/usr/bin/env python3
"""
Word Ladder Solver
Finds the shortest transformation sequence from start_word to end_word,
where each intermediate word differs by exactly one letter.
"""

from collections import deque
from typing import List, Set, Optional


def get_neighbors(word: str, word_set: Set[str]) -> List[str]:
    """
    Generate all valid one-letter transformations of a word.
    
    Args:
        word: The current word to transform
        word_set: Set of valid dictionary words
    
    Returns:
        List of valid neighboring words (one letter different)
    """
    neighbors = []
    # Try replacing each position with every letter a-z
    for i in range(len(word)):
        for char in 'abcdefghijklmnopqrstuvwxyz':
            if char == word[i]:
                continue  # Skip if it's the same letter
            
            # Build the candidate word
            candidate = word[:i] + char + word[i+1:]
            
            if candidate in word_set:
                neighbors.append(candidate)
    
    return neighbors


def find_word_ladder(start: str, end: str, word_list: List[str]) -> Optional[List[str]]:
    """
    Find shortest word ladder from start to end using BFS.
    
    The BFS approach guarantees we find the shortest path because we explore
    all words at distance n before exploring any at distance n+1.
    
    Args:
        start: Starting word
        end: Target word
        word_list: List of valid dictionary words
    
    Returns:
        List representing the transformation path, or None if no path exists
    """
    if start == end:
        return [start]
    
    # Convert to set for O(1) lookup - important for performance
    word_set = set(word_list)
    
    if end not in word_set:
        return None
    
    # BFS queue stores tuples of (current_word, path_to_current_word)
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        current_word, path = queue.popleft()
        
        # Check all possible one-letter transformations
        for neighbor in get_neighbors(current_word, word_set):
            if neighbor == end:
                return path + [neighbor]
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    # No path found
    return None


def print_ladder(ladder: Optional[List[str]]) -> None:
    """
    Pretty-print a word ladder with arrows and transformation highlights.
    
    Args:
        ladder: List of words forming the transformation path
    """
    if ladder is None:
        print("No valid ladder found!")
        return
    
    print(f"\nFound ladder with {len(ladder)} words:")
    print("-" * 40)
    
    for i, word in enumerate(ladder):
        if i > 0:
            # Highlight which letter changed from previous word
            prev = ladder[i-1]
            highlighted = ""
            for j, char in enumerate(word):
                if char != prev[j]:
                    highlighted += f"[{char}]"
                else:
                    highlighted += char
            print(f"  ↓")
            print(f"{i+1}. {highlighted} ({word})")
        else:
            print(f"{i+1}. {word}")
    
    print("-" * 40)


if __name__ == "__main__":
    # Demo with a small curated dictionary
    # In practice, you'd load from a file like /usr/share/dict/words
    demo_words = [
        "cat", "bat", "hat", "mat", "rat", "sat",
        "car", "bar", "tar", "mar",
        "cot", "bot", "hot", "lot", "pot", "rot",
        "cut", "but", "hut", "jut", "nut", "rut",
        "can", "ban", "fan", "man", "pan", "ran", "tan", "van",
        "cog", "dog", "fog", "hog", "jog", "log",
        "cab", "dab", "gab", "jab", "lab", "tab",
        "cap", "gap", "lap", "map", "nap", "rap", "sap", "tap",
        "cop", "hop", "mop", "pop", "sop", "top"
    ]
    
    print("=" * 40)
    print("Word Ladder Solver Demo")
    print("=" * 40)
    
    # Test case 1: Simple transformation
    print("\n[Test 1] cat → hat")
    ladder1 = find_word_ladder("cat", "hat", demo_words)
    print_ladder(ladder1)
    
    # Test case 2: Longer chain
    print("\n[Test 2] cat → dog")
    ladder2 = find_word_ladder("cat", "dog", demo_words)
    print_ladder(ladder2)
    
    # Test case 3: Multiple hops
    print("\n[Test 3] cat → cop")
    ladder3 = find_word_ladder("cat", "cop", demo_words)
    print_ladder(ladder3)
    
    # Test case 4: No solution
    print("\n[Test 4] cat → van (should fail)")
    ladder4 = find_word_ladder("cat", "xyz", demo_words)
    print_ladder(ladder4)