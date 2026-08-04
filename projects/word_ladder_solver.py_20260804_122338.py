"""
Date: 2026-08-04
Implemented a BFS-based word ladder puzzle solver that finds the shortest transformation sequence between two words, because I've always found these puzzles satisfying to crack algorithmically.
"""

#!/usr/bin/env python3
"""
Word Ladder Solver - finds the shortest path between two words by changing
one letter at a time. Each intermediate step must be a valid English word.

I wanted to build this after doing too many of these puzzles manually.
The BFS approach guarantees we find the shortest ladder, which is exactly
what we want for these kinds of optimization problems.
"""

from collections import deque
from typing import List, Set, Optional, Dict


def load_word_list() -> Set[str]:
    """
    Returns a set of valid English words.
    
    Using a hardcoded list here since we can't rely on external files.
    In a real scenario, you'd read from /usr/share/dict/words or similar.
    This is a subset of common 4-5 letter words for demo purposes.
    """
    words = """
    cold cord card ward warm barn yarn yawn dawn fawn
    tall fall ball call wall mall malt halt salt sail
    said paid pair hair fair fail tail mail male tale
    hate have wave wove wore more mode made mare care
    core cove love lose rose pose page sage sane same
    came cape tape type tire fire hire wire wise rise
    rice race pace face fade made make take cake bake
    bike bile file fill pill pull bull dull gull gulf
    golf wolf work word ward wart cart cast last list
    """.split()
    return set(word.strip().lower() for word in words if word.strip())


def get_neighbors(word: str, word_set: Set[str]) -> List[str]:
    """
    Find all valid words that differ by exactly one letter.
    
    This is the core of the puzzle - we try replacing each position
    with every letter a-z and check if it's in our valid word set.
    I'm using a character range instead of hardcoding the alphabet
    because it feels cleaner.
    """
    neighbors = []
    for i in range(len(word)):
        for c in 'abcdefghijklmnopqrstuvwxyz':
            if c == word[i]:
                continue  # Skip if it's the same letter
            candidate = word[:i] + c + word[i+1:]
            if candidate in word_set:
                neighbors.append(candidate)
    return neighbors


def find_word_ladder(start: str, end: str, word_set: Set[str]) -> Optional[List[str]]:
    """
    Use BFS to find the shortest transformation sequence from start to end.
    
    BFS is perfect here because we want the *shortest* path. DFS would work
    but might give us a longer ladder. We track the parent of each word so
    we can reconstruct the path once we reach the target.
    
    Returns None if no ladder exists, otherwise returns the list of words
    forming the ladder from start to end.
    """
    start = start.lower()
    end = end.lower()
    
    # Quick validation - words need to be same length and both valid
    if len(start) != len(end):
        return None
    if start not in word_set or end not in word_set:
        return None
    if start == end:
        return [start]
    
    # BFS setup - queue holds words to explore, parent tracks how we got there
    queue = deque([start])
    visited = {start}
    parent: Dict[str, str] = {}
    
    while queue:
        current = queue.popleft()
        
        # Check all one-letter transformations
        for neighbor in get_neighbors(current, word_set):
            if neighbor in visited:
                continue
                
            visited.add(neighbor)
            parent[neighbor] = current
            
            # Found it! Reconstruct the path by walking backwards
            if neighbor == end:
                path = []
                node = end
                while node in parent:
                    path.append(node)
                    node = parent[node]
                path.append(start)
                return list(reversed(path))
            
            queue.append(neighbor)
    
    # No path exists
    return None


def print_ladder(ladder: Optional[List[str]], start: str, end: str):
    """
    Pretty-print the word ladder result.
    
    I like seeing the step-by-step transformation with the changed letter
    highlighted (well, indicated with arrows at least).
    """
    if ladder is None:
        print(f"No word ladder found from '{start}' to '{end}'")
        return
    
    print(f"Word ladder from '{start}' to '{end}' ({len(ladder)} steps):")
    print()
    for i, word in enumerate(ladder):
        if i > 0:
            # Show which letter changed
            prev = ladder[i-1]
            diff_pos = next(j for j in range(len(word)) if word[j] != prev[j])
            print(f"  {i}. {word}  (changed position {diff_pos}: {prev[diff_pos]} -> {word[diff_pos]})")
        else:
            print(f"  {i}. {word}  (start)")
    print()


if __name__ == "__main__":
    # Load our word dictionary
    print("Loading word list...")
    words = load_word_list()
    print(f"Loaded {len(words)} words\n")
    
    # Test a few classic word ladders
    test_cases = [
        ("cold", "warm"),
        ("hate", "love"),
        ("tall", "fall"),
        ("cart", "list"),
        ("same", "core"),  # This one shouldn't work with our limited dict
    ]
    
    for start, end in test_cases:
        print("=" * 60)
        ladder = find_word_ladder(start, end, words)
        print_ladder(ladder, start, end)
    
    print("=" * 60)
    print("\nInteractive mode - try your own!")
    print("(Words must be in the dictionary and same length)")
    
    # Quick interactive demo
    try:
        start_word = input("Start word: ").strip()
        end_word = input("End word: ").strip()
        print()
        result = find_word_ladder(start_word, end_word, words)
        print_ladder(result, start_word, end_word)
    except (EOFError, KeyboardInterrupt):
        print("\nExiting...")
```