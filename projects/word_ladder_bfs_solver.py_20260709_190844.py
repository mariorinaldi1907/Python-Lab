"""
Date: 2026-07-09
Implemented a BFS-based word ladder puzzle solver that finds the shortest transformation sequence between two words, perfect for those NYT-style puzzles I keep seeing.
"""

#!/usr/bin/env python3
"""
Word Ladder Solver - finds shortest path between two words by changing one letter at a time.
Each intermediate word must be a valid English word.

I built this after getting stuck on too many word ladder puzzles online.
Uses BFS because we want the *shortest* path, not just any path.
"""

from collections import deque
from typing import List, Set, Optional, Dict


def load_word_list() -> Set[str]:
    """
    Load a basic word list for the puzzle.
    In a real scenario, you'd load from /usr/share/dict/words or similar.
    For this demo, I'm using a curated set of common 4-letter words.
    """
    # Small curated list for demo purposes — keeps output readable
    words = {
        "cold", "cord", "card", "ward", "warm", "harm", "hard", "hare",
        "care", "core", "wore", "wire", "fire", "fore", "food", "good",
        "wood", "word", "work", "pork", "port", "part", "past", "fast",
        "cast", "case", "base", "vase", "vast", "last", "lost", "cost",
        "host", "most", "mist", "fist", "fish", "dish", "wish", "wash",
        "bash", "dash", "rash", "rush", "gush", "push", "posh", "post",
        "pose", "rose", "lose", "loss", "boss", "toss", "toys", "boys",
        "bows", "cows", "rows", "crow", "grow", "glow", "slow", "slot",
        "shot", "shop", "ship", "skip", "skin", "spin", "spit", "spot"
    }
    return words


def get_neighbors(word: str, word_set: Set[str]) -> List[str]:
    """
    Find all valid words that differ by exactly one letter.
    This is the key operation for building our graph of word connections.
    """
    neighbors = []
    
    # Try changing each position to every letter a-z
    for i in range(len(word)):
        for c in 'abcdefghijklmnopqrstuvwxyz':
            if c == word[i]:
                continue  # Skip same letter
            
            # Build candidate word with one letter changed
            candidate = word[:i] + c + word[i+1:]
            
            if candidate in word_set:
                neighbors.append(candidate)
    
    return neighbors


def find_word_ladder(start: str, end: str, word_set: Set[str]) -> Optional[List[str]]:
    """
    Use BFS to find shortest transformation sequence from start to end.
    Returns the path as a list, or None if no path exists.
    
    BFS guarantees we find the shortest path because we explore level by level.
    """
    if start not in word_set or end not in word_set:
        return None
    
    if start == end:
        return [start]
    
    # BFS setup: queue stores (current_word, path_to_current)
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        current_word, path = queue.popleft()
        
        # Check all neighbors (words one letter away)
        for neighbor in get_neighbors(current_word, word_set):
            if neighbor == end:
                # Found it! Return the complete path
                return path + [neighbor]
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    # No path found
    return None


def print_ladder(ladder: Optional[List[str]]) -> None:
    """
    Pretty-print the word ladder solution.
    Shows each step and highlights what letter changed.
    """
    if ladder is None:
        print("❌ No solution found!")
        return
    
    print(f"✅ Found ladder with {len(ladder)} words:\n")
    
    for i, word in enumerate(ladder):
        if i == 0:
            print(f"  {i+1}. {word.upper()} (start)")
        elif i == len(ladder) - 1:
            print(f"  {i+1}. {word.upper()} (goal!)")
        else:
            # Show which letter changed from previous word
            prev = ladder[i-1]
            diff_pos = next((j for j in range(len(word)) if word[j] != prev[j]), -1)
            highlight = f"{word[:diff_pos]}[{word[diff_pos].upper()}]{word[diff_pos+1:]}"
            print(f"  {i+1}. {highlight}")


def solve_puzzle(start: str, end: str, word_set: Set[str]) -> None:
    """
    Main solver function that ties everything together.
    """
    print(f"\n{'='*50}")
    print(f"Word Ladder: {start.upper()} → {end.upper}")
    print(f"{'='*50}")
    
    ladder = find_word_ladder(start, end, word_set)
    print_ladder(ladder)
    print()


if __name__ == "__main__":
    # Load our word dictionary
    words = load_word_list()
    print(f"📚 Loaded {len(words)} words into dictionary\n")
    
    # Demo 1: Classic puzzle
    solve_puzzle("cold", "warm", words)
    
    # Demo 2: Slightly harder
    solve_puzzle("lost", "fish", words)
    
    # Demo 3: Another fun one
    solve_puzzle("slow", "fast", words)
    
    # Demo 4: Impossible puzzle (no path exists with our word set)
    solve_puzzle("slow", "boys", words)
    
    print("💡 Try modifying the word_set to add more words and solve harder puzzles!")