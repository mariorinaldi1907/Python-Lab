"""
Date: 2026-08-29
Created a tool that finds the shortest chain of single-letter transformations between two words, like a mini word puzzle solver I can actually use for fun.
"""

#!/usr/bin/env python3
"""
Word Ladder Solver - finds shortest transformation path between two words.

A word ladder is a sequence where each word differs from the previous by exactly
one letter. For example: CAT -> COT -> DOT -> DOG

I wanted to build this after playing around with word games and realizing BFS
is perfect for finding the shortest path through word transformations.
"""

from collections import deque
from typing import List, Set, Optional, Tuple


class WordLadderSolver:
    """
    Finds the shortest word ladder between two words using BFS.
    
    The approach: treat each word as a node in a graph, where edges exist between
    words that differ by exactly one letter. BFS guarantees we find the shortest path.
    """
    
    def __init__(self, word_list: List[str]):
        """
        Initialize solver with a dictionary of valid words.
        
        Args:
            word_list: List of valid words to use for transformations
        """
        # Store words in a set for O(1) lookup — much faster than list
        self.word_set = set(word.lower() for word in word_list)
        
    def _get_neighbors(self, word: str) -> List[str]:
        """
        Find all valid words that differ from the input by exactly one letter.
        
        I'm using a simple approach: try replacing each position with every letter
        from a-z and check if the result is in our word set.
        
        Args:
            word: The word to find neighbors for
            
        Returns:
            List of valid neighboring words
        """
        neighbors = []
        word_list = list(word)
        
        for i in range(len(word)):
            original_char = word_list[i]
            
            # Try every letter at this position
            for c in 'abcdefghijklmnopqrstuvwxyz':
                if c == original_char:
                    continue
                    
                word_list[i] = c
                candidate = ''.join(word_list)
                
                if candidate in self.word_set:
                    neighbors.append(candidate)
            
            # Restore original character before moving to next position
            word_list[i] = original_char
            
        return neighbors
    
    def find_ladder(self, start: str, end: str) -> Optional[List[str]]:
        """
        Find shortest word ladder from start to end using BFS.
        
        BFS is key here — it explores level by level, so the first time we reach
        the target word, we know we've found the shortest path.
        
        Args:
            start: Starting word
            end: Target word
            
        Returns:
            List of words forming the ladder, or None if no path exists
        """
        start = start.lower()
        end = end.lower()
        
        # Basic validation
        if len(start) != len(end):
            return None
        if start not in self.word_set or end not in self.word_set:
            return None
        if start == end:
            return [start]
        
        # BFS setup: queue stores (current_word, path_to_reach_it)
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            current_word, path = queue.popleft()
            
            # Check all neighboring words (one letter different)
            for neighbor in self._get_neighbors(current_word):
                if neighbor == end:
                    # Found it! Return the complete path
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        # No path exists
        return None
    
    def find_ladder_with_stats(self, start: str, end: str) -> Tuple[Optional[List[str]], dict]:
        """
        Find ladder and return statistics about the search.
        
        Args:
            start: Starting word
            end: Target word
            
        Returns:
            Tuple of (ladder path, stats dictionary)
        """
        start = start.lower()
        end = end.lower()
        
        stats = {
            'words_explored': 0,
            'max_queue_size': 0,
            'path_length': 0
        }
        
        if len(start) != len(end) or start not in self.word_set or end not in self.word_set:
            return None, stats
        
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            stats['max_queue_size'] = max(stats['max_queue_size'], len(queue))
            current_word, path = queue.popleft()
            stats['words_explored'] += 1
            
            for neighbor in self._get_neighbors(current_word):
                if neighbor == end:
                    result_path = path + [neighbor]
                    stats['path_length'] = len(result_path)
                    return result_path, stats
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None, stats


if __name__ == "__main__":
    # Demo with a small word list — normally you'd load from a dictionary file
    # but I wanted this to run standalone without external dependencies
    demo_words = [
        "cat", "cot", "dot", "dog", "dig", "big", "bag", "bat",
        "hat", "hot", "pot", "pat", "pit", "sit", "hit", "bit",
        "but", "cut", "cog", "log", "fog", "hog", "bog"
    ]
    
    solver = WordLadderSolver(demo_words)
    
    print("=== Word Ladder Solver Demo ===\n")
    
    # Test case 1: CAT -> DOG
    print("Finding ladder from CAT to DOG:")
    ladder, stats = solver.find_ladder_with_stats("cat", "dog")
    if ladder:
        print(f"  Path: {' -> '.join(ladder)}")
        print(f"  Length: {stats['path_length']} steps")
        print(f"  Explored {stats['words_explored']} words")
    else:
        print("  No path found!")
    
    print()
    
    # Test case 2: HIT -> COG
    print("Finding ladder from HIT to COG:")
    ladder, stats = solver.find_ladder_with_stats("hit", "cog")
    if ladder:
        print(f"  Path: {' -> '.join(ladder)}")
        print(f"  Length: {stats['path_length']} steps")
        print(f"  Explored {stats['words_explored']} words")
    else:
        print("  No path found!")
    
    print()
    
    # Test case 3: Impossible transformation
    print("Finding ladder from CAT to BIG:")
    ladder = solver.find_ladder("cat", "big")
    if ladder:
        print(f"  Path: {' -> '.join(ladder)}")
    else:
        print("  No path found! (probably need more connecting words)")