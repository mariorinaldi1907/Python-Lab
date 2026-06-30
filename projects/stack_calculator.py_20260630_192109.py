"""
Date: 2026-06-30
Implemented a reverse polish notation calculator because I wanted to revisit stack-based evaluation and see how clean I could make the error messages.
"""

#!/usr/bin/env python3
"""
A simple Reverse Polish Notation (RPN) calculator.

Supports basic arithmetic operations, variables, and custom functions.
I built this to practice stack-based evaluation and see how ergonomic
I could make the error reporting.
"""

import operator
from typing import Union, Dict, Callable


class RPNCalculator:
    """
    Stack-based calculator that evaluates expressions in Reverse Polish Notation.
    
    Example:
        calc = RPNCalculator()
        result = calc.evaluate("3 4 +")  # Returns 7
        result = calc.evaluate("5 x = x 2 *")  # Returns 10
    """
    
    def __init__(self):
        """Initialize calculator with operations and an empty variable store."""
        # Mapping of operator symbols to their Python functions
        self.operations: Dict[str, Callable] = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '//': operator.floordiv,
            '%': operator.mod,
            '**': operator.pow,
        }
        # Variable storage for assignments
        self.variables: Dict[str, float] = {}
    
    def evaluate(self, expression: str) -> Union[float, int]:
        """
        Evaluate an RPN expression and return the result.
        
        Args:
            expression: Space-separated RPN expression
            
        Returns:
            The computed result
            
        Raises:
            ValueError: If the expression is malformed
        """
        stack = []
        tokens = expression.split()
        
        for i, token in enumerate(tokens):
            try:
                # Try to parse as a number
                if '.' in token:
                    stack.append(float(token))
                else:
                    stack.append(int(token))
            except ValueError:
                # Not a number, check if it's an operation or variable
                if token in self.operations:
                    # Pop two operands and apply operation
                    if len(stack) < 2:
                        raise ValueError(
                            f"Not enough operands for '{token}' at position {i}"
                        )
                    b = stack.pop()
                    a = stack.pop()
                    result = self.operations[token](a, b)
                    stack.append(result)
                elif token == '=':
                    # Variable assignment: value name =
                    if len(stack) < 2:
                        raise ValueError(
                            f"Assignment needs value and variable name at position {i}"
                        )
                    var_name = stack.pop()
                    value = stack.pop()
                    
                    # Variable name should be a string (we pushed it as-is)
                    if not isinstance(var_name, str):
                        raise ValueError(
                            f"Expected variable name, got {var_name} at position {i}"
                        )
                    
                    self.variables[var_name] = value
                    stack.append(value)  # Push the value back for chaining
                elif token in self.variables:
                    # Load variable value
                    stack.append(self.variables[token])
                else:
                    # Treat as a variable name (string literal for assignment)
                    stack.append(token)
        
        if len(stack) != 1:
            raise ValueError(
                f"Invalid expression: stack has {len(stack)} items, expected 1"
            )
        
        return stack[0]
    
    def reset(self):
        """Clear all stored variables."""
        self.variables.clear()


def demo():
    """Run a demo showing various calculator capabilities."""
    calc = RPNCalculator()
    
    test_cases = [
        ("3 4 +", "Simple addition"),
        ("10 5 -", "Subtraction"),
        ("6 7 *", "Multiplication"),
        ("15 3 /", "Division"),
        ("2 3 **", "Exponentiation"),
        ("5 2 + 3 *", "Multiple operations: (5+2)*3"),
        ("100 25 - 5 / 3 +", "Complex: (100-25)/5+3"),
        ("5 x = x x *", "Variable assignment and reuse"),
        ("10 y = 5 z = y z +", "Multiple variables"),
    ]
    
    print("=== RPN Calculator Demo ===\n")
    
    for expression, description in test_cases:
        try:
            result = calc.evaluate(expression)
            print(f"{description}")
            print(f"  Expression: {expression}")
            print(f"  Result: {result}")
            print()
        except Exception as e:
            print(f"{description}")
            print(f"  Expression: {expression}")
            print(f"  ERROR: {e}")
            print()
    
    # Show current variables
    if calc.variables:
        print("Stored variables:")
        for name, value in calc.variables.items():
            print(f"  {name} = {value}")
        print()
    
    # Test error handling
    print("=== Error Handling Demo ===\n")
    
    error_cases = [
        "5 +",  # Not enough operands
        "1 2 3",  # Too many values on stack
        "5 0 /",  # Division by zero
    ]
    
    for expression in error_cases:
        try:
            result = calc.evaluate(expression)
            print(f"Expression: {expression}")
            print(f"Result: {result}\n")
        except Exception as e:
            print(f"Expression: {expression}")
            print(f"Caught error: {e}\n")


if __name__ == "__main__":
    demo()