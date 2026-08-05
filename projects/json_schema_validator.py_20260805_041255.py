"""
Date: 2026-08-05
Implemented a JSON schema validator from scratch to better understand how tools like jsonschema work under the hood — supports type checking, required fields, and nested validation.
"""

#!/usr/bin/env python3
"""
JSON Schema Validator

A lightweight JSON schema validator that supports basic validation rules
without external dependencies. Handles type checking, required fields,
nested objects, and arrays.
"""

import json
from typing import Any, Dict, List, Optional


class ValidationError(Exception):
    """Raised when JSON data doesn't match the schema."""
    pass


class JSONSchemaValidator:
    """
    Validates JSON data against a simple schema format.
    
    Schema format supports:
    - type: str, int, float, bool, list, dict, null
    - required: list of required field names (for objects)
    - properties: nested schema for object properties
    - items: schema for array elements
    """
    
    # Map schema type names to Python types
    TYPE_MAP = {
        'string': str,
        'integer': int,
        'number': (int, float),
        'boolean': bool,
        'array': list,
        'object': dict,
        'null': type(None)
    }
    
    def __init__(self, schema: Dict[str, Any]):
        """
        Initialize validator with a schema.
        
        Args:
            schema: Dictionary defining the expected structure
        """
        self.schema = schema
        self.errors = []
    
    def validate(self, data: Any, schema: Optional[Dict] = None, path: str = "root") -> bool:
        """
        Recursively validate data against schema.
        
        Args:
            data: The JSON data to validate
            schema: Schema to validate against (uses self.schema if None)
            path: Current path in data structure (for error messages)
            
        Returns:
            True if valid, False otherwise (check self.errors for details)
        """
        if schema is None:
            schema = self.schema
            self.errors = []  # Reset errors on top-level call
        
        # Check type if specified
        if 'type' in schema:
            if not self._check_type(data, schema['type'], path):
                return False
        
        # Handle object validation
        if isinstance(data, dict) and schema.get('type') == 'object':
            if not self._validate_object(data, schema, path):
                return False
        
        # Handle array validation
        elif isinstance(data, list) and schema.get('type') == 'array':
            if not self._validate_array(data, schema, path):
                return False
        
        return len(self.errors) == 0
    
    def _check_type(self, data: Any, expected_type: str, path: str) -> bool:
        """Check if data matches expected type."""
        if expected_type not in self.TYPE_MAP:
            self.errors.append(f"{path}: Unknown type '{expected_type}' in schema")
            return False
        
        expected_python_type = self.TYPE_MAP[expected_type]
        if not isinstance(data, expected_python_type):
            actual_type = type(data).__name__
            self.errors.append(f"{path}: Expected {expected_type}, got {actual_type}")
            return False
        
        return True
    
    def _validate_object(self, data: Dict, schema: Dict, path: str) -> bool:
        """Validate object properties and required fields."""
        valid = True
        
        # Check required fields
        required = schema.get('required', [])
        for field in required:
            if field not in data:
                self.errors.append(f"{path}: Missing required field '{field}'")
                valid = False
        
        # Validate properties that exist in both schema and data
        properties = schema.get('properties', {})
        for key, value in data.items():
            if key in properties:
                # Recursively validate nested structure
                field_path = f"{path}.{key}"
                if not self.validate(value, properties[key], field_path):
                    valid = False
        
        return valid
    
    def _validate_array(self, data: List, schema: Dict, path: str) -> bool:
        """Validate array items if items schema is provided."""
        valid = True
        
        # If there's an items schema, validate each element
        if 'items' in schema:
            items_schema = schema['items']
            for idx, item in enumerate(data):
                item_path = f"{path}[{idx}]"
                if not self.validate(item, items_schema, item_path):
                    valid = False
        
        return valid


def demo_user_validation():
    """Demonstrate validating user data with nested structure."""
    
    # Schema for a user profile with nested address
    user_schema = {
        'type': 'object',
        'required': ['name', 'email', 'age'],
        'properties': {
            'name': {'type': 'string'},
            'email': {'type': 'string'},
            'age': {'type': 'integer'},
            'address': {
                'type': 'object',
                'required': ['city', 'country'],
                'properties': {
                    'street': {'type': 'string'},
                    'city': {'type': 'string'},
                    'country': {'type': 'string'},
                    'zip': {'type': 'string'}
                }
            },
            'hobbies': {
                'type': 'array',
                'items': {'type': 'string'}
            }
        }
    }
    
    validator = JSONSchemaValidator(user_schema)
    
    # Valid user data
    valid_user = {
        'name': 'Mario',
        'email': 'mario@example.com',
        'age': 28,
        'address': {
            'street': '123 Main St',
            'city': 'San Francisco',
            'country': 'USA',
            'zip': '94102'
        },
        'hobbies': ['coding', 'hiking', 'photography']
    }
    
    print("=== Validating VALID user data ===")
    if validator.validate(valid_user):
        print("✓ Validation passed!")
    else:
        print("✗ Validation failed:")
        for error in validator.errors:
            print(f"  - {error}")
    
    # Invalid user data (multiple errors)
    invalid_user = {
        'name': 'Jane',
        'email': 'jane@example.com',
        # missing 'age' (required)
        'address': {
            'street': '456 Oak Ave',
            # missing 'city' and 'country' (required)
            'zip': 12345  # wrong type, should be string
        },
        'hobbies': ['reading', 42, 'gaming']  # contains integer instead of strings
    }
    
    print("\n=== Validating INVALID user data ===")
    if validator.validate(invalid_user):
        print("✓ Validation passed!")
    else:
        print("✗ Validation failed with errors:")
        for error in validator.errors:
            print(f"  - {error}")


if __name__ == "__main__":
    demo_user_validation()