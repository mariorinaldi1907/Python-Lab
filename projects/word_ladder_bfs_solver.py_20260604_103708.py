"""
Date: 2026-06-04
Built a word ladder puzzle solver that finds the shortest transformation path between two words using bidirectional BFS — fun excuse to optimize graph search.
"""

#!/usr/bin/env python3
"""
Word Ladder Solver using Bidirectional BFS

A word ladder is a sequence of words where each word differs from the previous
by exactly one letter. This solver finds the shortest ladder between two words.

I chose bidirectional BFS because it dramatically reduces the search space —
instead of exploring d^n nodes, we explore 2*(d^(n/2)) where d is branching
factor and n is distance. Makes a huge difference on longer paths.
"""

from collections import deque
from typing import Set, List, Optional, Dict


def load_dictionary(word_length: int = 4) -> Set[str]:
    """
    Load a simple built-in dictionary of words.
    
    In a real scenario I'd load from /usr/share/dict/words or similar,
    but for demo purposes I'm including a reasonable test set inline.
    """
    # Small curated list for demonstration — normally I'd read from a file
    words = {
        "cold", "cord", "card", "ward", "warm", "harm", "farm", "fork",
        "work", "word", "wood", "food", "fool", "cool", "pool", "poll",
        "pork", "port", "sort", "sore", "core", "come", "home", "dome",
        "dose", "rose", "lose", "lone", "line", "wine", "mine", "mint",
        "hint", "hunt", "hurt", "hart", "part", "park", "dark", "dare",
        "care", "cake", "make", "made", "mode", "mole", "hole", "hold",
        "gold", "golf", "wolf", "wood", "wool", "cool", "cook", "book",
        "look", "lock", "lick", "tick", "sick", "sink", "link", "pink",
        "pine", "pipe", "ripe", "rice", "race", "pace", "page", "rage",
        "sage", "save", "wave", "wake", "bake", "bike", "bite", "site"
    }
    return {w for w in words if len(w) == word_length}


def get_neighbors(word: str, dictionary: Set[str]) -> List[str]:
    """
    Find all valid one-letter transformations of the given word.
    
    I initially tried a smarter approach with pattern matching, but
    this brute force method is actually cleaner and fast enough.
    """
    neighbors = []
    for i in range(len(word)):
        for c in 'abcdefghijklmnopqrstuvwxyz':
            if c != word[i]:
                candidate = word[:i] + c + word[i+1:]
                if candidate in dictionary:
                    neighbors.append(candidate)
    return neighbors


def bidirectional_bfs(start: str, end: str, dictionary: Set[str]) -> Optional[List[str]]:
    """
    Find shortest word ladder using bidirectional BFS.
    
    The key insight: search from both ends simultaneously and stop when
    the frontiers meet. This cuts search time drastically compared to
    unidirectional BFS because we're searching two shallow trees instead
    of one deep tree.
    """
    if start == end:
        return [start]
    
    if start not in dictionary or end not in dictionary:
        return None
    
    # Forward search: from start
    forward_queue = deque([start])
    forward_visited = {start: None}  # Maps word -> parent for path reconstruction
    
    # Backward search: from end
    backward_queue = deque([end])
    backward_visited = {end: None}
    
    while forward_queue and backward_queue:
        # Expand the smaller frontier first (optimization I added after testing)
        if len(forward_queue) <= len(backward_queue):
            result = _bfs_step(forward_queue, forward_visited, backward_visited, dictionary)
            if result:
                meeting_point = result
                return _reconstruct_path(start, end, meeting_point, 
                                        forward_visited, backward_visited)
        else:
            result = _bfs_step(backward_queue, backward_visited, forward_visited, dictionary)
            if result:
                meeting_point = result
                return _reconstruct_path(start, end, meeting_point,
                                        forward_visited, backward_visited)
    
    return None  # No path exists


def _bfs_step(queue: deque, visited: Dict[str, Optional[str]], 
              other_visited: Dict[str, Optional[str]], dictionary: Set[str]) -> Optional[str]:
    """
    Perform one BFS expansion step.
    
    Returns the meeting point if frontiers collide, otherwise None.
    """
    current = queue.popleft()
    
    for neighbor in get_neighbors(current, dictionary):
        if neighbor in other_visited:
            # Frontiers met! Return the meeting point
            return neighbor
        
        if neighbor not in visited:
            visited[neighbor] = current
            queue.append(neighbor)
    
    return None


def _reconstruct_path(start: str, end: str, meeting_point: str,
                     forward_visited: Dict[str, Optional[str]],
                     backward_visited: Dict[str, Optional[str]]) -> List[str]:
    """
    Rebuild the full path once frontiers meet.
    
    Walk backwards from meeting point to start, then forward to end.
    """
    # Build path from start to meeting point
    path = []
    current = meeting_point
    while current is not None:
        path.append(current)
        current = forward_visited[current]
    path.reverse()
    
    # Build path from meeting point to end (excluding meeting point itself)
    current = backward_visited[meeting_point]
    while current is not None:
        path.append(current)
        current = backward_visited[current]
    
    return path


def solve_word_ladder(start: str, end: str, word_length: int = 4) -> None:
    """
    Main solver function that orchestrates dictionary loading and pathfinding.
    """
    print(f"\n{'='*60}")
    print(f"Word Ladder: {start.upper()} → {end.upper()}")
    print(f"{'='*60}")
    
    dictionary = load_dictionary(word_length)
    print(f"Loaded {len(dictionary)} words of length {word_length}")
    
    path = bidirectional_bfs(start, end, dictionary)
    
    if path:
        print(f"\nFound ladder in {len(path)} steps:")
        for i, word in enumerate(path):
            print(f"  {i+1}. {word.upper()}")
    else:
        print(f"\nNo valid ladder exists between '{start}' and '{end}'")


if __name__ == "__main__":
    # Demo with a few interesting word pairs
    # I picked these because they have nice medium-length paths
    
    solve_word_ladder("cold", "warm")
    solve_word_ladder("work", "play")  # This won't find a path with our limited dict
    solve_word_ladder("dark", "cool")
    
    print("\n" + "="*60)
    print("Solver complete! Bidirectional BFS really shines here.")
    print("="*60)