"""
Date: 2026-08-12
Wrote a CLI tool that finds duplicate files by content hash — useful for cleaning up my messy Downloads folder and project directories.
"""

#!/usr/bin/env python3
"""
File deduplicator that finds duplicate files by computing SHA256 hashes.
I got tired of manually finding duplicate files in my downloads folder,
so I built this to automate the process.
"""

import argparse
import hashlib
import os
import sys
from collections import defaultdict
from pathlib import Path


def compute_file_hash(filepath, chunk_size=8192):
    """
    Compute SHA256 hash of a file by reading it in chunks.
    
    Using chunks because I don't want to load entire multi-GB files into memory.
    Learned that lesson the hard way when trying to hash a 4GB ISO file.
    
    Args:
        filepath: Path to the file to hash
        chunk_size: Number of bytes to read at a time (default 8KB)
    
    Returns:
        Hex string of the SHA256 hash
    """
    hasher = hashlib.sha256()
    
    try:
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()
    except (IOError, OSError) as e:
        print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)
        return None


def find_duplicates(directory, recursive=True, min_size=0):
    """
    Find all duplicate files in a directory by comparing their hashes.
    
    Returns a dict mapping file hashes to lists of paths that share that hash.
    Only returns hashes that have more than one file (actual duplicates).
    
    Args:
        directory: Root directory to scan
        recursive: Whether to scan subdirectories
        min_size: Minimum file size in bytes to consider (skip tiny files)
    
    Returns:
        Dictionary where keys are hashes and values are lists of duplicate file paths
    """
    hash_map = defaultdict(list)
    
    # Convert to Path object for easier manipulation
    root_path = Path(directory)
    
    # Choose the right globbing pattern based on recursion flag
    pattern = "**/*" if recursive else "*"
    
    for filepath in root_path.glob(pattern):
        # Skip directories and files below minimum size
        if not filepath.is_file():
            continue
            
        try:
            file_size = filepath.stat().st_size
            if file_size < min_size:
                continue
        except OSError:
            continue
        
        # Compute hash and add to our map
        file_hash = compute_file_hash(filepath)
        if file_hash:
            hash_map[file_hash].append(str(filepath))
    
    # Filter out unique files (only keep duplicates)
    duplicates = {h: paths for h, paths in hash_map.items() if len(paths) > 1}
    
    return duplicates


def format_size(size_bytes):
    """
    Convert bytes to human-readable format (KB, MB, GB).
    
    Because seeing "4294967296 bytes" is way less helpful than "4.0 GB".
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def print_duplicates(duplicates, show_size=True):
    """
    Pretty-print the duplicate file groups to stdout.
    
    Args:
        duplicates: Dict mapping hashes to lists of duplicate file paths
        show_size: Whether to display file sizes
    """
    if not duplicates:
        print("No duplicates found!")
        return
    
    total_groups = len(duplicates)
    total_files = sum(len(paths) for paths in duplicates.values())
    
    print(f"Found {total_groups} groups of duplicates ({total_files} files total)\n")
    
    for i, (file_hash, paths) in enumerate(duplicates.items(), 1):
        # Get size of first file (all duplicates have same size)
        try:
            size = os.path.getsize(paths[0])
            size_str = f" [{format_size(size)}]" if show_size else ""
        except OSError:
            size_str = ""
        
        print(f"Group {i} - {len(paths)} duplicates{size_str}:")
        print(f"  Hash: {file_hash[:16]}...")
        
        for path in sorted(paths):
            print(f"    {path}")
        print()


def main():
    """
    Main entry point for the CLI tool.
    """
    parser = argparse.ArgumentParser(
        description="Find duplicate files by computing SHA256 hashes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example: %(prog)s ~/Downloads --min-size 1024"
    )
    
    parser.add_argument(
        'directory',
        help='Directory to scan for duplicates'
    )
    
    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Do not scan subdirectories'
    )
    
    parser.add_argument(
        '--min-size',
        type=int,
        default=0,
        metavar='BYTES',
        help='Minimum file size to consider (default: 0)'
    )
    
    parser.add_argument(
        '--no-size',
        action='store_true',
        help='Do not display file sizes in output'
    )
    
    args = parser.parse_args()
    
    # Validate directory exists
    if not os.path.isdir(args.directory):
        print(f"Error: '{args.directory}' is not a valid directory", file=sys.stderr)
        sys.exit(1)
    
    print(f"Scanning {args.directory}...")
    
    duplicates = find_duplicates(
        args.directory,
        recursive=not args.no_recursive,
        min_size=args.min_size
    )
    
    print_duplicates(duplicates, show_size=not args.no_size)


if __name__ == "__main__":
    # Demo: Create some test files and find duplicates among them
    import tempfile
    import shutil
    
    # Create a temporary directory for testing
    test_dir = tempfile.mkdtemp(prefix="dup_test_")
    
    try:
        print("=== DEMO MODE ===")
        print(f"Creating test files in {test_dir}\n")
        
        # Create some duplicate files
        test_content_a = b"Hello, this is file A content"
        test_content_b = b"Different content for file B"
        
        # Write duplicate files
        Path(test_dir, "file1.txt").write_bytes(test_content_a)
        Path(test_dir, "file2.txt").write_bytes(test_content_a)  # Duplicate of file1
        Path(test_dir, "file3.txt").write_bytes(test_content_b)
        Path(test_dir, "copy_of_file1.txt").write_bytes(test_content_a)  # Another duplicate
        
        # Create a subdirectory with more duplicates
        subdir = Path(test_dir, "subdir")
        subdir.mkdir()
        Path(subdir, "another_copy.txt").write_bytes(test_content_a)
        Path(subdir, "unique.txt").write_bytes(b"Unique content here")
        
        # Run the duplicate finder
        duplicates = find_duplicates(test_dir, recursive=True, min_size=0)
        print_duplicates(duplicates, show_size=True)
        
    finally:
        # Clean up test directory
        shutil.rmtree(test_dir)
        print(f"Cleaned up test directory: {test_dir}")