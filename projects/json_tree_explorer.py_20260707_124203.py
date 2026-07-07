"""
Date: 2026-07-07
Created a JSON tree explorer that lets me quickly understand deeply nested JSON files by printing their structure with types and sample values.
"""

#!/usr/bin/env python3
"""
JSON Tree Explorer - A CLI tool to visualize and explore JSON file structure.

I got tired of opening massive JSON files in editors just to understand their
shape, so I built this to show me the structure with data types and samples.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Union


class JSONTreeExplorer:
    """
    Explores and pretty-prints the structure of JSON data.
    
    Shows the hierarchy, data types, and optionally sample values to help
    understand complex nested structures without reading the whole file.
    """
    
    def __init__(self, max_depth: int = None, show_samples: bool = True):
        """
        Initialize the explorer with configuration.
        
        Args:
            max_depth: Maximum depth to traverse (None = unlimited)
            show_samples: Whether to show sample values for leaf nodes
        """
        self.max_depth = max_depth
        self.show_samples = show_samples
    
    def explore(self, data: Any, prefix: str = "", depth: int = 0) -> None:
        """
        Recursively explore and print JSON structure.
        
        This is where the actual tree building happens. I use different
        logic for dicts, lists, and primitives to make the output readable.
        
        Args:
            data: The JSON data to explore (can be any JSON type)
            prefix: Current indentation prefix for tree structure
            depth: Current depth in the tree (for max_depth limiting)
        """
        # Check depth limit to avoid infinitely deep structures
        if self.max_depth is not None and depth >= self.max_depth:
            print(f"{prefix}... (max depth reached)")
            return
        
        if isinstance(data, dict):
            self._explore_dict(data, prefix, depth)
        elif isinstance(data, list):
            self._explore_list(data, prefix, depth)
        else:
            # Leaf node - primitive value
            self._print_value(data, prefix)
    
    def _explore_dict(self, data: Dict, prefix: str, depth: int) -> None:
        """
        Handle dictionary exploration with key-value pairs.
        
        I sort the keys to make the output deterministic and easier to read.
        """
        if not data:
            print(f"{prefix}{{}} (empty dict)")
            return
        
        print(f"{prefix}{{}} dict with {len(data)} key(s)")
        sorted_keys = sorted(data.keys())
        
        for i, key in enumerate(sorted_keys):
            is_last = (i == len(sorted_keys) - 1)
            branch = "└── " if is_last else "├── "
            extension = "    " if is_last else "│   "
            
            value = data[key]
            type_info = self._get_type_info(value)
            print(f"{prefix}{branch}{key}: {type_info}")
            
            # Recursively explore the value
            self.explore(value, prefix + extension, depth + 1)
    
    def _explore_list(self, data: List, prefix: str, depth: int) -> None:
        """
        Handle list exploration, showing type of elements.
        
        For arrays, I sample the first element to show structure rather than
        printing every single item (which would be crazy for large arrays).
        """
        if not data:
            print(f"{prefix}[] (empty list)")
            return
        
        print(f"{prefix}[] list with {len(data)} item(s)")
        
        # Show structure of first element as a representative sample
        if data:
            type_info = self._get_type_info(data[0])
            print(f"{prefix}└── [0]: {type_info}")
            self.explore(data[0], prefix + "    ", depth + 1)
            
            if len(data) > 1:
                print(f"{prefix}    ... ({len(data) - 1} more items)")
    
    def _get_type_info(self, value: Any) -> str:
        """
        Get a human-readable type description for a value.
        
        Returns things like "string", "number", "bool", etc. instead of
        Python's internal type names which can be confusing.
        """
        if isinstance(value, bool):
            return "bool"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "number"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, dict):
            return "object"
        elif isinstance(value, list):
            return "array"
        elif value is None:
            return "null"
        else:
            return type(value).__name__
    
    def _print_value(self, value: Any, prefix: str) -> None:
        """
        Print a leaf value with optional sample data.
        
        I truncate long strings because seeing the first few chars is usually
        enough to understand what kind of data it is.
        """
        if not self.show_samples:
            return
        
        if isinstance(value, str):
            truncated = value[:50] + "..." if len(value) > 50 else value
            print(f"{prefix}→ \"{truncated}\"")
        elif value is not None:
            print(f"{prefix}→ {value}")


def load_json_file(filepath: Path) -> Any:
    """
    Load and parse a JSON file.
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        Parsed JSON data
        
    Raises:
        SystemExit: If file doesn't exist or isn't valid JSON
    """
    if not filepath.exists():
        print(f"Error: File '{filepath}' not found", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{filepath}': {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """
    Main entry point for the CLI tool.
    
    Sets up argument parsing and runs the explorer. I wanted to keep the
    interface simple — just point it at a JSON file and go.
    """
    parser = argparse.ArgumentParser(
        description="Explore and visualize JSON file structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example: python json_tree_explorer.py data.json --max-depth 3"
    )
    
    parser.add_argument(
        'filepath',
        type=Path,
        help='Path to the JSON file to explore'
    )
    
    parser.add_argument(
        '--max-depth', '-d',
        type=int,
        default=None,
        help='Maximum depth to traverse (default: unlimited)'
    )
    
    parser.add_argument(
        '--no-samples',
        action='store_true',
        help='Hide sample values for leaf nodes'
    )
    
    args = parser.parse_args()
    
    # Load the JSON data
    data = load_json_file(args.filepath)
    
    # Create explorer and run it
    explorer = JSONTreeExplorer(
        max_depth=args.max_depth,
        show_samples=not args.no_samples
    )
    
    print(f"\nExploring: {args.filepath}")
    print("=" * 60)
    explorer.explore(data)
    print()


if __name__ == "__main__":
    # Demo with sample data to show what this thing can do
    print("=== JSON Tree Explorer Demo ===\n")
    
    # Create a sample nested JSON structure that's realistic
    sample_data = {
        "user": {
            "id": 12345,
            "name": "Mario Rossi",
            "email": "mario@example.com",
            "active": True,
            "metadata": {
                "created_at": "2024-01-15T10:30:00Z",
                "last_login": "2024-01-20T15:45:30Z",
                "preferences": {
                    "theme": "dark",
                    "notifications": True
                }
            }
        },
        "posts": [
            {
                "id": 1,
                "title": "First Post",
                "tags": ["intro", "welcome"],
                "likes": 42
            },
            {
                "id": 2,
                "title": "Second Post",
                "tags": ["update"],
                "likes": 17
            }
        ],
        "stats": {
            "total_posts": 2,
            "total_likes": 59,
            "avg_likes": 29.5
        }
    }
    
    explorer = JSONTreeExplorer(show_samples=True)
    explorer.explore(sample_data)
    
    print("\n" + "=" * 60)
    print("Try it with a real file: python json_tree_explorer.py <file.json>")