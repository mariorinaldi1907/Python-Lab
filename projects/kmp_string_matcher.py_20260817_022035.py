"""
Date: 2026-08-17
Built a clean KMP pattern matching algorithm because I got tired of explaining how the failure function works without code to show.
"""

#!/usr/bin/env python3
"""
KMP (Knuth-Morris-Pratt) String Matching Algorithm

I wanted a solid implementation of KMP that I could actually point to when people
ask "why not just use str.find()?" — this shows the elegance of avoiding
re-scanning characters we've already matched.
"""


def build_prefix_table(pattern):
    """
    Build the KMP prefix (failure) table for a given pattern.
    
    This table tells us: for each position in the pattern, what's the length
    of the longest proper prefix that's also a suffix? This lets us avoid
    redundant comparisons when we hit a mismatch.
    
    Args:
        pattern: The string pattern to analyze
        
    Returns:
        A list where prefix_table[i] = length of longest proper prefix of
        pattern[0:i+1] that is also a suffix
    """
    m = len(pattern)
    prefix_table = [0] * m
    
    # length of the previous longest prefix suffix
    length = 0
    i = 1
    
    while i < m:
        if pattern[i] == pattern[length]:
            # We found a matching character, extend the current prefix
            length += 1
            prefix_table[i] = length
            i += 1
        else:
            # Mismatch after some matches
            if length != 0:
                # Try the next smaller prefix (backtrack using the table itself)
                length = prefix_table[length - 1]
            else:
                # No prefix to fall back to
                prefix_table[i] = 0
                i += 1
    
    return prefix_table


def kmp_search(text, pattern):
    """
    Search for all occurrences of pattern in text using KMP algorithm.
    
    The beauty of KMP is that we never go backwards in the text — we use the
    prefix table to figure out where to continue matching in the pattern instead.
    
    Args:
        text: The text to search in
        pattern: The pattern to search for
        
    Returns:
        A list of starting indices where the pattern occurs in the text
    """
    if not pattern or not text:
        return []
    
    n = len(text)
    m = len(pattern)
    
    if m > n:
        return []
    
    # Build the prefix table for the pattern
    prefix_table = build_prefix_table(pattern)
    
    matches = []
    i = 0  # index for text
    j = 0  # index for pattern
    
    while i < n:
        if text[i] == pattern[j]:
            # Characters match, advance both pointers
            i += 1
            j += 1
            
            if j == m:
                # Found a complete match
                matches.append(i - j)
                # Use prefix table to find where to continue searching
                j = prefix_table[j - 1]
        else:
            # Mismatch
            if j != 0:
                # We had some partial match, use the prefix table to skip ahead
                # This is the key optimization — we don't restart from scratch
                j = prefix_table[j - 1]
            else:
                # No partial match, just move forward in text
                i += 1
    
    return matches


def kmp_search_first(text, pattern):
    """
    Find just the first occurrence of pattern in text.
    
    Sometimes you don't need all matches, just the first one. This stops
    as soon as we find it.
    
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
    
    if m > n:
        return -1
    
    prefix_table = build_prefix_table(pattern)
    
    i = 0
    j = 0
    
    while i < n:
        if text[i] == pattern[j]:
            i += 1
            j += 1
            
            if j == m:
                return i - j
        else:
            if j != 0:
                j = prefix_table[j - 1]
            else:
                i += 1
    
    return -1


if __name__ == "__main__":
    # Demo with some real examples to show KMP in action
    
    print("=== KMP String Matching Demo ===\n")
    
    # Example 1: Multiple occurrences
    text1 = "ABABDABACDABABCABAB"
    pattern1 = "ABAB"
    matches1 = kmp_search(text1, pattern1)
    print(f"Text:    '{text1}'")
    print(f"Pattern: '{pattern1}'")
    print(f"Matches found at indices: {matches1}")
    print(f"Prefix table for '{pattern1}': {build_prefix_table(pattern1)}")
    print()
    
    # Example 2: DNA sequence search (realistic use case)
    dna_sequence = "ATCGATCGATCGTAGCTAGCTAGCTAACGATCGATCG"
    dna_pattern = "CGATCG"
    dna_matches = kmp_search(dna_sequence, dna_pattern)
    print(f"DNA Sequence: '{dna_sequence}'")
    print(f"Looking for:  '{dna_pattern}'")
    print(f"Found {len(dna_matches)} occurrences at positions: {dna_matches}")
    print()
    
    # Example 3: Repeating pattern (where KMP really shines)
    text3 = "AAAAAAAAAAAAAAAB"
    pattern3 = "AAAAB"
    first_match = kmp_search_first(text3, pattern3)
    print(f"Text:    '{text3}'")
    print(f"Pattern: '{pattern3}'")
    print(f"First match at index: {first_match}")
    print(f"Prefix table: {build_prefix_table(pattern3)}")
    print()
    
    # Example 4: No match
    text4 = "Hello, World!"
    pattern4 = "Python"
    matches4 = kmp_search(text4, pattern4)
    print(f"Text:    '{text4}'")
    print(f"Pattern: '{pattern4}'")
    print(f"Matches: {matches4 if matches4 else 'None found'}")
    print()
    
    # Show how prefix table helps with a tricky pattern
    tricky = "ACACAGT"
    print(f"Prefix table breakdown for '{tricky}':")
    table = build_prefix_table(tricky)
    for i, val in enumerate(table):
        print(f"  {tricky[:i+1]:10s} -> {val}")