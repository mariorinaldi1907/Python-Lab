"""
Date: 2026-06-03
Made a quick CSV statistics tool that figures out column types, computes summary stats, and flags potential data quality issues — useful for exploring new datasets.
"""

#!/usr/bin/env python3
"""
CSV Statistics Analyzer
Analyzes CSV files and provides column-level statistics, type detection, and data quality checks.
"""

import csv
import sys
from collections import defaultdict, Counter
from datetime import datetime
from typing import List, Dict, Any, Optional


class CSVAnalyzer:
    """
    Analyzes CSV files to detect column types and compute statistics.
    
    This was a fun weekend project to explore new datasets quickly without
    spinning up pandas. Helps me spot issues before writing actual ETL code.
    """
    
    def __init__(self, filepath: str, delimiter: str = ','):
        """
        Initialize the analyzer with a CSV file path.
        
        Args:
            filepath: Path to the CSV file
            delimiter: CSV delimiter character (default: comma)
        """
        self.filepath = filepath
        self.delimiter = delimiter
        self.headers = []
        self.rows = []
        self.column_stats = {}
        
    def load_data(self) -> None:
        """Load CSV data into memory for analysis."""
        with open(self.filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=self.delimiter)
            self.headers = next(reader)
            self.rows = list(reader)
    
    def detect_column_type(self, values: List[str]) -> str:
        """
        Detect the most likely data type for a column.
        
        I'm using a simple heuristic here: try parsing as each type in order
        of specificity. Could be smarter but works for most cases.
        
        Args:
            values: List of string values from a column
            
        Returns:
            Detected type as string: 'integer', 'float', 'date', 'boolean', or 'string'
        """
        non_empty = [v for v in values if v.strip()]
        if not non_empty:
            return 'string'
        
        # Check if all values are integers
        try:
            for v in non_empty:
                int(v)
            return 'integer'
        except ValueError:
            pass
        
        # Check if all values are floats
        try:
            for v in non_empty:
                float(v)
            return 'float'
        except ValueError:
            pass
        
        # Check if all values are dates (common formats)
        date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y', '%Y/%m/%d']
        for fmt in date_formats:
            try:
                for v in non_empty:
                    datetime.strptime(v, fmt)
                return 'date'
            except ValueError:
                continue
        
        # Check if boolean-like
        bool_values = {'true', 'false', 'yes', 'no', '1', '0', 't', 'f'}
        if all(v.lower() in bool_values for v in non_empty):
            return 'boolean'
        
        return 'string'
    
    def analyze_column(self, col_idx: int) -> Dict[str, Any]:
        """
        Compute statistics for a single column.
        
        Args:
            col_idx: Index of the column to analyze
            
        Returns:
            Dictionary with column statistics
        """
        values = [row[col_idx] if col_idx < len(row) else '' for row in self.rows]
        non_empty = [v for v in values if v.strip()]
        
        stats = {
            'name': self.headers[col_idx],
            'total_rows': len(values),
            'non_empty': len(non_empty),
            'empty': len(values) - len(non_empty),
            'unique_values': len(set(non_empty)),
            'type': self.detect_column_type(non_empty)
        }
        
        # Add type-specific stats
        if stats['type'] == 'integer':
            nums = [int(v) for v in non_empty]
            stats['min'] = min(nums)
            stats['max'] = max(nums)
            stats['mean'] = sum(nums) / len(nums)
        elif stats['type'] == 'float':
            nums = [float(v) for v in non_empty]
            stats['min'] = min(nums)
            stats['max'] = max(nums)
            stats['mean'] = sum(nums) / len(nums)
        elif stats['type'] == 'string':
            lengths = [len(v) for v in non_empty]
            stats['min_length'] = min(lengths) if lengths else 0
            stats['max_length'] = max(lengths) if lengths else 0
            stats['avg_length'] = sum(lengths) / len(lengths) if lengths else 0
            # Show most common values if cardinality is low
            if stats['unique_values'] <= 10:
                counter = Counter(non_empty)
                stats['top_values'] = counter.most_common(5)
        
        return stats
    
    def analyze(self) -> Dict[int, Dict[str, Any]]:
        """
        Run full analysis on all columns.
        
        Returns:
            Dictionary mapping column index to its statistics
        """
        self.load_data()
        for i in range(len(self.headers)):
            self.column_stats[i] = self.analyze_column(i)
        return self.column_stats
    
    def print_report(self) -> None:
        """Print a human-readable analysis report."""
        print(f"\n{'='*70}")
        print(f"CSV Analysis Report: {self.filepath}")
        print(f"{'='*70}\n")
        print(f"Total Rows: {len(self.rows)}")
        print(f"Total Columns: {len(self.headers)}\n")
        
        for idx, stats in self.column_stats.items():
            print(f"Column {idx + 1}: {stats['name']}")
            print(f"  Type: {stats['type']}")
            print(f"  Non-empty: {stats['non_empty']} ({stats['non_empty']/stats['total_rows']*100:.1f}%)")
            print(f"  Unique values: {stats['unique_values']}")
            
            if stats['type'] in ['integer', 'float']:
                print(f"  Range: {stats['min']} to {stats['max']}")
                print(f"  Mean: {stats['mean']:.2f}")
            elif stats['type'] == 'string':
                print(f"  Length: {stats['min_length']}-{stats['max_length']} chars (avg: {stats['avg_length']:.1f})")
                if 'top_values' in stats:
                    print(f"  Top values: {stats['top_values']}")
            
            print()


if __name__ == "__main__":
    # Create a sample CSV for demo purposes
    sample_csv = "sample_data.csv"
    with open(sample_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['user_id', 'age', 'score', 'signup_date', 'active', 'country'])
        writer.writerows([
            ['1', '25', '87.5', '2023-01-15', 'true', 'USA'],
            ['2', '32', '92.3', '2023-02-20', 'true', 'Canada'],
            ['3', '28', '78.9', '2023-01-22', 'false', 'USA'],
            ['4', '45', '95.1', '2023-03-10', 'true', 'UK'],
            ['5', '22', '', '2023-02-15', 'true', 'USA'],
            ['6', '35', '88.7', '2023-04-01', 'false', 'Canada'],
        ])
    
    print("Running CSV analyzer on sample dataset...")
    analyzer = CSVAnalyzer(sample_csv)
    analyzer.analyze()
    analyzer.print_report()
    
    # Clean up the sample file
    import os
    os.remove(sample_csv)
    print(f"Demo complete! (cleaned up {sample_csv})")