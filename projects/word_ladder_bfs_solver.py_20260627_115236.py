"""
Date: 2026-06-27
Implemented a BFS-based word ladder puzzle solver that finds the shortest transformation path between two words by changing one letter at a time.
"""

#!/usr/bin/env python3
"""
Word Ladder Solver using Breadth-First Search

Finds the shortest path to transform one word into another by changing
one letter at a time, where each intermediate step must be a valid word.
Classic AI search problem that I wanted to tackle with clean BFS.
"""

from collections import deque
from typing import List, Set, Optional, Tuple


def load_word_list() -> Set[str]:
    """
    Load a basic word list for demonstration purposes.
    
    In production I'd load from /usr/share/dict/words or a file,
    but keeping it self-contained for portability.
    """
    # Just a small curated list for demo - normally I'd read from a file
    words = {
        "hit", "hot", "dot", "dog", "log", "cog", "lot", "hat", "cat",
        "bat", "bad", "bed", "fed", "fee", "see", "set", "sat", "mat",
        "pat", "pit", "sit", "fit", "fat", "rat", "rot", "pot", "got",
        "god", "cod", "cop", "cap", "can", "man", "mad", "pad", "sad",
        "say", "bay", "day", "gay", "may", "way", "war", "car", "bar",
        "far", "tar", "tan", "ten", "pen", "hen", "den", "men", "met",
        "net", "pet", "vet", "bet", "get", "jet", "yet", "let", "wet"
    }
    return words


def get_neighbors(word: str, word_set: Set[str]) -> List[str]:
    """
    Find all valid words that differ by exactly one letter.
    
    I tried a few approaches here - this alphabet iteration is faster
    than checking edit distance for every word in the dictionary.
    """
    neighbors = []
    
    for i in range(len(word)):
        for c in 'abcdefghijklmnopqrstuvwxyz':
            if c == word[i]:
                continue  # Skip the same letter
            
            # Build the candidate word with one letter changed
            candidate = word[:i] + c + word[i+1:]
            
            if candidate in word_set:
                neighbors.append(candidate)
    
    return neighbors


def find_word_ladder(start: str, end: str, word_set: Set[str]) -> Optional[List[str]]:
    """
    Use BFS to find the shortest transformation path from start to end.
    
    Returns the path as a list of words, or None if no path exists.
    BFS guarantees we find the shortest path since all edges have weight 1.
    """
    if start == end:
        return [start]
    
    if start not in word_set or end not in word_set:
        return None
    
    # BFS queue: each element is (current_word, path_to_reach_it)
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        current_word, path = queue.popleft()
        
        # Check all neighbors (words differing by one letter)
        for neighbor in get_neighbors(current_word, word_set):
            if neighbor == end:
                # Found it! Return the complete path
                return path + [neighbor]
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    # No path exists
    return None


def print_ladder(path: Optional[List[str]]) -> None:
    """
    Pretty-print the word ladder path with visual formatting.
    
    Highlights which letter changed at each step - makes it easier
    to see that the transformation is valid.
    """
    if path is None:
        print("No valid word ladder found!")
        return
    
    print(f"\nFound ladder with {len(path)} steps:")
    print("=" * 40)
    
    for i, word in enumerate(path):
        if i == 0:
            print(f"{i+1}. {word.upper()}")
        else:
            # Find and highlight the changed letter
            prev_word = path[i-1]
            highlighted = ""
            
            for j, char in enumerate(word):
                if char != prev_word[j]:
                    highlighted += f"[{char.upper()}]"
                else:
                    highlighted += char
            
            print(f"{i+1}. {highlighted}")
    
    print("=" * 40)


def run_demo_puzzles(word_set: Set[str]) -> None:
    """
    Run a few interesting word ladder puzzles to show it works.
    
    I picked these because they have nice visual transformations
    and demonstrate different path lengths.
    """
    puzzles = [
        ("hit", "cog"),
        ("cat", "dog"),
        ("cold", "warm"),  # This won't work with our limited dictionary
        ("bad", "bat"),
        ("man", "met"),
    ]
    
    for start, end in puzzles:
        print(f"\n{'='*50}")
        print(f"Solving: '{start}' → '{end}'")
        print('='*50)
        
        path = find_word_ladder(start, end, word_set)
        print_ladder(path)


if __name__ == "__main__":
    print("Word Ladder Solver - BFS Implementation")
    print("Transforms one word into another, one letter at a time\n")
    
    # Load our word dictionary
    words = load_word_list()
    print(f"Loaded {len(words)} words into dictionary\n")
    
    # Run demonstration puzzles
    run_demo_puzzles(words)
    
    # Interactive example with a custom puzzle
    print("\n" + "="*50)
    print("Custom Example: 'hit' → 'cog'")
    print("="*50)
    
    result = find_word_ladder("hit", "cog", words)
    if result:
        print(f"\nShortest path has {len(result)-1} transformations:")
        for i in range(len(result)-1):
            print(f"  {result[i]} → {result[i+1]}")
    else:
        print("No solution found!")