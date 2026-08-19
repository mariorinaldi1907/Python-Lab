"""
Date: 2026-08-19
Created a pure-Python JSON schema validator because I wanted to validate config files without pulling in jsonschema as a dependency.
"""

#!/usr/bin/env python3
"""
A lightweight JSON schema validator using only the standard library.
Supports basic types, nested objects, arrays, required fields, and enums.
"""

import json
from typing import Any, Dict, List, Union


class ValidationError(Exception):
    """Raised when JSON data doesn't match the schema."""
    pass


class JSONSchemaValidator:
    """
    Validates JSON data against a simplified schema format.
    
    Schema format supports:
    - type: string, number, integer, boolean, object, array, null
    - required: list of required field names (for objects)
    - properties: dict of nested schemas (for objects)
    - items: schema for array elements
    - enum: list of allowed values
    """
    
    def __init__(self, schema: Dict[str, Any]):
        """
        Initialize validator with a schema.
        
        Args:
            schema: Dictionary describing the expected JSON structure
        """
        self.schema = schema
    
    def validate(self, data: Any, schema: Dict[str, Any] = None, path: str = "root") -> bool:
        """
        Validate data against the schema.
        
        Args:
            data: The JSON data to validate
            schema: Schema to validate against (uses self.schema if None)
            path: Current path in the data structure (for error messages)
        
        Returns:
            True if valid
        
        Raises:
            ValidationError: If validation fails
        """
        if schema is None:
            schema = self.schema
        
        # Check enum first if present (works for any type)
        if "enum" in schema:
            if data not in schema["enum"]:
                raise ValidationError(
                    f"{path}: value '{data}' not in allowed values {schema['enum']}"
                )
            return True
        
        # Type validation
        expected_type = schema.get("type")
        if expected_type:
            if not self._check_type(data, expected_type, path):
                return False
        
        # Type-specific validation
        if expected_type == "object":
            self._validate_object(data, schema, path)
        elif expected_type == "array":
            self._validate_array(data, schema, path)
        
        return True
    
    def _check_type(self, data: Any, expected_type: str, path: str) -> bool:
        """Check if data matches the expected type."""
        type_map = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "null": type(None),
            "object": dict,
            "array": list,
        }
        
        if expected_type not in type_map:
            raise ValidationError(f"{path}: unknown type '{expected_type}'")
        
        expected_python_type = type_map[expected_type]
        
        # Special case: integers are numbers, but not all numbers are integers
        if expected_type == "number" and isinstance(data, bool):
            raise ValidationError(f"{path}: expected number, got boolean")
        
        if not isinstance(data, expected_python_type):
            actual_type = type(data).__name__
            raise ValidationError(
                f"{path}: expected {expected_type}, got {actual_type}"
            )
        
        return True
    
    def _validate_object(self, data: Dict, schema: Dict, path: str):
        """Validate object properties and required fields."""
        # Check required fields
        required = schema.get("required", [])
        for field in required:
            if field not in data:
                raise ValidationError(f"{path}: missing required field '{field}'")
        
        # Validate properties if schema defines them
        properties = schema.get("properties", {})
        for key, value in data.items():
            if key in properties:
                self.validate(value, properties[key], f"{path}.{key}")
    
    def _validate_array(self, data: List, schema: Dict, path: str):
        """Validate array items against the items schema."""
        items_schema = schema.get("items")
        if items_schema:
            for i, item in enumerate(data):
                self.validate(item, items_schema, f"{path}[{i}]")


def load_and_validate(json_file: str, schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load a JSON file and validate it against a schema.
    
    Args:
        json_file: Path to JSON file
        schema: Schema to validate against
    
    Returns:
        Parsed JSON data if valid
    
    Raises:
        ValidationError: If validation fails
    """
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    validator = JSONSchemaValidator(schema)
    validator.validate(data)
    
    return data


if __name__ == "__main__":
    # Demo: validate a user configuration
    print("=== JSON Schema Validator Demo ===\n")
    
    # Define a schema for a user profile config
    user_schema = {
        "type": "object",
        "required": ["username", "email", "age"],
        "properties": {
            "username": {"type": "string"},
            "email": {"type": "string"},
            "age": {"type": "integer"},
            "role": {"type": "string", "enum": ["admin", "user", "guest"]},
            "settings": {
                "type": "object",
                "properties": {
                    "theme": {"type": "string"},
                    "notifications": {"type": "boolean"}
                }
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"}
            }
        }
    }
    
    validator = JSONSchemaValidator(user_schema)
    
    # Test case 1: Valid data
    valid_user = {
        "username": "mario_dev",
        "email": "mario@example.com",
        "age": 28,
        "role": "admin",
        "settings": {
            "theme": "dark",
            "notifications": True
        },
        "tags": ["python", "rust", "vim"]
    }
    
    print("Test 1: Valid user data")
    try:
        validator.validate(valid_user)
        print("✓ Validation passed!\n")
    except ValidationError as e:
        print(f"✗ Validation failed: {e}\n")
    
    # Test case 2: Missing required field
    invalid_user = {
        "username": "mario_dev",
        "age": 28
    }
    
    print("Test 2: Missing required 'email' field")
    try:
        validator.validate(invalid_user)
        print("✓ Validation passed!\n")
    except ValidationError as e:
        print(f"✗ Validation failed: {e}\n")
    
    # Test case 3: Wrong type
    wrong_type_user = {
        "username": "mario_dev",
        "email": "mario@example.com",
        "age": "twenty-eight"  # Should be integer
    }
    
    print("Test 3: Wrong type for 'age' (string instead of integer)")
    try:
        validator.validate(wrong_type_user)
        print("✓ Validation passed!\n")
    except ValidationError as e:
        print(f"✗ Validation failed: {e}\n")
    
    # Test case 4: Invalid enum value
    invalid_enum_user = {
        "username": "mario_dev",
        "email": "mario@example.com",
        "age": 28,
        "role": "superuser"  # Not in enum
    }
    
    print("Test 4: Invalid enum value for 'role'")
    try:
        validator.validate(invalid_enum_user)
        print("✓ Validation passed!\n")
    except ValidationError as e:
        print(f"✗ Validation failed: {e}\n")