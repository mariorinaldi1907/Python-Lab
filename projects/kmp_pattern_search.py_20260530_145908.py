"""
Date: 2026-05-30
Built the Knuth-Morris-Pratt algorithm for fast substring matching — wanted to actually understand how the prefix table works instead of just reading about it.
"""

#!/usr/bin/env python3
"""
KMP (Knuth-Morris-Pratt) pattern matching algorithm.

I always thought KMP was some black magic, but after implementing it myself
I finally get why the prefix table is so clever. Basically, we preprocess
the pattern to avoid backtracking in the main text when there's a mismatch.
"""


def build_lps_table(pattern):
    """
    Build the Longest Proper Prefix which is also Suffix (LPS) table.
    
    This is the heart of KMP. For each position in the pattern, we store
    the length of the longest prefix that's also a suffix up to that point.
    
    Example: pattern = "ABABC"
    LPS table = [0, 0, 1, 2, 0]
    Because at index 3, "ABAB" has "AB" as both prefix and suffix (length 2).
    
    Args:
        pattern: The search pattern string
        
    Returns:
        List of integers representing the LPS values for each position
    """
    m = len(pattern)
    lps = [0] * m
    
    # length of previous longest prefix suffix
    length = 0
    i = 1
    
    while i < m:
        if pattern[i] == pattern[length]:
            # We found a match, extend the current LPS
            length += 1
            lps[i] = length
            i += 1
        else:
            # Mismatch after length matches
            if length != 0:
                # Try the previous smaller LPS value
                # This is the key insight: we don't start from 0
                length = lps[length - 1]
            else:
                # No prefix to fall back to
                lps[i] = 0
                i += 1
    
    return lps


def kmp_search(text, pattern):
    """
    Search for all occurrences of pattern in text using KMP algorithm.
    
    Time complexity: O(n + m) where n = len(text), m = len(pattern)
    Space complexity: O(m) for the LPS table
    
    The beauty of KMP is that we never backtrack in the text. We only
    use the LPS table to know where to continue in the pattern.
    
    Args:
        text: The text to search in
        pattern: The pattern to search for
        
    Returns:
        List of starting indices where pattern is found in text
    """
    if not pattern or not text:
        return []
    
    n = len(text)
    m = len(pattern)
    
    # Preprocess the pattern
    lps = build_lps_table(pattern)
    
    matches = []
    i = 0  # index for text
    j = 0  # index for pattern
    
    while i < n:
        if text[i] == pattern[j]:
            # Characters match, advance both pointers
            i += 1
            j += 1
        
        if j == m:
            # We found a complete match
            matches.append(i - j)
            # Use LPS to find next potential match
            j = lps[j - 1]
        elif i < n and text[i] != pattern[j]:
            # Mismatch after j matches
            if j != 0:
                # Don't match lps[0..lps[j-1]] characters, they will match anyway
                j = lps[j - 1]
            else:
                # No prefix to use, just move to next character in text
                i += 1
    
    return matches


def kmp_search_first(text, pattern):
    """
    Find just the first occurrence of pattern in text.
    
    Sometimes you only need to know if the pattern exists and where,
    not all occurrences. This short-circuits as soon as we find one.
    
    Args:
        text: The text to search in
        pattern: The pattern to search for
        
    Returns:
        Index of first occurrence, or -1 if not found
    """
    if not pattern or not text:
        return -1
    
    n = len(text)
    m = len(pattern)
    lps = build_lps_table(pattern)
    
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
                j = lps[j - 1]
            else:
                i += 1
    
    return -1


def visualize_lps(pattern):
    """
    Print the LPS table in a readable format.
    
    This helped me debug and understand what's happening. Useful for
    seeing how the preprocessing works.
    
    Args:
        pattern: The pattern to visualize
    """
    lps = build_lps_table(pattern)
    print(f"Pattern: {pattern}")
    print(f"Index:   {' '.join(str(i) for i in range(len(pattern)))}")
    print(f"Char:    {' '.join(pattern)}")
    print(f"LPS:     {' '.join(str(x) for x in lps)}")


if __name__ == "__main__":
    # Test case 1: Basic search with multiple occurrences
    print("=" * 60)
    print("Test 1: Finding 'ABA' in a longer text")
    print("=" * 60)
    text1 = "ABABDABACDABABCABAB"
    pattern1 = "ABA"
    
    matches = kmp_search(text1, pattern1)
    print(f"Text:    {text1}")
    print(f"Pattern: {pattern1}")
    print(f"Matches found at indices: {matches}")
    
    # Visualize where matches occur
    for idx in matches:
        spaces = " " * idx
        print(f"         {spaces}{pattern1}")
    
    print("\n" + "=" * 60)
    print("Test 2: LPS table visualization")
    print("=" * 60)
    visualize_lps("ABABC")
    print()
    visualize_lps("AAAA")
    print()
    visualize_lps("ABCDABC")
    
    print("\n" + "=" * 60)
    print("Test 3: Finding first occurrence only")
    print("=" * 60)
    text3 = "The quick brown fox jumps over the lazy dog"
    pattern3 = "fox"
    first_match = kmp_search_first(text3, pattern3)
    print(f"Text:    {text3}")
    print(f"Pattern: {pattern3}")
    print(f"First occurrence at index: {first_match}")
    if first_match != -1:
        print(f"Match:   {text3[first_match:first_match + len(pattern3)]}")
    
    print("\n" + "=" * 60)
    print("Test 4: Pattern not found")
    print("=" * 60)
    text4 = "AABAACAADAABAABA"
    pattern4 = "AABAAX"
    matches4 = kmp_search(text4, pattern4)
    print(f"Text:    {text4}")
    print(f"Pattern: {pattern4}")
    print(f"Matches found: {matches4 if matches4 else 'None'}")
    
    print("\n" + "=" * 60)
    print("Test 5: DNA sequence search (practical use case)")
    print("=" * 60)
    dna = "ATCGATCGATCGTAGCTAGCTAGCTAGCTAGCT"
    motif = "TAGC"
    dna_matches = kmp_search(dna, motif)
    print(f"DNA:     {dna}")
    print(f"Motif:   {motif}")
    print(f"Motif appears {len(dna_matches)} times at positions: {dna_matches}")
```