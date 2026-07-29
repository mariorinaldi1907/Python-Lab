"""
Date: 2026-07-29
Built a word ladder puzzle solver that finds the shortest transformation path between two words by changing one letter at a time — uses BFS for optimal paths.
"""

#!/usr/bin/env python3
"""
Word Ladder Solver

Finds the shortest sequence of words to transform one word into another,
changing only one letter at a time. Each intermediate step must be a valid word.

Example: CAT -> DOG
CAT -> COT -> DOT -> DOG
"""

from collections import deque
from typing import List, Set, Optional, Dict


def load_word_list() -> Set[str]:
    """
    Load a basic word list for the puzzle.
    
    In a real scenario, I'd load from /usr/share/dict/words or a file,
    but for portability I'm using a hardcoded list of common 3-letter words.
    """
    # Small subset for demo purposes - normally I'd read from a file
    words = {
        'cat', 'cot', 'dot', 'dog', 'log', 'cog', 'bat', 'hat', 'hot',
        'lot', 'hit', 'bit', 'bot', 'but', 'cut', 'can', 'car', 'bar',
        'bag', 'big', 'bog', 'box', 'fox', 'fix', 'six', 'sit', 'set',
        'sat', 'fat', 'far', 'tar', 'war', 'was', 'has', 'had', 'bad',
        'bed', 'red', 'rod', 'god', 'got', 'not', 'net', 'met', 'mat',
        'man', 'may', 'say', 'way', 'day', 'pay', 'pan', 'tan', 'ten',
        'pen', 'pet', 'pit', 'pat', 'put', 'gut', 'get', 'jet', 'let',
        'lit', 'lid', 'kid', 'kin', 'sin', 'sun', 'son', 'won', 'one',
        'ore', 'are', 'ark', 'art', 'apt', 'opt', 'oat', 'eat', 'ear'
    }
    return words


def get_neighbors(word: str, word_set: Set[str]) -> List[str]:
    """
    Find all valid words that differ by exactly one letter.
    
    I'm generating all possible single-letter mutations and checking
    if they exist in the word set. More efficient than checking every word.
    """
    neighbors = []
    
    for i in range(len(word)):
        for c in 'abcdefghijklmnopqrstuvwxyz':
            if c == word[i]:
                continue  # Skip the same letter
            
            # Build the mutation
            candidate = word[:i] + c + word[i+1:]
            
            if candidate in word_set:
                neighbors.append(candidate)
    
    return neighbors


def find_word_ladder(start: str, end: str, word_set: Set[str]) -> Optional[List[str]]:
    """
    Use BFS to find the shortest transformation path from start to end.
    
    BFS guarantees we find the shortest path because we explore level by level.
    I'm tracking the full path in the queue to reconstruct the solution easily.
    """
    if start not in word_set or end not in word_set:
        return None
    
    if start == end:
        return [start]
    
    # Queue stores (current_word, path_to_current_word)
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        current_word, path = queue.popleft()
        
        # Check all valid one-letter transformations
        for neighbor in get_neighbors(current_word, word_set):
            if neighbor == end:
                return path + [neighbor]  # Found it!
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    return None  # No path exists


def print_ladder(ladder: Optional[List[str]], start: str, end: str) -> None:
    """
    Pretty-print the word ladder result.
    
    Highlights the letter that changed at each step for clarity.
    """
    if ladder is None:
        print(f"\nNo path found from '{start}' to '{end}'")
        return
    
    print(f"\nFound ladder from '{start}' to '{end}' in {len(ladder) - 1} steps:")
    print("-" * 40)
    
    for i, word in enumerate(ladder):
        if i == 0:
            print(f"{i}: {word.upper()}")
        else:
            # Find which letter changed
            prev = ladder[i - 1]
            changed_idx = next(j for j in range(len(word)) if word[j] != prev[j])
            
            # Highlight the change
            highlighted = (
                word[:changed_idx] + 
                f"[{word[changed_idx]}]" + 
                word[changed_idx + 1:]
            )
            print(f"{i}: {highlighted}")
    
    print("-" * 40)


if __name__ == "__main__":
    # Load our dictionary
    dictionary = load_word_list()
    
    print("=" * 50)
    print("Word Ladder Solver")
    print("=" * 50)
    print(f"Dictionary loaded with {len(dictionary)} words")
    
    # Test cases that I know have interesting solutions
    test_cases = [
        ('cat', 'dog'),
        ('hit', 'cog'),
        ('red', 'tax'),  # This one has no solution in our small dict
        ('bat', 'man'),
        ('fox', 'dog')
    ]
    
    for start, end in test_cases:
        ladder = find_word_ladder(start, end, dictionary)
        print_ladder(ladder, start, end)
    
    # Interactive mode demo
    print("\n" + "=" * 50)
    print("Try your own (both must be 3-letter words in dictionary):")
    print("=" * 50)
    
    # Example with user words
    custom_start = 'cat'
    custom_end = 'bat'
    
    print(f"\nExample: Finding path from '{custom_start}' to '{custom_end}'...")
    result = find_word_ladder(custom_start, custom_end, dictionary)
    print_ladder(result, custom_start, custom_end)