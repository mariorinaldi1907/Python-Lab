"""
Date: 2026-07-11
Made a CLI tool that prints directory trees with file sizes and lets me exclude patterns like node_modules or .git — uses only stdlib and handles symlinks gracefully.
"""

#!/usr/bin/env python3
"""
Directory tree printer with size calculation and pattern filtering.
Prints a visual tree structure of directories with optional size info.
"""

import argparse
import os
from pathlib import Path
from typing import List, Set


def should_ignore(path: Path, ignore_patterns: Set[str]) -> bool:
    """
    Check if a path matches any of the ignore patterns.
    
    I'm doing simple substring matching here instead of regex because
    for my use case (ignoring .git, __pycache__, etc.) it's sufficient
    and way more readable.
    """
    path_str = str(path)
    return any(pattern in path_str for pattern in ignore_patterns)


def format_size(size_bytes: int) -> str:
    """
    Convert bytes to human-readable format.
    
    Returns strings like '1.5K', '23.4M', '1.2G' etc.
    I prefer this over raw byte counts when scanning large dirs.
    """
    for unit in ['B', 'K', 'M', 'G', 'T']:
        if size_bytes < 1024.0:
            return f"{size_bytes:3.1f}{unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f}P"


def get_dir_size(path: Path, ignore_patterns: Set[str]) -> int:
    """
    Recursively calculate total size of a directory.
    
    Skips symlinks to avoid circular references and potential issues.
    Also respects ignore patterns when calculating size.
    """
    total = 0
    try:
        for entry in path.iterdir():
            if entry.is_symlink():
                continue
            if should_ignore(entry, ignore_patterns):
                continue
            
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry, ignore_patterns)
    except PermissionError:
        # Sometimes we hit dirs we can't read, just skip them
        pass
    return total


def print_tree(
    path: Path,
    prefix: str = "",
    is_last: bool = True,
    ignore_patterns: Set[str] = None,
    show_sizes: bool = False,
    max_depth: int = None,
    current_depth: int = 0
):
    """
    Recursively print directory tree structure.
    
    Uses box-drawing characters (├──, └──, │) to make it look nice.
    The prefix accumulates as we go deeper to maintain proper indentation.
    """
    if ignore_patterns is None:
        ignore_patterns = set()
    
    if max_depth is not None and current_depth > max_depth:
        return
    
    # Skip if this path matches ignore patterns
    if should_ignore(path, ignore_patterns):
        return
    
    # Build the tree branch characters
    connector = "└── " if is_last else "├── "
    
    # Format the output line
    display_name = path.name if path.name else str(path)
    
    if show_sizes and path.is_file():
        size = path.stat().st_size
        print(f"{prefix}{connector}{display_name} ({format_size(size)})")
    elif show_sizes and path.is_dir():
        size = get_dir_size(path, ignore_patterns)
        print(f"{prefix}{connector}{display_name}/ ({format_size(size)})")
    else:
        suffix = "/" if path.is_dir() else ""
        print(f"{prefix}{connector}{display_name}{suffix}")
    
    # If it's a directory, recurse into it
    if path.is_dir() and not path.is_symlink():
        try:
            entries = sorted(path.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
            # Filter out ignored entries
            entries = [e for e in entries if not should_ignore(e, ignore_patterns)]
            
            for i, entry in enumerate(entries):
                is_last_entry = (i == len(entries) - 1)
                # Update prefix: add vertical bar if not last, space otherwise
                extension = "    " if is_last else "│   "
                print_tree(
                    entry,
                    prefix + extension,
                    is_last_entry,
                    ignore_patterns,
                    show_sizes,
                    max_depth,
                    current_depth + 1
                )
        except PermissionError:
            # Can't read this directory, just note it and move on
            pass


def main():
    """Parse arguments and run the tree printer."""
    parser = argparse.ArgumentParser(
        description="Print directory tree structure with optional size information",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s .                          # Print tree of current directory
  %(prog)s ~/Projects -s              # Show with sizes
  %(prog)s . -d 2 -i node_modules     # Max depth 2, ignore node_modules
  %(prog)s . -i .git -i __pycache__   # Ignore multiple patterns
        """
    )
    
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Directory path to print (default: current directory)'
    )
    
    parser.add_argument(
        '-s', '--sizes',
        action='store_true',
        help='Show file and directory sizes'
    )
    
    parser.add_argument(
        '-d', '--max-depth',
        type=int,
        help='Maximum depth to traverse'
    )
    
    parser.add_argument(
        '-i', '--ignore',
        action='append',
        default=[],
        help='Patterns to ignore (can be used multiple times)'
    )
    
    args = parser.parse_args()
    
    target_path = Path(args.path).resolve()
    
    if not target_path.exists():
        print(f"Error: Path '{args.path}' does not exist")
        return 1
    
    print(target_path)
    print_tree(
        target_path,
        ignore_patterns=set(args.ignore),
        show_sizes=args.sizes,
        max_depth=args.max_depth
    )
    
    return 0


if __name__ == "__main__":
    # Demo: print the current script's parent directory with sizes
    print("=== Demo: Tree of current directory (max depth 2, with sizes) ===\n")
    
    import sys
    current_dir = Path(__file__).parent
    
    print(current_dir)
    print_tree(
        current_dir,
        show_sizes=True,
        max_depth=2,
        ignore_patterns={'.git', '__pycache__', '.pyc'}
    )
    
    print("\n=== Run with -h for full usage info ===")