"""
Date: 2026-05-28
Built a word ladder solver that finds the shortest transformation path between two words using BFS — throws in bidirectional search when the word list gets big.
"""

#!/usr/bin/env python3
"""
Word Ladder Solver - finds shortest path between two words by changing one letter at a time.

I always thought word ladders were a neat little puzzle. This implementation uses BFS
to find the shortest path, and I added bidirectional search because why not make it faster
when dealing with larger dictionaries. The key insight is that each word is a node and
edges exist between words that differ by exactly one letter.
"""

from collections import deque, defaultdict
from typing import List, Set, Tuple, Optional


def load_word_list() -> Set[str]:
    """
    Returns a curated set of 4-letter words for demo purposes.
    
    In a real scenario I'd load from /usr/share/dict/words or similar,
    but keeping it self-contained for now.
    """
    return {
        "cold", "cord", "card", "ward", "warm", "harm", "hard", "hare",
        "care", "case", "cast", "last", "lost", "cost", "most", "mist",
        "fist", "fish", "wish", "wash", "bash", "base", "bask", "task",
        "tall", "tale", "pale", "pall", "poll", "pool", "cool", "fool",
        "food", "good", "gold", "bold", "bind", "wind", "wine", "mine",
        "line", "lane", "sane", "sand", "said", "sail", "tail", "fail",
        "fair", "hair", "pair", "pain", "rain", "ruin", "rein", "vein"
    }


def get_neighbors(word: str, word_set: Set[str]) -> List[str]:
    """
    Find all valid words that differ by exactly one letter.
    
    I'm using the "try all 26 letters" approach rather than pre-building
    a graph because it's simpler and fast enough for reasonable word lengths.
    """
    neighbors = []
    for i in range(len(word)):
        for c in 'abcdefghijklmnopqrstuvwxyz':
            if c != word[i]:
                candidate = word[:i] + c + word[i+1:]
                if candidate in word_set:
                    neighbors.append(candidate)
    return neighbors


def bfs_word_ladder(start: str, end: str, word_set: Set[str]) -> Optional[List[str]]:
    """
    Standard BFS to find shortest transformation path.
    
    Returns the path as a list of words, or None if no path exists.
    """
    if start == end:
        return [start]
    if start not in word_set or end not in word_set:
        return None
    
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        current_word, path = queue.popleft()
        
        for neighbor in get_neighbors(current_word, word_set):
            if neighbor == end:
                return path + [neighbor]
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    return None


def bidirectional_bfs(start: str, end: str, word_set: Set[str]) -> Optional[List[str]]:
    """
    Bidirectional BFS - search from both ends and meet in the middle.
    
    This can be significantly faster for long paths since we're essentially
    cutting the search depth in half. The tricky part is reconstructing the
    path when the two searches meet.
    """
    if start == end:
        return [start]
    if start not in word_set or end not in word_set:
        return None
    
    # Forward search: start -> end
    forward_queue = deque([start])
    forward_visited = {start: [start]}
    
    # Backward search: end -> start
    backward_queue = deque([end])
    backward_visited = {end: [end]}
    
    while forward_queue and backward_queue:
        # Expand forward frontier
        current = forward_queue.popleft()
        for neighbor in get_neighbors(current, word_set):
            if neighbor in backward_visited:
                # Found intersection! Reconstruct path
                forward_path = forward_visited[current]
                backward_path = backward_visited[neighbor]
                return forward_path + backward_path[::-1]
            
            if neighbor not in forward_visited:
                forward_visited[neighbor] = forward_visited[current] + [neighbor]
                forward_queue.append(neighbor)
        
        # Expand backward frontier
        current = backward_queue.popleft()
        for neighbor in get_neighbors(current, word_set):
            if neighbor in forward_visited:
                # Found intersection!
                forward_path = forward_visited[neighbor]
                backward_path = backward_visited[current]
                return forward_path + backward_path[::-1]
            
            if neighbor not in backward_visited:
                backward_visited[neighbor] = backward_visited[current] + [neighbor]
                backward_queue.append(neighbor)
    
    return None


def print_ladder(path: Optional[List[str]], start: str, end: str) -> None:
    """Pretty print the word ladder solution."""
    print(f"\n{'='*50}")
    print(f"Word Ladder: {start.upper()} → {end.upper()}")
    print('='*50)
    
    if path is None:
        print("❌ No valid transformation path exists!")
    else:
        print(f"✓ Found path with {len(path)} steps:\n")
        for i, word in enumerate(path):
            if i > 0:
                # Highlight the changed letter
                prev = path[i-1]
                highlighted = ""
                for j in range(len(word)):
                    if word[j] != prev[j]:
                        highlighted += f"[{word[j].upper()}]"
                    else:
                        highlighted += word[j]
                print(f"  {i}. {highlighted}")
            else:
                print(f"  {i}. {word}")
    print('='*50)


if __name__ == "__main__":
    words = load_word_list()
    
    print("Word Ladder Solver")
    print("=" * 50)
    print(f"Dictionary size: {len(words)} words\n")
    
    # Test cases - some easy, some harder
    test_cases = [
        ("cold", "warm"),
        ("fish", "tail"),
        ("good", "cold"),
        ("mine", "task"),
    ]
    
    for start, end in test_cases:
        # Using bidirectional search since it's cooler
        path = bidirectional_bfs(start, end, words)
        print_ladder(path, start, end)
        print()
    
    print("\n💡 Try it yourself!")
    print("Available words include: cold, warm, fish, gold, wine, pool, etc.")