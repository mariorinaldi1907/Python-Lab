"""
Date: 2026-05-29
Built the Knuth-Morris-Pratt algorithm from scratch to see how partial match tables eliminate redundant comparisons in pattern searching.
"""

"""
KMP (Knuth-Morris-Pratt) String Matching Algorithm

I kept hearing about how KMP is "the fast way" to search for patterns in text,
but never really understood the failure function until I sat down and coded it myself.
This implementation builds the longest proper prefix-suffix (LPS) array and uses it
to skip unnecessary character comparisons.
"""


def compute_lps_array(pattern):
    """
    Compute the Longest Proper Prefix which is also Suffix (LPS) array.
    
    This is the "magic" of KMP — it tells us where to resume searching
    when we hit a mismatch, based on what we've already matched.
    
    Args:
        pattern: The string pattern to preprocess
        
    Returns:
        List of integers where lps[i] is the length of the longest proper prefix
        of pattern[0..i] which is also a suffix of pattern[0..i]
    """
    m = len(pattern)
    lps = [0] * m
    length = 0  # length of the previous longest prefix suffix
    i = 1
    
    # lps[0] is always 0, so we start from index 1
    while i < m:
        if pattern[i] == pattern[length]:
            # We found a matching character, extend the current LPS
            length += 1
            lps[i] = length
            i += 1
        else:
            # Mismatch after length matches
            if length != 0:
                # Don't increment i here — we want to compare pattern[i] with the
                # character at the previous LPS position
                length = lps[length - 1]
            else:
                # No prefix to fall back to
                lps[i] = 0
                i += 1
    
    return lps


def kmp_search(text, pattern):
    """
    Search for all occurrences of pattern in text using KMP algorithm.
    
    The beauty here is that we never backtrack in the text — only in the pattern,
    using the LPS array to know how far we can skip ahead.
    
    Args:
        text: The string to search in
        pattern: The pattern to search for
        
    Returns:
        List of starting indices where pattern occurs in text
    """
    if not pattern or not text:
        return []
    
    n = len(text)
    m = len(pattern)
    
    # Precompute the LPS array for the pattern
    lps = compute_lps_array(pattern)
    
    matches = []
    i = 0  # index for text
    j = 0  # index for pattern
    
    while i < n:
        if text[i] == pattern[j]:
            # Characters match, move both pointers forward
            i += 1
            j += 1
        
        if j == m:
            # We've matched the entire pattern
            matches.append(i - j)
            # Use LPS to find the next possible match position
            j = lps[j - 1]
        elif i < n and text[i] != pattern[j]:
            # Mismatch after j matches
            if j != 0:
                # Don't increment i, but fall back in the pattern using LPS
                j = lps[j - 1]
            else:
                # No matches at all, move to next character in text
                i += 1
    
    return matches


def kmp_search_first(text, pattern):
    """
    Find just the first occurrence of pattern in text.
    
    Sometimes you don't need all matches, just need to know if it exists
    and where it starts.
    
    Args:
        text: The string to search in
        pattern: The pattern to search for
        
    Returns:
        Index of first occurrence, or -1 if not found
    """
    if not pattern or not text:
        return -1
    
    n = len(text)
    m = len(pattern)
    lps = compute_lps_array(pattern)
    
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


if __name__ == "__main__":
    # Demo with a classic example that shows why KMP is better than naive search
    text = "ABABDABACDABABCABAB"
    pattern = "ABABCABAB"
    
    print("KMP String Search Demo")
    print("=" * 50)
    print(f"Text:    {text}")
    print(f"Pattern: {pattern}")
    print()
    
    # Show the LPS array computation
    lps = compute_lps_array(pattern)
    print(f"LPS array for pattern '{pattern}':")
    print(f"Pattern:  {' '.join(pattern)}")
    print(f"LPS:      {' '.join(map(str, lps))}")
    print()
    print("The LPS array tells us how many characters we can skip")
    print("when we hit a mismatch, based on what we already matched.")
    print()
    
    # Find all occurrences
    matches = kmp_search(text, pattern)
    if matches:
        print(f"Found pattern at index/indices: {matches}")
        for idx in matches:
            print(f"\n  Position {idx}:")
            print(f"  {text}")
            print(f"  {' ' * idx}{pattern}")
    else:
        print("Pattern not found in text")
    
    print("\n" + "=" * 50)
    
    # Another example with multiple occurrences
    text2 = "AABAACAADAABAABA"
    pattern2 = "AABA"
    
    print(f"\nSecond example:")
    print(f"Text:    {text2}")
    print(f"Pattern: {pattern2}")
    
    matches2 = kmp_search(text2, pattern2)
    print(f"All occurrences at indices: {matches2}")
    
    # Demo the "first occurrence only" version
    first_idx = kmp_search_first(text2, pattern2)
    print(f"First occurrence at index: {first_idx}")
    
    print("\n" + "=" * 50)
    
    # Edge case: pattern not found
    text3 = "ABCDEFGH"
    pattern3 = "XYZ"
    print(f"\nEdge case (no match):")
    print(f"Text:    {text3}")
    print(f"Pattern: {pattern3}")
    print(f"Result:  {kmp_search(text3, pattern3)}")