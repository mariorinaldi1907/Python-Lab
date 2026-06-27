"""
Date: 2026-06-27
Built a line-based diff tool using the Myers algorithm because I wanted to understand how git diff actually works under the hood.
"""

#!/usr/bin/env python3
"""
A line-by-line diff tool implementing the Myers diff algorithm.

I wrote this to better understand how version control systems compute diffs.
The Myers algorithm finds the shortest edit script (SES) to transform one
sequence into another using dynamic programming on the edit graph.
"""

def myers_diff(old_lines, new_lines):
    """
    Compute the shortest edit script using Myers' diff algorithm.
    
    This finds the minimal set of insertions and deletions needed to
    transform old_lines into new_lines. I'm using the greedy algorithm
    variant which is O((M+N)D) where D is the size of the diff.
    
    Returns a list of tuples: ('equal', line), ('delete', line), or ('insert', line)
    """
    n = len(old_lines)
    m = len(new_lines)
    max_d = n + m
    
    # v[k] represents the furthest reaching x coordinate on diagonal k
    # Using a dict instead of array for simpler negative indexing
    v = {1: 0}
    
    # trace stores v for each d value so we can backtrack later
    trace = []
    
    for d in range(max_d + 1):
        trace.append(v.copy())
        
        for k in range(-d, d + 1, 2):
            # Move down or right based on which gives us further reach
            if k == -d or (k != d and v.get(k - 1, -1) < v.get(k + 1, -1)):
                x = v.get(k + 1, 0)  # Move down (insertion)
            else:
                x = v.get(k - 1, 0) + 1  # Move right (deletion)
            
            y = x - k
            
            # Follow diagonal matches as far as possible
            while x < n and y < m and old_lines[x] == new_lines[y]:
                x += 1
                y += 1
            
            v[k] = x
            
            # Found the end point
            if x >= n and y >= m:
                return _backtrack(trace, old_lines, new_lines, d)
    
    # Shouldn't reach here but handle it gracefully
    return []


def _backtrack(trace, old_lines, new_lines, d):
    """
    Backtrack through the trace to build the actual diff output.
    
    This reconstructs the path through the edit graph by working backwards
    from the solution. I found this part trickier than the forward pass.
    """
    x = len(old_lines)
    y = len(new_lines)
    
    # Build the diff in reverse, then flip it
    diff = []
    
    for depth in range(d, -1, -1):
        v = trace[depth]
        k = x - y
        
        # Determine if we came from a horizontal or vertical edge
        if k == -depth or (k != depth and v.get(k - 1, -1) < v.get(k + 1, -1)):
            prev_k = k + 1
        else:
            prev_k = k - 1
        
        prev_x = v.get(prev_k, 0)
        prev_y = prev_x - prev_k
        
        # Follow the diagonal back (these are matches)
        while x > prev_x and y > prev_y:
            x -= 1
            y -= 1
            diff.append(('equal', old_lines[x]))
        
        # Record the insertion or deletion
        if depth > 0:
            if x == prev_x:
                # Vertical edge = insertion from new
                y -= 1
                diff.append(('insert', new_lines[y]))
            else:
                # Horizontal edge = deletion from old
                x -= 1
                diff.append(('delete', old_lines[x]))
    
    diff.reverse()
    return diff


def format_unified_diff(diff, old_name="old", new_name="new"):
    """
    Format the diff output in a unified diff style.
    
    I wanted the output to look similar to git diff so it's familiar.
    This groups consecutive changes into hunks with context lines.
    """
    output = []
    output.append(f"--- {old_name}")
    output.append(f"+++ {new_name}")
    
    i = 0
    while i < len(diff):
        # Skip equal lines until we find a change
        while i < len(diff) and diff[i][0] == 'equal':
            i += 1
        
        if i >= len(diff):
            break
        
        # Found a change - back up to include context
        hunk_start = max(0, i - 3)
        hunk_old_start = sum(1 for j in range(hunk_start) 
                            if diff[j][0] in ('equal', 'delete'))
        
        # Collect the hunk
        hunk = []
        old_count = 0
        new_count = 0
        
        j = hunk_start
        while j < len(diff):
            op, line = diff[j]
            
            if op == 'equal':
                hunk.append(f" {line}")
                old_count += 1
                new_count += 1
                # Stop if we've gone 3+ equal lines past the last change
                if j > i and sum(1 for k in range(i, j + 1) 
                               if diff[k][0] == 'equal') >= 3:
                    break
            elif op == 'delete':
                hunk.append(f"-{line}")
                old_count += 1
                i = j  # Update last change position
            elif op == 'insert':
                hunk.append(f"+{line}")
                new_count += 1
                i = j  # Update last change position
            
            j += 1
        
        # Output the hunk header and content
        output.append(f"@@ -{hunk_old_start + 1},{old_count} "
                     f"+{hunk_old_start + 1},{new_count} @@")
        output.extend(hunk)
        
        i = j
    
    return '\n'.join(output)


if __name__ == "__main__":
    # Demo with some sample text showing how the diff works
    old_text = """The quick brown fox
jumps over the lazy dog.
Hello world!
This is a test.
Python is great."""
    
    new_text = """The quick brown fox
leaps over the lazy dog.
Hello world!
This is a demo.
Python is awesome.
Added a new line here."""
    
    old_lines = old_text.strip().split('\n')
    new_lines = new_text.strip().split('\n')
    
    print("Computing diff between two text snippets...\n")
    
    diff = myers_diff(old_lines, new_lines)
    unified = format_unified_diff(diff)
    
    print(unified)
    print("\n" + "="*50)
    print("Raw diff operations:")
    for op, line in diff:
        symbol = ' ' if op == 'equal' else ('-' if op == 'delete' else '+')
        print(f"{symbol} {line}")