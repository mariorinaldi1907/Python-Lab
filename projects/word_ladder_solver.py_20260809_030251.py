"""
Date: 2026-08-09
Implemented a BFS-based word ladder puzzle solver that finds the shortest transformation sequence between two words, changing only one letter per step.
"""

#!/usr/bin/env python3
"""
Word Ladder Solver - finds the shortest path between two words by changing
one letter at a time. Each intermediate step must be a valid English word.

I built this after thinking about the classic word ladder puzzle. The BFS
approach guarantees we find the shortest path, and I added a simple word
validation system using a built-in dictionary.
"""

from collections import deque
from typing import List, Set, Optional


class WordLadderSolver:
    """
    Solves word ladder puzzles using breadth-first search.
    
    The solver finds the shortest transformation sequence between two words
    where each step changes exactly one letter and forms a valid word.
    """
    
    def __init__(self, word_list: Set[str]):
        """
        Initialize the solver with a set of valid words.
        
        Args:
            word_list: Set of valid dictionary words to use for transformations
        """
        self.word_list = word_list
    
    def _get_neighbors(self, word: str) -> List[str]:
        """
        Find all valid words that differ by exactly one letter.
        
        I'm generating neighbors by trying all possible single-letter
        substitutions. It's not the most efficient, but it's simple and
        works well for reasonably-sized word lists.
        
        Args:
            word: The current word
            
        Returns:
            List of valid neighboring words
        """
        neighbors = []
        word_chars = list(word)
        
        # Try changing each position to every letter a-z
        for i in range(len(word)):
            original_char = word_chars[i]
            for c in 'abcdefghijklmnopqrstuvwxyz':
                if c != original_char:
                    word_chars[i] = c
                    candidate = ''.join(word_chars)
                    if candidate in self.word_list:
                        neighbors.append(candidate)
            word_chars[i] = original_char  # restore original
        
        return neighbors
    
    def solve(self, start: str, end: str) -> Optional[List[str]]:
        """
        Find the shortest word ladder from start to end.
        
        Uses BFS because we want the shortest path. I'm tracking the full
        path in the queue rather than reconstructing it later — uses more
        memory but keeps the code cleaner.
        
        Args:
            start: Starting word
            end: Target word
            
        Returns:
            List of words forming the ladder, or None if no path exists
        """
        if start == end:
            return [start]
        
        if start not in self.word_list or end not in self.word_list:
            return None
        
        if len(start) != len(end):
            return None  # Can't ladder between different length words
        
        # BFS queue stores (current_word, path_to_current)
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            current_word, path = queue.popleft()
            
            # Check all neighbors (words that differ by one letter)
            for neighbor in self._get_neighbors(current_word):
                if neighbor == end:
                    return path + [neighbor]  # Found it!
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None  # No path exists


def load_sample_dictionary() -> Set[str]:
    """
    Create a small sample dictionary for demo purposes.
    
    In a real version, I'd load from /usr/share/dict/words or a file,
    but for portability I'm just hardcoding a small set of words.
    """
    words = {
        'cat', 'bat', 'bet', 'bit', 'sit', 'hit', 'hot', 'dot', 'dog',
        'cot', 'hat', 'mat', 'rat', 'rot', 'pot', 'pat', 'pit', 'pig',
        'big', 'bag', 'bad', 'bed', 'bid', 'hid', 'had', 'ham', 'jam',
        'jag', 'jog', 'job', 'cob', 'cod', 'god', 'got', 'cog', 'log',
        'lot', 'lat', 'led', 'leg', 'peg', 'pen', 'hen', 'den', 'ten',
        'tea', 'sea', 'set', 'sat', 'fat', 'fit', 'fin', 'fun', 'sun',
        'son', 'won', 'ton', 'tan', 'can', 'man', 'men', 'met', 'net',
        'nut', 'but', 'bun', 'run', 'rut', 'rat', 'ram', 'rim', 'dim',
        'dam', 'dam', 'day', 'bay', 'way', 'war', 'car', 'bar', 'tar',
        'tag', 'tap', 'top', 'hop', 'mop', 'map', 'mad', 'lad', 'lag',
        'rag', 'ran', 'pan', 'pin', 'win', 'bin', 'ban', 'van'
    }
    return words


def print_ladder(ladder: Optional[List[str]], start: str, end: str) -> None:
    """
    Pretty-print the word ladder result.
    
    Args:
        ladder: The word ladder path, or None if no solution
        start: Starting word
        end: Ending word
    """
    print(f"\nWord Ladder: {start.upper()} → {end.upper()}")
    print("=" * 40)
    
    if ladder is None:
        print("No solution found!")
    else:
        print(f"Found path with {len(ladder)} steps:\n")
        for i, word in enumerate(ladder):
            print(f"  {i + 1}. {word}")
        print(f"\nSolution length: {len(ladder) - 1} transformations")


if __name__ == "__main__":
    # Load our dictionary and create solver
    dictionary = load_sample_dictionary()
    solver = WordLadderSolver(dictionary)
    
    # Test cases - various difficulty levels
    test_cases = [
        ("cat", "dog"),
        ("hit", "cog"),
        ("pig", "pen"),
        ("fun", "war"),
    ]
    
    print("Word Ladder Solver Demo")
    print("=" * 40)
    print(f"Dictionary size: {len(dictionary)} words\n")
    
    for start, end in test_cases:
        ladder = solver.solve(start, end)
        print_ladder(ladder, start, end)
    
    # Demonstrate a case with no solution
    print("\nTesting impossible ladder:")
    impossible = solver.solve("cat", "zzz")
    print_ladder(impossible, "cat", "zzz")