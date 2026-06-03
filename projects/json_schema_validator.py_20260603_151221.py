"""
Date: 2026-06-03
Implemented a custom JSON schema validator that checks types, required fields, and constraints without external dependencies — wanted to understand how validation libraries work under the hood.
"""

#!/usr/bin/env python3
"""
A simple JSON schema validator that I built to understand validation logic.
Supports type checking, required fields, min/max constraints, and nested objects.
"""

import json
from typing import Any, Dict, List, Optional


class ValidationError(Exception):
    """Custom exception for validation failures."""
    pass


class JSONSchemaValidator:
    """
    A basic JSON schema validator that checks data against a schema definition.
    
    Schema format example:
    {
        "type": "object",
        "properties": {
            "name": {"type": "string", "required": True},
            "age": {"type": "number", "min": 0, "max": 150}
        }
    }
    """
    
    # Map schema types to Python types - had to think through all the edge cases here
    TYPE_MAP = {
        "string": str,
        "number": (int, float),
        "integer": int,
        "boolean": bool,
        "array": list,
        "object": dict,
        "null": type(None)
    }
    
    def __init__(self, schema: Dict[str, Any]):
        """Initialize validator with a schema definition."""
        self.schema = schema
    
    def validate(self, data: Any, schema: Optional[Dict[str, Any]] = None) -> bool:
        """
        Validate data against the schema.
        Returns True if valid, raises ValidationError otherwise.
        
        I made this recursive so nested objects just work naturally.
        """
        if schema is None:
            schema = self.schema
        
        schema_type = schema.get("type")
        
        # Check if type matches - this is the core validation
        if schema_type and not self._check_type(data, schema_type):
            raise ValidationError(
                f"Type mismatch: expected {schema_type}, got {type(data).__name__}"
            )
        
        # Dispatch to specific validators based on type
        if schema_type == "object":
            self._validate_object(data, schema)
        elif schema_type == "array":
            self._validate_array(data, schema)
        elif schema_type in ("number", "integer"):
            self._validate_number(data, schema)
        elif schema_type == "string":
            self._validate_string(data, schema)
        
        return True
    
    def _check_type(self, data: Any, schema_type: str) -> bool:
        """Check if data matches the schema type."""
        expected_type = self.TYPE_MAP.get(schema_type)
        if expected_type is None:
            raise ValidationError(f"Unknown schema type: {schema_type}")
        return isinstance(data, expected_type)
    
    def _validate_object(self, data: Dict[str, Any], schema: Dict[str, Any]) -> None:
        """Validate object properties and check required fields."""
        properties = schema.get("properties", {})
        
        # Check required fields first - this was important for user-facing errors
        for prop_name, prop_schema in properties.items():
            if prop_schema.get("required", False) and prop_name not in data:
                raise ValidationError(f"Required field missing: {prop_name}")
        
        # Validate each property that exists in the data
        for key, value in data.items():
            if key in properties:
                # Recursive call here handles nested objects elegantly
                self.validate(value, properties[key])
    
    def _validate_array(self, data: List[Any], schema: Dict[str, Any]) -> None:
        """Validate array items and length constraints."""
        min_items = schema.get("minItems")
        max_items = schema.get("maxItems")
        
        if min_items is not None and len(data) < min_items:
            raise ValidationError(f"Array too short: minimum {min_items} items required")
        
        if max_items is not None and len(data) > max_items:
            raise ValidationError(f"Array too long: maximum {max_items} items allowed")
        
        # If items schema is provided, validate each item
        items_schema = schema.get("items")
        if items_schema:
            for i, item in enumerate(data):
                try:
                    self.validate(item, items_schema)
                except ValidationError as e:
                    raise ValidationError(f"Array item {i} invalid: {str(e)}")
    
    def _validate_number(self, data: float, schema: Dict[str, Any]) -> None:
        """Validate numeric constraints like min/max."""
        minimum = schema.get("min")
        maximum = schema.get("max")
        
        if minimum is not None and data < minimum:
            raise ValidationError(f"Value {data} below minimum {minimum}")
        
        if maximum is not None and data > maximum:
            raise ValidationError(f"Value {data} above maximum {maximum}")
    
    def _validate_string(self, data: str, schema: Dict[str, Any]) -> None:
        """Validate string constraints like length."""
        min_length = schema.get("minLength")
        max_length = schema.get("maxLength")
        
        if min_length is not None and len(data) < min_length:
            raise ValidationError(f"String too short: minimum {min_length} characters")
        
        if max_length is not None and len(data) > max_length:
            raise ValidationError(f"String too long: maximum {max_length} characters")


if __name__ == "__main__":
    # Test schema for a user profile - based on a real API I worked with
    user_schema = {
        "type": "object",
        "properties": {
            "username": {"type": "string", "required": True, "minLength": 3},
            "email": {"type": "string", "required": True},
            "age": {"type": "integer", "min": 0, "max": 150},
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "maxItems": 10
            },
            "settings": {
                "type": "object",
                "properties": {
                    "notifications": {"type": "boolean"}
                }
            }
        }
    }
    
    validator = JSONSchemaValidator(user_schema)
    
    print("=== JSON Schema Validator Demo ===\n")
    
    # Valid data - should pass
    valid_user = {
        "username": "mario_dev",
        "email": "mario@example.com",
        "age": 28,
        "tags": ["python", "javascript"],
        "settings": {"notifications": True}
    }
    
    print("Testing VALID user data:")
    print(json.dumps(valid_user, indent=2))
    try:
        validator.validate(valid_user)
        print("✓ Validation passed!\n")
    except ValidationError as e:
        print(f"✗ Validation failed: {e}\n")
    
    # Invalid data - missing required field
    invalid_user_1 = {
        "email": "test@example.com",
        "age": 25
    }
    
    print("Testing INVALID user data (missing username):")
    print(json.dumps(invalid_user_1, indent=2))
    try:
        validator.validate(invalid_user_1)
        print("✓ Validation passed!\n")
    except ValidationError as e:
        print(f"✗ Validation failed: {e}\n")
    
    # Invalid data - age out of range
    invalid_user_2 = {
        "username": "bob",
        "email": "bob@example.com",
        "age": 200
    }
    
    print("Testing INVALID user data (age out of range):")
    print(json.dumps(invalid_user_2, indent=2))
    try:
        validator.validate(invalid_user_2)
        print("✓ Validation passed!\n")
    except ValidationError as e:
        print(f"✗ Validation failed: {e}\n")