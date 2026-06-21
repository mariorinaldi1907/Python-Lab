"""
Date: 2026-06-21
Built a word ladder solver using BFS to find the shortest transformation path between two words — added bidirectional search because I got curious about optimization.
"""

#!/usr/bin/env python3
"""
Word Ladder Solver using BFS with bidirectional search optimization.

A word ladder connects two words by changing one letter at a time,
where each intermediate step must also be a valid word.
"""

from collections import deque
from typing import Set, List, Optional, Dict


def load_word_list() -> Set[str]:
    """
    Load a basic word list for demonstration.
    
    In a real scenario, I'd read from /usr/share/dict/words or a file,
    but keeping it self-contained here with a curated sample set.
    """
    words = {
        "cold", "cord", "card", "ward", "warm", "harm", "farm", "form",
        "coal", "foal", "fail", "fall", "gall", "ball", "bell", "bill",
        "bolt", "colt", "cols", "cogs", "dogs", "doge", "dose", "rose",
        "code", "cods", "gods", "gold", "hold", "told", "toll", "tall",
        "tail", "mail", "main", "rain", "ruin", "spin", "span", "swan",
        "seed", "sees", "bees", "been", "bean", "bear", "fear", "gear",
        "lead", "read", "road", "load", "goad", "good", "food", "fool",
        "cool", "pool", "poll", "pole", "pale", "sale", "same", "came",
        "cape", "tape", "tale", "tall", "call", "cell", "sell", "seal",
        "teal", "tell", "well", "wall", "walk", "talk", "balk", "bark"
    }
    return words


def get_neighbors(word: str, word_set: Set[str]) -> List[str]:
    """
    Find all valid words that differ by exactly one letter.
    
    I'm generating neighbors by trying all possible single-letter substitutions
    instead of using a more complex bucket/pattern approach — simpler for small sets.
    """
    neighbors = []
    for i in range(len(word)):
        for c in 'abcdefghijklmnopqrstuvwxyz':
            if c != word[i]:
                candidate = word[:i] + c + word[i+1:]
                if candidate in word_set:
                    neighbors.append(candidate)
    return neighbors


def bidirectional_bfs(start: str, end: str, word_set: Set[str]) -> Optional[List[str]]:
    """
    Use bidirectional BFS to find the shortest word ladder.
    
    Why bidirectional? It explores from both ends simultaneously, which can
    dramatically reduce the search space. When the two searches meet, we've
    found our path. This is especially helpful for longer ladders.
    """
    if start not in word_set or end not in word_set:
        return None
    
    if start == end:
        return [start]
    
    # Track visited nodes and their parents for path reconstruction
    visited_start = {start: None}
    visited_end = {end: None}
    
    queue_start = deque([start])
    queue_end = deque([end])
    
    while queue_start and queue_end:
        # Always expand the smaller frontier to keep things balanced
        if len(queue_start) <= len(queue_end):
            meeting_point = _bfs_step(queue_start, visited_start, visited_end, word_set)
            if meeting_point:
                return _reconstruct_path(meeting_point, visited_start, visited_end)
        else:
            meeting_point = _bfs_step(queue_end, visited_end, visited_start, word_set)
            if meeting_point:
                return _reconstruct_path(meeting_point, visited_start, visited_end)
    
    return None  # No path exists


def _bfs_step(queue: deque, visited_this: Dict[str, Optional[str]], 
              visited_other: Dict[str, Optional[str]], word_set: Set[str]) -> Optional[str]:
    """
    Perform one BFS step and check if we've met the other search.
    
    Returns the meeting point word if searches have met, otherwise None.
    """
    current = queue.popleft()
    
    for neighbor in get_neighbors(current, word_set):
        if neighbor in visited_other:
            # The two searches have met!
            visited_this[neighbor] = current
            return neighbor
        
        if neighbor not in visited_this:
            visited_this[neighbor] = current
            queue.append(neighbor)
    
    return None


def _reconstruct_path(meeting_point: str, visited_start: Dict[str, Optional[str]], 
                      visited_end: Dict[str, Optional[str]]) -> List[str]:
    """
    Reconstruct the full path by tracing back from the meeting point.
    
    Build the path from start to meeting point, then from meeting point to end,
    being careful not to duplicate the meeting point itself.
    """
    # Build path from start to meeting point
    path_start = []
    node = meeting_point
    while node is not None:
        path_start.append(node)
        node = visited_start[node]
    path_start.reverse()
    
    # Build path from meeting point to end
    path_end = []
    node = visited_end[meeting_point]
    while node is not None:
        path_end.append(node)
        node = visited_end[node]
    
    return path_start + path_end


def solve_word_ladder(start: str, end: str, word_set: Set[str]) -> Optional[List[str]]:
    """
    Main solver function — validates inputs and delegates to BFS.
    """
    if len(start) != len(end):
        return None
    
    # Normalize to lowercase for consistency
    start = start.lower()
    end = end.lower()
    
    return bidirectional_bfs(start, end, word_set)


if __name__ == "__main__":
    print("Word Ladder Solver Demo")
    print("=" * 50)
    
    words = load_word_list()
    print(f"Loaded {len(words)} words\n")
    
    # Test cases that I know have interesting paths
    test_cases = [
        ("cold", "warm"),
        ("lead", "gold"),
        ("code", "data"),  # This one won't have a path with our word set
        ("ball", "bear"),
    ]
    
    for start, end in test_cases:
        print(f"Finding ladder from '{start}' to '{end}'...")
        path = solve_word_ladder(start, end, words)
        
        if path:
            print(f"  Found path (length {len(path)}): {' -> '.join(path)}")
        else:
            print(f"  No path exists (or word not in dictionary)")
        print()