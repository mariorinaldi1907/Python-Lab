"""
Date: 2026-06-07
Built a word ladder puzzle solver that finds the shortest transformation sequence between two words using breadth-first search — useful for those NYT-style word games.
"""

#!/usr/bin/env python3
"""
Word Ladder Solver using BFS
Finds the shortest transformation sequence between two words,
changing one letter at a time. Each intermediate word must be valid.
"""

from collections import deque
from typing import List, Set, Optional


def load_word_list() -> Set[str]:
    """
    Load a simple word list for demonstration.
    In a real scenario, I'd read from /usr/share/dict/words or a file.
    For now, using a curated set of common 4-letter words.
    """
    words = {
        "cold", "cord", "card", "ward", "warm", "harm", "farm", "form",
        "fort", "font", "foot", "food", "good", "gold", "bold", "bond",
        "band", "hand", "hard", "yard", "cart", "part", "port", "post",
        "cost", "cast", "last", "fast", "fact", "pact", "pace", "race",
        "rice", "rich", "rick", "pick", "sick", "sink", "pink", "link",
        "line", "wine", "wire", "fire", "hire", "here", "hero", "zero",
        "code", "rode", "role", "pole", "pale", "tale", "tall", "ball",
        "bell", "belt", "melt", "molt", "bolt", "colt", "cola", "cool",
        "pool", "poll", "polo", "solo", "sold", "told", "toll", "tool",
        "fool", "foul", "soul", "soup", "soap", "soak", "sock", "rock",
        "lock", "look", "book", "boom", "room", "roof", "hoof", "hook",
        "cook", "cork", "work", "worm", "word", "lord", "load", "toad",
        "toed", "tied", "tier", "pier", "pies", "ties", "lies", "life",
        "lift", "left", "loft", "soft", "sort", "sore", "core", "cone",
        "bone", "zone", "done", "dine", "fine", "find", "fund", "funk"
    }
    return words


def get_neighbors(word: str, word_set: Set[str]) -> List[str]:
    """
    Generate all valid one-letter transformations of a word.
    This is the heart of the graph construction — each word is a node,
    and edges connect words that differ by exactly one letter.
    """
    neighbors = []
    for i in range(len(word)):
        # Try replacing each position with every letter
        for char in 'abcdefghijklmnopqrstuvwxyz':
            if char != word[i]:
                candidate = word[:i] + char + word[i+1:]
                if candidate in word_set:
                    neighbors.append(candidate)
    return neighbors


def find_word_ladder(start: str, end: str, word_set: Set[str]) -> Optional[List[str]]:
    """
    Use BFS to find the shortest transformation path from start to end.
    Returns the path as a list of words, or None if no path exists.
    
    Why BFS? Because it guarantees the shortest path in an unweighted graph.
    Each word transformation has the same "cost", so BFS is perfect here.
    """
    if start not in word_set or end not in word_set:
        return None
    
    if start == end:
        return [start]
    
    # Queue stores tuples of (current_word, path_to_current_word)
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
    
    # No path found
    return None


def print_ladder(ladder: Optional[List[str]], start: str, end: str) -> None:
    """
    Pretty-print the word ladder result.
    I wanted the output to be clear and show each transformation step.
    """
    print(f"\nWord Ladder: {start.upper()} → {end.upper()}")
    print("=" * 50)
    
    if ladder is None:
        print(f"❌ No path found between '{start}' and '{end}'")
    else:
        print(f"✓ Found path in {len(ladder) - 1} steps:\n")
        for i, word in enumerate(ladder):
            if i < len(ladder) - 1:
                # Highlight the changed letter
                next_word = ladder[i + 1]
                diff_pos = [j for j in range(len(word)) if word[j] != next_word[j]]
                display = list(word)
                if diff_pos:
                    display[diff_pos[0]] = f"[{display[diff_pos[0]]}]"
                print(f"  {i + 1}. {''.join(display)}")
            else:
                print(f"  {i + 1}. {word}")
    print()


if __name__ == "__main__":
    # Load our word dictionary
    words = load_word_list()
    print(f"Loaded {len(words)} words into dictionary\n")
    
    # Test cases I wanted to verify
    test_cases = [
        ("cold", "warm"),  # Classic example
        ("code", "data"),  # Should fail - no path
        ("good", "evil"),  # Should fail
        ("hero", "zero"),  # Should work
        ("word", "code"),  # Should work
    ]
    
    for start, end in test_cases:
        ladder = find_word_ladder(start, end, words)
        print_ladder(ladder, start, end)