"""
Date: 2026-08-07
Built a word ladder puzzle solver that finds the shortest transformation path between two words by changing one letter at a time — uses BFS for optimal pathfinding.
"""

#!/usr/bin/env python3
"""
Word Ladder Solver using BFS

Finds the shortest transformation sequence from a start word to an end word,
where each intermediate word differs by exactly one letter and must be valid.
Classic puzzle that I remember from those word game apps.
"""

from collections import deque
from typing import List, Set, Optional


def get_neighbors(word: str, word_set: Set[str]) -> List[str]:
    """
    Find all valid words that differ by exactly one letter.
    
    I'm using the approach where we try all 26 letters at each position
    instead of checking every word in the dictionary — much faster for
    smaller word sets since it's O(26 * word_length) instead of O(dict_size).
    """
    neighbors = []
    for i in range(len(word)):
        for char in 'abcdefghijklmnopqrstuvwxyz':
            if char != word[i]:
                candidate = word[:i] + char + word[i+1:]
                if candidate in word_set:
                    neighbors.append(candidate)
    return neighbors


def word_ladder(start: str, end: str, word_list: List[str]) -> Optional[List[str]]:
    """
    Find shortest word ladder from start to end using BFS.
    
    Returns the path as a list of words, or None if no path exists.
    BFS guarantees we find the shortest path since all edges have equal weight.
    """
    if start == end:
        return [start]
    
    # Convert to set for O(1) lookup
    word_set = set(word_list)
    
    if end not in word_set:
        return None
    
    # Add start word to the set in case it's not there
    word_set.add(start)
    
    # BFS queue stores (current_word, path_to_current_word)
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        current_word, path = queue.popleft()
        
        # Try all possible one-letter transformations
        for neighbor in get_neighbors(current_word, word_set):
            if neighbor == end:
                return path + [neighbor]
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    # No path found
    return None


def bidirectional_word_ladder(start: str, end: str, word_list: List[str]) -> Optional[List[str]]:
    """
    Faster bidirectional BFS approach for word ladder.
    
    Search from both start and end simultaneously, which can significantly
    reduce the search space. When the two searches meet, we've found the path.
    This is overkill for small dictionaries but fun to implement.
    """
    if start == end:
        return [start]
    
    word_set = set(word_list)
    if end not in word_set:
        return None
    
    word_set.add(start)
    
    # Forward and backward frontiers (just sets of words at current level)
    forward_frontier = {start}
    backward_frontier = {end}
    
    # Store the full paths
    forward_paths = {start: [start]}
    backward_paths = {end: [end]}
    
    while forward_frontier and backward_frontier:
        # Always expand the smaller frontier for efficiency
        if len(forward_frontier) > len(backward_frontier):
            forward_frontier, backward_frontier = backward_frontier, forward_frontier
            forward_paths, backward_paths = backward_paths, forward_paths
        
        next_frontier = set()
        next_paths = {}
        
        for word in forward_frontier:
            for neighbor in get_neighbors(word, word_set):
                # Check if we've met the other search
                if neighbor in backward_frontier:
                    # Reconstruct the full path
                    forward_path = forward_paths[word] + [neighbor]
                    backward_path = backward_paths[neighbor]
                    # Reverse one path and combine (avoiding duplicate middle word)
                    return forward_path + backward_path[::-1][1:]
                
                if neighbor not in forward_paths:
                    next_frontier.add(neighbor)
                    next_paths[neighbor] = forward_paths[word] + [neighbor]
        
        forward_frontier = next_frontier
        forward_paths.update(next_paths)
    
    return None


if __name__ == "__main__":
    # Demo with a simple word list
    # In a real app, I'd load this from /usr/share/dict/words or similar
    demo_words = [
        "hit", "hot", "dot", "dog", "lot", "log", "cog",
        "dit", "hat", "hog", "dag", "dig", "big", "bag",
        "cat", "can", "man", "mat", "bat", "bad", "mad"
    ]
    
    print("Word Ladder Solver Demo")
    print("=" * 50)
    
    # Test case 1: Classic example
    start1, end1 = "hit", "cog"
    path1 = word_ladder(start1, end1, demo_words)
    print(f"\nFinding path from '{start1}' to '{end1}':")
    if path1:
        print(f"  Path ({len(path1)} steps): {' -> '.join(path1)}")
    else:
        print("  No path found!")
    
    # Test case 2: Another transformation
    start2, end2 = "cat", "dog"
    path2 = word_ladder(start2, end2, demo_words)
    print(f"\nFinding path from '{start2}' to '{end2}':")
    if path2:
        print(f"  Path ({len(path2)} steps): {' -> '.join(path2)}")
    else:
        print("  No path found!")
    
    # Test case 3: Using bidirectional search
    start3, end3 = "hit", "cog"
    path3 = bidirectional_word_ladder(start3, end3, demo_words)
    print(f"\nBidirectional search from '{start3}' to '{end3}':")
    if path3:
        print(f"  Path ({len(path3)} steps): {' -> '.join(path3)}")
    else:
        print("  No path found!")
    
    # Test case 4: Impossible transformation
    start4, end4 = "cat", "xyz"
    path4 = word_ladder(start4, end4, demo_words)
    print(f"\nFinding path from '{start4}' to '{end4}' (should fail):")
    if path4:
        print(f"  Path ({len(path4)} steps): {' -> '.join(path4)}")
    else:
        print("  No path found! (expected)")