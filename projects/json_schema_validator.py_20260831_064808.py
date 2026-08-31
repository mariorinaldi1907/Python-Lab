"""
Date: 2026-08-31
Created a JSON schema validator from scratch to validate API responses and config files in my projects without pulling in heavy libraries.
"""

#!/usr/bin/env python3
"""
Lightweight JSON schema validator using only the standard library.
Supports type checking, required fields, nested objects, and arrays.
"""

import json
from typing import Any, Dict, List, Union


class ValidationError(Exception):
    """Raised when JSON data doesn't match the schema."""
    pass


class JSONSchemaValidator:
    """
    Validates JSON data against a simple schema definition.
    
    Schema format:
    {
        "type": "object",
        "properties": {
            "field_name": {
                "type": "string|number|boolean|array|object|null",
                "required": True/False,
                "items": {...}  # for arrays
                "properties": {...}  # for nested objects
            }
        }
    }
    """
    
    # Map JSON schema types to Python types
    TYPE_MAP = {
        "string": str,
        "number": (int, float),
        "boolean": bool,
        "array": list,
        "object": dict,
        "null": type(None)
    }
    
    def __init__(self, schema: Dict[str, Any]):
        """Initialize validator with a schema definition."""
        self.schema = schema
    
    def validate(self, data: Any, schema: Dict[str, Any] = None, path: str = "root") -> bool:
        """
        Validate data against the schema.
        
        Args:
            data: The JSON data to validate
            schema: Schema to validate against (uses self.schema if None)
            path: Current path in the data tree (for error messages)
        
        Returns:
            True if valid
        
        Raises:
            ValidationError: If validation fails
        """
        if schema is None:
            schema = self.schema
        
        expected_type = schema.get("type")
        
        if expected_type not in self.TYPE_MAP:
            raise ValidationError(f"Unknown type '{expected_type}' in schema at {path}")
        
        # Check type
        python_type = self.TYPE_MAP[expected_type]
        if not isinstance(data, python_type):
            raise ValidationError(
                f"At {path}: expected {expected_type}, got {type(data).__name__}"
            )
        
        # Validate object properties
        if expected_type == "object":
            self._validate_object(data, schema, path)
        
        # Validate array items
        elif expected_type == "array":
            self._validate_array(data, schema, path)
        
        return True
    
    def _validate_object(self, data: Dict, schema: Dict, path: str):
        """Validate object properties and check for required fields."""
        properties = schema.get("properties", {})
        
        # Check each defined property
        for prop_name, prop_schema in properties.items():
            is_required = prop_schema.get("required", False)
            
            if prop_name not in data:
                if is_required:
                    raise ValidationError(f"Missing required field '{prop_name}' at {path}")
                continue
            
            # Recursively validate the property
            new_path = f"{path}.{prop_name}"
            self.validate(data[prop_name], prop_schema, new_path)
        
        # Optionally check for extra fields not in schema
        if schema.get("strict", False):
            extra_fields = set(data.keys()) - set(properties.keys())
            if extra_fields:
                raise ValidationError(f"Unexpected fields {extra_fields} at {path}")
    
    def _validate_array(self, data: List, schema: Dict, path: str):
        """Validate array items against item schema."""
        items_schema = schema.get("items")
        
        if items_schema is None:
            return  # No item validation specified
        
        # Validate each item
        for idx, item in enumerate(data):
            new_path = f"{path}[{idx}]"
            self.validate(item, items_schema, new_path)
    
    def validate_file(self, filepath: str) -> bool:
        """
        Load and validate a JSON file.
        
        Args:
            filepath: Path to JSON file
        
        Returns:
            True if valid
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        return self.validate(data)


def create_user_schema() -> Dict[str, Any]:
    """Example schema for a user object with nested address."""
    return {
        "type": "object",
        "properties": {
            "id": {
                "type": "number",
                "required": True
            },
            "username": {
                "type": "string",
                "required": True
            },
            "email": {
                "type": "string",
                "required": True
            },
            "active": {
                "type": "boolean",
                "required": False
            },
            "address": {
                "type": "object",
                "required": False,
                "properties": {
                    "street": {"type": "string", "required": True},
                    "city": {"type": "string", "required": True},
                    "zipcode": {"type": "string", "required": False}
                }
            },
            "tags": {
                "type": "array",
                "required": False,
                "items": {"type": "string"}
            }
        }
    }


if __name__ == "__main__":
    # Create a schema for user validation
    schema = create_user_schema()
    validator = JSONSchemaValidator(schema)
    
    print("=" * 60)
    print("JSON Schema Validator Demo")
    print("=" * 60)
    
    # Valid user data
    valid_user = {
        "id": 42,
        "username": "mario_dev",
        "email": "mario@example.com",
        "active": True,
        "address": {
            "street": "123 Main St",
            "city": "San Francisco"
        },
        "tags": ["developer", "python", "github"]
    }
    
    print("\n✓ Testing VALID user data:")
    print(json.dumps(valid_user, indent=2))
    try:
        validator.validate(valid_user)
        print("→ Validation PASSED")
    except ValidationError as e:
        print(f"→ Validation FAILED: {e}")
    
    # Invalid user - missing required field
    invalid_user_1 = {
        "id": 43,
        "email": "test@example.com"
        # missing required 'username'
    }
    
    print("\n✗ Testing INVALID user data (missing username):")
    print(json.dumps(invalid_user_1, indent=2))
    try:
        validator.validate(invalid_user_1)
        print("→ Validation PASSED")
    except ValidationError as e:
        print(f"→ Validation FAILED: {e}")
    
    # Invalid user - wrong type
    invalid_user_2 = {
        "id": "not_a_number",  # should be number
        "username": "test_user",
        "email": "test@example.com"
    }
    
    print("\n✗ Testing INVALID user data (wrong type):")
    print(json.dumps(invalid_user_2, indent=2))
    try:
        validator.validate(invalid_user_2)
        print("→ Validation PASSED")
    except ValidationError as e:
        print(f"→ Validation FAILED: {e}")
    
    # Invalid nested object
    invalid_user_3 = {
        "id": 44,
        "username": "nested_fail",
        "email": "nested@example.com",
        "address": {
            "street": "456 Oak Ave"
            # missing required 'city' in nested object
        }
    }
    
    print("\n✗ Testing INVALID user data (missing nested field):")
    print(json.dumps(invalid_user_3, indent=2))
    try:
        validator.validate(invalid_user_3)
        print("→ Validation PASSED")
    except ValidationError as e:
        print(f"→ Validation FAILED: {e}")
    
    print("\n" + "=" * 60)