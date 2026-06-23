"""
Date: 2026-06-23
Built a text diff tool using longest common subsequence to compare files and show insertions/deletions — wanted something lightweight for quick file comparisons.
"""

#!/usr/bin/env python3
"""
Text diff tool using Longest Common Subsequence (LCS) algorithm.
Compares two text files or strings and outputs a unified-style diff.
"""


def lcs_length_table(seq1, seq2):
    """
    Build the LCS length table using dynamic programming.
    
    Returns a 2D list where table[i][j] represents the length of the LCS
    of seq1[:i] and seq2[:j]. This is the core of the diff algorithm.
    """
    m, n = len(seq1), len(seq2)
    # Initialize table with zeros
    table = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if seq1[i - 1] == seq2[j - 1]:
                table[i][j] = table[i - 1][j - 1] + 1
            else:
                table[i][j] = max(table[i - 1][j], table[i][j - 1])
    
    return table


def backtrack_diff(seq1, seq2, table):
    """
    Backtrack through the LCS table to generate diff operations.
    
    Returns a list of tuples: ('equal', line), ('delete', line), or ('insert', line).
    This tells us exactly what changed between the two sequences.
    """
    i, j = len(seq1), len(seq2)
    diff = []
    
    while i > 0 or j > 0:
        if i > 0 and j > 0 and seq1[i - 1] == seq2[j - 1]:
            # Lines match - part of the LCS
            diff.append(('equal', seq1[i - 1]))
            i -= 1
            j -= 1
        elif j > 0 and (i == 0 or table[i][j - 1] >= table[i - 1][j]):
            # Line was inserted in seq2
            diff.append(('insert', seq2[j - 1]))
            j -= 1
        else:
            # Line was deleted from seq1
            diff.append(('delete', seq1[i - 1]))
            i -= 1
    
    diff.reverse()
    return diff


def compute_diff(text1, text2):
    """
    Compute the diff between two texts.
    
    Splits texts into lines and uses LCS to find differences.
    Returns a list of diff operations.
    """
    lines1 = text1.splitlines()
    lines2 = text2.splitlines()
    
    table = lcs_length_table(lines1, lines2)
    return backtrack_diff(lines1, lines2, table)


def format_unified_diff(diff, filename1="original", filename2="modified"):
    """
    Format diff operations as a unified diff output.
    
    This mimics the output format of Unix diff -u, with context lines
    and +/- markers for changes. I wanted it to look familiar.
    """
    output = []
    output.append(f"--- {filename1}")
    output.append(f"+++ {filename2}")
    
    # Group changes into hunks for better readability
    i = 0
    while i < len(diff):
        # Skip equal lines until we find a change
        while i < len(diff) and diff[i][0] == 'equal':
            i += 1
        
        if i >= len(diff):
            break
        
        # Found a change - start a hunk
        hunk_start = max(0, i - 3)  # Include 3 lines of context
        hunk = []
        
        # Collect the hunk
        j = hunk_start
        while j < len(diff) and (j < i + 10 or diff[j][0] != 'equal'):
            op, line = diff[j]
            if op == 'equal':
                hunk.append(f" {line}")
            elif op == 'delete':
                hunk.append(f"-{line}")
            elif op == 'insert':
                hunk.append(f"+{line}")
            j += 1
        
        if hunk:
            output.append(f"@@ -{hunk_start + 1},{len(hunk)} +{hunk_start + 1},{len(hunk)} @@")
            output.extend(hunk)
        
        i = j
    
    return '\n'.join(output)


def simple_diff_output(diff):
    """
    Generate a simple, readable diff output.
    
    Just marks deletions with '-' and insertions with '+'.
    Easier to read for small changes.
    """
    output = []
    for op, line in diff:
        if op == 'delete':
            output.append(f"- {line}")
        elif op == 'insert':
            output.append(f"+ {line}")
        elif op == 'equal':
            output.append(f"  {line}")
    return '\n'.join(output)


if __name__ == "__main__":
    # Demo with some sample texts - simulating a code change
    original_text = """def greet(name):
    print("Hello, " + name)
    return True

def main():
    greet("World")
    print("Done")"""

    modified_text = """def greet(name):
    # Added proper formatting
    print(f"Hello, {name}!")
    return True

def main():
    greet("World")
    greet("Python")
    print("All done!")"""

    print("=" * 60)
    print("TEXT DIFF TOOL - LCS Algorithm")
    print("=" * 60)
    print()
    
    print("ORIGINAL:")
    print("-" * 60)
    print(original_text)
    print()
    
    print("MODIFIED:")
    print("-" * 60)
    print(modified_text)
    print()
    
    # Compute and display the diff
    diff = compute_diff(original_text, modified_text)
    
    print("SIMPLE DIFF OUTPUT:")
    print("=" * 60)
    print(simple_diff_output(diff))
    print()
    
    print("UNIFIED DIFF OUTPUT:")
    print("=" * 60)
    print(format_unified_diff(diff, "original.py", "modified.py"))