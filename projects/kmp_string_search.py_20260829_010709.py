"""
Date: 2026-08-29
Built a clean KMP algorithm implementation with visual debugging to finally understand why it's O(n+m) instead of the naive O(n*m).
"""

"""
Knuth-Morris-Pratt (KMP) string search algorithm.

I kept having to explain this algorithm to people (and honestly, to myself)
so I sat down and wrote a clear implementation with the prefix table logic
spelled out. The key insight is pre-processing the pattern to avoid
re-scanning characters we already know match.
"""


def build_prefix_table(pattern):
    """
    Build the "partial match" table (also called failure function).
    
    This tells us: if we mismatch at position j, how far back should we
    reset in the pattern instead of starting over from scratch?
    
    The value at prefix[j] is the length of the longest proper prefix
    of pattern[0..j] that is also a suffix.
    
    Args:
        pattern: The string pattern to preprocess
        
    Returns:
        List of integers representing the prefix table
    """
    m = len(pattern)
    prefix = [0] * m
    
    # length of the previous longest prefix suffix
    length = 0
    i = 1
    
    while i < m:
        if pattern[i] == pattern[length]:
            # characters match, extend the current prefix
            length += 1
            prefix[i] = length
            i += 1
        else:
            # mismatch after some matches
            if length != 0:
                # try with the previous longest prefix suffix
                # this is the "jump" trick that makes KMP fast
                length = prefix[length - 1]
            else:
                # no match at all, move on
                prefix[i] = 0
                i += 1
    
    return prefix


def kmp_search(text, pattern, debug=False):
    """
    Search for all occurrences of pattern in text using KMP algorithm.
    
    Time complexity: O(n + m) where n = len(text), m = len(pattern)
    Space complexity: O(m) for the prefix table
    
    Args:
        text: The text to search in
        pattern: The pattern to search for
        debug: If True, print step-by-step matching process
        
    Returns:
        List of starting indices where pattern is found in text
    """
    if not pattern or not text:
        return []
    
    n = len(text)
    m = len(pattern)
    
    # build the prefix table once
    prefix = build_prefix_table(pattern)
    
    if debug:
        print(f"Pattern: {pattern}")
        print(f"Prefix table: {prefix}")
        print(f"Searching in: {text}\n")
    
    matches = []
    i = 0  # index for text
    j = 0  # index for pattern
    
    while i < n:
        if debug:
            print(f"Comparing text[{i}]='{text[i]}' with pattern[{j}]='{pattern[j]}'")
        
        if pattern[j] == text[i]:
            # characters match, advance both pointers
            i += 1
            j += 1
            
        if j == m:
            # found a complete match!
            match_start = i - j
            matches.append(match_start)
            if debug:
                print(f"*** MATCH FOUND at index {match_start} ***\n")
            # use prefix table to continue searching
            j = prefix[j - 1]
            
        elif i < n and pattern[j] != text[i]:
            # mismatch after some matches
            if j != 0:
                # don't restart from scratch - use the prefix table
                # this is where we save time compared to naive search
                if debug:
                    print(f"Mismatch! Jumping back using prefix[{j-1}]={prefix[j-1]}\n")
                j = prefix[j - 1]
            else:
                # no matches at all, just move to next character in text
                if debug:
                    print(f"No match, moving forward\n")
                i += 1
    
    return matches


def naive_search(text, pattern):
    """
    Naive string search for comparison/validation.
    
    Time complexity: O(n * m) in worst case
    Just slides the pattern across the text checking every position.
    """
    matches = []
    n = len(text)
    m = len(pattern)
    
    for i in range(n - m + 1):
        if text[i:i+m] == pattern:
            matches.append(i)
    
    return matches


if __name__ == "__main__":
    # Demo 1: Basic search
    print("=" * 60)
    print("DEMO 1: Basic Pattern Search")
    print("=" * 60)
    text = "ababcabcabababd"
    pattern = "ababd"
    
    matches = kmp_search(text, pattern)
    print(f"Text: {text}")
    print(f"Pattern: {pattern}")
    print(f"Matches found at indices: {matches}")
    
    # visual representation
    for idx in matches:
        print(f"  {' ' * idx}{pattern}")
    print()
    
    # Demo 2: Multiple matches with debug output
    print("=" * 60)
    print("DEMO 2: Multiple Matches (with debug output)")
    print("=" * 60)
    text2 = "AABAACAADAABAABA"
    pattern2 = "AABA"
    
    matches2 = kmp_search(text2, pattern2, debug=True)
    print(f"\nFinal result: Found {len(matches2)} matches at positions {matches2}\n")
    
    # Demo 3: Edge cases
    print("=" * 60)
    print("DEMO 3: Edge Cases")
    print("=" * 60)
    
    test_cases = [
        ("hello world", "world", "pattern at end"),
        ("abcdefgh", "abc", "pattern at start"),
        ("mississippi", "issi", "overlapping patterns"),
        ("aaaaaa", "aaa", "repeated characters"),
        ("short", "this is longer than text", "pattern longer than text"),
    ]
    
    for text, pattern, description in test_cases:
        kmp_result = kmp_search(text, pattern)
        naive_result = naive_search(text, pattern)
        
        # verify KMP matches naive implementation
        assert kmp_result == naive_result, f"Mismatch on {description}!"
        
        print(f"{description}:")
        print(f"  Text='{text}', Pattern='{pattern}'")
        print(f"  Matches: {kmp_result}")
    
    print("\n✓ All tests passed! KMP and naive search agree.")