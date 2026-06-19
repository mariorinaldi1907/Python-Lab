"""
Date: 2026-06-19
Built a patience diff implementation because I wanted to understand why Git prefers it for certain files - turns out anchoring on unique lines really does produce more readable diffs.
"""

#!/usr/bin/env python3
"""
Patience Diff Algorithm Implementation

This is my take on the patience diff algorithm, which I find produces more
intuitive diffs than Myers' algorithm when dealing with code that has lots
of rearranged blocks. The key insight is to first match up unique lines
(lines that appear exactly once in both files), then recursively diff
the regions between those anchors.
"""

from collections import Counter
from typing import List, Tuple, Optional


class PatienceDiff:
    """
    Implements the patience diff algorithm for comparing two sequences.
    
    The algorithm works by:
    1. Finding lines that are unique to both sequences
    2. Finding the longest common subsequence (LCS) of those unique lines
    3. Using those as "anchors" and recursively diffing between them
    """
    
    def __init__(self, seq_a: List[str], seq_b: List[str]):
        """Initialize with two sequences to compare."""
        self.seq_a = seq_a
        self.seq_b = seq_b
    
    def _find_unique_common_lines(self, a_range: Tuple[int, int], 
                                  b_range: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Find lines that appear exactly once in both sequences within given ranges.
        
        Returns a list of (index_in_a, index_in_b) tuples for unique common lines.
        This is the "patience" part - we're patient and only match truly unique lines.
        """
        a_start, a_end = a_range
        b_start, b_end = b_range
        
        # Count occurrences in each range
        a_counts = Counter(self.seq_a[a_start:a_end])
        b_counts = Counter(self.seq_b[b_start:b_end])
        
        # Find lines that appear exactly once in both
        unique_common = {}  # line -> index in a
        for i in range(a_start, a_end):
            line = self.seq_a[i]
            if a_counts[line] == 1 and b_counts[line] == 1:
                unique_common[line] = i
        
        # Now find their positions in b
        result = []
        for j in range(b_start, b_end):
            line = self.seq_b[j]
            if line in unique_common:
                result.append((unique_common[line], j))
        
        return result
    
    def _lcs_indices(self, pairs: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        Find longest increasing subsequence of the unique line pairs.
        
        This ensures we get a consistent ordering of anchors - we can't have
        an anchor at line 10 in A matching line 5 in B, then another anchor
        at line 8 in A matching line 7 in B (that would be backwards).
        """
        if not pairs:
            return []
        
        # Dynamic programming approach to LCS
        # dp[i] = length of longest subsequence ending at pairs[i]
        n = len(pairs)
        dp = [1] * n
        parent = [-1] * n
        
        for i in range(1, n):
            for j in range(i):
                # Can extend if both indices are increasing
                if pairs[j][0] < pairs[i][0] and pairs[j][1] < pairs[i][1]:
                    if dp[j] + 1 > dp[i]:
                        dp[i] = dp[j] + 1
                        parent[i] = j
        
        # Reconstruct the LCS
        max_len = max(dp)
        max_idx = dp.index(max_len)
        
        lcs = []
        idx = max_idx
        while idx != -1:
            lcs.append(pairs[idx])
            idx = parent[idx]
        
        return list(reversed(lcs))
    
    def diff(self) -> List[Tuple[str, str, Optional[int], Optional[int]]]:
        """
        Generate the diff between the two sequences.
        
        Returns a list of (operation, line, line_num_a, line_num_b) tuples where:
        - operation is one of: 'equal', 'delete', 'insert'
        - line is the actual line content
        - line_num_a/b are the line numbers (1-indexed), None if not applicable
        """
        result = []
        self._diff_recursive((0, len(self.seq_a)), (0, len(self.seq_b)), result)
        return result
    
    def _diff_recursive(self, a_range: Tuple[int, int], b_range: Tuple[int, int],
                       result: List):
        """
        Recursively diff regions by finding unique anchors and diffing between them.
        """
        a_start, a_end = a_range
        b_start, b_end = b_range
        
        # Base cases
        if a_start >= a_end and b_start >= b_end:
            return
        if a_start >= a_end:
            # Only insertions left
            for i in range(b_start, b_end):
                result.append(('insert', self.seq_b[i], None, i + 1))
            return
        if b_start >= b_end:
            # Only deletions left
            for i in range(a_start, a_end):
                result.append(('delete', self.seq_a[i], i + 1, None))
            return
        
        # Find unique common lines and their LCS
        unique_pairs = self._find_unique_common_lines(a_range, b_range)
        anchors = self._lcs_indices(unique_pairs)
        
        if not anchors:
            # No unique common lines - fall back to simple comparison
            # Just mark everything as delete then insert (not optimal but works)
            for i in range(a_start, a_end):
                result.append(('delete', self.seq_a[i], i + 1, None))
            for i in range(b_start, b_end):
                result.append(('insert', self.seq_b[i], None, i + 1))
            return
        
        # Process regions between anchors
        prev_a, prev_b = a_start, b_start
        
        for anchor_a, anchor_b in anchors:
            # Recursively diff the region before this anchor
            self._diff_recursive((prev_a, anchor_a), (prev_b, anchor_b), result)
            
            # The anchor itself is equal
            result.append(('equal', self.seq_a[anchor_a], anchor_a + 1, anchor_b + 1))
            
            prev_a, prev_b = anchor_a + 1, anchor_b + 1
        
        # Don't forget the region after the last anchor
        self._diff_recursive((prev_a, a_end), (prev_b, b_end), result)


def format_diff(diff_result: List[Tuple]) -> str:
    """Format diff result in a readable way, similar to unified diff format."""
    output = []
    for op, line, line_a, line_b in diff_result:
        if op == 'equal':
            output.append(f"  {line}")
        elif op == 'delete':
            output.append(f"- {line}")
        elif op == 'insert':
            output.append(f"+ {line}")
    return '\n'.join(output)


if __name__ == "__main__":
    # Demo: comparing two versions of a simple function
    original = [
        "def calculate_total(items):",
        "    total = 0",
        "    for item in items:",
        "        total += item.price",
        "    return total",
    ]
    
    modified = [
        "def calculate_total(items):",
        "    total = 0",
        "    tax_rate = 0.08",
        "    for item in items:",
        "        total += item.price",
        "    total *= (1 + tax_rate)",
        "    return total",
    ]
    
    print("=== Patience Diff Demo ===\n")
    print("Original:")
    for i, line in enumerate(original, 1):
        print(f"{i}: {line}")
    
    print("\nModified:")
    for i, line in enumerate(modified, 1):
        print(f"{i}: {line}")
    
    differ = PatienceDiff(original, modified)
    diff_result = differ.diff()
    
    print("\n--- Diff Output ---")
    print(format_diff(diff_result))
    
    print("\n--- Raw Diff Operations ---")
    for op, line, num_a, num_b in diff_result:
        print(f"{op:8} | A:{num_a or '-':3} B:{num_b or '-':3} | {line}")