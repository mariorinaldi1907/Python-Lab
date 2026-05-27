"""
Date: 2026-05-27
Built a word-level diff tool using the Myers algorithm because I got tired of character-by-character diffs being noisy — shows additions, deletions, and unchanged sections.
"""

#!/usr/bin/env python3
"""
Word-level diff implementation using Myers' algorithm.
I wanted something lighter than difflib for comparing text at word granularity.
"""


def compute_shortest_edit_script(old_words, new_words):
    """
    Compute the shortest edit script using Myers' diff algorithm.
    
    This finds the minimum number of additions/deletions needed to transform
    old_words into new_words. Returns the edit graph path as coordinates.
    
    Args:
        old_words: List of words from original text
        new_words: List of words from new text
    
    Returns:
        List of (x, y) coordinates representing the path through edit graph
    """
    n, m = len(old_words), len(new_words)
    max_d = n + m
    
    # v[k] stores the furthest reaching x coordinate for diagonal k
    # Using a dict because k can be negative
    v = {1: 0}
    trace = []
    
    for d in range(max_d + 1):
        trace.append(v.copy())
        
        for k in range(-d, d + 1, 2):
            # Decide whether to move down or right in the edit graph
            # Down = delete from old, Right = insert from new
            if k == -d or (k != d and v.get(k - 1, -1) < v.get(k + 1, -1)):
                x = v.get(k + 1, 0)  # Move down (deletion)
            else:
                x = v.get(k - 1, 0) + 1  # Move right (insertion)
            
            y = x - k
            
            # Follow diagonal matches (unchanged words)
            while x < n and y < m and old_words[x] == new_words[y]:
                x += 1
                y += 1
            
            v[k] = x
            
            # Found the target?
            if x >= n and y >= m:
                return backtrack(trace, old_words, new_words, d)
    
    return []


def backtrack(trace, old_words, new_words, d):
    """
    Backtrack through the trace to build the actual diff path.
    
    Args:
        trace: History of v dictionaries from each iteration
        old_words: Original word list
        new_words: New word list
        d: The edit distance found
    
    Returns:
        List of (x, y) coordinates representing moves through edit graph
    """
    n, m = len(old_words), len(new_words)
    x, y = n, m
    path = [(x, y)]
    
    # Walk backwards through the trace
    for depth in range(d, 0, -1):
        v = trace[depth]
        k = x - y
        
        # Figure out if we came from k-1 or k+1
        prev_k = None
        if k == -depth or (k != depth and v.get(k - 1, -1) < v.get(k + 1, -1)):
            prev_k = k + 1
        else:
            prev_k = k - 1
        
        prev_x = trace[depth - 1].get(prev_k, 0)
        prev_y = prev_x - prev_k
        
        # Walk back along any diagonal
        while x > prev_x and y > prev_y:
            x -= 1
            y -= 1
            path.append((x, y))
        
        # Add the insertion or deletion step
        if x > prev_x:
            x -= 1
        else:
            y -= 1
        path.append((x, y))
    
    path.reverse()
    return path


def generate_diff(old_text, new_text):
    """
    Generate a human-readable diff between two texts.
    
    Splits on whitespace to get word-level granularity, which I find
    more useful than character-level for most text comparison tasks.
    
    Args:
        old_text: Original text string
        new_text: Modified text string
    
    Returns:
        List of tuples (operation, word) where operation is '+', '-', or ' '
    """
    old_words = old_text.split()
    new_words = new_text.split()
    
    path = compute_shortest_edit_script(old_words, new_words)
    diff = []
    
    prev_x, prev_y = 0, 0
    for x, y in path[1:]:  # Skip initial (0,0)
        if x == prev_x:
            # Moved vertically (insertion)
            diff.append(('+', new_words[prev_y]))
            prev_y = y
        elif y == prev_y:
            # Moved horizontally (deletion)
            diff.append(('-', old_words[prev_x]))
            prev_x = x
        else:
            # Moved diagonally (match)
            diff.append((' ', old_words[prev_x]))
            prev_x, prev_y = x, y
    
    return diff


def format_diff(diff):
    """
    Pretty-print a diff with color-like markers.
    
    Args:
        diff: List of (operation, word) tuples
    
    Returns:
        Formatted string with visual indicators for changes
    """
    lines = []
    lines.append("=" * 60)
    
    for op, word in diff:
        if op == '+':
            lines.append(f"+ {word}")
        elif op == '-':
            lines.append(f"- {word}")
        else:
            lines.append(f"  {word}")
    
    lines.append("=" * 60)
    return "\n".join(lines)


if __name__ == "__main__":
    # Demo with some sample texts that show different types of changes
    original = "The quick brown fox jumps over the lazy dog"
    modified = "The quick red fox leaps over a lazy cat"
    
    print("Word-Level Diff Tool")
    print("=" * 60)
    print(f"Original: {original}")
    print(f"Modified: {modified}")
    print()
    
    diff = generate_diff(original, modified)
    print(format_diff(diff))
    
    print("\n\nDiff Statistics:")
    additions = sum(1 for op, _ in diff if op == '+')
    deletions = sum(1 for op, _ in diff if op == '-')
    unchanged = sum(1 for op, _ in diff if op == ' ')
    
    print(f"  Additions: {additions}")
    print(f"  Deletions: {deletions}")
    print(f"  Unchanged: {unchanged}")
    print(f"  Total changes: {additions + deletions}")