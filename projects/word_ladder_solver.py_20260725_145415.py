"""
Date: 2026-07-25
Created a BFS-based word ladder puzzle solver that finds the shortest transformation sequence between two words, like turning "COLD" into "WARM".
"""

#!/usr/bin/env python3
"""
Word Ladder Solver - Find shortest path between two words by changing one letter at a time.

I've always found word ladder puzzles fascinating — the idea that you can transform
one word into another by changing just one letter at each step is pretty cool.
This implementation uses BFS to guarantee we find the shortest path.
"""

from collections import deque
from typing import List, Set, Dict, Optional


def get_neighbors(word: str, word_set: Set[str]) -> List[str]:
    """
    Find all valid one-letter transformations of the given word.
    
    This is the core of the puzzle — for each position in the word,
    we try all 26 letters and see if the result is a valid word.
    I'm using a set lookup for O(1) checking rather than a list.
    """
    neighbors = []
    for i in range(len(word)):
        for char in 'abcdefghijklmnopqrstuvwxyz':
            if char != word[i]:
                candidate = word[:i] + char + word[i+1:]
                if candidate in word_set:
                    neighbors.append(candidate)
    return neighbors


def find_word_ladder(start: str, end: str, word_list: List[str]) -> Optional[List[str]]:
    """
    Use BFS to find the shortest transformation sequence from start to end.
    
    Returns the path as a list of words, or None if no path exists.
    BFS guarantees we find the shortest path since we explore level by level.
    """
    # Normalize everything to lowercase to avoid case issues
    start = start.lower()
    end = end.lower()
    word_set = {word.lower() for word in word_list}
    
    # Quick validation checks
    if start == end:
        return [start]
    if end not in word_set:
        return None
    if len(start) != len(end):
        return None
    
    # BFS setup: queue stores (current_word, path_to_current_word)
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        current_word, path = queue.popleft()
        
        # Check all one-letter transformations
        for neighbor in get_neighbors(current_word, word_set):
            if neighbor == end:
                return path + [neighbor]
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    # No path found
    return None


def get_sample_dictionary() -> List[str]:
    """
    Return a sample word list for testing.
    
    In a real implementation, you'd load this from /usr/share/dict/words
    or a similar file, but I'm keeping this self-contained for demo purposes.
    """
    return [
        'cold', 'cord', 'card', 'ward', 'warm', 'worm', 'word', 'wood',
        'gold', 'hold', 'bold', 'bald', 'ball', 'wall', 'wail', 'wait',
        'coil', 'coal', 'cost', 'most', 'must', 'mist', 'mint', 'mind',
        'heat', 'head', 'dead', 'lead', 'load', 'loan', 'lean', 'bean',
        'hate', 'have', 'wave', 'wake', 'cake', 'came', 'lame', 'lamb',
        'code', 'mode', 'made', 'mare', 'care', 'cave', 'cove', 'love',
        'hero', 'here', 'were', 'wire', 'wise', 'rise', 'rice', 'race',
        'pare', 'park', 'bark', 'dark', 'dart', 'part', 'past', 'fast',
        'cast', 'case', 'base', 'bask', 'task', 'talk', 'tail', 'fail'
    ]


def print_ladder(ladder: Optional[List[str]], start: str, end: str) -> None:
    """
    Pretty-print the word ladder result.
    
    I wanted nice output that clearly shows the transformation steps.
    """
    print(f"\nFinding path from '{start.upper()}' to '{end.upper()}':")
    print("-" * 50)
    
    if ladder is None:
        print(f"❌ No valid word ladder found!")
    else:
        print(f"✓ Found ladder with {len(ladder)} steps:\n")
        for i, word in enumerate(ladder):
            arrow = "  ↓" if i < len(ladder) - 1 else ""
            print(f"  {i+1}. {word.upper()}{arrow}")
        print(f"\nTotal transformations: {len(ladder) - 1}")


if __name__ == "__main__":
    # Demo with several interesting word ladder puzzles
    dictionary = get_sample_dictionary()
    
    print("=" * 50)
    print("WORD LADDER SOLVER")
    print("=" * 50)
    print(f"Dictionary size: {len(dictionary)} words\n")
    
    # Test case 1: Classic COLD -> WARM transformation
    ladder1 = find_word_ladder("COLD", "WARM", dictionary)
    print_ladder(ladder1, "COLD", "WARM")
    
    # Test case 2: HEAD -> TAIL
    ladder2 = find_word_ladder("HEAD", "TAIL", dictionary)
    print_ladder(ladder2, "HEAD", "TAIL")
    
    # Test case 3: HATE -> LOVE
    ladder3 = find_word_ladder("HATE", "LOVE", dictionary)
    print_ladder(ladder3, "HATE", "LOVE")
    
    # Test case 4: Impossible transformation (different lengths)
    ladder4 = find_word_ladder("CAT", "MOUSE", dictionary)
    print_ladder(ladder4, "CAT", "MOUSE")
    
    print("\n" + "=" * 50)