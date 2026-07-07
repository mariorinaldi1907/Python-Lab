"""
Date: 2026-07-07
Built a word ladder puzzle solver that finds the shortest transformation sequence between two words, changing one letter at a time through valid dictionary words.
"""

#!/usr/bin/env python3
"""
Word Ladder Solver using BFS

Finds the shortest transformation sequence from a start word to an end word,
where each intermediate step must be a valid word differing by exactly one letter.
Classic problem but always fun to implement — reminds me why BFS is so elegant.
"""

from collections import deque
from typing import List, Set, Optional


def load_word_list() -> Set[str]:
    """
    Load a basic word list for the demo.
    
    In a real implementation I'd read from /usr/share/dict/words or a file,
    but for portability I'm just hardcoding a small test dictionary here.
    """
    return {
        'hit', 'hot', 'dot', 'dog', 'lot', 'log', 'cog',
        'dit', 'lit', 'let', 'lat', 'cat', 'bat', 'hat',
        'mad', 'bad', 'dad', 'sad', 'had', 'mat', 'sat',
        'bit', 'bot', 'got', 'god', 'hog', 'fog', 'for',
        'fort', 'port', 'post', 'host', 'most', 'mist',
        'fist', 'fish', 'dish', 'wish', 'wash', 'wast',
        'last', 'lost', 'cost', 'cast', 'fast', 'fist'
    }


def get_neighbors(word: str, word_set: Set[str]) -> List[str]:
    """
    Generate all valid one-letter transformations of the given word.
    
    I'm trying all 26 letters at each position — a bit brute force but
    it's cleaner than other approaches and fast enough for short words.
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
    Find the shortest word ladder from start to end using BFS.
    
    Returns the path as a list of words, or None if no path exists.
    BFS guarantees we find the shortest path since all edges have equal weight.
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
        
        # Try all valid transformations
        for neighbor in get_neighbors(current_word, word_set):
            if neighbor == end:
                return path + [neighbor]
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    # No path found
    return None


def find_all_ladders(start: str, end: str, word_set: Set[str]) -> List[List[str]]:
    """
    Find ALL shortest word ladders from start to end.
    
    This is trickier than finding just one path — we need to track all paths
    at the same depth level before marking nodes as visited. Otherwise we'd
    miss alternate paths of the same length.
    """
    if start not in word_set or end not in word_set:
        return []
    
    if start == end:
        return [[start]]
    
    # Queue stores (current_word, path_to_current_word)
    queue = deque([(start, [start])])
    visited = {start}
    all_paths = []
    found_length = None  # Track the length once we find the first solution
    
    while queue:
        current_word, path = queue.popleft()
        
        # If we already found solutions and this path is longer, stop
        if found_length and len(path) > found_length:
            break
        
        for neighbor in get_neighbors(current_word, word_set):
            if neighbor == end:
                solution = path + [neighbor]
                all_paths.append(solution)
                if found_length is None:
                    found_length = len(solution)
            elif neighbor not in visited:
                # Mark as visited at this level
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    return all_paths


def print_ladder(ladder: Optional[List[str]]) -> None:
    """Pretty print a word ladder with arrows."""
    if ladder is None:
        print("No path found!")
    else:
        print(" → ".join(ladder))
        print(f"Length: {len(ladder)} words")


if __name__ == "__main__":
    # Load our test dictionary
    words = load_word_list()
    
    print("=" * 60)
    print("Word Ladder Solver - BFS Implementation")
    print("=" * 60)
    print()
    
    # Test case 1: Classic hit → cog example
    print("Test 1: Finding path from 'hit' to 'cog'")
    print("-" * 60)
    ladder = find_word_ladder('hit', 'cog', words)
    print_ladder(ladder)
    print()
    
    # Test case 2: Another example
    print("Test 2: Finding path from 'cat' to 'dog'")
    print("-" * 60)
    ladder = find_word_ladder('cat', 'dog', words)
    print_ladder(ladder)
    print()
    
    # Test case 3: Impossible transformation
    print("Test 3: Finding path from 'hit' to 'fish' (might not exist)")
    print("-" * 60)
    ladder = find_word_ladder('hit', 'fish', words)
    print_ladder(ladder)
    print()
    
    # Test case 4: Find all shortest paths
    print("Test 4: Finding ALL shortest paths from 'hit' to 'cog'")
    print("-" * 60)
    all_ladders = find_all_ladders('hit', 'cog', words)
    if all_ladders:
        print(f"Found {len(all_ladders)} path(s):")
        for i, path in enumerate(all_ladders, 1):
            print(f"  Path {i}: {' → '.join(path)}")
    else:
        print("No paths found!")
    print()
    
    print("=" * 60)
    print("Demo complete! The BFS approach guarantees shortest paths.")
    print("=" * 60)