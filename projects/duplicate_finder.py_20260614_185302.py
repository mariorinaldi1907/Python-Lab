"""
Date: 2026-06-14
Made a duplicate file finder that uses SHA256 hashing to identify identical files across directories — helps me reclaim disk space from accidentally duplicated photos and documents.
"""

#!/usr/bin/env python3
"""
Duplicate File Finder - CLI tool to locate duplicate files based on content hashing.

This script walks through directories, computes SHA256 hashes of file contents,
and groups files that are byte-for-byte identical. Useful for finding and
optionally removing duplicate files to free up disk space.
"""

import argparse
import hashlib
import os
import sys
from collections import defaultdict
from pathlib import Path


def compute_file_hash(filepath, chunk_size=8192):
    """
    Compute SHA256 hash of a file's contents.
    
    Args:
        filepath: Path to the file to hash
        chunk_size: Size of chunks to read (default 8KB, balances memory vs I/O)
    
    Returns:
        Hexadecimal string of the file's SHA256 hash
    """
    hasher = hashlib.sha256()
    
    try:
        with open(filepath, 'rb') as f:
            # Read file in chunks to handle large files without loading entirely into memory
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (IOError, OSError) as e:
        print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)
        return None


def find_duplicates(paths, min_size=0, verbose=False):
    """
    Find duplicate files across one or more directory paths.
    
    Args:
        paths: List of directory paths to scan
        min_size: Minimum file size in bytes to consider (filters out tiny files)
        verbose: Print progress information
    
    Returns:
        Dictionary mapping hash -> list of file paths with that hash
    """
    file_hashes = defaultdict(list)
    file_count = 0
    
    for base_path in paths:
        base_path = Path(base_path)
        
        if not base_path.exists():
            print(f"Warning: Path {base_path} does not exist, skipping", file=sys.stderr)
            continue
        
        # Walk the directory tree
        for root, dirs, files in os.walk(base_path):
            for filename in files:
                filepath = Path(root) / filename
                
                # Skip symbolic links to avoid infinite loops
                if filepath.is_symlink():
                    continue
                
                try:
                    file_size = filepath.stat().st_size
                    
                    # Skip files smaller than minimum size
                    if file_size < min_size:
                        continue
                    
                    file_count += 1
                    if verbose and file_count % 100 == 0:
                        print(f"Processed {file_count} files...", file=sys.stderr)
                    
                    file_hash = compute_file_hash(filepath)
                    if file_hash:
                        file_hashes[file_hash].append(str(filepath))
                
                except OSError as e:
                    print(f"Warning: Could not access {filepath}: {e}", file=sys.stderr)
    
    # Only return hashes that have duplicates (more than one file)
    duplicates = {h: files for h, files in file_hashes.items() if len(files) > 1}
    
    if verbose:
        print(f"Scanned {file_count} files total", file=sys.stderr)
    
    return duplicates


def format_size(size_bytes):
    """
    Convert bytes to human-readable format.
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def print_duplicates(duplicates, show_size=True):
    """
    Print duplicate file groups in a readable format.
    
    Args:
        duplicates: Dictionary of hash -> file list
        show_size: Whether to show file sizes
    """
    if not duplicates:
        print("No duplicates found!")
        return
    
    total_groups = len(duplicates)
    total_wasted = 0
    
    print(f"Found {total_groups} group(s) of duplicate files:\n")
    
    for idx, (file_hash, files) in enumerate(duplicates.items(), 1):
        file_size = Path(files[0]).stat().st_size
        wasted_space = file_size * (len(files) - 1)
        total_wasted += wasted_space
        
        print(f"Group {idx} ({len(files)} duplicates, {format_size(wasted_space)} wasted):")
        
        for filepath in sorted(files):
            if show_size:
                print(f"  [{format_size(file_size)}] {filepath}")
            else:
                print(f"  {filepath}")
        
        print()  # Blank line between groups
    
    print(f"Total wasted space: {format_size(total_wasted)}")


def main():
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        description="Find duplicate files based on content hashing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example: %(prog)s ~/Downloads ~/Documents --min-size 1024"
    )
    
    parser.add_argument(
        'paths',
        nargs='+',
        help='One or more directories to scan for duplicates'
    )
    
    parser.add_argument(
        '--min-size',
        type=int,
        default=0,
        metavar='BYTES',
        help='Minimum file size to consider (default: 0, no filter)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Print verbose progress information'
    )
    
    args = parser.parse_args()
    
    # Find and display duplicates
    duplicates = find_duplicates(args.paths, min_size=args.min_size, verbose=args.verbose)
    print_duplicates(duplicates)


if __name__ == "__main__":
    # Demo with a simple test setup
    import tempfile
    
    print("=== DEMO MODE ===\n")
    print("Creating temporary test files to demonstrate duplicate detection...\n")
    
    # Create a temporary directory with some duplicate files
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir) / "test_files"
        test_dir.mkdir()
        
        # Create some duplicate files
        (test_dir / "file1.txt").write_text("Hello, this is file content A")
        (test_dir / "file2.txt").write_text("Hello, this is file content A")  # Duplicate of file1
        (test_dir / "file3.txt").write_text("Different content here")
        (test_dir / "file4.txt").write_text("Hello, this is file content A")  # Another duplicate
        (test_dir / "unique.txt").write_text("I am unique!")
        
        # Create a subdirectory with more duplicates
        subdir = test_dir / "subdir"
        subdir.mkdir()
        (subdir / "another_dup.txt").write_text("Different content here")  # Duplicate of file3
        
        print(f"Created test directory: {test_dir}\n")
        
        # Run the duplicate finder on the test directory
        duplicates = find_duplicates([test_dir], verbose=True)
        print()  # Blank line after verbose output
        print_duplicates(duplicates)