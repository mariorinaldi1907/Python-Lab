"""
Date: 2026-07-12
Made a file deduplicator that uses MD5 hashing with size-based pre-filtering to quickly find duplicate files across directories.
"""

#!/usr/bin/env python3
"""
File deduplicator that finds duplicate files based on content hash.
Uses file size as a first-pass filter to avoid unnecessary hashing.
"""

import argparse
import hashlib
import os
from collections import defaultdict
from pathlib import Path


def calculate_file_hash(filepath, chunk_size=8192):
    """
    Calculate MD5 hash of a file by reading it in chunks.
    
    Args:
        filepath: Path to the file to hash
        chunk_size: Size of chunks to read (default 8KB)
    
    Returns:
        Hex string of the MD5 hash
    """
    # Using MD5 because we just need to detect duplicates, not security
    hasher = hashlib.md5()
    
    try:
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()
    except (IOError, PermissionError) as e:
        # Skip files we can't read
        return None


def find_duplicates(directory, recursive=True, min_size=1):
    """
    Find duplicate files in a directory based on content hash.
    
    Args:
        directory: Root directory to search
        recursive: Whether to search subdirectories
        min_size: Minimum file size in bytes to consider (skip empty files by default)
    
    Returns:
        Dictionary mapping hash to list of file paths with that hash
    """
    # First pass: group files by size (cheap operation)
    size_groups = defaultdict(list)
    
    path = Path(directory)
    pattern = '**/*' if recursive else '*'
    
    for filepath in path.glob(pattern):
        if filepath.is_file():
            try:
                size = filepath.stat().st_size
                if size >= min_size:
                    size_groups[size].append(filepath)
            except OSError:
                # Skip files we can't stat
                continue
    
    # Second pass: only hash files that share a size with at least one other file
    # This avoids hashing unique files
    hash_groups = defaultdict(list)
    
    for size, files in size_groups.items():
        if len(files) > 1:  # Only hash if multiple files share this size
            for filepath in files:
                file_hash = calculate_file_hash(filepath)
                if file_hash:
                    hash_groups[file_hash].append(filepath)
    
    # Return only groups with actual duplicates
    return {h: files for h, files in hash_groups.items() if len(files) > 1}


def format_size(size_bytes):
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted string like '1.5 MB'
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def print_duplicates(duplicates, show_size=True):
    """
    Print duplicate file groups in a readable format.
    
    Args:
        duplicates: Dictionary mapping hash to list of file paths
        show_size: Whether to display file sizes
    """
    if not duplicates:
        print("No duplicate files found.")
        return
    
    total_duplicates = sum(len(files) - 1 for files in duplicates.values())
    total_waste = 0
    
    print(f"Found {len(duplicates)} sets of duplicate files:\n")
    
    for idx, (file_hash, files) in enumerate(duplicates.items(), 1):
        file_size = files[0].stat().st_size
        waste = file_size * (len(files) - 1)
        total_waste += waste
        
        print(f"Duplicate set #{idx} ({len(files)} files):")
        if show_size:
            print(f"  Size: {format_size(file_size)} each, {format_size(waste)} wasted")
        print(f"  Hash: {file_hash}")
        
        for filepath in sorted(files):
            print(f"    - {filepath}")
        print()
    
    print(f"Summary: {total_duplicates} duplicate files wasting {format_size(total_waste)}")


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description='Find duplicate files based on content hash',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ~/Downloads
  %(prog)s /path/to/dir --no-recursive
  %(prog)s . --min-size 1048576  # Only files >= 1MB
        """
    )
    
    parser.add_argument(
        'directory',
        help='Directory to search for duplicates'
    )
    
    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Do not search subdirectories'
    )
    
    parser.add_argument(
        '--min-size',
        type=int,
        default=1,
        help='Minimum file size in bytes to consider (default: 1)'
    )
    
    parser.add_argument(
        '--no-size-display',
        action='store_true',
        help='Do not display file sizes in output'
    )
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.directory):
        parser.error(f"Directory not found: {args.directory}")
    
    print(f"Scanning {args.directory}...")
    duplicates = find_duplicates(
        args.directory,
        recursive=not args.no_recursive,
        min_size=args.min_size
    )
    
    print_duplicates(duplicates, show_size=not args.no_size_display)


if __name__ == "__main__":
    # Demo mode: create some test files in a temp directory
    import tempfile
    import shutil
    
    print("=== DEMO MODE ===\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create some duplicate files for demonstration
        test_dir = Path(tmpdir) / "test_files"
        test_dir.mkdir()
        
        # Create original files
        (test_dir / "file1.txt").write_text("Hello, World!")
        (test_dir / "file2.txt").write_text("Different content here.")
        (test_dir / "file3.txt").write_text("Hello, World!")  # Duplicate of file1
        
        # Create a subdirectory with more duplicates
        subdir = test_dir / "subdir"
        subdir.mkdir()
        (subdir / "copy1.txt").write_text("Hello, World!")  # Another duplicate
        (subdir / "unique.txt").write_text("Unique content!")
        
        print(f"Created test directory: {test_dir}\n")
        
        # Run the duplicate finder on our test directory
        duplicates = find_duplicates(test_dir, recursive=True, min_size=1)
        print_duplicates(duplicates)