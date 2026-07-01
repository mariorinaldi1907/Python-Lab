"""
Date: 2026-07-01
Made a tool to scan directories for duplicate files using MD5 hashing — was tired of manually finding duplicate photos and videos on my drives.
"""

#!/usr/bin/env python3
"""
Duplicate File Finder - Scans directories and identifies duplicate files based on MD5 hashes.
Uses a chunk-based approach to handle large files without eating all the RAM.
"""

import argparse
import hashlib
import os
import sys
from collections import defaultdict
from pathlib import Path


def compute_file_hash(filepath, chunk_size=8192):
    """
    Compute MD5 hash of a file by reading it in chunks.
    
    Args:
        filepath: Path to the file to hash
        chunk_size: Size of chunks to read (default 8KB)
    
    Returns:
        MD5 hash as hexadecimal string
    
    The chunk approach prevents loading huge files entirely into memory.
    """
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
        print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)
        return None


def scan_directory(directory, recursive=True, show_progress=False):
    """
    Scan a directory and build a mapping of file hashes to file paths.
    
    Args:
        directory: Root directory to scan
        recursive: Whether to scan subdirectories
        show_progress: Print progress messages while scanning
    
    Returns:
        Dictionary mapping hash -> list of file paths with that hash
    """
    hash_map = defaultdict(list)
    file_count = 0
    
    # Use rglob for recursive, glob for non-recursive
    pattern = '**/*' if recursive else '*'
    
    for path in Path(directory).glob(pattern):
        if not path.is_file():
            continue
        
        file_count += 1
        if show_progress and file_count % 100 == 0:
            print(f"Scanned {file_count} files...", file=sys.stderr)
        
        file_hash = compute_file_hash(path)
        if file_hash:
            hash_map[file_hash].append(str(path))
    
    if show_progress:
        print(f"Finished scanning {file_count} files.", file=sys.stderr)
    
    return hash_map


def find_duplicates(hash_map):
    """
    Filter hash map to only include entries with duplicate files.
    
    Args:
        hash_map: Dictionary mapping hash -> list of file paths
    
    Returns:
        Dictionary containing only hashes with multiple files
    """
    return {h: paths for h, paths in hash_map.items() if len(paths) > 1}


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


def print_duplicates(duplicates, show_size=True):
    """
    Pretty-print duplicate file groups.
    
    Args:
        duplicates: Dictionary mapping hash -> list of duplicate file paths
        show_size: Whether to display file sizes
    """
    if not duplicates:
        print("No duplicate files found!")
        return
    
    total_groups = len(duplicates)
    total_duplicates = sum(len(paths) - 1 for paths in duplicates.values())
    
    print(f"\nFound {total_groups} duplicate file groups ({total_duplicates} duplicate files):\n")
    
    for idx, (file_hash, paths) in enumerate(duplicates.items(), 1):
        file_size = os.path.getsize(paths[0])
        size_info = f" ({format_size(file_size)})" if show_size else ""
        wasted_space = file_size * (len(paths) - 1)
        
        print(f"Group {idx}{size_info} - {len(paths)} copies (wasting {format_size(wasted_space)}):")
        for path in sorted(paths):
            print(f"  - {path}")
        print()


def main():
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        description="Find duplicate files in a directory by comparing MD5 hashes"
    )
    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='Directory to scan (default: current directory)'
    )
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        default=True,
        help='Scan subdirectories recursively (default: True)'
    )
    parser.add_argument(
        '--no-recursive',
        action='store_false',
        dest='recursive',
        help='Do not scan subdirectories'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show progress while scanning'
    )
    parser.add_argument(
        '--no-size',
        action='store_false',
        dest='show_size',
        help='Do not show file sizes in output'
    )
    
    args = parser.parse_args()
    
    # Validate directory exists
    if not os.path.isdir(args.directory):
        print(f"Error: '{args.directory}' is not a valid directory", file=sys.stderr)
        sys.exit(1)
    
    # Scan and find duplicates
    hash_map = scan_directory(args.directory, recursive=args.recursive, show_progress=args.verbose)
    duplicates = find_duplicates(hash_map)
    
    # Display results
    print_duplicates(duplicates, show_size=args.show_size)


if __name__ == "__main__":
    # Demo: Create a small test scenario if run directly without args
    if len(sys.argv) == 1:
        print("=== Demo Mode ===")
        print("Creating temporary test files to demonstrate duplicate detection...\n")
        
        # Create temp directory with some duplicate files
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some test files with duplicate content
            (Path(tmpdir) / "file1.txt").write_text("Hello, World!")
            (Path(tmpdir) / "file2.txt").write_text("Hello, World!")  # Duplicate of file1
            (Path(tmpdir) / "file3.txt").write_text("Different content")
            (Path(tmpdir) / "another_copy.txt").write_text("Hello, World!")  # Another duplicate
            
            print(f"Test directory: {tmpdir}\n")
            
            # Run the duplicate finder
            hash_map = scan_directory(tmpdir, recursive=False, show_progress=False)
            duplicates = find_duplicates(hash_map)
            print_duplicates(duplicates, show_size=True)
            
            print("\nDemo complete! Run with a real directory path to scan your files.")
            print("Example: python duplicate_file_finder.py ~/Documents --verbose")
    else:
        main()