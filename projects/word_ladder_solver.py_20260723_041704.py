"""
Date: 2026-07-23
Built a word ladder puzzle solver that finds the shortest chain of single-letter transformations between two words using breadth-first search.
"""

#!/usr/bin/env python3
"""
Word Ladder Solver - finds shortest transformation path between two words.

A word ladder is a puzzle where you transform one word into another by changing
one letter at a time, with each intermediate step being a valid word.
For example: CAT -> COT -> DOT -> DOG

I originally built this after watching a YouTube video about word games and
wanted to see how efficient BFS would be for solving these puzzles.
"""

from collections import deque
from typing import List, Set, Optional, Tuple


def load_word_list() -> Set[str]:
    """
    Load a basic word list for demonstration purposes.
    
    In a real implementation, I'd load from /usr/share/dict/words or a file,
    but for portability I'm just using a hardcoded set of common 3-letter words.
    """
    return {
        'cat', 'cot', 'dot', 'dog', 'bat', 'bad', 'dad', 'mad', 'mat',
        'hat', 'hot', 'pot', 'lot', 'log', 'bog', 'big', 'pig', 'pin',
        'pan', 'can', 'car', 'bar', 'far', 'for', 'fog', 'cog', 'cab',
        'lab', 'lag', 'tag', 'tan', 'ban', 'bin', 'bit', 'sit', 'set',
        'sat', 'rat', 'rag', 'bag', 'gag', 'gap', 'sap', 'say', 'way',
        'war', 'tar', 'tap', 'top', 'tip', 'hip', 'hit', 'kit', 'lit',
        'pit', 'pat', 'fat', 'fit', 'fin', 'fun', 'bun', 'run', 'rut',
        'but', 'gut', 'got', 'god', 'rod', 'rot', 'not', 'nut'
    }


def get_neighbors(word: str, word_set: Set[str]) -> List[str]:
    """
    Find all valid words that differ by exactly one letter.
    
    This is the core of the graph construction - each word is a node,
    and edges exist between words that differ by a single character.
    I'm using a simple brute-force approach here (try all 26 letters at
    each position) which works fine for small word lengths.
    """
    neighbors = []
    for i in range(len(word)):
        for char in 'abcdefghijklmnopqrstuvwxyz':
            if char != word[i]:
                candidate = word[:i] + char + word[i+1:]
                if candidate in word_set:
                    neighbors.append(candidate)
    return neighbors


def find_word_ladder(start: str, end: str, word_set: Set[str]) -> Optional[List[str]]:
    """
    Use BFS to find the shortest transformation path between start and end words.
    
    BFS guarantees we find the shortest path because we explore all words at
    distance k before exploring any at distance k+1. I'm tracking the full path
    in the queue rather than reconstructing it afterward - uses more memory but
    simpler to implement and the paths are short anyway.
    
    Returns None if no path exists, otherwise returns the list of words forming
    the transformation sequence.
    """
    if start == end:
        return [start]
    
    if start not in word_set or end not in word_set:
        return None
    
    # Queue stores (current_word, path_to_current_word)
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        current_word, path = queue.popleft()
        
        # Check all valid one-letter transformations
        for neighbor in get_neighbors(current_word, word_set):
            if neighbor == end:
                return path + [neighbor]
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    return None


def print_ladder(ladder: Optional[List[str]], start: str, end: str) -> None:
    """
    Pretty-print the word ladder solution.
    
    Shows each transformation step with the changed letter highlighted.
    """
    if ladder is None:
        print(f"No path found from '{start}' to '{end}'")
        return
    
    print(f"Found ladder from '{start}' to '{end}' in {len(ladder) - 1} steps:")
    for i, word in enumerate(ladder):
        if i == 0:
            print(f"  {i}: {word.upper()}")
        else:
            prev = ladder[i-1]
            # Find which letter changed
            changed_pos = next(j for j in range(len(word)) if word[j] != prev[j])
            highlighted = word[:changed_pos] + f"[{word[changed_pos]}]" + word[changed_pos+1:]
            print(f"  {i}: {highlighted}")


if __name__ == "__main__":
    # Load our dictionary
    words = load_word_list()
    
    print("=" * 60)
    print("Word Ladder Solver")
    print("=" * 60)
    print(f"Dictionary size: {len(words)} words\n")
    
    # Test a few interesting transformations
    test_cases = [
        ('cat', 'dog'),
        ('hot', 'dog'),
        ('pig', 'sty'),  # This one won't work with our limited dictionary
        ('hit', 'run'),
    ]
    
    for start, end in test_cases:
        print()
        ladder = find_word_ladder(start, end, words)
        print_ladder(ladder, start, end)
        print("-" * 60)