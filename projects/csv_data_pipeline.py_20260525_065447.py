# A little ETL tool I made that reads CSV data, validates it against a schema, cleans it up, and writes the results to a new file.
# written: 2026-05-25

#!/usr/bin/env python3
"""
Simple ETL pipeline for CSV data with schema validation and transformations.
Reads data, validates types, applies cleaning rules, and outputs clean CSV.
"""

import csv
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Callable


class SchemaValidator:
    """Validates data rows against a defined schema with type checking."""
    
    def __init__(self, schema: Dict[str, str]):
        """
        Initialize validator with a schema definition.
        
        Args:
            schema: Dict mapping field names to expected types (str, int, float, email, date)
        """
        self.schema = schema
        self.validators = {
            'str': lambda x: str(x),
            'int': lambda x: int(x),
            'float': lambda x: float(x),
            'email': self._validate_email,
            'date': self._validate_date
        }
    
    def _validate_email(self, value: str) -> str:
        """Check if value looks like an email."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, value):
            raise ValueError(f"Invalid email: {value}")
        return value.strip().lower()
    
    def _validate_date(self, value: str) -> str:
        """Parse and validate date string (supports YYYY-MM-DD)."""
        try:
            datetime.strptime(value, '%Y-%m-%d')
            return value
        except ValueError:
            raise ValueError(f"Invalid date format: {value}")
    
    def validate_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """
        Validate a single row against the schema.
        
        Args:
            row: Dictionary representing one data row
            
        Returns:
            Validated and type-converted row
        """
        validated = {}
        for field, expected_type in self.schema.items():
            if field not in row:
                raise ValueError(f"Missing required field: {field}")
            
            validator = self.validators.get(expected_type)
            if not validator:
                raise ValueError(f"Unknown type: {expected_type}")
            
            try:
                validated[field] = validator(row[field])
            except (ValueError, TypeError) as e:
                raise ValueError(f"Field '{field}' validation failed: {e}")
        
        return validated


class DataTransformer:
    """Applies transformation rules to clean and standardize data."""
    
    def __init__(self):
        """Initialize transformer with default rules."""
        self.transforms: List[Callable] = []
    
    def add_transform(self, func: Callable) -> None:
        """Add a transformation function to the pipeline."""
        self.transforms.append(func)
    
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply all transformation rules to the dataset.
        
        Args:
            data: List of data rows
            
        Returns:
            Transformed data
        """
        result = data
        for transform_func in self.transforms:
            result = [transform_func(row) for row in result]
        return result


class ETLPipeline:
    """Main ETL pipeline orchestrator."""
    
    def __init__(self, schema: Dict[str, str]):
        """
        Initialize the pipeline with a schema.
        
        Args:
            schema: Schema definition for validation
        """
        self.validator = SchemaValidator(schema)
        self.transformer = DataTransformer()
        self.errors = []
    
    def extract(self, filepath: str) -> List[Dict[str, str]]:
        """Read data from CSV file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    
    def load(self, data: List[Dict[str, Any]], filepath: str) -> None:
        """Write cleaned data to CSV file."""
        if not data:
            print("No data to write!")
            return
        
        fieldnames = list(data[0].keys())
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    
    def run(self, input_file: str, output_file: str) -> int:
        """
        Execute the full ETL pipeline.
        
        Returns:
            Number of successfully processed rows
        """
        print(f"Starting ETL pipeline...")
        print(f"Extracting from: {input_file}")
        
        # Extract
        raw_data = self.extract(input_file)
        print(f"Extracted {len(raw_data)} rows")
        
        # Validate and clean
        validated_data = []
        for i, row in enumerate(raw_data, 1):
            try:
                validated_row = self.validator.validate_row(row)
                validated_data.append(validated_row)
            except ValueError as e:
                self.errors.append(f"Row {i}: {e}")
        
        print(f"Validated {len(validated_data)} rows ({len(self.errors)} errors)")
        
        # Transform
        transformed_data = self.transformer.transform(validated_data)
        print(f"Applied {len(self.transformer.transforms)} transformations")
        
        # Load
        self.load(transformed_data, output_file)
        print(f"Loaded data to: {output_file}")
        
        return len(transformed_data)


if __name__ == "__main__":
    # Demo: create sample data and run the pipeline
    import tempfile
    import os
    
    # Create sample input CSV
    sample_data = """name,email,age,join_date
Mario Rossi,MARIO@example.com,25,2023-01-15
Luigi Verdi,luigi@test.com,30,2023-02-20
Anna Bianchi,anna.bianchi@email.com,28,2023-03-10
Bad Row,invalid-email,not_a_number,2023-04-01
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(sample_data)
        input_file = f.name
    
    output_file = tempfile.mktemp(suffix='_clean.csv')
    
    # Define schema
    schema = {
        'name': 'str',
        'email': 'email',
        'age': 'int',
        'join_date': 'date'
    }
    
    # Create and configure pipeline
    pipeline = ETLPipeline(schema)
    
    # Add custom transformation: capitalize names
    def capitalize_name(row):
        row['name'] = row['name'].title()
        return row
    
    pipeline.transformer.add_transform(capitalize_name)
    
    # Run the pipeline
    try:
        processed = pipeline.run(input_file, output_file)
        
        print(f"\nPipeline completed!")
        print(f"Processed: {processed} rows")
        
        if pipeline.errors:
            print(f"\nErrors encountered:")
            for error in pipeline.errors:
                print(f"  - {error}")
        
        print(f"\nCleaned data preview:")
        with open(output_file, 'r') as f:
            print(f.read())
        
    finally:
        # Cleanup temp files
        os.unlink(input_file)
        if os.path.exists(output_file):
            os.unlink(output_file)