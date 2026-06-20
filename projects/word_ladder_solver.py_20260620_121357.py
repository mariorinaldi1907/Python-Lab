"""
Date: 2026-06-20
Built a word ladder puzzle solver using breadth-first search to find the shortest chain of single-letter transformations between two words.
"""

#!/usr/bin/env python3
"""
Word Ladder Solver - finds the shortest path between two words.

Each step in the ladder changes exactly one letter, and every intermediate
word must be a valid English word. I used BFS because it guarantees the
shortest path, and built a simple word list filter to keep things fast.
"""

from collections import deque
from typing import List, Set, Optional


def load_word_list() -> Set[str]:
    """
    Load a basic word list for the puzzle.
    
    In a real scenario I'd load from /usr/share/dict/words or an external file,
    but for this demo I'm using a hardcoded list of common 4-letter words.
    """
    # Small curated list for demo purposes - in production I'd load from a file
    words = {
        "cold", "cord", "card", "ward", "warm", "harm", "farm", "fare",
        "fire", "firs", "fits", "sits", "side", "hide", "hike", "bike",
        "bile", "bale", "ball", "tall", "tell", "well", "will", "wild",
        "wind", "wine", "pine", "line", "lint", "hint", "hunt", "hung",
        "sung", "sunk", "dunk", "dune", "done", "dome", "home", "hope",
        "cope", "code", "cole", "hole", "hold", "bold", "gold", "golf"
    }
    return words


def get_neighbors(word: str, word_set: Set[str]) -> List[str]:
    """
    Find all valid words that differ by exactly one letter.
    
    This is the core of the graph construction - each word is a node,
    and edges connect words that are one letter apart. I iterate through
    each position and try all 26 letters instead of checking the entire
    word list, which is way faster for small word lengths.
    """
    neighbors = []
    for i in range(len(word)):
        for c in 'abcdefghijklmnopqrstuvwxyz':
            if c == word[i]:
                continue  # Skip the original letter
            
            candidate = word[:i] + c + word[i+1:]
            if candidate in word_set:
                neighbors.append(candidate)
    
    return neighbors


def find_word_ladder(start: str, end: str, word_set: Set[str]) -> Optional[List[str]]:
    """
    Use BFS to find the shortest transformation path from start to end.
    
    BFS is perfect here because we want the shortest path, not just any path.
    I track the full path in the queue rather than reconstructing it later
    because it's simpler and the paths are short enough that memory isn't an issue.
    """
    if start == end:
        return [start]
    
    if start not in word_set or end not in word_set:
        return None
    
    # Queue stores (current_word, path_to_current_word)
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        current_word, path = queue.popleft()
        
        # Check all words that are one letter different
        for neighbor in get_neighbors(current_word, word_set):
            if neighbor == end:
                return path + [neighbor]  # Found it!
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    return None  # No path exists


def print_ladder(ladder: Optional[List[str]], start: str, end: str) -> None:
    """
    Pretty-print the word ladder result.
    
    Highlights which letter changed at each step to make it easier to verify
    that the solution is actually valid (helpful during testing).
    """
    if ladder is None:
        print(f"No word ladder found from '{start}' to '{end}'")
        return
    
    print(f"Found ladder from '{start}' to '{end}' in {len(ladder) - 1} steps:\n")
    
    for i, word in enumerate(ladder):
        if i == 0:
            print(f"  {i + 1}. {word} (start)")
        elif i == len(ladder) - 1:
            print(f"  {i + 1}. {word} (end)")
        else:
            # Show which letter changed from previous word
            prev = ladder[i - 1]
            changed_pos = next((j for j in range(len(word)) if word[j] != prev[j]), -1)
            if changed_pos >= 0:
                print(f"  {i + 1}. {word} (changed position {changed_pos + 1}: {prev[changed_pos]} → {word[changed_pos]})")
            else:
                print(f"  {i + 1}. {word}")


if __name__ == "__main__":
    # Load our dictionary
    word_set = load_word_list()
    print(f"Loaded {len(word_set)} words into dictionary\n")
    print("=" * 60)
    
    # Test case 1: Classic example
    print("\nTest 1: COLD → WARM")
    print("-" * 60)
    ladder = find_word_ladder("cold", "warm", word_set)
    print_ladder(ladder, "cold", "warm")
    
    # Test case 2: Another path
    print("\n" + "=" * 60)
    print("\nTest 2: HIDE → HUNT")
    print("-" * 60)
    ladder = find_word_ladder("hide", "hunt", word_set)
    print_ladder(ladder, "hide", "hunt")
    
    # Test case 3: Impossible (words not in dictionary)
    print("\n" + "=" * 60)
    print("\nTest 3: COLD → ZZZZ (impossible)")
    print("-" * 60)
    ladder = find_word_ladder("cold", "zzzz", word_set)
    print_ladder(ladder, "cold", "zzzz")
    
    print("\n" + "=" * 60)
    print("\nDone! The BFS approach guarantees we always find the shortest path.")