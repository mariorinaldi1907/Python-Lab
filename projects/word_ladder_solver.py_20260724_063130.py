"""
Date: 2026-07-24
Implemented a BFS-based word ladder puzzle solver that finds the shortest transformation sequence between two words, because I got nerdsniped by a word game at 2am.
"""

#!/usr/bin/env python3
"""
Word Ladder Solver - finds the shortest path between two words by changing one letter at a time.

I wrote this after getting stuck on a word puzzle where you have to transform one word into
another by changing a single letter each step (and each intermediate step must be a valid word).
Turns out BFS is perfect for this since we want the *shortest* path.
"""

from collections import deque
from typing import List, Set, Optional, Tuple


def load_dictionary(word_length: int) -> Set[str]:
    """
    Load a basic dictionary of common English words.
    
    In a real version I'd load from /usr/share/dict/words or a file,
    but for portability I'm hardcoding a small set of common words.
    Only returns words of the specified length.
    """
    # Small hardcoded dictionary for demo purposes
    words = {
        "cat", "bat", "hat", "rat", "mat", "sat", "fat", "pat",
        "car", "bar", "tar", "war", "far", "par", "jar",
        "can", "ban", "tan", "ran", "man", "pan", "fan", "van",
        "cot", "bot", "hot", "rot", "not", "pot", "dot", "got",
        "cut", "but", "hut", "rut", "nut", "put", "gut", "jut",
        "cab", "dab", "jab", "lab", "nab", "tab", "gab",
        "cog", "dog", "fog", "hog", "jog", "log", "bog",
        "bit", "hit", "kit", "lit", "pit", "sit", "wit", "fit",
        "bag", "gag", "hag", "lag", "nag", "rag", "sag", "tag", "wag",
        "big", "dig", "fig", "gig", "jig", "pig", "rig", "wig",
        "bog", "cog", "dog", "fog", "hog", "jog", "log",
        "bug", "dug", "hug", "jug", "lug", "mug", "pug", "rug", "tug",
    }
    return {w for w in words if len(w) == word_length}


def get_neighbors(word: str, dictionary: Set[str]) -> List[str]:
    """
    Find all valid words that differ by exactly one letter.
    
    This is the core of the puzzle — we try replacing each position with each
    letter a-z and check if the result is in our dictionary.
    """
    neighbors = []
    for i in range(len(word)):
        for c in 'abcdefghijklmnopqrstuvwxyz':
            if c != word[i]:  # Don't include the word itself
                candidate = word[:i] + c + word[i+1:]
                if candidate in dictionary:
                    neighbors.append(candidate)
    return neighbors


def find_word_ladder(start: str, end: str, dictionary: Set[str]) -> Optional[List[str]]:
    """
    Use BFS to find the shortest transformation sequence from start to end.
    
    Returns the path as a list of words, or None if no path exists.
    BFS guarantees we find the shortest path since all edges have equal weight.
    """
    if start == end:
        return [start]
    
    if start not in dictionary or end not in dictionary:
        return None
    
    # BFS queue stores (current_word, path_to_current_word)
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        current_word, path = queue.popleft()
        
        # Try all valid one-letter transformations
        for neighbor in get_neighbors(current_word, dictionary):
            if neighbor == end:
                # Found it! Return the complete path
                return path + [neighbor]
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    # No path exists
    return None


def print_ladder(ladder: Optional[List[str]]) -> None:
    """Pretty print the word ladder solution."""
    if ladder is None:
        print("No solution found!")
        return
    
    print(f"Found ladder with {len(ladder)} steps:")
    for i, word in enumerate(ladder):
        if i > 0:
            # Highlight which letter changed
            prev = ladder[i-1]
            diff_pos = next(j for j in range(len(word)) if word[j] != prev[j])
            print(f"  {i}. {word[:diff_pos]}[{word[diff_pos]}]{word[diff_pos+1:]} (changed position {diff_pos})")
        else:
            print(f"  {i}. {word} (start)")


if __name__ == "__main__":
    print("=== Word Ladder Solver ===\n")
    
    # Demo 1: cat -> dog (classic example)
    print("Example 1: CAT -> DOG")
    dictionary = load_dictionary(3)
    ladder = find_word_ladder("cat", "dog", dictionary)
    print_ladder(ladder)
    
    print("\n" + "-"*40 + "\n")
    
    # Demo 2: hat -> bat (easy one)
    print("Example 2: HAT -> BAT")
    ladder = find_word_ladder("hat", "bat", dictionary)
    print_ladder(ladder)
    
    print("\n" + "-"*40 + "\n")
    
    # Demo 3: impossible case
    print("Example 3: CAT -> ZOO (should fail with our limited dictionary)")
    ladder = find_word_ladder("cat", "zoo", dictionary)
    print_ladder(ladder)
    
    print("\n" + "-"*40 + "\n")
    
    # Demo 4: longer path
    print("Example 4: BIT -> DOG")
    ladder = find_word_ladder("bit", "dog", dictionary)
    print_ladder(ladder)
    
    print("\n=== Stats ===")
    print(f"Dictionary size: {len(dictionary)} words")
    print(f"All words are length: 3")