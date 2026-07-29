"""
Date: 2026-07-29
Built a word ladder puzzle solver that finds the shortest path between two words by changing one letter at a time — uses BFS and actually generates pretty readable output.
"""

"""
Word Ladder Solver - finds shortest path between two words.

A word ladder is a sequence where each word differs by exactly one letter.
For example: CAT -> COT -> DOT -> DOG

I wanted to build this because I always loved these puzzles as a kid, and 
BFS is the perfect algorithm for finding the shortest transformation path.
"""

from collections import deque
from typing import List, Set, Dict, Optional


def get_neighbors(word: str, word_set: Set[str]) -> List[str]:
    """
    Find all valid words that differ by exactly one letter.
    
    Instead of checking every word in the dictionary, I generate all possible
    one-letter variations and check if they exist. Much faster for large wordlists.
    """
    neighbors = []
    for i in range(len(word)):
        for c in 'abcdefghijklmnopqrstuvwxyz':
            if c != word[i]:
                candidate = word[:i] + c + word[i+1:]
                if candidate in word_set:
                    neighbors.append(candidate)
    return neighbors


def word_ladder(start: str, end: str, word_list: List[str]) -> Optional[List[str]]:
    """
    Find shortest word ladder from start to end using BFS.
    
    Returns the path as a list, or None if no path exists.
    BFS guarantees we find the shortest path first, which is why I chose it
    over DFS or other approaches.
    """
    # Normalize everything to lowercase to avoid case issues
    start = start.lower()
    end = end.lower()
    word_set = set(w.lower() for w in word_list)
    
    # Basic validation - can't solve if words aren't same length or end not in dict
    if len(start) != len(end):
        return None
    if end not in word_set:
        return None
    
    # Add start word to set in case it's not already there
    word_set.add(start)
    
    # BFS setup: queue stores (current_word, path_to_current_word)
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        current, path = queue.popleft()
        
        # Found the target!
        if current == end:
            return path
        
        # Explore all neighbors
        for neighbor in get_neighbors(current, word_set):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    # No path exists
    return None


def print_ladder(ladder: Optional[List[str]]) -> None:
    """
    Pretty-print the word ladder with arrows and step numbers.
    
    I added highlighting to show which letter changed at each step,
    makes it easier to see the transformations.
    """
    if ladder is None:
        print("No valid word ladder found!")
        return
    
    print(f"\nFound ladder in {len(ladder)} steps:\n")
    for i, word in enumerate(ladder):
        if i > 0:
            # Highlight the changed letter by showing before/after
            prev = ladder[i-1]
            for j, (c1, c2) in enumerate(zip(prev, word)):
                if c1 != c2:
                    print(f"  Step {i}: {word.upper()} (changed position {j}: {c1} → {c2})")
                    break
        else:
            print(f"  Start: {word.upper()}")
    print()


def load_default_words() -> List[str]:
    """
    Returns a small default word list for testing.
    
    In a real scenario, you'd load from /usr/share/dict/words or similar,
    but I wanted this to be completely self-contained and runnable anywhere.
    """
    return [
        "cat", "cot", "cog", "dog", "dot", "lot", "log", "lag", "bag", "bat",
        "hat", "hot", "pot", "pat", "mat", "sat", "rat", "rot", "got", "not",
        "hit", "hut", "but", "bit", "fit", "fat", "eat", "oat", "oak", "oar",
        "car", "far", "tar", "tan", "ten", "pen", "men", "hen", "den", "den",
        "dew", "new", "net", "set", "sit", "pit", "put", "cut", "cub", "rub",
        "rug", "bug", "hug", "hub", "pub", "pup", "cup", "cop", "top", "tip",
        "sip", "zip", "zap", "gap", "gas", "has", "was", "way", "say", "bay",
        "day", "may", "ray", "pay", "lay", "hay"
    ]


if __name__ == "__main__":
    # Demo with some classic word ladder puzzles
    words = load_default_words()
    
    print("=" * 50)
    print("WORD LADDER SOLVER")
    print("=" * 50)
    
    # Test case 1: CAT to DOG (classic puzzle)
    print("\n🎯 Puzzle 1: Transform CAT into DOG")
    print("-" * 50)
    result = word_ladder("CAT", "DOG", words)
    print_ladder(result)
    
    # Test case 2: HIT to COG
    print("🎯 Puzzle 2: Transform HIT into COG")
    print("-" * 50)
    result = word_ladder("HIT", "COG", words)
    print_ladder(result)
    
    # Test case 3: Impossible puzzle (different lengths)
    print("🎯 Puzzle 3: Transform CAT into DOGS (impossible - different lengths)")
    print("-" * 50)
    result = word_ladder("CAT", "DOGS", words)
    print_ladder(result)
    
    # Test case 4: No path exists
    print("🎯 Puzzle 4: Transform ZAP into HUG")
    print("-" * 50)
    result = word_ladder("ZAP", "HUG", words)
    print_ladder(result)
    
    print("=" * 50)
    print("All demos complete!")
    print("=" * 50)