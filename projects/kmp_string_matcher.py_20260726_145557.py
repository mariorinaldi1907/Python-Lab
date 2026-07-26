"""
Date: 2026-07-26
Built a KMP pattern matcher because I was curious how Linux `grep` avoids backtracking — includes a demo that shows the prefix table construction step-by-step.
"""

#!/usr/bin/env python3
"""
KMP (Knuth-Morris-Pratt) String Matching Algorithm

I wanted to understand how to avoid redundant comparisons when searching for patterns.
The key insight: if we mismatch after matching k characters, we already know what those
k characters were (they matched the pattern), so we can skip ahead intelligently.
"""


def build_prefix_table(pattern):
    """
    Build the "partial match" table (also called failure function or LPS array).
    
    For each position i in the pattern, lps[i] stores the length of the longest
    proper prefix of pattern[0..i] that is also a suffix of pattern[0..i].
    
    This tells us: "if we mismatch at position i+1, how far back should we jump
    in the pattern instead of restarting from the beginning?"
    
    Args:
        pattern: The string pattern to preprocess
        
    Returns:
        List of integers representing the prefix table
    """
    m = len(pattern)
    lps = [0] * m  # Longest Proper Prefix which is also Suffix
    
    # length of the previous longest prefix suffix
    length = 0
    i = 1
    
    # lps[0] is always 0 (no proper prefix for single character)
    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            # This is tricky: if length != 0, we don't reset to 0
            # Instead, we try the previous lps value because there might
            # be a shorter prefix-suffix match
            if length != 0:
                length = lps[length - 1]
                # Don't increment i here, we retry with the same character
            else:
                lps[i] = 0
                i += 1
    
    return lps


def kmp_search(text, pattern):
    """
    Search for all occurrences of pattern in text using KMP algorithm.
    
    Time complexity: O(n + m) where n = len(text), m = len(pattern)
    Space complexity: O(m) for the prefix table
    
    The beauty of KMP is that we never move backwards in the text — we only
    shift the pattern forward based on the prefix table.
    
    Args:
        text: The text to search in
        pattern: The pattern to search for
        
    Returns:
        List of starting indices where pattern occurs in text
    """
    if not pattern or not text:
        return []
    
    n = len(text)
    m = len(pattern)
    
    # Build the prefix table once, up front
    lps = build_prefix_table(pattern)
    
    matches = []
    i = 0  # index for text
    j = 0  # index for pattern
    
    while i < n:
        if text[i] == pattern[j]:
            i += 1
            j += 1
        
        if j == m:
            # Found a complete match!
            matches.append(i - j)
            # Look for next match: use the prefix table to avoid rechecking
            j = lps[j - 1]
        elif i < n and text[i] != pattern[j]:
            # Mismatch after j matches
            if j != 0:
                # Don't reset j to 0; use the prefix table to skip ahead
                j = lps[j - 1]
            else:
                # No partial match, move to next character in text
                i += 1
    
    return matches


def visualize_prefix_table(pattern):
    """
    Pretty-print the prefix table construction for educational purposes.
    
    Args:
        pattern: The pattern to visualize
    """
    lps = build_prefix_table(pattern)
    
    print(f"\nPrefix table for pattern: '{pattern}'")
    print("=" * 50)
    print("Index:  ", end="")
    for i in range(len(pattern)):
        print(f"{i:3}", end=" ")
    print()
    
    print("Char:   ", end="")
    for char in pattern:
        print(f"{char:>3}", end=" ")
    print()
    
    print("LPS:    ", end="")
    for val in lps:
        print(f"{val:3}", end=" ")
    print("\n")
    
    # Explain what the LPS values mean
    print("Explanation:")
    for i, val in enumerate(lps):
        if val > 0:
            prefix = pattern[:val]
            suffix = pattern[i-val+1:i+1]
            print(f"  Position {i}: longest prefix-suffix = {val} ('{prefix}' = '{suffix}')")


if __name__ == "__main__":
    print("KMP String Matching - Demo")
    print("=" * 60)
    
    # Demo 1: Simple pattern with repetition
    pattern1 = "ABABC"
    visualize_prefix_table(pattern1)
    
    # Demo 2: Pattern with more interesting prefix-suffix matches
    pattern2 = "AABAAA"
    visualize_prefix_table(pattern2)
    
    # Demo 3: Actual search in text
    print("\n" + "=" * 60)
    print("STRING SEARCH EXAMPLES")
    print("=" * 60)
    
    test_cases = [
        ("ABABDABACDABABCABAB", "ABABC"),
        ("AABAACAADAABAABA", "AABA"),
        ("hello world, hello universe, hello everyone", "hello"),
        ("AAAAA", "AAA"),  # Overlapping matches
    ]
    
    for text, pattern in test_cases:
        matches = kmp_search(text, pattern)
        print(f"\nText:    '{text}'")
        print(f"Pattern: '{pattern}'")
        
        if matches:
            print(f"Found {len(matches)} occurrence(s) at position(s): {matches}")
            # Show the matches visually
            for idx in matches:
                marker = " " * idx + "^" * len(pattern)
                print(f"         {marker}")
        else:
            print("No matches found")
    
    # Demo 4: Performance comparison hint
    print("\n" + "=" * 60)
    print("Why KMP matters:")
    print("  - Naive search: O(n*m) worst case")
    print("  - KMP search:   O(n+m) always")
    print("  - Never backtracks in the text (important for streams!)")
    print("=" * 60)