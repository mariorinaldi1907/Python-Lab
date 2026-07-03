"""
Date: 2026-07-03
Created a CLI tool that prints directory trees with Unicode box-drawing characters, file sizes, and pattern filtering because I got tired of piping `tree` through grep.
"""

#!/usr/bin/env python3
"""
Directory tree visualization tool with filtering capabilities.

This script recursively walks through directories and prints a visual tree
representation with optional filtering and file size information.
"""

import argparse
import os
import sys
from pathlib import Path
from fnmatch import fnmatch


class TreePrinter:
    """Handles the visual representation of directory structures."""

    def __init__(self, show_sizes=False, show_hidden=False, pattern=None):
        """
        Initialize the tree printer with display options.

        Args:
            show_sizes: Whether to display file sizes in human-readable format
            show_hidden: Whether to include hidden files/directories
            pattern: Optional glob pattern to filter files (e.g., "*.py")
        """
        self.show_sizes = show_sizes
        self.show_hidden = show_hidden
        self.pattern = pattern
        self.stats = {"dirs": 0, "files": 0, "total_size": 0}

    def _human_readable_size(self, size_bytes):
        """Convert bytes to human-readable format (KB, MB, GB)."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:3.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    def _should_include(self, path):
        """
        Determine if a path should be included based on filters.

        Returns False for hidden files if show_hidden is disabled,
        or if the file doesn't match the pattern filter.
        """
        name = path.name
        
        # Skip hidden files unless explicitly requested
        if not self.show_hidden and name.startswith("."):
            return False
        
        # If pattern is set, only include matching files (dirs always included)
        if self.pattern and path.is_file():
            return fnmatch(name, self.pattern)
        
        return True

    def print_tree(self, directory, prefix="", is_last=True):
        """
        Recursively print directory tree structure.

        Uses Unicode box-drawing characters for a clean visual representation.
        The prefix accumulates as we go deeper, maintaining proper indentation.
        """
        path = Path(directory)
        
        if not path.exists():
            print(f"Error: {directory} does not exist", file=sys.stderr)
            return
        
        if not path.is_dir():
            print(f"Error: {directory} is not a directory", file=sys.stderr)
            return

        # Print the root directory name
        if prefix == "":
            print(f"📁 {path.name}/")
            self.stats["dirs"] += 1

        try:
            # Get all entries and filter them
            entries = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            entries = [e for e in entries if self._should_include(e)]
        except PermissionError:
            print(f"{prefix}└── [Permission Denied]")
            return

        for index, entry in enumerate(entries):
            is_last_entry = index == len(entries) - 1
            
            # Choose the appropriate connector characters
            connector = "└── " if is_last_entry else "├── "
            
            # Build the display name with optional size info
            display_name = entry.name
            size_info = ""
            
            if entry.is_file():
                self.stats["files"] += 1
                try:
                    size = entry.stat().st_size
                    self.stats["total_size"] += size
                    if self.show_sizes:
                        size_info = f" ({self._human_readable_size(size)})"
                except (OSError, PermissionError):
                    size_info = " (unknown size)"
                
                # Use different emoji for files vs directories
                icon = "📄"
            elif entry.is_symlink():
                icon = "🔗"
                try:
                    target = os.readlink(entry)
                    display_name = f"{display_name} -> {target}"
                except OSError:
                    display_name = f"{display_name} -> [broken link]"
            else:
                icon = "📁"
                display_name = f"{display_name}/"
                self.stats["dirs"] += 1
            
            print(f"{prefix}{connector}{icon} {display_name}{size_info}")
            
            # Recursively print subdirectories
            if entry.is_dir() and not entry.is_symlink():
                # Extension for the prefix depends on whether this is the last entry
                extension = "    " if is_last_entry else "│   "
                self.print_tree(entry, prefix + extension, is_last_entry)

    def print_stats(self):
        """Print summary statistics about the tree."""
        print()
        print(f"📊 Summary: {self.stats['dirs']} directories, {self.stats['files']} files")
        if self.show_sizes:
            print(f"💾 Total size: {self._human_readable_size(self.stats['total_size'])}")


def main():
    """Parse arguments and execute the tree printer."""
    parser = argparse.ArgumentParser(
        description="Print a visual tree representation of directory contents.",
        epilog="Example: %(prog)s ~/projects -s -p '*.py' --no-hidden"
    )
    
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to visualize (default: current directory)"
    )
    
    parser.add_argument(
        "-s", "--sizes",
        action="store_true",
        help="Show file sizes in human-readable format"
    )
    
    parser.add_argument(
        "-a", "--all",
        action="store_true",
        help="Include hidden files and directories"
    )
    
    parser.add_argument(
        "-p", "--pattern",
        help="Only show files matching this pattern (e.g., '*.txt', '*.py')"
    )
    
    args = parser.parse_args()
    
    printer = TreePrinter(
        show_sizes=args.sizes,
        show_hidden=args.all,
        pattern=args.pattern
    )
    
    printer.print_tree(args.directory)
    printer.print_stats()


if __name__ == "__main__":
    main()