"""
Date: 2026-08-12
Created a file deduplicator that recursively scans directories and groups duplicate files by content hash — useful for cleaning up my downloads folder that's gotten out of control.
"""

#!/usr/bin/env python3
"""
File deduplicator that finds duplicate files based on content hash.
Recursively scans directories and groups files with identical content.
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
    
    Args:
        filepath: Path to the file to hash
        chunk_size: Size of chunks to read (default 8KB to avoid memory issues on large files)
    
    Returns:
        Hexadecimal hash string, or None if file can't be read
    """
    hash_obj = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(chunk_size):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except (PermissionError, OSError) as e:
        print(f"Warning: Couldn't read {filepath}: {e}", file=sys.stderr)
        return None


def find_duplicates(root_paths, min_size=0, show_progress=False):
    """
    Find duplicate files across one or more root directories.
    
    Args:
        root_paths: List of directory paths to scan
        min_size: Minimum file size in bytes to consider (ignore tiny files)
        show_progress: Whether to print progress messages
    
    Returns:
        Dictionary mapping hash -> list of file paths with that hash
    """
    # First pass: group by size (cheap optimization before expensive hashing)
    size_groups = defaultdict(list)
    
    for root_path in root_paths:
        if show_progress:
            print(f"Scanning {root_path}...", file=sys.stderr)
        
        for dirpath, _, filenames in os.walk(root_path):
            for filename in filenames:
                filepath = Path(dirpath) / filename
                
                # Skip symlinks to avoid following them into weird places
                if filepath.is_symlink():
                    continue
                
                try:
                    file_size = filepath.stat().st_size
                    if file_size >= min_size:
                        size_groups[file_size].append(filepath)
                except OSError:
                    continue
    
    # Second pass: hash only files that share a size with at least one other file
    hash_groups = defaultdict(list)
    files_to_hash = [f for files in size_groups.values() if len(files) > 1 for f in files]
    
    if show_progress:
        print(f"Hashing {len(files_to_hash)} potential duplicates...", file=sys.stderr)
    
    for filepath in files_to_hash:
        file_hash = compute_file_hash(filepath)
        if file_hash:
            hash_groups[file_hash].append(filepath)
    
    # Return only hashes that actually have duplicates
    return {h: files for h, files in hash_groups.items() if len(files) > 1}


def format_size(size_bytes):
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def print_duplicates(duplicates, show_size=True):
    """
    Print duplicate file groups in a readable format.
    
    Args:
        duplicates: Dictionary from find_duplicates()
        show_size: Whether to show file sizes in output
    """
    if not duplicates:
        print("No duplicate files found!")
        return
    
    total_groups = len(duplicates)
    total_wasted = 0
    
    print(f"\nFound {total_groups} groups of duplicate files:\n")
    
    for idx, (file_hash, files) in enumerate(duplicates.items(), 1):
        file_size = files[0].stat().st_size
        wasted_space = file_size * (len(files) - 1)  # Keep one, delete the rest
        total_wasted += wasted_space
        
        size_str = f" ({format_size(file_size)})" if show_size else ""
        print(f"Group {idx}: {len(files)} duplicates{size_str}")
        print(f"  Hash: {file_hash[:16]}...")
        
        for filepath in sorted(files):
            print(f"    {filepath}")
        
        print()
    
    print(f"Total wasted space: {format_size(total_wasted)}")


def main():
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        description="Find duplicate files based on content hash (SHA256)",
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
        default=1,
        help='Minimum file size in bytes to consider (default: 1)'
    )
    
    parser.add_argument(
        '--no-size',
        action='store_true',
        help='Don\'t show file sizes in output'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Don\'t show progress messages'
    )
    
    args = parser.parse_args()
    
    # Validate that paths exist
    for path in args.paths:
        if not os.path.isdir(path):
            print(f"Error: {path} is not a valid directory", file=sys.stderr)
            sys.exit(1)
    
    duplicates = find_duplicates(
        args.paths,
        min_size=args.min_size,
        show_progress=not args.quiet
    )
    
    print_duplicates(duplicates, show_size=not args.no_size)


if __name__ == "__main__":
    # Demo: create some test files in /tmp and find duplicates
    import tempfile
    import shutil
    
    print("=== DEMO MODE: Creating test files ===\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)
        
        # Create some duplicate files
        (test_dir / "file1.txt").write_text("This is the same content")
        (test_dir / "file2.txt").write_text("This is the same content")
        (test_dir / "file3.txt").write_text("Different content here")
        
        subdir = test_dir / "subdir"
        subdir.mkdir()
        (subdir / "copy.txt").write_text("This is the same content")
        (subdir / "unique.txt").write_text("Only one of these")
        
        print(f"Created test directory: {test_dir}\n")
        
        # Find duplicates in the test directory
        duplicates = find_duplicates([test_dir], show_progress=True)
        print_duplicates(duplicates)