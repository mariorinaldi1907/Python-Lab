"""
Date: 2026-08-16
Made a tool to clean up my messy downloads folder by finding duplicate files across directories using content hashing instead of just filenames.
"""

#!/usr/bin/env python3
"""
Duplicate File Finder - finds identical files by comparing their SHA256 hashes.
I got tired of having the same PDFs and images scattered across my drive.
"""

import argparse
import hashlib
import os
import sys
from collections import defaultdict
from pathlib import Path


def hash_file(filepath, chunk_size=8192):
    """
    Calculate SHA256 hash of a file by reading it in chunks.
    
    Using chunks so we don't blow up memory on large video files.
    Learned this the hard way when trying to hash a 4GB ISO.
    
    Args:
        filepath: Path to the file to hash
        chunk_size: Size of chunks to read (8KB default works well)
    
    Returns:
        Hexadecimal digest string of the file's SHA256 hash
    """
    sha256_hash = hashlib.sha256()
    
    try:
        with open(filepath, 'rb') as f:
            # Read and hash file in chunks
            while chunk := f.read(chunk_size):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except (IOError, PermissionError) as e:
        # Sometimes we hit permission errors on system files
        print(f"Warning: Cannot read {filepath}: {e}", file=sys.stderr)
        return None


def find_duplicates(directories, recursive=True, min_size=0):
    """
    Find duplicate files across one or more directories.
    
    Groups files by hash - if multiple files have the same hash,
    they're duplicates (SHA256 collision is astronomically unlikely).
    
    Args:
        directories: List of directory paths to scan
        recursive: Whether to scan subdirectories
        min_size: Ignore files smaller than this (in bytes)
    
    Returns:
        Dictionary mapping hash -> list of file paths with that hash
    """
    hash_to_files = defaultdict(list)
    total_files = 0
    
    for directory in directories:
        dir_path = Path(directory)
        
        if not dir_path.exists():
            print(f"Warning: Directory '{directory}' does not exist", file=sys.stderr)
            continue
        
        if not dir_path.is_dir():
            print(f"Warning: '{directory}' is not a directory", file=sys.stderr)
            continue
        
        # Choose glob pattern based on recursive flag
        pattern = '**/*' if recursive else '*'
        
        for filepath in dir_path.glob(pattern):
            if not filepath.is_file():
                continue
            
            # Skip files below minimum size threshold
            file_size = filepath.stat().st_size
            if file_size < min_size:
                continue
            
            total_files += 1
            file_hash = hash_file(filepath)
            
            if file_hash:  # None if we couldn't read the file
                hash_to_files[file_hash].append(str(filepath))
    
    # Only keep hashes that have duplicates (2+ files)
    duplicates = {h: files for h, files in hash_to_files.items() if len(files) > 1}
    
    print(f"\nScanned {total_files} files")
    return duplicates


def format_size(size_bytes):
    """
    Convert bytes to human-readable format.
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted string like "1.5 MB"
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def display_duplicates(duplicates):
    """
    Pretty-print the duplicate files found.
    
    Args:
        duplicates: Dictionary of hash -> file paths
    """
    if not duplicates:
        print("\nNo duplicate files found! 🎉")
        return
    
    total_waste = 0
    
    print(f"\nFound {len(duplicates)} sets of duplicate files:\n")
    
    for idx, (file_hash, files) in enumerate(duplicates.items(), 1):
        # Calculate wasted space (size of duplicates beyond the first)
        file_size = os.path.getsize(files[0])
        wasted = file_size * (len(files) - 1)
        total_waste += wasted
        
        print(f"[Set {idx}] {len(files)} duplicates - {format_size(file_size)} each")
        print(f"Hash: {file_hash[:16]}...")
        
        for filepath in sorted(files):
            print(f"  • {filepath}")
        
        print(f"  Wasted space: {format_size(wasted)}\n")
    
    print(f"Total wasted space: {format_size(total_waste)}")


def main():
    """Main entry point - parse args and run the duplicate finder."""
    parser = argparse.ArgumentParser(
        description="Find duplicate files by comparing their content hashes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example: %(prog)s ~/Downloads ~/Documents --min-size 1048576"
    )
    
    parser.add_argument(
        'directories',
        nargs='+',
        help='One or more directories to scan for duplicates'
    )
    
    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help="Don't scan subdirectories"
    )
    
    parser.add_argument(
        '--min-size',
        type=int,
        default=0,
        metavar='BYTES',
        help='Ignore files smaller than this many bytes (default: 0)'
    )
    
    args = parser.parse_args()
    
    duplicates = find_duplicates(
        args.directories,
        recursive=not args.no_recursive,
        min_size=args.min_size
    )
    
    display_duplicates(duplicates)


if __name__ == "__main__":
    # Demo: create some test files in a temp directory to show it works
    import tempfile
    import shutil
    
    print("=== Running demo with temporary test files ===\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create some duplicate files
        test_dir = Path(tmpdir) / "test_files"
        test_dir.mkdir()
        
        # Same content, different names
        (test_dir / "file1.txt").write_text("Hello, World!")
        (test_dir / "file2.txt").write_text("Hello, World!")
        (test_dir / "different.txt").write_text("Different content")
        
        # Subdirectory with another duplicate
        sub_dir = test_dir / "subdir"
        sub_dir.mkdir()
        (sub_dir / "file3.txt").write_text("Hello, World!")
        
        # Run the finder on our test directory
        duplicates = find_duplicates([str(test_dir)], recursive=True, min_size=0)
        display_duplicates(duplicates)
    
    print("\n=== Demo complete ===")
    print("Run with --help to see usage for real directories")