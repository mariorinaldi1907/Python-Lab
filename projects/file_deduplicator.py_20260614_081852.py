"""
Date: 2026-06-14
Created a CLI tool that finds duplicate files by comparing hashes instead of filenames, since I kept accumulating duplicate downloads and backups in my projects folder.
"""

#!/usr/bin/env python3
"""
File deduplicator that finds duplicate files based on content hash.
I built this because I kept downloading the same datasets and PDFs multiple times
and wasting disk space without realizing it.
"""

import argparse
import hashlib
import os
import sys
from collections import defaultdict
from pathlib import Path


def hash_file(filepath, block_size=65536):
    """
    Compute SHA-256 hash of a file by reading it in chunks.
    
    Using chunks instead of loading the whole file because some of my video files
    are gigabytes and I don't want to blow up memory.
    
    Args:
        filepath: Path to the file to hash
        block_size: Bytes to read per iteration (default 64KB)
    
    Returns:
        Hexadecimal hash string
    """
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(block_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (IOError, PermissionError) as e:
        print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)
        return None


def find_duplicates(root_dir, extensions=None, min_size=0):
    """
    Scan directory tree and find duplicate files based on content hash.
    
    I'm grouping by size first as an optimization — files with different sizes
    can't possibly be duplicates, so no need to hash them.
    
    Args:
        root_dir: Root directory to scan
        extensions: List of file extensions to check (e.g. ['.jpg', '.png']), or None for all
        min_size: Minimum file size in bytes to consider (skip tiny files)
    
    Returns:
        Dict mapping hash -> list of file paths with that hash
    """
    # Group files by size first (cheap operation)
    size_groups = defaultdict(list)
    
    for root, dirs, files in os.walk(root_dir):
        for filename in files:
            filepath = Path(root) / filename
            
            # Filter by extension if specified
            if extensions and filepath.suffix.lower() not in extensions:
                continue
            
            try:
                size = filepath.stat().st_size
                if size < min_size:
                    continue
                size_groups[size].append(filepath)
            except OSError:
                continue
    
    # Now hash only files that have the same size as at least one other file
    hash_groups = defaultdict(list)
    total_files = sum(len(files) for files in size_groups.values() if len(files) > 1)
    processed = 0
    
    for size, filepaths in size_groups.items():
        if len(filepaths) < 2:
            # No duplicates possible if only one file has this size
            continue
        
        for filepath in filepaths:
            processed += 1
            if processed % 50 == 0:
                print(f"Hashing files... {processed}/{total_files}", file=sys.stderr)
            
            file_hash = hash_file(filepath)
            if file_hash:
                hash_groups[file_hash].append(filepath)
    
    # Filter to only return groups with actual duplicates
    return {h: paths for h, paths in hash_groups.items() if len(paths) > 1}


def format_size(bytes_size):
    """Convert bytes to human-readable format (KB, MB, GB)."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"


def print_duplicates(duplicate_groups):
    """
    Print duplicate file groups in a readable format.
    
    Args:
        duplicate_groups: Dict from find_duplicates()
    """
    if not duplicate_groups:
        print("No duplicates found!")
        return
    
    total_duplicates = sum(len(paths) - 1 for paths in duplicate_groups.values())
    total_wasted = 0
    
    print(f"\nFound {len(duplicate_groups)} groups of duplicates:\n")
    
    for i, (file_hash, paths) in enumerate(duplicate_groups.items(), 1):
        # Get size from first file (all duplicates have same size)
        size = paths[0].stat().st_size
        wasted = size * (len(paths) - 1)
        total_wasted += wasted
        
        print(f"Group {i} — {len(paths)} copies, {format_size(size)} each "
              f"({format_size(wasted)} wasted)")
        print(f"Hash: {file_hash[:16]}...")
        for path in sorted(paths):
            print(f"  • {path}")
        print()
    
    print(f"Total: {total_duplicates} duplicate files wasting {format_size(total_wasted)}")


def main():
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        description="Find duplicate files based on content hash (SHA-256)"
    )
    parser.add_argument(
        'directory',
        help='Directory to scan for duplicates'
    )
    parser.add_argument(
        '-e', '--extensions',
        nargs='+',
        help='Only check specific extensions (e.g. -e .jpg .png .pdf)'
    )
    parser.add_argument(
        '-m', '--min-size',
        type=int,
        default=0,
        help='Minimum file size in bytes (default: 0)'
    )
    
    args = parser.parse_args()
    
    root_path = Path(args.directory)
    if not root_path.is_dir():
        print(f"Error: '{args.directory}' is not a valid directory", file=sys.stderr)
        sys.exit(1)
    
    print(f"Scanning {root_path} for duplicates...")
    if args.extensions:
        print(f"Filtering for extensions: {', '.join(args.extensions)}")
    if args.min_size > 0:
        print(f"Ignoring files smaller than {format_size(args.min_size)}")
    
    duplicates = find_duplicates(root_path, args.extensions, args.min_size)
    print_duplicates(duplicates)


if __name__ == "__main__":
    # Demo mode: create some test files and show how it works
    if len(sys.argv) == 1:
        print("=== DEMO MODE ===\n")
        
        # Create a temp directory with some duplicate files
        import tempfile
        import shutil
        
        demo_dir = Path(tempfile.mkdtemp(prefix="dedup_demo_"))
        print(f"Created demo directory: {demo_dir}\n")
        
        # Create some files with duplicate content
        (demo_dir / "file1.txt").write_text("This is some content")
        (demo_dir / "file2.txt").write_text("This is some content")  # duplicate!
        (demo_dir / "file3.txt").write_text("Different content here")
        (demo_dir / "subdir").mkdir()
        (demo_dir / "subdir" / "copy.txt").write_text("This is some content")  # another duplicate!
        (demo_dir / "unique.txt").write_text("Unique stuff")
        
        print("Created test files:")
        for f in demo_dir.rglob("*"):
            if f.is_file():
                print(f"  {f.relative_to(demo_dir)}")
        
        print("\nRunning deduplicator...\n")
        duplicates = find_duplicates(demo_dir)
        print_duplicates(duplicates)
        
        # Cleanup
        shutil.rmtree(demo_dir)
        print(f"\nDemo directory cleaned up.")
        print(f"\nTry it for real: python {sys.argv[0]} /path/to/directory")
    else:
        main()