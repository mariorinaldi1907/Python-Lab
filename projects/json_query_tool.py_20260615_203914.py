"""
Date: 2026-06-15
Created a CLI tool to extract and filter JSON data using dot notation paths, with optional pretty printing and value filtering.
"""

#!/usr/bin/env python3
"""
JSON Query Tool - Extract values from JSON files using dot notation paths.

I built this because I was constantly grepping through JSON responses and
thought, why not make something that handles nested structures cleanly?
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, List, Optional


def load_json_file(filepath: str) -> Any:
    """
    Load and parse a JSON file.
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        Parsed JSON data (dict, list, or primitive)
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file isn't valid JSON
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def query_json(data: Any, path: str) -> Any:
    """
    Extract value from JSON data using dot notation path.
    
    Supports:
    - Nested objects: "user.profile.name"
    - Array indexing: "items[0].id"
    - Mixed: "data.users[2].email"
    
    Args:
        data: The JSON data structure to query
        path: Dot-notation path (e.g., "foo.bar[0].baz")
        
    Returns:
        The value at the specified path, or None if not found
    """
    if not path:
        return data
    
    # Split path into tokens, handling both dots and brackets
    tokens = []
    current_token = ""
    
    for char in path:
        if char == '.':
            if current_token:
                tokens.append(current_token)
                current_token = ""
        elif char == '[':
            if current_token:
                tokens.append(current_token)
                current_token = ""
        elif char == ']':
            if current_token:
                # This is an array index
                tokens.append(int(current_token))
                current_token = ""
        else:
            current_token += char
    
    if current_token:
        tokens.append(current_token)
    
    # Traverse the data structure
    result = data
    for token in tokens:
        try:
            if isinstance(token, int):
                # Array index
                result = result[token]
            elif isinstance(result, dict):
                result = result.get(token)
            elif isinstance(result, list):
                # Try to map over list items if it's an object key
                result = [item.get(token) if isinstance(item, dict) else None 
                         for item in result]
            else:
                return None
            
            if result is None:
                return None
        except (KeyError, IndexError, TypeError):
            return None
    
    return result


def filter_results(data: Any, filter_value: Optional[str]) -> Any:
    """
    Filter results to only include items matching a specific value.
    
    Useful when querying returns a list and you want specific entries.
    
    Args:
        data: The data to filter (can be list or single value)
        filter_value: The value to match against
        
    Returns:
        Filtered data (list or single value)
    """
    if filter_value is None:
        return data
    
    if isinstance(data, list):
        return [item for item in data if str(item) == filter_value]
    
    return data if str(data) == filter_value else None


def format_output(data: Any, pretty: bool = False) -> str:
    """
    Format data for output, either compact or pretty-printed.
    
    Args:
        data: The data to format
        pretty: Whether to use pretty printing with indentation
        
    Returns:
        Formatted JSON string
    """
    if pretty:
        return json.dumps(data, indent=2, ensure_ascii=False)
    return json.dumps(data, ensure_ascii=False)


def main():
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        description="Query JSON files using dot notation paths (like jq but simpler)",
        epilog="Example: %(prog)s data.json 'users[0].email' --pretty"
    )
    
    parser.add_argument(
        'file',
        help='JSON file to query'
    )
    
    parser.add_argument(
        'path',
        nargs='?',
        default='',
        help='Dot notation path (e.g., "foo.bar[0].baz"). Omit to print entire file.'
    )
    
    parser.add_argument(
        '-p', '--pretty',
        action='store_true',
        help='Pretty print the output with indentation'
    )
    
    parser.add_argument(
        '-f', '--filter',
        metavar='VALUE',
        help='Filter results to only show items matching this value'
    )
    
    args = parser.parse_args()
    
    try:
        # Load the JSON file
        data = load_json_file(args.file)
        
        # Query the path
        result = query_json(data, args.path)
        
        # Apply filter if specified
        if args.filter:
            result = filter_results(result, args.filter)
        
        # Output the result
        if result is None:
            print("null")
        else:
            print(format_output(result, args.pretty))
        
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    # Demo: Create a sample JSON file and query it
    print("=== JSON Query Tool Demo ===\n")
    
    # Create sample data
    sample_data = {
        "users": [
            {"id": 1, "name": "Alice", "email": "alice@example.com", "active": True},
            {"id": 2, "name": "Bob", "email": "bob@example.com", "active": False},
            {"id": 3, "name": "Charlie", "email": "charlie@example.com", "active": True}
        ],
        "metadata": {
            "total": 3,
            "version": "1.0",
            "nested": {
                "deep": {
                    "value": "found it!"
                }
            }
        }
    }
    
    print("Sample JSON structure:")
    print(format_output(sample_data, pretty=True))
    print("\n" + "="*50 + "\n")
    
    # Demo various queries
    print("Query: 'users[0].name'")
    print(f"Result: {query_json(sample_data, 'users[0].name')}\n")
    
    print("Query: 'users[1].email'")
    print(f"Result: {query_json(sample_data, 'users[1].email')}\n")
    
    print("Query: 'metadata.nested.deep.value'")
    print(f"Result: {query_json(sample_data, 'metadata.nested.deep.value')}\n")
    
    print("Query: 'users.name' (maps over array)")
    result = query_json(sample_data, 'users.name')
    print(f"Result: {format_output(result)}\n")
    
    print("Query: 'metadata.total'")
    print(f"Result: {query_json(sample_data, 'metadata.total')}\n")
    
    print("="*50)
    print("\nTo use with actual files, run:")
    print("  python json_query_tool.py <file.json> <path> [--pretty]")