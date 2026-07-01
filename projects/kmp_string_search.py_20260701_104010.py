"""
Date: 2026-07-01
Built a KMP string search algorithm because I was curious how text editors find patterns so fast without checking every possible substring.
"""

#!/usr/bin/env python3
"""
KMP (Knuth-Morris-Pratt) String Matching Algorithm

I wanted to understand how efficient pattern matching actually works under the hood.
The naive approach of sliding a pattern over text is O(n*m), but KMP does it in O(n+m)
by cleverly reusing information about partial matches.

The key insight: when a mismatch happens, we already know some characters matched,
so we can skip ahead instead of starting over from the beginning.
"""


def build_prefix_table(pattern):
    """
    Build the prefix table (also called failure function or LPS array).
    
    The table tells us: if we fail at position i, how far back should we jump?
    Specifically, what's the length of the longest proper prefix that's also a suffix?
    
    Example: for pattern "ABABC"
    - At index 0: no proper prefix, so 0
    - At index 1: "A" vs "AB", no match, so 0
    - At index 2: "A" matches first char, so 1
    - At index 3: "AB" matches first two chars, so 2
    - At index 4: "AB" doesn't match "ABA" or "ABAB", but "A" works, so 1
    
    Result: [0, 0, 1, 2, 0]
    """
    m = len(pattern)
    prefix = [0] * m
    
    # length of previous longest prefix suffix
    length = 0
    i = 1
    
    while i < m:
        if pattern[i] == pattern[length]:
            # We found a match, extend the current prefix
            length += 1
            prefix[i] = length
            i += 1
        else:
            if length != 0:
                # Try a shorter prefix by jumping back
                # This is the recursive nature of KMP in action
                length = prefix[length - 1]
            else:
                # No prefix works, move on
                prefix[i] = 0
                i += 1
    
    return prefix


def kmp_search(text, pattern):
    """
    Find all occurrences of pattern in text using KMP algorithm.
    
    Returns a list of starting indices where the pattern is found.
    Returns empty list if pattern is not found.
    
    Time complexity: O(n + m) where n = len(text), m = len(pattern)
    Space complexity: O(m) for the prefix table
    """
    if not pattern or not text:
        return []
    
    n = len(text)
    m = len(pattern)
    
    # Build the prefix table once
    prefix = build_prefix_table(pattern)
    matches = []
    
    i = 0  # index for text
    j = 0  # index for pattern
    
    while i < n:
        if text[i] == pattern[j]:
            # Characters match, advance both pointers
            i += 1
            j += 1
        
        if j == m:
            # Found a complete match!
            matches.append(i - j)
            # Use prefix table to continue searching for overlapping matches
            j = prefix[j - 1]
        elif i < n and text[i] != pattern[j]:
            # Mismatch after j matches
            if j != 0:
                # Don't start over; jump back using prefix table
                # This is the magic of KMP
                j = prefix[j - 1]
            else:
                # No progress made, just move to next character in text
                i += 1
    
    return matches


def kmp_search_first(text, pattern):
    """
    Find only the first occurrence of pattern in text.
    
    Returns the index of the first match, or -1 if not found.
    Slightly optimized version when you only need the first match.
    """
    if not pattern or not text:
        return -1
    
    n = len(text)
    m = len(pattern)
    prefix = build_prefix_table(pattern)
    
    i = 0
    j = 0
    
    while i < n:
        if text[i] == pattern[j]:
            i += 1
            j += 1
        
        if j == m:
            return i - j
        elif i < n and text[i] != pattern[j]:
            if j != 0:
                j = prefix[j - 1]
            else:
                i += 1
    
    return -1


def visualize_search(text, pattern):
    """
    Print a visual representation of where the pattern appears in the text.
    Useful for debugging and understanding how the algorithm works.
    """
    matches = kmp_search(text, pattern)
    
    print(f"Text:    {text}")
    print(f"Pattern: {pattern}")
    print(f"\nPrefix table: {build_prefix_table(pattern)}")
    print(f"\nFound {len(matches)} match(es) at position(s): {matches}")
    
    if matches:
        # Create a visual marker showing where matches occur
        marker = [' '] * len(text)
        for pos in matches:
            for i in range(len(pattern)):
                marker[pos + i] = '^'
        print(f"Matches: {''.join(marker)}")


if __name__ == "__main__":
    print("=== KMP String Search Demo ===\n")
    
    # Test 1: Simple search
    print("Test 1: Basic search")
    text1 = "ABABDABACDABABCABAB"
    pattern1 = "ABABC"
    visualize_search(text1, pattern1)
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Overlapping patterns
    print("Test 2: Overlapping patterns")
    text2 = "AAAAAAAAAA"
    pattern2 = "AAA"
    visualize_search(text2, pattern2)
    
    print("\n" + "="*50 + "\n")
    
    # Test 3: Real-world example
    print("Test 3: Finding words in a sentence")
    text3 = "the quick brown fox jumps over the lazy dog"
    pattern3 = "the"
    visualize_search(text3, pattern3)
    
    print("\n" + "="*50 + "\n")
    
    # Test 4: No match
    print("Test 4: Pattern not found")
    text4 = "hello world"
    pattern4 = "xyz"
    visualize_search(text4, pattern4)
    
    print("\n" + "="*50 + "\n")
    
    # Test 5: Complex pattern with repeating prefix
    print("Test 5: Pattern with repeating prefix")
    text5 = "ABCABCABABCABC"
    pattern5 = "ABCABC"
    visualize_search(text5, pattern5)