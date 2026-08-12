"""
Date: 2026-08-12
Built a word ladder puzzle solver that finds the shortest transformation path between two words by changing one letter at a time.
"""

"""
Word Ladder Solver - finds shortest path between two words by changing one letter at a time.

I've always found word ladder puzzles fascinating, so I built this BFS solver
to find the shortest transformation sequence. The tricky part was efficiently
generating neighbors without pre-building the entire graph.
"""

from collections import deque
from typing import List, Set, Optional, Dict


def load_word_list() -> Set[str]:
    """
    Load a built-in word list for the solver.
    
    Using a small curated list here since we can't rely on external files.
    In a real scenario, I'd load from /usr/share/dict/words or similar.
    """
    words = {
        "hit", "hot", "dot", "dog", "lot", "log", "cog",
        "hat", "cat", "bat", "mat", "rat", "fat", "sat",
        "hog", "fog", "bog", "cot", "pot", "rot", "got",
        "bit", "fit", "pit", "sit", "wit", "lit", "kit",
        "cop", "pop", "mop", "top", "hop", "sop",
        "cape", "tape", "gape", "gate", "late", "hate", "fate", "mate",
        "cold", "cord", "card", "ward", "warm", "worm", "word", "ford",
        "code", "coke", "cone", "bone", "done", "dote", "dose", "rose",
        "sage", "page", "rage", "cage", "came", "same", "sane", "pane"
    }
    return words


def get_neighbors(word: str, word_set: Set[str]) -> List[str]:
    """
    Find all valid one-letter transformations of the given word.
    
    I iterate through each position and try all 26 letters. It's brute force
    but works well for typical word lengths. Could optimize with pattern matching
    but this is clearer and fast enough.
    """
    neighbors = []
    
    for i in range(len(word)):
        for c in 'abcdefghijklmnopqrstuvwxyz':
            if c == word[i]:
                continue  # Skip same letter
            
            candidate = word[:i] + c + word[i+1:]
            if candidate in word_set:
                neighbors.append(candidate)
    
    return neighbors


def find_word_ladder(start: str, end: str, word_set: Set[str]) -> Optional[List[str]]:
    """
    Use BFS to find shortest transformation path from start to end word.
    
    BFS guarantees we find the shortest path. I track the parent of each word
    so I can reconstruct the path once we reach the target. Returns None if
    no path exists.
    """
    if start == end:
        return [start]
    
    if start not in word_set or end not in word_set:
        return None
    
    # BFS setup
    queue = deque([start])
    visited = {start}
    parent: Dict[str, str] = {}
    
    while queue:
        current = queue.popleft()
        
        # Try all one-letter transformations
        for neighbor in get_neighbors(current, word_set):
            if neighbor in visited:
                continue
            
            visited.add(neighbor)
            parent[neighbor] = current
            queue.append(neighbor)
            
            # Found the target!
            if neighbor == end:
                return reconstruct_path(start, end, parent)
    
    # No path exists
    return None


def reconstruct_path(start: str, end: str, parent: Dict[str, str]) -> List[str]:
    """
    Backtrack from end to start using parent pointers to build the path.
    
    I reverse at the end since we build the path backwards. Could use
    a deque and appendleft but this is simpler.
    """
    path = [end]
    current = end
    
    while current != start:
        current = parent[current]
        path.append(current)
    
    path.reverse()
    return path


def print_ladder(path: Optional[List[str]], start: str, end: str) -> None:
    """
    Pretty-print the word ladder result.
    
    Shows each transformation step and highlights what changed.
    """
    print(f"\nWord Ladder: '{start}' → '{end}'")
    print("=" * 40)
    
    if path is None:
        print("No solution found!")
        return
    
    print(f"Found path with {len(path)} steps:\n")
    
    for i, word in enumerate(path):
        if i == 0:
            print(f"  {i+1}. {word} (start)")
        elif i == len(path) - 1:
            print(f"  {i+1}. {word} (goal!)")
        else:
            # Show which letter changed
            prev = path[i-1]
            diff_pos = next(j for j in range(len(word)) if word[j] != prev[j])
            print(f"  {i+1}. {word} (changed position {diff_pos}: '{prev[diff_pos]}' → '{word[diff_pos]}')")


if __name__ == "__main__":
    # Load our dictionary
    word_dict = load_word_list()
    
    print("Word Ladder Solver")
    print("==================\n")
    print(f"Dictionary size: {len(word_dict)} words")
    
    # Test case 1: Classic example
    start1, end1 = "hit", "cog"
    path1 = find_word_ladder(start1, end1, word_dict)
    print_ladder(path1, start1, end1)
    
    # Test case 2: Another transformation
    start2, end2 = "cold", "warm"
    path2 = find_word_ladder(start2, end2, word_dict)
    print_ladder(path2, start2, end2)
    
    # Test case 3: No solution exists
    start3, end3 = "cape", "dog"
    path3 = find_word_ladder(start3, end3, word_dict)
    print_ladder(path3, start3, end3)
    
    # Test case 4: Same length path
    start4, end4 = "cat", "dog"
    path4 = find_word_ladder(start4, end4, word_dict)
    print_ladder(path4, start4, end4)