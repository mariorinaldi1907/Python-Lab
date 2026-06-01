"""
Date: 2026-06-01
Implemented a word ladder puzzle solver using bidirectional breadth-first search to find the shortest path between two words by changing one letter at a time.
"""

"""
Word Ladder Solver - finds shortest transformation path between two words.

This was fun to build because I wanted to explore bidirectional BFS properly.
The idea is to search from both ends simultaneously and meet in the middle,
which dramatically cuts down the search space compared to regular BFS.
"""

from collections import deque, defaultdict
from typing import List, Set, Optional, Tuple


class WordLadderSolver:
    """
    Solves word ladder puzzles using bidirectional BFS.
    
    A word ladder transforms one word into another by changing one letter
    at a time, with each intermediate step being a valid word.
    """
    
    def __init__(self, word_list: List[str]):
        """
        Initialize solver with a dictionary of valid words.
        
        Args:
            word_list: List of valid words to use in transformations
        """
        self.word_set = set(word.lower() for word in word_list)
        self._build_pattern_map()
    
    def _build_pattern_map(self):
        """
        Pre-compute pattern mappings for efficient neighbor finding.
        
        For example, "hot" creates patterns: "*ot", "h*t", "ho*"
        This lets us quickly find all words that differ by one letter.
        """
        self.pattern_map = defaultdict(list)
        for word in self.word_set:
            for i in range(len(word)):
                pattern = word[:i] + '*' + word[i+1:]
                self.pattern_map[pattern].append(word)
    
    def _get_neighbors(self, word: str) -> Set[str]:
        """
        Find all words that differ from the given word by exactly one letter.
        
        Args:
            word: The word to find neighbors for
            
        Returns:
            Set of neighboring words
        """
        neighbors = set()
        for i in range(len(word)):
            pattern = word[:i] + '*' + word[i+1:]
            neighbors.update(self.pattern_map.get(pattern, []))
        neighbors.discard(word)  # Don't include the word itself
        return neighbors
    
    def solve(self, start: str, end: str) -> Optional[List[str]]:
        """
        Find shortest word ladder from start to end using bidirectional BFS.
        
        The bidirectional approach searches from both ends and meets in the middle,
        which is way faster than searching from just one direction.
        
        Args:
            start: Starting word
            end: Target word
            
        Returns:
            List of words forming the ladder, or None if impossible
        """
        start, end = start.lower(), end.lower()
        
        # Basic validation
        if start == end:
            return [start]
        if len(start) != len(end):
            return None
        if start not in self.word_set or end not in self.word_set:
            return None
        
        # Two frontiers: searching from start and from end
        front_queue = deque([start])
        back_queue = deque([end])
        
        # Track visited nodes and their parents for path reconstruction
        front_visited = {start: None}
        back_visited = {end: None}
        
        while front_queue and back_queue:
            # Always expand the smaller frontier for efficiency
            if len(front_queue) <= len(back_queue):
                meeting_point = self._bfs_step(front_queue, front_visited, back_visited)
                if meeting_point:
                    return self._build_path(meeting_point, front_visited, back_visited)
            else:
                meeting_point = self._bfs_step(back_queue, back_visited, front_visited)
                if meeting_point:
                    return self._build_path(meeting_point, front_visited, back_visited)
        
        return None  # No path found
    
    def _bfs_step(self, queue: deque, visited: dict, other_visited: dict) -> Optional[str]:
        """
        Perform one BFS expansion step.
        
        Args:
            queue: Current frontier queue
            visited: Visited set for this direction
            other_visited: Visited set for the other direction
            
        Returns:
            Meeting point if frontiers meet, None otherwise
        """
        word = queue.popleft()
        
        for neighbor in self._get_neighbors(word):
            if neighbor in other_visited:
                # Frontiers met!
                return neighbor
            
            if neighbor not in visited:
                visited[neighbor] = word
                queue.append(neighbor)
        
        return None
    
    def _build_path(self, meeting: str, front_visited: dict, back_visited: dict) -> List[str]:
        """
        Reconstruct the full path when the two searches meet.
        
        Args:
            meeting: The word where searches met
            front_visited: Visited dict from start
            back_visited: Visited dict from end
            
        Returns:
            Complete path from start to end
        """
        # Build path from start to meeting point
        path = []
        current = meeting
        while current is not None:
            path.append(current)
            current = front_visited[current]
        path.reverse()
        
        # Build path from meeting point to end
        current = back_visited[meeting]
        while current is not None:
            path.append(current)
            current = back_visited[current]
        
        return path


if __name__ == "__main__":
    # Demo with a small test dictionary
    test_words = [
        "hit", "hot", "dot", "dog", "lot", "log", "cog",
        "hat", "cat", "bat", "mat", "sat", "rat", "fat",
        "bog", "hog", "fog", "jog", "tog"
    ]
    
    solver = WordLadderSolver(test_words)
    
    print("Word Ladder Solver Demo")
    print("=" * 50)
    
    test_cases = [
        ("hit", "cog"),
        ("cat", "dog"),
        ("hat", "fog"),
        ("bat", "rat"),
    ]
    
    for start, end in test_cases:
        print(f"\nFinding ladder from '{start}' to '{end}':")
        ladder = solver.solve(start, end)
        
        if ladder:
            print(f"  Found path ({len(ladder)} steps): {' -> '.join(ladder)}")
        else:
            print(f"  No path found!")