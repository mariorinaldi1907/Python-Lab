"""
Date: 2026-06-23
Built a word ladder puzzle solver that uses BFS to find the shortest path transforming one word into another by changing one letter at a time.
"""

#!/usr/bin/env python3
"""
Word Ladder Solver
------------------
Finds the shortest transformation sequence from a start word to an end word,
changing only one letter at a time. Each intermediate word must be valid.

I've always found word ladder puzzles fascinating — this was my excuse to
implement a clean BFS solution with a built-in word list.
"""

from collections import deque
from typing import List, Set, Optional


class WordLadderSolver:
    """
    Solves word ladder puzzles using breadth-first search.
    
    The key insight is that this is a shortest-path problem on an implicit graph
    where nodes are words and edges connect words differing by one letter.
    """
    
    def __init__(self, word_list: List[str]):
        """
        Initialize solver with a dictionary of valid words.
        
        Args:
            word_list: List of valid words to use in transformations
        """
        # Using a set for O(1) lookup when checking valid words
        self.word_set = set(word.lower() for word in word_list)
    
    def get_neighbors(self, word: str) -> List[str]:
        """
        Generate all valid words that differ by exactly one letter.
        
        I tried a wildcard pattern approach but generating all 26 possibilities
        per position ended up being simpler and just as fast for typical cases.
        
        Args:
            word: The word to find neighbors for
            
        Returns:
            List of valid neighboring words
        """
        neighbors = []
        word_list = list(word)
        
        for i in range(len(word)):
            original_char = word_list[i]
            # Try all 26 letters at this position
            for c in 'abcdefghijklmnopqrstuvwxyz':
                if c == original_char:
                    continue
                word_list[i] = c
                candidate = ''.join(word_list)
                if candidate in self.word_set:
                    neighbors.append(candidate)
            # Restore original character for next position
            word_list[i] = original_char
        
        return neighbors
    
    def find_ladder(self, start: str, end: str) -> Optional[List[str]]:
        """
        Find shortest word ladder from start to end using BFS.
        
        BFS guarantees we find the shortest path since all edges have weight 1.
        We track the full path in the queue to make reconstruction trivial.
        
        Args:
            start: Starting word
            end: Target word
            
        Returns:
            List representing the transformation sequence, or None if impossible
        """
        start = start.lower()
        end = end.lower()
        
        # Quick validation
        if len(start) != len(end):
            return None
        if start not in self.word_set or end not in self.word_set:
            return None
        if start == end:
            return [start]
        
        # BFS setup: queue stores (current_word, path_so_far)
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            current_word, path = queue.popleft()
            
            # Try all valid one-letter transformations
            for neighbor in self.get_neighbors(current_word):
                if neighbor == end:
                    # Found it! Return the complete path
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        # No path exists
        return None


def get_sample_dictionary() -> List[str]:
    """
    Return a small but interesting set of words for demos.
    
    In a real app I'd load from /usr/share/dict/words or similar,
    but this keeps the script self-contained.
    """
    return [
        'hit', 'hot', 'dot', 'dog', 'lot', 'log', 'cog',
        'cat', 'hat', 'bat', 'bit', 'bot', 'box', 'fox',
        'big', 'pig', 'fig', 'fit', 'sit', 'set', 'bet',
        'but', 'put', 'pit', 'pot', 'cot', 'cut', 'gut',
        'bag', 'tag', 'lag', 'rag', 'rat', 'mat', 'sat'
    ]


def print_ladder(ladder: Optional[List[str]], start: str, end: str):
    """
    Pretty-print the ladder result.
    
    Args:
        ladder: The transformation sequence or None
        start: Starting word
        end: Target word
    """
    if ladder:
        print(f"\n✓ Found ladder from '{start}' to '{end}' in {len(ladder)} steps:")
        for i, word in enumerate(ladder):
            print(f"  {i + 1}. {word}")
    else:
        print(f"\n✗ No ladder exists from '{start}' to '{end}'")


if __name__ == "__main__":
    # Demo with a few interesting examples
    dictionary = get_sample_dictionary()
    solver = WordLadderSolver(dictionary)
    
    print("Word Ladder Solver Demo")
    print("=" * 40)
    print(f"Dictionary size: {len(dictionary)} words")
    
    # Classic example
    print_ladder(solver.find_ladder('hit', 'cog'), 'hit', 'cog')
    
    # Another path
    print_ladder(solver.find_ladder('cat', 'dog'), 'cat', 'dog')
    
    # Impossible case
    print_ladder(solver.find_ladder('hit', 'fox'), 'hit', 'fox')
    
    # Single step
    print_ladder(solver.find_ladder('cat', 'bat'), 'cat', 'bat')