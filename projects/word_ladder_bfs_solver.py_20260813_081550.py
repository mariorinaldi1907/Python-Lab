"""
Date: 2026-08-13
Implemented a word ladder puzzle solver that uses breadth-first search to find the shortest transformation sequence between two words, with a built-in dictionary and path reconstruction.
"""

#!/usr/bin/env python3
"""
Word Ladder Solver using BFS
Finds the shortest transformation sequence between two words,
changing only one letter at a time, where each intermediate word must be valid.
"""

from collections import deque
from typing import List, Set, Optional, Dict


class WordLadderSolver:
    """
    Solves word ladder puzzles using breadth-first search.
    Each step changes exactly one letter, and all intermediate words must be valid.
    """
    
    def __init__(self, dictionary: Set[str]):
        """
        Initialize the solver with a dictionary of valid words.
        
        Args:
            dictionary: Set of valid words (all should be same length for a given puzzle)
        """
        self.dictionary = dictionary
    
    def get_neighbors(self, word: str) -> List[str]:
        """
        Generate all valid words that differ by exactly one letter.
        
        Args:
            word: The current word
            
        Returns:
            List of valid neighbor words
        """
        neighbors = []
        word_list = list(word)
        
        # Try changing each position to every letter
        for i in range(len(word)):
            original_char = word_list[i]
            for c in 'abcdefghijklmnopqrstuvwxyz':
                if c != original_char:
                    word_list[i] = c
                    candidate = ''.join(word_list)
                    if candidate in self.dictionary:
                        neighbors.append(candidate)
            word_list[i] = original_char  # restore original character
        
        return neighbors
    
    def solve(self, start: str, end: str) -> Optional[List[str]]:
        """
        Find the shortest word ladder from start to end using BFS.
        
        Args:
            start: Starting word
            end: Target word
            
        Returns:
            List of words forming the ladder, or None if no path exists
        """
        if start == end:
            return [start]
        
        if len(start) != len(end):
            return None
        
        if start not in self.dictionary or end not in self.dictionary:
            return None
        
        # BFS queue: each element is a word
        queue = deque([start])
        # Track visited words to avoid cycles
        visited = {start}
        # Track parent relationships to reconstruct path
        parent: Dict[str, str] = {start: None}
        
        while queue:
            current = queue.popleft()
            
            # Found the target!
            if current == end:
                return self._reconstruct_path(parent, start, end)
            
            # Explore all neighbors
            for neighbor in self.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.append(neighbor)
        
        # No path found
        return None
    
    def _reconstruct_path(self, parent: Dict[str, str], start: str, end: str) -> List[str]:
        """
        Reconstruct the path from start to end using parent pointers.
        
        Args:
            parent: Dictionary mapping each word to its parent in the search
            start: Starting word
            end: Ending word
            
        Returns:
            List of words from start to end
        """
        path = []
        current = end
        
        while current is not None:
            path.append(current)
            current = parent[current]
        
        path.reverse()
        return path


def create_sample_dictionary() -> Set[str]:
    """
    Create a sample dictionary of 4-letter words for testing.
    In a real application, you'd load this from a file.
    
    Returns:
        Set of valid words
    """
    words = {
        'cold', 'cord', 'card', 'ward', 'warm', 'worm', 'word', 'work',
        'pork', 'port', 'fort', 'form', 'foam', 'flam', 'flaw', 'flow',
        'glow', 'grow', 'brow', 'crow', 'crew', 'brew', 'bred', 'bead',
        'beat', 'meat', 'heat', 'head', 'heal', 'teal', 'tell', 'tall',
        'ball', 'call', 'fall', 'fail', 'tail', 'mail', 'main', 'rain',
        'pain', 'pair', 'hair', 'fair', 'fear', 'dear', 'bear', 'gear',
        'pear', 'peak', 'beak', 'bean', 'mean', 'lean', 'lead', 'load',
        'lord', 'lore', 'lose', 'lost', 'post', 'pose', 'rose', 'role',
        'hole', 'hope', 'cope', 'cape', 'tape', 'take', 'make', 'wake',
        'cake', 'came', 'same', 'save', 'wave', 'have', 'hive', 'five',
        'fire', 'dire', 'dine', 'mine', 'mint', 'hint', 'pint', 'pine'
    }
    return words


if __name__ == "__main__":
    # Create solver with sample dictionary
    dictionary = create_sample_dictionary()
    solver = WordLadderSolver(dictionary)
    
    # Test cases - these are classic word ladder puzzles
    test_cases = [
        ('cold', 'warm'),
        ('head', 'tail'),
        ('fire', 'make'),
        ('lost', 'find'),  # This one has no solution in our limited dictionary
    ]
    
    print("=" * 60)
    print("WORD LADDER SOLVER")
    print("=" * 60)
    print(f"Dictionary size: {len(dictionary)} words\n")
    
    for start, end in test_cases:
        print(f"\nSolving: {start.upper()} → {end.upper()}")
        print("-" * 40)
        
        result = solver.solve(start, end)
        
        if result:
            print(f"Found ladder in {len(result)} steps:")
            for i, word in enumerate(result):
                if i == 0:
                    print(f"  {i+1}. {word.upper()} (start)")
                elif i == len(result) - 1:
                    print(f"  {i+1}. {word.upper()} (goal!)")
                else:
                    print(f"  {i+1}. {word.upper()}")
        else:
            print("  ❌ No solution found with current dictionary")
    
    print("\n" + "=" * 60)