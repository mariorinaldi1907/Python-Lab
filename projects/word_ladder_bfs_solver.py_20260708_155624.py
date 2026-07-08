"""
Date: 2026-07-08
Built a word ladder puzzle solver using BFS to find the shortest transformation path between two words, because I wanted to practice graph traversal on implicit graphs.
"""

#!/usr/bin/env python3
"""
Word Ladder Solver - finds shortest transformation path between two words.

A word ladder puzzle asks you to change one word into another by changing
one letter at a time, where each intermediate step must also be a valid word.
Example: CAT -> COT -> DOT -> DOG

I built this to practice BFS on implicit graphs (where edges aren't pre-computed).
The graph is generated on-the-fly by checking which words differ by exactly one letter.
"""

from collections import deque
from typing import List, Set, Optional, Tuple


def load_word_list() -> Set[str]:
    """
    Load a set of valid English words for the puzzle.
    
    In a real scenario, you'd load from /usr/share/dict/words or similar.
    For demo purposes, I'm using a small hardcoded list to keep it self-contained.
    """
    # Small dictionary for demo - in production I'd read from a file
    words = {
        "cat", "cot", "dot", "dog", "cog", "log", "lot", "hot", "hat",
        "bat", "bad", "dad", "mad", "mat", "rat", "rot", "pot", "pit",
        "sit", "set", "wet", "wit", "hit", "bit", "big", "bag", "bug",
        "dug", "dig", "pig", "rig", "rag", "tag", "tan", "can", "car",
        "bar", "tar", "war", "way", "say", "bay", "day", "may", "man",
        "ban", "van", "vat", "eat", "oat", "bat", "fat", "far", "for",
        "fog", "hog", "hop", "top", "toy", "try", "cry", "dry", "fry"
    }
    return words


def get_neighbors(word: str, word_set: Set[str]) -> List[str]:
    """
    Find all valid words that differ from `word` by exactly one letter.
    
    This is the core of building our implicit graph. Instead of precomputing
    all edges, we generate them on demand during BFS traversal.
    """
    neighbors = []
    
    # Try replacing each position with every letter a-z
    for i in range(len(word)):
        for c in 'abcdefghijklmnopqrstuvwxyz':
            if c == word[i]:
                continue  # Skip if it's the same letter
            
            # Build the candidate word with one letter changed
            candidate = word[:i] + c + word[i+1:]
            
            if candidate in word_set:
                neighbors.append(candidate)
    
    return neighbors


def solve_word_ladder(start: str, target: str, word_set: Set[str]) -> Optional[List[str]]:
    """
    Use BFS to find the shortest transformation path from start to target.
    
    Returns the complete path (including start and target) if one exists,
    otherwise returns None. BFS guarantees we find the shortest path.
    
    Why BFS? Because we're looking for the shortest path in an unweighted graph.
    Each transformation has equal "cost" (one letter change).
    """
    if start not in word_set or target not in word_set:
        return None
    
    if start == target:
        return [start]
    
    # Queue stores tuples of (current_word, path_to_reach_it)
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        current_word, path = queue.popleft()
        
        # Explore all neighbors (words one letter away)
        for neighbor in get_neighbors(current_word, word_set):
            if neighbor == target:
                # Found it! Return the complete path
                return path + [neighbor]
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    # Exhausted all possibilities, no path exists
    return None


def print_ladder(path: Optional[List[str]], start: str, target: str) -> None:
    """
    Pretty-print the word ladder result.
    
    Shows each transformation step and highlights what changed.
    """
    print(f"\nWord Ladder: {start.upper()} → {target.upper()}")
    print("=" * 50)
    
    if path is None:
        print(f"❌ No path found from '{start}' to '{target}'")
        return
    
    print(f"✓ Found path with {len(path)} words ({len(path)-1} transformations):\n")
    
    for i, word in enumerate(path):
        if i > 0:
            # Show which letter changed
            prev = path[i-1]
            diff_idx = next(j for j in range(len(word)) if word[j] != prev[j])
            print(f"  {i}. {word.upper()} (changed position {diff_idx}: {prev[diff_idx]}→{word[diff_idx]})")
        else:
            print(f"  {i}. {word.upper()} (start)")
    
    print()


def demo_solver() -> None:
    """
    Run a few example word ladders to demonstrate the solver.
    
    I picked these examples to show both successful paths and impossible ones.
    """
    words = load_word_list()
    
    test_cases = [
        ("cat", "dog"),
        ("hit", "cog"),
        ("hot", "dog"),
        ("cat", "bat"),  # Should be easy, one transformation
        ("cat", "xyz"),  # Impossible - xyz not in dictionary
    ]
    
    print("🎮 WORD LADDER SOLVER DEMO")
    print("=" * 50)
    print(f"Dictionary size: {len(words)} words\n")
    
    for start, target in test_cases:
        path = solve_word_ladder(start, target, words)
        print_ladder(path, start, target)


if __name__ == "__main__":
    # Run the demo when script is executed directly
    demo_solver()