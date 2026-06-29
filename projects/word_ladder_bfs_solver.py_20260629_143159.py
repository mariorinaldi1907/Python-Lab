"""
Date: 2026-06-29
Built a word ladder puzzle solver that finds the shortest path between two words by changing one letter at a time, using BFS because I wanted to revisit graph traversal algorithms.
"""

"""
Word Ladder Solver using BFS

Finds the shortest transformation sequence from a start word to an end word,
changing only one letter at a time. Each intermediate word must be valid.

I wrote this because word ladder puzzles are fun and it's a clean application
of BFS — plus it forced me to think about efficient neighbor generation.
"""

from collections import deque
from typing import List, Set, Optional


def load_word_list() -> Set[str]:
    """
    Load a basic English word list for demonstration.
    
    In a real implementation I'd load from /usr/share/dict/words or a file,
    but for portability I'm just using a hardcoded set of common words.
    """
    # Small sample dictionary for demo purposes
    words = {
        "hit", "hot", "dot", "dog", "lot", "log", "cog",
        "hat", "bat", "cat", "car", "bar", "bet", "set",
        "sit", "bit", "bot", "but", "cut", "cot", "got",
        "rot", "pot", "pat", "rat", "mat", "sat", "fat",
        "fit", "pit", "kit", "lit", "wit", "wig", "wag",
        "tag", "tar", "war", "was", "has", "had", "bad",
        "dad", "sad", "say", "way", "day", "bay", "may",
        "man", "can", "ban", "ran", "tan", "ten", "den",
        "hen", "pen", "pet", "net", "met", "let", "get"
    }
    return words


def get_neighbors(word: str, word_set: Set[str]) -> List[str]:
    """
    Generate all valid one-letter transformations of the given word.
    
    This is the core of the algorithm. For each position, I try all 26 letters
    and check if the result is in our dictionary. Could optimize with a trie
    or preprocessing, but brute force works fine for small word lists.
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
    Find shortest transformation sequence from start to end using BFS.
    
    Returns the path as a list of words, or None if no path exists.
    BFS guarantees we find the shortest path because we explore level by level.
    """
    if start == end:
        return [start]
    
    if end not in word_set:
        return None
    
    # BFS setup: queue stores (current_word, path_so_far)
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        current_word, path = queue.popleft()
        
        # Try all valid one-letter transformations
        for neighbor in get_neighbors(current_word, word_set):
            if neighbor == end:
                return path + [neighbor]
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    # No path found
    return None


def print_ladder(path: Optional[List[str]], start: str, end: str) -> None:
    """
    Pretty-print the word ladder result.
    
    Shows the transformation step by step, highlighting which letter changed.
    """
    print(f"\nWord Ladder: {start} → {end}")
    print("=" * 40)
    
    if path is None:
        print("No valid transformation path found!")
        return
    
    print(f"Found path with {len(path)} words:\n")
    for i, word in enumerate(path, 1):
        if i < len(path):
            # Find which letter changed
            next_word = path[i]
            diff_pos = next((j for j in range(len(word)) if word[j] != next_word[j]), -1)
            print(f"{i}. {word.upper()}")
            if diff_pos >= 0:
                print(f"   ↓ (change position {diff_pos}: '{word[diff_pos]}' → '{next_word[diff_pos]}')")
        else:
            print(f"{i}. {word.upper()}")
    
    print(f"\nTotal transformations: {len(path) - 1}")


if __name__ == "__main__":
    # Load our word dictionary
    words = load_word_list()
    
    # Demo 1: Classic example from CLRS/leetcode
    print("Demo 1: Classic word ladder puzzle")
    path1 = find_word_ladder("hit", "cog", words)
    print_ladder(path1, "hit", "cog")
    
    # Demo 2: Another example
    print("\n" + "=" * 60)
    print("\nDemo 2: Transforming 'cat' to 'dog'")
    path2 = find_word_ladder("cat", "dog", words)
    print_ladder(path2, "cat", "dog")
    
    # Demo 3: Impossible transformation
    print("\n" + "=" * 60)
    print("\nDemo 3: Impossible transformation (no path)")
    path3 = find_word_ladder("hit", "wig", words)
    print_ladder(path3, "hit", "wig")
    
    # Show some stats
    print("\n" + "=" * 60)
    print(f"\nDictionary stats: {len(words)} words loaded")
    print("All words are 3 letters long in this demo dictionary")