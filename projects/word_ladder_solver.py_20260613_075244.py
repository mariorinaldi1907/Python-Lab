"""
Date: 2026-06-13
Built a word ladder puzzle solver that finds the shortest path between two words by changing one letter at a time, using BFS because it guarantees the shortest path.
"""

"""
Word Ladder Solver - finds the shortest transformation path between two words.

This was fun to build because it's basically a graph search problem in disguise.
Each word is a node, and edges exist between words that differ by exactly one letter.
I'm using BFS because we want the *shortest* path, not just any path.
"""

from collections import deque
from typing import List, Set, Optional, Tuple


def get_neighbors(word: str, word_set: Set[str]) -> List[str]:
    """
    Find all valid words that differ by exactly one letter.
    
    Instead of checking every word in the dictionary, I generate all possible
    one-letter transformations and check if they're valid. Way faster for
    large dictionaries.
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
    Find the shortest transformation sequence from start to end.
    
    Returns the path as a list of words, or None if no path exists.
    Uses BFS to guarantee we find the shortest path first.
    """
    # Basic validation
    if start == end:
        return [start]
    
    word_set = set(word_list)
    if end not in word_set:
        return None
    
    # BFS setup: queue stores (current_word, path_taken)
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        current_word, path = queue.popleft()
        
        # Check all neighbors (words one letter away)
        for neighbor in get_neighbors(current_word, word_set):
            if neighbor == end:
                return path + [neighbor]
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    return None


def generate_sample_dictionary() -> List[str]:
    """
    Create a small but interesting word list for testing.
    
    I picked words that create multiple possible paths, making the
    solver actually do some work to find the shortest one.
    """
    return [
        'hit', 'hot', 'dot', 'dog', 'lot', 'log', 'cog',
        'dit', 'hat', 'hog', 'bog', 'bag', 'big', 'dig',
        'pig', 'fig', 'fit', 'fat', 'cat', 'cot', 'bat',
        'mat', 'mit', 'sit', 'set', 'sat', 'pat', 'pot',
        'got', 'bot', 'rot', 'rat', 'rag', 'tag', 'tan',
        'can', 'man', 'map', 'cap', 'cop', 'top', 'tip',
        'hip', 'hop', 'pop', 'pep', 'rep', 'red', 'led',
        'bed', 'bad', 'dad', 'mad', 'had', 'has', 'was',
        'war', 'car', 'bar', 'far', 'tar', 'par'
    ]


def print_solution(start: str, end: str, path: Optional[List[str]]) -> None:
    """
    Pretty-print the solution path with visual indicators of what changed.
    
    This makes it way easier to see that each step really is just one letter.
    """
    print(f"\n{'='*50}")
    print(f"Finding path from '{start}' to '{end}'")
    print(f"{'='*50}")
    
    if path is None:
        print("❌ No valid transformation path exists!")
        return
    
    print(f"✓ Found path in {len(path)} steps:\n")
    
    for i, word in enumerate(path):
        if i == 0:
            print(f"  {i+1}. {word} (start)")
        elif i == len(path) - 1:
            print(f"  {i+1}. {word} (end)")
        else:
            # Highlight what changed from previous word
            prev = path[i-1]
            changes = [f"[{word[j]}]" if word[j] != prev[j] else word[j] 
                      for j in range(len(word))]
            print(f"  {i+1}. {''.join(changes)}")


if __name__ == "__main__":
    # Set up test dictionary
    dictionary = generate_sample_dictionary()
    print(f"Loaded dictionary with {len(dictionary)} words")
    
    # Test case 1: Classic example
    test_cases = [
        ("hit", "cog"),
        ("dog", "cat"),
        ("hot", "dog"),
        ("pig", "pot"),
        ("hit", "xyz"),  # Impossible case
    ]
    
    for start, end in test_cases:
        result = word_ladder(start, end, dictionary)
        print_solution(start, end, result)
    
    # Show some stats
    print(f"\n{'='*50}")
    print("Algorithm notes:")
    print("• Uses BFS for guaranteed shortest path")
    print("• Visited set prevents cycles and redundant work")
    print("• Neighbor generation is O(26*n) where n is word length")
    print(f"{'='*50}\n")