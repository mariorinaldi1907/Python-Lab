"""
Date: 2026-06-17
Created a reverse polish notation calculator that tokenizes input, validates syntax, and evaluates expressions using a stack-based approach.
"""

#!/usr/bin/env python3
"""
RPN (Reverse Polish Notation) Calculator
Supports basic arithmetic operations plus power and modulo.
Example: "3 4 + 2 *" evaluates to 14
"""

import re
from typing import List, Union


class RPNCalculator:
    """
    A simple stack-based calculator for evaluating RPN expressions.
    Supports +, -, *, /, %, ** (power), and unary negation.
    """
    
    def __init__(self):
        """Initialize the calculator with supported operations."""
        # Dictionary mapping operators to their functions and required operand count
        self.operators = {
            '+': (lambda a, b: a + b, 2),
            '-': (lambda a, b: a - b, 2),
            '*': (lambda a, b: a * b, 2),
            '/': (lambda a, b: a / b, 2),
            '%': (lambda a, b: a % b, 2),
            '**': (lambda a, b: a ** b, 2),
            'neg': (lambda a: -a, 1),  # unary negation
        }
    
    def tokenize(self, expression: str) -> List[str]:
        """
        Tokenize the input expression into numbers and operators.
        Handles negative numbers and multi-character operators.
        """
        # Split on whitespace but keep everything that's not whitespace
        tokens = expression.split()
        return tokens
    
    def is_number(self, token: str) -> bool:
        """Check if a token represents a valid number (int or float)."""
        try:
            float(token)
            return True
        except ValueError:
            return False
    
    def evaluate(self, expression: str) -> Union[float, int]:
        """
        Evaluate an RPN expression and return the result.
        
        Args:
            expression: A string containing the RPN expression
            
        Returns:
            The numeric result of the evaluation
            
        Raises:
            ValueError: If the expression is invalid or malformed
            ZeroDivisionError: If division by zero is attempted
        """
        tokens = self.tokenize(expression)
        stack = []
        
        for token in tokens:
            if self.is_number(token):
                # Push numbers onto the stack
                # Use int if possible to keep results clean
                num = float(token)
                if num == int(num):
                    stack.append(int(num))
                else:
                    stack.append(num)
            elif token in self.operators:
                operation, operand_count = self.operators[token]
                
                # Check if we have enough operands on the stack
                if len(stack) < operand_count:
                    raise ValueError(
                        f"Insufficient operands for operator '{token}' "
                        f"(need {operand_count}, have {len(stack)})"
                    )
                
                # Pop the required number of operands
                # Note: for binary ops, we pop in reverse order
                if operand_count == 1:
                    operand = stack.pop()
                    result = operation(operand)
                else:  # operand_count == 2
                    b = stack.pop()
                    a = stack.pop()
                    
                    # Handle division by zero explicitly
                    if token == '/' and b == 0:
                        raise ZeroDivisionError("Division by zero")
                    
                    result = operation(a, b)
                
                # Keep results as ints when possible for cleaner output
                if isinstance(result, float) and result == int(result):
                    result = int(result)
                
                stack.append(result)
            else:
                raise ValueError(f"Unknown token: '{token}'")
        
        # After processing all tokens, stack should have exactly one element
        if len(stack) != 1:
            raise ValueError(
                f"Invalid expression: {len(stack)} values remain on stack "
                f"(expected 1). Stack: {stack}"
            )
        
        return stack[0]


def run_demo():
    """Run a demonstration of the RPN calculator with various examples."""
    calc = RPNCalculator()
    
    # Test cases: (expression, description)
    test_cases = [
        ("3 4 +", "Simple addition: 3 + 4"),
        ("15 7 1 1 + - /", "Complex expression: 15 / (7 - (1 + 1))"),
        ("5 1 2 + 4 * + 3 -", "Multi-step: 5 + ((1 + 2) * 4) - 3"),
        ("2 3 **", "Exponentiation: 2^3"),
        ("10 3 %", "Modulo: 10 % 3"),
        ("100 5 / 2 *", "Chained ops: (100 / 5) * 2"),
        ("-5 3 +", "Negative number: -5 + 3"),
        ("2 3 * 4 5 * +", "Two operations: (2*3) + (4*5)"),
    ]
    
    print("RPN Calculator Demo")
    print("=" * 60)
    
    for expression, description in test_cases:
        try:
            result = calc.evaluate(expression)
            print(f"\n{description}")
            print(f"  Expression: {expression}")
            print(f"  Result: {result}")
        except Exception as e:
            print(f"\n{description}")
            print(f"  Expression: {expression}")
            print(f"  Error: {e}")
    
    # Demonstrate error handling
    print("\n" + "=" * 60)
    print("Error Handling Examples:")
    print("=" * 60)
    
    error_cases = [
        ("5 0 /", "Division by zero"),
        ("3 +", "Insufficient operands"),
        ("1 2 3 +", "Too many operands"),
        ("5 foo *", "Invalid operator"),
    ]
    
    for expression, description in error_cases:
        try:
            result = calc.evaluate(expression)
            print(f"\n{description}: {expression} = {result}")
        except Exception as e:
            print(f"\n{description}: {expression}")
            print(f"  Caught: {type(e).__name__}: {e}")


if __name__ == "__main__":
    run_demo()