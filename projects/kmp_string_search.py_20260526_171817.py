"""
Date: 2026-05-26
Built the Knuth-Morris-Pratt algorithm for fast substring searching because I was curious how text editors do it efficiently.
"""

#!/usr/bin/env python3
"""
KMP (Knuth-Morris-Pratt) string searching algorithm.

I wanted to understand how efficient pattern matching actually works under the hood.
The naive approach is O(n*m) but KMP brings it down to O(n+m) by avoiding
redundant comparisons when a mismatch happens.

The key insight: when we find a mismatch, we've already matched part of the pattern,
so we can use that info to skip ahead instead of starting over from scratch.
"""


def compute_lps_array(pattern):
    """
    Build the Longest Proper Prefix which is also Suffix (LPS) array.
    
    This is the "magic" of KMP. For each position in the pattern, we store
    the length of the longest proper prefix that's also a suffix.
    
    Example: pattern = "ABABC"
    lps = [0, 0, 1, 2, 0]
    
    At index 3 (second 'B'), we've seen "ABAB", and "AB" appears at both
    the start and end, so lps[3] = 2.
    
    Args:
        pattern: The string pattern to preprocess
        
    Returns:
        List of integers representing the LPS array
    """
    m = len(pattern)
    lps = [0] * m
    length = 0  # length of the previous longest prefix suffix
    i = 1
    
    # lps[0] is always 0, so we start from 1
    while i < m:
        if pattern[i] == pattern[length]:
            # We found a match, extend the current prefix-suffix
            length += 1
            lps[i] = length
            i += 1
        else:
            # Mismatch after length matches
            if length != 0:
                # Try the previous longest prefix suffix
                # This is the clever part - we don't start from 0
                length = lps[length - 1]
            else:
                # No match at all, move on
                lps[i] = 0
                i += 1
    
    return lps


def kmp_search(text, pattern):
    """
    Search for all occurrences of pattern in text using KMP algorithm.
    
    The algorithm maintains two pointers:
    - i for the text (always moves forward)
    - j for the pattern (can jump back using LPS array)
    
    When we hit a mismatch, instead of resetting j to 0 and moving i back
    (like naive search), we use the LPS array to figure out where j should
    jump to, and i keeps moving forward.
    
    Args:
        text: The text to search in
        pattern: The pattern to search for
        
    Returns:
        List of starting indices where pattern is found in text
    """
    n = len(text)
    m = len(pattern)
    
    if m == 0:
        return []
    
    # Preprocess the pattern to build LPS array
    lps = compute_lps_array(pattern)
    
    matches = []
    i = 0  # index for text
    j = 0  # index for pattern
    
    while i < n:
        if pattern[j] == text[i]:
            # Characters match, advance both pointers
            i += 1
            j += 1
        
        if j == m:
            # Found a complete match!
            matches.append(i - j)
            # Use LPS to find the next possible match position
            j = lps[j - 1]
        elif i < n and pattern[j] != text[i]:
            # Mismatch after j matches
            if j != 0:
                # Don't start over, use the LPS array to skip ahead
                j = lps[j - 1]
            else:
                # No matches yet, just move to next character in text
                i += 1
    
    return matches


def kmp_search_first(text, pattern):
    """
    Find just the first occurrence of pattern in text.
    
    Sometimes you only need to know if/where the pattern appears once,
    not all occurrences. This is a slightly optimized version that
    returns immediately after finding the first match.
    
    Args:
        text: The text to search in
        pattern: The pattern to search for
        
    Returns:
        Index of first occurrence, or -1 if not found
    """
    n = len(text)
    m = len(pattern)
    
    if m == 0:
        return -1
    
    lps = compute_lps_array(pattern)
    
    i = 0
    j = 0
    
    while i < n:
        if pattern[j] == text[i]:
            i += 1
            j += 1
        
        if j == m:
            return i - j
        elif i < n and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    
    return -1


if __name__ == "__main__":
    # Demo 1: Basic search with multiple matches
    print("=== Demo 1: Finding all occurrences ===")
    text1 = "ABABDABACDABABCABAB"
    pattern1 = "ABABC"
    
    matches = kmp_search(text1, pattern1)
    print(f"Text: {text1}")
    print(f"Pattern: {pattern1}")
    print(f"Found at indices: {matches}")
    
    # Visualize the matches
    for idx in matches:
        print(" " * idx + "^" * len(pattern1))
    
    # Demo 2: Pattern with repetitive structure (where KMP really shines)
    print("\n=== Demo 2: Repetitive pattern ===")
    text2 = "AAAAAAAAAAAAAAAB"
    pattern2 = "AAAAB"
    
    lps = compute_lps_array(pattern2)
    print(f"Pattern: {pattern2}")
    print(f"LPS array: {lps}")
    print(f"Text: {text2}")
    
    matches = kmp_search(text2, pattern2)
    print(f"Found at indices: {matches}")
    
    # Demo 3: Real-world-ish example
    print("\n=== Demo 3: Searching in a sentence ===")
    text3 = "The quick brown fox jumps over the lazy dog. The fox is quick."
    pattern3 = "fox"
    
    matches = kmp_search(text3, pattern3)
    print(f"Searching for '{pattern3}' in:")
    print(f"'{text3}'")
    print(f"\nFound {len(matches)} occurrence(s) at index/indices: {matches}")
    
    # Demo 4: First occurrence only
    print("\n=== Demo 4: Finding first occurrence ===")
    text4 = "GCATCGCAGAGAGTATACAGTACG"
    pattern4 = "GAGAG"
    
    first = kmp_search_first(text4, pattern4)
    print(f"Text: {text4}")
    print(f"Pattern: {pattern4}")
    if first != -1:
        print(f"First occurrence at index: {first}")
        print(" " * first + "^" * len(pattern4))
    else:
        print("Pattern not found")
    
    # Demo 5: Edge case - pattern not found
    print("\n=== Demo 5: Pattern not found ===")
    text5 = "ABCDEFGH"
    pattern5 = "XYZ"
    
    matches = kmp_search(text5, pattern5)
    print(f"Text: {text5}")
    print(f"Pattern: {pattern5}")
    print(f"Found at indices: {matches if matches else 'Not found'}")