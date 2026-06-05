"""
Date: 2026-06-05
Built a word ladder puzzle solver that finds the shortest path between two words by changing one letter at a time — uses BFS and a built-in dictionary to keep it lightweight.
"""

#!/usr/bin/env python3
"""
Word Ladder Solver - finds the shortest transformation path between two words.

A word ladder puzzle asks you to transform one word into another by changing
exactly one letter at a time, where each intermediate step must be a valid word.
For example: CAT -> COT -> DOT -> DOG

I'm using BFS here because we want the *shortest* path, and BFS guarantees
we'll find it before exploring longer paths.
"""

import string
from collections import deque


def load_dictionary(word_length):
    """
    Load a basic dictionary of common English words.
    
    In a real project I'd read from /usr/share/dict/words or a file,
    but for portability I'm hardcoding a small dictionary here.
    Only returns words matching the target length.
    
    Args:
        word_length: Filter dictionary to only words of this length
        
    Returns:
        set: Valid words of the specified length
    """
    # Small dictionary for demo purposes - in practice you'd load a real word list
    sample_words = {
        "cat", "cot", "dot", "dog", "cog", "log", "lot", "hat", "hot", "hit",
        "bit", "bat", "rat", "mat", "sat", "fat", "tat", "pat", "vat", "oat",
        "bot", "not", "got", "pot", "rot", "tot", "jot", "cod", "hog", "fog",
        "bog", "jog", "dig", "big", "pig", "wig", "fig", "jig", "rig", "gig",
        "bag", "tag", "rag", "lag", "sag", "wag", "nag", "gag", "hag", "jag",
        "bet", "get", "let", "met", "net", "pet", "set", "vet", "wet", "yet",
        "gate", "late", "mate", "rate", "fate", "hate", "date", "gale", "tale",
        "male", "pale", "sale", "bale", "vale", "dale", "hale", "game", "came",
        "name", "same", "tame", "dame", "fame", "lame", "gage", "cage", "page",
        "rage", "sage", "wage", "made", "fade", "jade", "mare", "care", "dare",
        "fare", "hare", "rare", "ware", "make", "take", "wake", "bake", "cake",
        "fake", "lake", "rake", "sake", "mage", "gave", "save", "wave", "cave",
        "have", "pave", "rave"
    }
    
    return {word.lower() for word in sample_words if len(word) == word_length}


def get_neighbors(word, dictionary):
    """
    Find all valid words that differ by exactly one letter.
    
    This is the core of the graph construction - each word is a node,
    and edges connect words that differ by one letter.
    
    Args:
        word: The current word
        dictionary: Set of valid words to check against
        
    Returns:
        list: All valid one-letter transformations of word
    """
    neighbors = []
    
    # Try replacing each position with each letter
    for i in range(len(word)):
        for letter in string.ascii_lowercase:
            if letter == word[i]:
                continue  # Skip if it's the same letter
            
            # Build the candidate word
            candidate = word[:i] + letter + word[i+1:]
            
            if candidate in dictionary:
                neighbors.append(candidate)
    
    return neighbors


def solve_word_ladder(start, end, dictionary=None):
    """
    Find the shortest word ladder from start to end using BFS.
    
    BFS is perfect here because it explores level by level, guaranteeing
    we find the shortest path first. Each level represents one more word
    transformation in the chain.
    
    Args:
        start: Starting word
        end: Target word
        dictionary: Optional set of valid words (will generate if not provided)
        
    Returns:
        list: The shortest path from start to end, or None if impossible
    """
    start = start.lower()
    end = end.lower()
    
    if len(start) != len(end):
        return None  # Can't transform words of different lengths
    
    if dictionary is None:
        dictionary = load_dictionary(len(start))
    
    if start not in dictionary or end not in dictionary:
        return None  # One or both words aren't in our dictionary
    
    # BFS setup: queue stores (word, path_to_word)
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        current_word, path = queue.popleft()
        
        # Found it!
        if current_word == end:
            return path
        
        # Explore all one-letter transformations
        for neighbor in get_neighbors(current_word, dictionary):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    # No path exists
    return None


def print_ladder(path):
    """
    Pretty print a word ladder solution.
    
    Args:
        path: List of words forming the ladder
    """
    if path is None:
        print("No solution found!")
        return
    
    print(f"Found ladder with {len(path)} words:")
    for i, word in enumerate(path):
        print(f"  {i + 1}. {word.upper()}")
    print(f"Total steps: {len(path) - 1}")


if __name__ == "__main__":
    print("=== Word Ladder Solver ===\n")
    
    # Test case 1: Classic example
    print("Challenge 1: CAT -> DOG")
    solution = solve_word_ladder("cat", "dog")
    print_ladder(solution)
    
    print("\n" + "-" * 40 + "\n")
    
    # Test case 2: Longer words
    print("Challenge 2: GATE -> MATE")
    solution = solve_word_ladder("gate", "mate")
    print_ladder(solution)
    
    print("\n" + "-" * 40 + "\n")
    
    # Test case 3: Impossible case
    print("Challenge 3: CAT -> PIG (checking impossible case)")
    solution = solve_word_ladder("cat", "pig")
    print_ladder(solution)
    
    print("\n" + "-" * 40 + "\n")
    
    # Test case 4: Same word
    print("Challenge 4: MAKE -> TAKE")
    solution = solve_word_ladder("make", "take")
    print_ladder(solution)