"""
Date: 2026-06-16
Built a word ladder puzzle solver that finds the shortest transformation path between two words by changing one letter at a time.
"""

#!/usr/bin/env python3
"""
Word Ladder Solver - finds shortest path between two words.

The classic word ladder puzzle: transform one word into another by
changing exactly one letter at a time, with each intermediate step
being a valid word.

I built this because I was curious about BFS and wanted a fun problem
to practice graph traversal without explicitly building the graph.
"""

from collections import deque
from typing import List, Set, Optional, Tuple


def load_word_list() -> Set[str]:
    """
    Load a basic word list for testing.
    
    In production I'd load from /usr/share/dict/words or similar,
    but for demo purposes I'm embedding a small list of common words.
    """
    # Small curated list that makes for interesting ladders
    words = {
        "cold", "cord", "card", "ward", "warm", "harm", "hard",
        "heat", "head", "heal", "teal", "tell", "tall", "tail",
        "fail", "fall", "fell", "fill", "file", "fine", "wine",
        "wind", "wand", "want", "pant", "pint", "pine", "line",
        "lint", "hint", "hunt", "hurt", "curt", "curl", "cure",
        "cute", "mute", "mate", "gate", "hate", "have", "cave",
        "wave", "ware", "ware", "mare", "care", "dare", "dark",
        "dork", "work", "word", "lord", "ford", "food", "good",
        "gold", "goad", "road", "toad", "load", "lead", "read",
    }
    return words


def get_neighbors(word: str, word_set: Set[str]) -> List[str]:
    """
    Find all valid words that differ by exactly one letter.
    
    Instead of precomputing a graph, I generate neighbors on-the-fly.
    This is less memory-intensive and works well for word ladders.
    """
    neighbors = []
    
    # Try replacing each position with each letter
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
    Find shortest transformation path using BFS.
    
    Returns None if no path exists, otherwise returns the list of words
    forming the ladder from start to end (inclusive).
    """
    if start not in word_set or end not in word_set:
        return None
    
    if start == end:
        return [start]
    
    # BFS queue stores (current_word, path_so_far)
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        current, path = queue.popleft()
        
        # Check all neighbors (words differing by one letter)
        for neighbor in get_neighbors(current, word_set):
            if neighbor in visited:
                continue
            
            new_path = path + [neighbor]
            
            # Found the target!
            if neighbor == end:
                return new_path
            
            visited.add(neighbor)
            queue.append((neighbor, new_path))
    
    # No path exists
    return None


def print_ladder(ladder: Optional[List[str]], start: str, end: str) -> None:
    """
    Pretty-print the word ladder result.
    
    Highlights the changing letter at each step because it looks cool
    and makes the transformations easier to follow.
    """
    if ladder is None:
        print(f"No ladder found from '{start}' to '{end}'")
        return
    
    print(f"Ladder from '{start}' to '{end}' ({len(ladder)} steps):")
    print()
    
    for i, word in enumerate(ladder):
        if i > 0:
            # Find which letter changed
            prev = ladder[i - 1]
            diff_idx = next(j for j in range(len(word)) if word[j] != prev[j])
            highlighted = word[:diff_idx] + f"[{word[diff_idx]}]" + word[diff_idx+1:]
            print(f"  {i}. {highlighted}")
        else:
            print(f"  {i}. {word}")


if __name__ == "__main__":
    # Load our word dictionary
    words = load_word_list()
    
    print("=" * 60)
    print("Word Ladder Solver")
    print("=" * 60)
    print()
    
    # Test a few interesting ladders
    test_cases = [
        ("cold", "warm"),
        ("head", "tail"),
        ("gold", "lead"),
        ("hate", "love"),  # This one won't work with our limited word set
    ]
    
    for start, end in test_cases:
        ladder = find_word_ladder(start, end, words)
        print_ladder(ladder, start, end)
        print()