"""
Date: 2026-07-13
Implemented a BFS-based word ladder solver that finds the shortest path between two words by changing one letter at a time, because I wanted to practice graph traversal on something more interesting than just trees.
"""

"""
Word Ladder Solver using BFS

Finds the shortest transformation sequence from a start word to an end word,
where each intermediate word differs by exactly one letter. Classic BFS problem
that I wanted to implement cleanly with proper path reconstruction.
"""

from collections import deque
from typing import List, Set, Dict, Optional


def get_word_variants(word: str, valid_words: Set[str]) -> List[str]:
    """
    Generate all valid one-letter transformations of a word.
    
    I'm using the alphabet iteration approach here because it's cleaner than
    trying to filter a massive dictionary. For each position, try all 26 letters
    and keep the ones that are actually valid words.
    """
    variants = []
    for i in range(len(word)):
        for char in 'abcdefghijklmnopqrstuvwxyz':
            if char != word[i]:
                variant = word[:i] + char + word[i+1:]
                if variant in valid_words:
                    variants.append(variant)
    return variants


def find_word_ladder(start: str, end: str, word_list: List[str]) -> Optional[List[str]]:
    """
    Find shortest word ladder from start to end using BFS.
    
    Returns the path as a list of words, or None if no path exists.
    I'm tracking parents to reconstruct the path at the end rather than
    storing full paths in the queue (way more memory efficient).
    """
    if start == end:
        return [start]
    
    # Convert to set for O(1) lookups
    valid_words = set(word_list)
    
    if end not in valid_words:
        return None
    
    # BFS setup
    queue = deque([start])
    visited = {start}
    parent_map: Dict[str, str] = {}
    
    while queue:
        current = queue.popleft()
        
        # Try all one-letter transformations
        for variant in get_word_variants(current, valid_words):
            if variant in visited:
                continue
            
            visited.add(variant)
            parent_map[variant] = current
            
            # Found the target!
            if variant == end:
                # Reconstruct path by walking backwards through parents
                path = []
                node = end
                while node in parent_map:
                    path.append(node)
                    node = parent_map[node]
                path.append(start)
                return path[::-1]
            
            queue.append(variant)
    
    # No path exists
    return None


def load_sample_dictionary() -> List[str]:
    """
    Return a hardcoded word list for demo purposes.
    
    In a real implementation I'd load from a file, but for a self-contained
    demo this works fine. These are all 3-letter words.
    """
    return [
        'hot', 'dot', 'dog', 'lot', 'log', 'cog',
        'hit', 'hat', 'hog', 'bog', 'bag', 'big',
        'dig', 'dim', 'dam', 'ham', 'jam', 'jag',
        'tag', 'tan', 'ten', 'pen', 'pin', 'tin',
        'win', 'wit', 'bit', 'bat', 'cat', 'rat',
        'mat', 'mad', 'bad', 'bid', 'kid', 'kit'
    ]


def print_ladder(ladder: Optional[List[str]], start: str, end: str) -> None:
    """
    Pretty-print the word ladder result.
    
    Shows the transformation step-by-step with arrows, or a failure message.
    """
    print(f"\nSearching for path from '{start}' to '{end}'...")
    print("-" * 50)
    
    if ladder is None:
        print(f"❌ No valid word ladder found!")
    else:
        print(f"✓ Found ladder with {len(ladder)} words:\n")
        for i, word in enumerate(ladder):
            if i < len(ladder) - 1:
                # Highlight the changed letter
                next_word = ladder[i + 1]
                diff_idx = next((j for j in range(len(word)) if word[j] != next_word[j]), -1)
                print(f"  {i+1}. {word}  →  (change position {diff_idx})")
            else:
                print(f"  {i+1}. {word}  ✓ TARGET")


if __name__ == "__main__":
    print("=" * 50)
    print("Word Ladder Solver (BFS)")
    print("=" * 50)
    
    # Load dictionary
    dictionary = load_sample_dictionary()
    print(f"\nLoaded dictionary with {len(dictionary)} words")
    
    # Test case 1: Classic example
    result1 = find_word_ladder('hit', 'cog', dictionary)
    print_ladder(result1, 'hit', 'cog')
    
    # Test case 2: Shorter path
    result2 = find_word_ladder('cat', 'dog', dictionary)
    print_ladder(result2, 'cat', 'dog')
    
    # Test case 3: Impossible transformation
    result3 = find_word_ladder('hit', 'xyz', dictionary)
    print_ladder(result3, 'hit', 'xyz')
    
    # Test case 4: Adjacent words
    result4 = find_word_ladder('hot', 'hat', dictionary)
    print_ladder(result4, 'hot', 'hat')
    
    print("\n" + "=" * 50)