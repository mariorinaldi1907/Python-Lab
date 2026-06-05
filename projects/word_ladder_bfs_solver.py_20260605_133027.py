"""
Date: 2026-06-05
Built a BFS-based word ladder solver that finds the shortest transformation path between two words by changing one letter at a time — actually pretty satisfying to watch it find paths through the dictionary.
"""

#!/usr/bin/env python3
"""
Word Ladder Solver using BFS

Finds the shortest transformation sequence from a start word to an end word,
changing only one letter at a time. Each intermediate word must exist in the
provided dictionary.

Example: "hit" -> "cog" might be: hit -> hot -> dot -> dog -> cog
"""

from collections import deque
from typing import List, Set, Dict, Optional


def get_neighbors(word: str, word_set: Set[str]) -> List[str]:
    """
    Generate all valid one-letter transformations of a word.
    
    Args:
        word: The current word to transform
        word_set: Set of valid dictionary words
    
    Returns:
        List of valid neighbor words (one letter different, exists in dict)
    """
    neighbors = []
    # Try replacing each position with every letter a-z
    for i in range(len(word)):
        for c in 'abcdefghijklmnopqrstuvwxyz':
            if c != word[i]:  # Don't include the original word
                candidate = word[:i] + c + word[i+1:]
                if candidate in word_set:
                    neighbors.append(candidate)
    return neighbors


def find_word_ladder(start: str, end: str, word_list: List[str]) -> Optional[List[str]]:
    """
    Find shortest word ladder from start to end using BFS.
    
    BFS guarantees we find the shortest path. I'm tracking parent pointers
    instead of storing full paths at each node to save memory.
    
    Args:
        start: Starting word
        end: Target word
        word_list: List of valid dictionary words
    
    Returns:
        List representing the transformation path, or None if no path exists
    """
    if start == end:
        return [start]
    
    # Convert to set for O(1) lookups - super important for performance
    word_set = set(word_list)
    
    # Edge case: if either word isn't in the dictionary, can't solve
    if start not in word_set or end not in word_set:
        return None
    
    # BFS setup: queue holds words to explore
    queue = deque([start])
    visited = {start}
    # Parent map lets us reconstruct the path backwards from end to start
    parent: Dict[str, str] = {}
    
    while queue:
        current = queue.popleft()
        
        # Check all possible one-letter transformations
        for neighbor in get_neighbors(current, word_set):
            if neighbor in visited:
                continue
            
            visited.add(neighbor)
            parent[neighbor] = current
            
            # Found the target! Reconstruct path by walking back through parents
            if neighbor == end:
                path = []
                node = end
                while node in parent:
                    path.append(node)
                    node = parent[node]
                path.append(start)
                return path[::-1]  # Reverse to get start -> end
            
            queue.append(neighbor)
    
    # Exhausted all possibilities without finding end
    return None


def print_ladder(path: Optional[List[str]]) -> None:
    """
    Pretty-print the word ladder result.
    
    Args:
        path: The transformation path, or None if no solution
    """
    if path is None:
        print("No solution found!")
        return
    
    print(f"Found ladder with {len(path)} words:")
    for i, word in enumerate(path):
        if i > 0:
            # Highlight which letter changed
            prev = path[i-1]
            changes = [j for j in range(len(word)) if word[j] != prev[j]]
            print(f"  {i}: {word}  (changed position {changes[0]})")
        else:
            print(f"  {i}: {word}")


if __name__ == "__main__":
    # Small test dictionary - in real use you'd load a full word list
    # These words let us build some interesting ladders
    test_dict = [
        "hit", "hot", "dot", "dog", "lot", "log", "cog",
        "hat", "cat", "bat", "rat", "mat", "sat", "fat",
        "dig", "big", "bag", "hag", "had", "mad", "man",
        "pan", "pin", "tin", "tan", "ten", "tea", "pea"
    ]
    
    print("=" * 50)
    print("Word Ladder Solver - BFS Demo")
    print("=" * 50)
    
    # Test case 1: Classic example
    print("\nTest 1: 'hit' -> 'cog'")
    result = find_word_ladder("hit", "cog", test_dict)
    print_ladder(result)
    
    # Test case 2: Another path
    print("\nTest 2: 'cat' -> 'dog'")
    result = find_word_ladder("cat", "dog", test_dict)
    print_ladder(result)
    
    # Test case 3: Longer chain
    print("\nTest 3: 'hat' -> 'tea'")
    result = find_word_ladder("hat", "tea", test_dict)
    print_ladder(result)
    
    # Test case 4: No solution possible
    print("\nTest 4: 'hit' -> 'xyz' (should fail)")
    result = find_word_ladder("hit", "xyz", test_dict)
    print_ladder(result)
    
    print("\n" + "=" * 50)
    print("The BFS approach guarantees shortest path!")
    print("=" * 50)