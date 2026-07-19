"""
Date: 2026-07-19
Wrote a BFS-based word ladder solver that finds the shortest transformation sequence between two words, changing only one letter per step.
"""

#!/usr/bin/env python3
"""
Word Ladder Solver - finds shortest path between two words.

I always thought word ladders were a fun puzzle, so I wanted to code up
a proper solver using BFS. The trick is efficiently finding neighbors
(words that differ by exactly one letter) without checking every word
in the dictionary each time.
"""

from collections import deque
from typing import List, Set, Dict, Optional


def load_word_list() -> Set[str]:
    """
    Load a basic word list for the puzzle.
    
    In a real scenario I'd load from /usr/share/dict/words or similar,
    but for this demo I'm just using a hardcoded list of common 4-letter words.
    """
    # Using a curated small set for demo purposes
    words = {
        'cold', 'cord', 'card', 'ward', 'warm', 'worm', 'word', 'work',
        'pork', 'port', 'part', 'past', 'last', 'lash', 'hash', 'bash',
        'base', 'case', 'cast', 'mast', 'most', 'cost', 'lost', 'list',
        'fist', 'fish', 'dish', 'dash', 'rash', 'cash', 'came', 'come',
        'home', 'hope', 'rope', 'rose', 'nose', 'note', 'vote', 'vole',
        'role', 'hole', 'pole', 'pale', 'tale', 'take', 'make', 'made',
        'fade', 'face', 'pace', 'race', 'rare', 'care', 'core', 'gore',
        'more', 'move', 'love', 'lose', 'dose', 'dove', 'dote', 'date',
        'dare', 'hare', 'hard', 'harm', 'farm', 'form', 'fork', 'fort',
        'foot', 'food', 'good', 'mood', 'wood', 'wool', 'cool', 'pool',
        'poll', 'toll', 'tall', 'ball', 'call', 'wall', 'walk', 'talk',
        'tail', 'fail', 'fall', 'fell', 'tell', 'bell', 'well', 'will',
        'till', 'hill', 'fill', 'kill', 'kite', 'site', 'sire', 'fire',
        'fine', 'line', 'wine', 'mine', 'mint', 'hint', 'hunt', 'hurt',
        'curt', 'cart', 'cats', 'bats', 'bits', 'sits', 'sets', 'bets'
    }
    return words


def get_neighbors(word: str, word_set: Set[str]) -> List[str]:
    """
    Find all valid words that differ by exactly one letter.
    
    This generates all possible one-letter variations and checks
    if they exist in our word set. Not the most efficient approach
    for huge dictionaries, but clean and works great for this scale.
    """
    neighbors = []
    for i in range(len(word)):
        for c in 'abcdefghijklmnopqrstuvwxyz':
            if c != word[i]:
                candidate = word[:i] + c + word[i+1:]
                if candidate in word_set:
                    neighbors.append(candidate)
    return neighbors


def find_word_ladder(start: str, end: str, word_set: Set[str]) -> Optional[List[str]]:
    """
    Use BFS to find the shortest transformation sequence.
    
    BFS guarantees we find the shortest path. We track the path to each
    word so we can reconstruct the full ladder at the end. I used a dict
    to store parent pointers instead of storing full paths in the queue
    to save memory.
    """
    if start not in word_set or end not in word_set:
        return None
    
    if start == end:
        return [start]
    
    # BFS setup
    queue = deque([start])
    visited = {start}
    parent: Dict[str, str] = {}
    
    while queue:
        current = queue.popleft()
        
        # Check all neighbors
        for neighbor in get_neighbors(current, word_set):
            if neighbor in visited:
                continue
                
            visited.add(neighbor)
            parent[neighbor] = current
            
            # Found the target!
            if neighbor == end:
                # Reconstruct path by following parent pointers backward
                path = []
                node = end
                while node in parent:
                    path.append(node)
                    node = parent[node]
                path.append(start)
                return path[::-1]  # Reverse to get start->end order
            
            queue.append(neighbor)
    
    # No path exists
    return None


def print_ladder(ladder: Optional[List[str]], start: str, end: str) -> None:
    """
    Pretty-print the word ladder result.
    
    Shows each transformation step and highlights what changed.
    """
    if ladder is None:
        print(f"No ladder found from '{start}' to '{end}'")
        return
    
    print(f"Found ladder from '{start}' to '{end}' in {len(ladder)} steps:")
    for i, word in enumerate(ladder):
        if i > 0:
            # Highlight the changed letter
            prev = ladder[i-1]
            diff_idx = [j for j in range(len(word)) if word[j] != prev[j]]
            if diff_idx:
                changed = word[diff_idx[0]]
                print(f"  {i}. {word}  (changed to '{changed}')")
            else:
                print(f"  {i}. {word}")
        else:
            print(f"  {i}. {word}  (start)")
    print()


if __name__ == "__main__":
    # Load our word dictionary
    words = load_word_list()
    
    # Test cases I found interesting while building this
    test_cases = [
        ('cold', 'warm'),  # Classic example
        ('lost', 'find'),  # Impossible with this word set
        ('love', 'hate'),  # Philosophical :)
        ('code', 'data'),  # Dev-themed
        ('make', 'hard'),  # Random test
    ]
    
    print("=" * 50)
    print("Word Ladder Solver Demo")
    print("=" * 50)
    print()
    
    for start, end in test_cases:
        # Only process if both words are in our set
        if start in words and end in words:
            ladder = find_word_ladder(start, end, words)
            print_ladder(ladder, start, end)
        else:
            missing = []
            if start not in words:
                missing.append(f"'{start}'")
            if end not in words:
                missing.append(f"'{end}'")
            print(f"Skipping {start}->{end}: {', '.join(missing)} not in dictionary\n")