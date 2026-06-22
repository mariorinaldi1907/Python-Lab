"""
Date: 2026-06-22
Built a word ladder puzzle solver that finds the shortest transformation sequence between two words by changing one letter at a time.
"""

#!/usr/bin/env python3
"""
Word Ladder Solver using BFS

Finds the shortest transformation sequence from a start word to an end word,
where each step changes exactly one letter and every intermediate word must be valid.
Classic problem but always fun to implement — the BFS guarantees we find the shortest path.
"""

from collections import deque
from typing import List, Set, Optional


def get_word_variants(word: str, word_set: Set[str]) -> List[str]:
    """
    Generate all valid one-letter variations of a word.
    
    Instead of checking the entire dictionary for every word, we generate all
    possible single-letter changes and check if they exist in our word set.
    Way faster than iterating through thousands of words.
    
    Args:
        word: The word to generate variants for
        word_set: Set of valid words to check against
    
    Returns:
        List of valid words that differ by exactly one letter
    """
    variants = []
    for i in range(len(word)):
        for char in 'abcdefghijklmnopqrstuvwxyz':
            if char != word[i]:
                new_word = word[:i] + char + word[i+1:]
                if new_word in word_set:
                    variants.append(new_word)
    return variants


def find_word_ladder(start: str, end: str, word_list: List[str]) -> Optional[List[str]]:
    """
    Find shortest word ladder from start to end using BFS.
    
    BFS is perfect here because it explores level-by-level, guaranteeing that
    the first path we find to the target is the shortest one.
    
    Args:
        start: Starting word
        end: Target word
        word_list: List of valid dictionary words
    
    Returns:
        List representing the shortest transformation path, or None if impossible
    """
    if start == end:
        return [start]
    
    # Quick validation
    if len(start) != len(end):
        return None
    
    # Convert to set for O(1) lookups
    word_set = set(word_list)
    
    if end not in word_set:
        return None
    
    # BFS queue: each element is (current_word, path_to_current_word)
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        current_word, path = queue.popleft()
        
        # Try all single-letter variations
        for variant in get_word_variants(current_word, word_set):
            if variant == end:
                return path + [variant]
            
            if variant not in visited:
                visited.add(variant)
                queue.append((variant, path + [variant]))
    
    # No path found
    return None


def load_sample_dictionary() -> List[str]:
    """
    Create a sample dictionary for demonstration.
    
    In a real implementation I'd load from /usr/share/dict/words or a file,
    but keeping it self-contained for this demo. Just enough words to show
    interesting transformations.
    
    Returns:
        List of valid dictionary words
    """
    return [
        'hit', 'hot', 'dot', 'dog', 'lot', 'log', 'cog',
        'hat', 'cat', 'bat', 'rat', 'mat', 'sat', 'fat',
        'cab', 'lab', 'tab', 'dab', 'gab', 'jab', 'nab',
        'led', 'red', 'fed', 'bed', 'wed', 'ted',
        'lead', 'read', 'bead', 'dead', 'head',
        'heap', 'heat', 'peat', 'beat', 'meat', 'feat',
        'seat', 'peal', 'real', 'seal', 'teal', 'veal', 'zeal',
        'code', 'cade', 'care', 'core', 'come', 'home', 'dome',
        'cold', 'cord', 'card', 'ward', 'warm', 'worm', 'worn', 'word',
        'more', 'morn', 'torn', 'corn', 'coin', 'join', 'chin', 'thin',
        'sink', 'pink', 'link', 'lint', 'hint', 'mint', 'mind', 'kind',
        'king', 'ring', 'rang', 'bang', 'gang', 'fang', 'hang', 'sang',
    ]


def print_ladder(ladder: Optional[List[str]], start: str, end: str) -> None:
    """
    Pretty-print the word ladder result.
    
    Args:
        ladder: The transformation path (or None if no solution)
        start: Starting word
        end: Target word
    """
    print(f"\n{'='*50}")
    print(f"Word Ladder: '{start}' → '{end}'")
    print(f"{'='*50}")
    
    if ladder is None:
        print("❌ No solution found!")
        print("These words cannot be connected with the given dictionary.")
    else:
        print(f"✓ Found solution in {len(ladder)} steps:\n")
        for i, word in enumerate(ladder):
            if i < len(ladder) - 1:
                # Show which letter changed
                next_word = ladder[i + 1]
                diff_pos = [j for j in range(len(word)) if word[j] != next_word[j]][0]
                print(f"  {i+1}. {word}")
                print(f"     {'   ' * diff_pos}↓ (change '{word[diff_pos]}' to '{next_word[diff_pos]}')")
            else:
                print(f"  {i+1}. {word} ← TARGET")


if __name__ == "__main__":
    # Load our sample dictionary
    dictionary = load_sample_dictionary()
    
    print("Word Ladder Solver")
    print("==================")
    print(f"Dictionary loaded: {len(dictionary)} words\n")
    
    # Test cases that show different scenarios
    test_cases = [
        ('hit', 'cog'),  # Classic example
        ('cold', 'warm'), # Longer path
        ('cat', 'dog'),  # Should fail with our limited dictionary
        ('code', 'dome'), # Another valid path
    ]
    
    for start, end in test_cases:
        result = find_word_ladder(start, end, dictionary)
        print_ladder(result, start, end)
    
    print(f"\n{'='*50}")
    print("Done! BFS guarantees these are the shortest paths.")
    print(f"{'='*50}\n")