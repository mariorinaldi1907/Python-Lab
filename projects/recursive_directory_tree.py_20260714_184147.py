"""
Date: 2026-07-14
Wrote a CLI tool that prints directory structures in a visual tree format with file sizes, because I got tired of installing `tree` on every new machine.
"""

#!/usr/bin/env python3
"""
Directory tree printer with file size statistics.
Prints a visual tree structure of directories and files, with optional
filtering and size reporting. Kind of like the `tree` command but with
some custom tweaks I wanted.
"""

import argparse
import os
from pathlib import Path
from typing import List, Set


class DirectoryTree:
    """
    Handles the recursive traversal and formatting of directory structures.
    
    I wanted this to be flexible enough to handle gitignore patterns and
    depth limits without getting too complicated.
    """
    
    def __init__(self, show_hidden: bool = False, max_depth: int = None, show_sizes: bool = False):
        """
        Initialize the tree printer with display options.
        
        Args:
            show_hidden: Whether to show files/dirs starting with '.'
            max_depth: Maximum depth to traverse (None = unlimited)
            show_sizes: Whether to display file sizes
        """
        self.show_hidden = show_hidden
        self.max_depth = max_depth
        self.show_sizes = show_sizes
        self.ignored_patterns = self._load_gitignore_patterns()
    
    def _load_gitignore_patterns(self) -> Set[str]:
        """
        Load patterns from .gitignore if it exists.
        
        This is a simple implementation - just matches exact names, not full
        gitignore spec (that would need a proper parser). Good enough for
        common cases like __pycache__, .git, node_modules, etc.
        """
        patterns = set()
        gitignore_path = Path('.gitignore')
        
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith('#'):
                        # Remove leading/trailing slashes for simple matching
                        patterns.add(line.strip('/'))
        
        return patterns
    
    def _should_ignore(self, name: str) -> bool:
        """Check if a file/directory should be ignored based on patterns."""
        if not self.show_hidden and name.startswith('.'):
            return True
        
        # Check against gitignore patterns (simple exact match)
        if name in self.ignored_patterns:
            return True
        
        return False
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}TB"
    
    def _get_entries(self, directory: Path) -> List[Path]:
        """
        Get sorted directory entries.
        
        Sort directories first, then files, both alphabetically.
        This makes the output much easier to read.
        """
        try:
            entries = list(directory.iterdir())
            # Filter out ignored entries
            entries = [e for e in entries if not self._should_ignore(e.name)]
            # Sort: directories first, then files, both alphabetical
            entries.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
            return entries
        except PermissionError:
            return []
    
    def print_tree(self, directory: Path, prefix: str = "", depth: int = 0):
        """
        Recursively print the directory tree.
        
        Uses box-drawing characters for the tree structure because it looks
        way better than ASCII art with pipes and dashes.
        
        Args:
            directory: Path to the directory to print
            prefix: Current line prefix for tree structure
            depth: Current recursion depth
        """
        if self.max_depth is not None and depth > self.max_depth:
            return
        
        entries = self._get_entries(directory)
        
        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            
            # Choose the right tree characters
            connector = "└── " if is_last else "├── "
            
            # Build the display name
            display_name = entry.name
            if entry.is_dir():
                display_name += "/"
            elif self.show_sizes and entry.is_file():
                try:
                    size = entry.stat().st_size
                    display_name += f" ({self._format_size(size)})"
                except (OSError, PermissionError):
                    pass
            
            print(f"{prefix}{connector}{display_name}")
            
            # Recurse into subdirectories
            if entry.is_dir():
                extension = "    " if is_last else "│   "
                self.print_tree(entry, prefix + extension, depth + 1)


def main():
    """
    Parse arguments and execute the directory tree printing.
    
    I made the default behavior pretty conservative (no hidden files, limited
    depth) since that's what I usually want when exploring unfamiliar codebases.
    """
    parser = argparse.ArgumentParser(
        description="Print a visual tree structure of directories and files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Print current directory
  %(prog)s /path/to/dir             # Print specific directory
  %(prog)s -a -d 2                  # Show hidden files, max depth 2
  %(prog)s -s                       # Include file sizes
        """
    )
    
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Directory to print (default: current directory)'
    )
    parser.add_argument(
        '-a', '--all',
        action='store_true',
        help='Show hidden files and directories'
    )
    parser.add_argument(
        '-d', '--depth',
        type=int,
        metavar='N',
        help='Maximum depth to traverse'
    )
    parser.add_argument(
        '-s', '--sizes',
        action='store_true',
        help='Show file sizes'
    )
    
    args = parser.parse_args()
    
    path = Path(args.path).resolve()
    
    if not path.exists():
        print(f"Error: Path '{path}' does not exist")
        return 1
    
    if not path.is_dir():
        print(f"Error: Path '{path}' is not a directory")
        return 1
    
    print(f"{path}/")
    
    tree = DirectoryTree(
        show_hidden=args.all,
        max_depth=args.depth,
        show_sizes=args.sizes
    )
    tree.print_tree(path)
    
    return 0


if __name__ == "__main__":
    # Demo run on the current directory with limited depth
    print("=== Demo: Printing current directory tree (depth=2, with sizes) ===\n")
    
    import sys
    
    # Simulate command line args for demo
    original_argv = sys.argv
    sys.argv = ['recursive_directory_tree.py', '.', '-d', '2', '-s']
    
    exit_code = main()
    
    sys.argv = original_argv
    sys.exit(exit_code)