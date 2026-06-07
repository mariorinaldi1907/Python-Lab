"""
Date: 2026-06-07
Made a CLI tool that prints pretty directory trees with configurable depth limits and pattern filtering — needed something lighter than tree(1) with more control.
"""

#!/usr/bin/env python3
"""
Directory tree printer with filtering and depth control.
Prints a visual tree structure of directories and files.
"""

import os
import argparse
import fnmatch
from pathlib import Path


class TreePrinter:
    """Handles the visual representation of directory trees."""
    
    # Box-drawing characters for the tree structure
    # Using these because they look way cleaner than ASCII art
    BRANCH = "├── "
    LAST = "└── "
    VERTICAL = "│   "
    SPACE = "    "
    
    def __init__(self, show_hidden=False, max_depth=None, pattern=None):
        """
        Initialize the tree printer.
        
        Args:
            show_hidden: Include hidden files/dirs (starting with .)
            max_depth: Maximum depth to traverse (None = unlimited)
            pattern: Glob pattern to filter entries (e.g., "*.py")
        """
        self.show_hidden = show_hidden
        self.max_depth = max_depth
        self.pattern = pattern
        self.dir_count = 0
        self.file_count = 0
    
    def should_include(self, name):
        """
        Check if an entry should be included based on filters.
        
        Args:
            name: The file or directory name
            
        Returns:
            True if the entry passes all filters
        """
        # Skip hidden files unless explicitly requested
        if not self.show_hidden and name.startswith('.'):
            return False
        
        # Apply glob pattern if provided
        if self.pattern and not fnmatch.fnmatch(name, self.pattern):
            return False
        
        return True
    
    def print_tree(self, path, prefix="", depth=0):
        """
        Recursively print the directory tree.
        
        Args:
            path: Path object to print
            prefix: String prefix for proper indentation
            depth: Current depth in the tree (for max_depth check)
        """
        # Check depth limit
        if self.max_depth is not None and depth > self.max_depth:
            return
        
        try:
            entries = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        except PermissionError:
            # Can't read this directory, just note it and move on
            print(f"{prefix}[Permission Denied]")
            return
        
        # Filter entries based on our criteria
        entries = [e for e in entries if self.should_include(e.name)]
        
        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            connector = self.LAST if is_last else self.BRANCH
            
            # Print the entry
            display_name = entry.name
            if entry.is_symlink():
                # Show where symlinks point
                try:
                    target = os.readlink(entry)
                    display_name = f"{display_name} -> {target}"
                except OSError:
                    display_name = f"{display_name} -> [broken symlink]"
            elif entry.is_dir():
                display_name = f"{display_name}/"
                self.dir_count += 1
            else:
                self.file_count += 1
            
            print(f"{prefix}{connector}{display_name}")
            
            # Recurse into directories (but not symlinks to avoid loops)
            if entry.is_dir() and not entry.is_symlink():
                extension = self.SPACE if is_last else self.VERTICAL
                self.print_tree(entry, prefix + extension, depth + 1)
    
    def print_summary(self):
        """Print a summary of directories and files found."""
        print(f"\n{self.dir_count} directories, {self.file_count} files")


def parse_arguments():
    """
    Parse command-line arguments.
    
    Returns:
        Parsed argument namespace
    """
    parser = argparse.ArgumentParser(
        description="Print a visual directory tree structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s .                    # Print tree from current directory
  %(prog)s /home/user -d 2      # Limit depth to 2 levels
  %(prog)s . -p "*.py"          # Show only Python files
  %(prog)s . -a                 # Include hidden files
        """
    )
    
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Directory to print (default: current directory)'
    )
    
    parser.add_argument(
        '-d', '--depth',
        type=int,
        metavar='N',
        help='Maximum depth to traverse'
    )
    
    parser.add_argument(
        '-a', '--all',
        action='store_true',
        help='Show hidden files and directories'
    )
    
    parser.add_argument(
        '-p', '--pattern',
        metavar='PATTERN',
        help='Filter entries by glob pattern (e.g., "*.txt")'
    )
    
    return parser.parse_args()


def main():
    """Main entry point for the directory tree printer."""
    args = parse_arguments()
    
    target_path = Path(args.path).resolve()
    
    # Validate the path exists
    if not target_path.exists():
        print(f"Error: Path '{args.path}' does not exist")
        return 1
    
    if not target_path.is_dir():
        print(f"Error: Path '{args.path}' is not a directory")
        return 1
    
    # Print the root
    print(target_path)
    
    # Create printer and start traversal
    printer = TreePrinter(
        show_hidden=args.all,
        max_depth=args.depth,
        pattern=args.pattern
    )
    
    printer.print_tree(target_path)
    printer.print_summary()
    
    return 0


if __name__ == "__main__":
    # Demo: create a small test directory structure and print it
    import tempfile
    import shutil
    
    print("=== Demo: Creating and printing a test directory tree ===\n")
    
    # Create a temporary test structure
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Build a realistic project structure
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("# Main module")
        (tmp_path / "src" / "utils.py").write_text("# Utilities")
        (tmp_path / "src" / "__init__.py").touch()
        
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test_main.py").write_text("# Tests")
        
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "README.md").write_text("# Documentation")
        
        (tmp_path / ".git").mkdir()
        (tmp_path / ".gitignore").write_text("*.pyc")
        (tmp_path / "requirements.txt").write_text("requests")
        
        # Print the tree
        print(tmp_path)
        printer = TreePrinter(show_hidden=True, max_depth=2)
        printer.print_tree(tmp_path)
        printer.print_summary()
    
    print("\n=== Demo complete! Run with --help for usage ===")