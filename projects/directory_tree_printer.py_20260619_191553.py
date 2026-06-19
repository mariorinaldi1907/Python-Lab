"""
Date: 2026-06-19
Made a CLI tool that prints directory structures with file sizes and lets you filter by extension or depth, because I got tired of using `tree` without good filtering options.
"""

#!/usr/bin/env python3
"""
Directory tree printer with file sizes and filtering capabilities.
Prints a nice visual tree of directories with optional filtering by extension,
depth limit, and file size display.
"""

import argparse
import os
from pathlib import Path
from typing import List, Optional


class TreeNode:
    """Represents a file or directory in the tree structure."""
    
    def __init__(self, path: Path, is_last: bool = False):
        """
        Initialize a tree node.
        
        Args:
            path: Path object for this node
            is_last: Whether this is the last item in its parent directory
        """
        self.path = path
        self.is_last = is_last
        self.is_dir = path.is_dir()
        self.size = self._get_size()
    
    def _get_size(self) -> int:
        """Get file size in bytes, returns 0 for directories."""
        if self.is_dir or self.path.is_symlink():
            return 0
        try:
            return self.path.stat().st_size
        except (OSError, PermissionError):
            return 0


def format_size(size_bytes: int) -> str:
    """
    Convert bytes to human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted string like "1.5 KB" or "2.3 MB"
    """
    if size_bytes == 0:
        return ""
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def should_include(path: Path, extensions: Optional[List[str]]) -> bool:
    """
    Check if a file should be included based on extension filter.
    Directories are always included.
    
    Args:
        path: Path to check
        extensions: List of extensions to filter by (e.g., ['.py', '.txt'])
        
    Returns:
        True if the file should be included
    """
    if path.is_dir():
        return True
    
    if not extensions:
        return True
    
    return path.suffix.lower() in extensions


def print_tree(
    root_path: Path,
    prefix: str = "",
    extensions: Optional[List[str]] = None,
    show_size: bool = True,
    max_depth: Optional[int] = None,
    current_depth: int = 0
):
    """
    Recursively print directory tree structure.
    
    Args:
        root_path: Root directory to start from
        prefix: String prefix for tree formatting (manages the visual lines)
        extensions: Optional list of file extensions to filter
        show_size: Whether to display file sizes
        max_depth: Maximum depth to traverse (None = unlimited)
        current_depth: Current depth in the recursion
    """
    if max_depth is not None and current_depth >= max_depth:
        return
    
    try:
        # Get all items, filter them, and sort (dirs first, then alphabetically)
        items = [p for p in root_path.iterdir() if should_include(p, extensions)]
        items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
    except PermissionError:
        print(f"{prefix}[Permission Denied]")
        return
    
    # I'm using enumerate with total count to know which item is last
    # This helps with the tree branch characters (└── vs ├──)
    for idx, item in enumerate(items):
        is_last = (idx == len(items) - 1)
        
        # Choose the right tree characters
        connector = "└── " if is_last else "├── "
        
        # Build the display name
        display_name = item.name
        if item.is_symlink():
            display_name += " -> " + str(item.resolve())
        
        # Add size info if requested and it's a file
        size_str = ""
        if show_size and item.is_file():
            size = item.stat().st_size if not item.is_symlink() else 0
            size_str = f" ({format_size(size)})"
        
        print(f"{prefix}{connector}{display_name}{size_str}")
        
        # Recurse into directories
        if item.is_dir() and not item.is_symlink():
            # The extension for the next level depends on whether this is the last item
            # If it's the last item, use spaces; otherwise, use a vertical line
            extension = "    " if is_last else "│   "
            print_tree(
                item,
                prefix + extension,
                extensions,
                show_size,
                max_depth,
                current_depth + 1
            )


def main():
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        description="Print directory tree structure with optional filtering and sizing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s .                           # Print tree of current directory
  %(prog)s /path/to/dir -d 2           # Limit depth to 2 levels
  %(prog)s . -e .py .txt               # Only show Python and text files
  %(prog)s . --no-size                 # Don't show file sizes
        """
    )
    
    parser.add_argument(
        'path',
        type=str,
        nargs='?',
        default='.',
        help='Directory path to visualize (default: current directory)'
    )
    
    parser.add_argument(
        '-d', '--depth',
        type=int,
        metavar='N',
        help='Maximum depth to traverse'
    )
    
    parser.add_argument(
        '-e', '--extensions',
        nargs='+',
        metavar='EXT',
        help='Filter by file extensions (e.g., .py .txt)'
    )
    
    parser.add_argument(
        '--no-size',
        action='store_true',
        help='Hide file sizes'
    )
    
    args = parser.parse_args()
    
    # Convert string path to Path object and validate
    root = Path(args.path).resolve()
    
    if not root.exists():
        print(f"Error: Path '{args.path}' does not exist")
        return 1
    
    if not root.is_dir():
        print(f"Error: Path '{args.path}' is not a directory")
        return 1
    
    # Normalize extensions to include the dot
    extensions = None
    if args.extensions:
        extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in args.extensions]
    
    # Print the root directory name first
    print(root.name + "/")
    
    # Print the tree
    print_tree(
        root,
        extensions=extensions,
        show_size=not args.no_size,
        max_depth=args.depth
    )
    
    return 0


if __name__ == "__main__":
    # Demo: create a small test directory structure to showcase the tool
    import tempfile
    import shutil
    
    print("=== DEMO: Creating test directory structure ===\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_root = Path(tmpdir) / "demo_project"
        test_root.mkdir()
        
        # Create some sample files and directories
        (test_root / "src").mkdir()
        (test_root / "src" / "main.py").write_text("print('hello')")
        (test_root / "src" / "utils.py").write_text("def helper(): pass")
        
        (test_root / "tests").mkdir()
        (test_root / "tests" / "test_main.py").write_text("import unittest")
        
        (test_root / "docs").mkdir()
        (test_root / "docs" / "README.md").write_text("# Documentation")
        (test_root / "docs" / "guide.txt").write_text("User guide content here")
        
        (test_root / "config.json").write_text('{"version": "1.0"}')
        (test_root / ".gitignore").write_text("*.pyc\n__pycache__/")
        
        print(f"Created test structure at: {test_root}\n")
        print("--- Full tree with sizes ---")
        print_tree(test_root, show_size=True)
        
        print("\n--- Only Python files ---")
        print_tree(test_root, extensions=['.py'], show_size=True)
        
        print("\n--- Depth limit of 1 ---")
        print_tree(test_root, show_size=True, max_depth=1)