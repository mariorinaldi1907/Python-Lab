"""
Date: 2026-07-26
Built a word ladder puzzle solver that finds the shortest path between two words by changing one letter at a time — uses BFS and a dictionary lookup for valid words.
"""

#!/usr/bin/env python3
"""
Word Ladder Solver - finds the shortest transformation between two words.

A word ladder is a sequence where each word differs from the previous by exactly
one letter. For example: CAT -> COT -> DOT -> DOG

I built this because I always found these puzzles interesting but tedious to solve
manually. The BFS approach guarantees we find the shortest path if one exists.
"""

from collections import deque
from typing import List, Set, Optional


def load_dictionary() -> Set[str]:
    """
    Load a simple dictionary of common 3-letter words.
    
    In a real version I'd load from /usr/share/dict/words or similar,
    but keeping it self-contained here for portability.
    """
    # Just a small sample dictionary for demo purposes
    words = {
        'cat', 'cot', 'dot', 'dog', 'bat', 'hat', 'hot', 'lot', 'log', 'lag',
        'bag', 'big', 'pig', 'pit', 'sit', 'sat', 'mat', 'map', 'tap', 'top',
        'pop', 'pot', 'rot', 'rat', 'rag', 'rug', 'rut', 'cut', 'cup', 'cop',
        'cap', 'car', 'bar', 'far', 'fat', 'fit', 'hit', 'kit', 'bit', 'bet',
        'set', 'net', 'not', 'nut', 'but', 'bud', 'bad', 'bed', 'red', 'rod',
        'god', 'got', 'gut', 'gag', 'gas', 'has', 'was', 'way', 'bay', 'day',
        'say', 'may', 'man', 'can', 'ban', 'tan', 'tag', 'wag', 'wan', 'win',
        'wit', 'wet', 'get', 'jet', 'yet', 'yes', 'yep', 'pep', 'per', 'pet'
    }
    return words


def get_neighbors(word: str, dictionary: Set[str]) -> List[str]:
    """
    Find all valid words that differ from the given word by exactly one letter.
    
    This is the core of the graph connectivity — each word is a node,
    and edges exist to words that differ by one character.
    """
    neighbors = []
    word_list = list(word)
    
    # Try replacing each position with every letter a-z
    for i in range(len(word)):
        original_char = word_list[i]
        for c in 'abcdefghijklmnopqrstuvwxyz':
            if c == original_char:
                continue
            word_list[i] = c
            candidate = ''.join(word_list)
            if candidate in dictionary:
                neighbors.append(candidate)
        word_list[i] = original_char  # restore original character
    
    return neighbors


def find_word_ladder(start: str, end: str, dictionary: Set[str]) -> Optional[List[str]]:
    """
    Use BFS to find the shortest word ladder from start to end.
    
    Returns the path as a list of words, or None if no path exists.
    BFS is perfect here because we want the *shortest* path, and BFS
    explores level-by-level, guaranteeing the first solution found is optimal.
    """
    if start not in dictionary or end not in dictionary:
        return None
    
    if start == end:
        return [start]
    
    # BFS setup: queue stores (current_word, path_to_current_word)
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        current_word, path = queue.popleft()
        
        # Explore all neighbors (words differing by one letter)
        for neighbor in get_neighbors(current_word, dictionary):
            if neighbor == end:
                return path + [neighbor]
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    return None  # No path found


def print_ladder(ladder: Optional[List[str]]) -> None:
    """
    Pretty-print the word ladder result.
    
    Shows each transformation step with an arrow for readability.
    """
    if ladder is None:
        print("No word ladder found!")
    else:
        print(f"Found ladder in {len(ladder)} steps:")
        for i, word in enumerate(ladder):
            if i == 0:
                print(f"  {word.upper()}")
            else:
                print(f"  ↓")
                print(f"  {word.upper()}")


if __name__ == "__main__":
    print("=== Word Ladder Solver ===\n")
    
    # Load our dictionary
    dictionary = load_dictionary()
    print(f"Dictionary loaded with {len(dictionary)} words.\n")
    
    # Test case 1: Classic CAT to DOG
    print("Example 1: CAT → DOG")
    ladder = find_word_ladder('cat', 'dog', dictionary)
    print_ladder(ladder)
    print()
    
    # Test case 2: Another transformation
    print("Example 2: HIT → COT")
    ladder = find_word_ladder('hit', 'cot', dictionary)
    print_ladder(ladder)
    print()
    
    # Test case 3: Longer path
    print("Example 3: BAT → WIN")
    ladder = find_word_ladder('bat', 'win', dictionary)
    print_ladder(ladder)
    print()
    
    # Test case 4: No path exists (demonstrate failure case)
    print("Example 4: PIG → YEP (checking if path exists)")
    ladder = find_word_ladder('pig', 'yep', dictionary)
    print_ladder(ladder)