"""
Date: 2026-07-17
Built a word ladder solver using BFS to find the shortest transformation sequence between two words — something I wanted after playing too much Wordle.
"""

#!/usr/bin/env python3
"""
Word Ladder Solver using Breadth-First Search

Finds the shortest transformation sequence from a start word to an end word,
where each intermediate word differs by exactly one letter and must be valid.
I built this after getting frustrated with word ladder puzzles and wanting
to see the optimal solution path.
"""

from collections import deque
from typing import List, Set, Optional, Tuple


def load_word_list() -> Set[str]:
    """
    Load a basic word list for demonstration purposes.
    
    In a real scenario, you'd load from /usr/share/dict/words or similar.
    For now, I'm using a curated set that makes for interesting puzzles.
    """
    return {
        "hit", "hot", "dot", "dog", "lot", "log", "cog",
        "hat", "cat", "bat", "bad", "bid", "big", "bag",
        "bug", "bus", "bit", "bet", "set", "sit", "six",
        "fix", "fox", "box", "boy", "toy", "try", "cry",
        "say", "way", "why", "shy", "she", "see", "sea",
        "tea", "ten", "hen", "pen", "pin", "win", "wit",
        "fit", "fat", "rat", "mat", "map", "tap", "top",
        "hop", "hip", "dip", "dim", "dam", "ham", "him"
    }


def get_neighbors(word: str, word_set: Set[str]) -> List[str]:
    """
    Find all valid words that differ by exactly one letter.
    
    I iterate through each position and try all 26 letters because it's
    simpler than other approaches and plenty fast for typical word lengths.
    """
    neighbors = []
    for i in range(len(word)):
        for c in 'abcdefghijklmnopqrstuvwxyz':
            if c != word[i]:
                candidate = word[:i] + c + word[i+1:]
                if candidate in word_set:
                    neighbors.append(candidate)
    return neighbors


def find_word_ladder(start: str, end: str, word_set: Set[str]) -> Optional[List[str]]:
    """
    Use BFS to find the shortest transformation path from start to end.
    
    Returns the complete path including start and end words, or None if
    no path exists. BFS guarantees the shortest path since all edges have
    equal weight (one letter change).
    """
    if start == end:
        return [start]
    
    if end not in word_set:
        return None
    
    # BFS queue stores (current_word, path_to_current_word)
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        current_word, path = queue.popleft()
        
        # Check all neighbors (words that differ by one letter)
        for neighbor in get_neighbors(current_word, word_set):
            if neighbor == end:
                # Found the target! Return the complete path
                return path + [neighbor]
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    # No path exists
    return None


def print_ladder(path: Optional[List[str]]) -> None:
    """
    Pretty-print the word ladder path with visual indicators.
    
    I added the arrows and difference highlighting to make it easier
    to see exactly which letter changed at each step.
    """
    if path is None:
        print("❌ No valid word ladder found!")
        return
    
    print(f"✓ Found ladder in {len(path) - 1} steps:\n")
    
    for i, word in enumerate(path):
        if i > 0:
            # Highlight the letter that changed
            prev = path[i - 1]
            diff_pos = next(j for j in range(len(word)) if word[j] != prev[j])
            highlighted = word[:diff_pos] + f"[{word[diff_pos]}]" + word[diff_pos+1:]
            print(f"  → {highlighted}")
        else:
            print(f"  {word}")


def solve_puzzle(start: str, end: str, word_set: Set[str]) -> None:
    """
    Solve and display a word ladder puzzle.
    
    Wraps the solver with nice output formatting.
    """
    print(f"\n{'='*50}")
    print(f"Word Ladder: {start.upper()} → {end.upper()}")
    print(f"{'='*50}")
    
    path = find_word_ladder(start, end, word_set)
    print_ladder(path)


if __name__ == "__main__":
    # Load our word dictionary
    words = load_word_list()
    
    print("Word Ladder Solver")
    print("==================")
    print(f"Dictionary loaded with {len(words)} words\n")
    
    # Demo 1: Classic example
    solve_puzzle("hit", "cog", words)
    
    # Demo 2: Longer path
    solve_puzzle("cat", "dog", words)
    
    # Demo 3: Simple transformation
    solve_puzzle("hit", "hot", words)
    
    # Demo 4: Impossible puzzle (no path exists in our limited dictionary)
    solve_puzzle("six", "ham", words)
    
    # Demo 5: Another interesting path
    solve_puzzle("tea", "win", words)