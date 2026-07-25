"""
Date: 2026-07-25
Implemented a stack-based RPN calculator that supports basic math ops and is easy to extend with new operators — handles edge cases like division by zero.
"""

#!/usr/bin/env python3
"""
RPN (Reverse Polish Notation) Calculator

A simple stack-based calculator that evaluates expressions in postfix notation.
Example: "3 4 +" evaluates to 7, "5 1 2 + 4 * + 3 -" evaluates to 14
"""

import operator
from typing import List, Callable, Union


class RPNCalculator:
    """
    Stack-based calculator for evaluating RPN expressions.
    
    Supports basic arithmetic operators and is designed to be easily
    extensible with new operators.
    """
    
    def __init__(self):
        """Initialize the calculator with supported operators."""
        # Using a dict makes it super easy to add new operators later
        self.operators = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '//': operator.floordiv,
            '%': operator.mod,
            '**': operator.pow,
        }
        self.stack: List[float] = []
    
    def _is_number(self, token: str) -> bool:
        """Check if a token is a valid number (int or float)."""
        try:
            float(token)
            return True
        except ValueError:
            return False
    
    def _apply_operator(self, op: str) -> None:
        """
        Apply an operator to the top elements of the stack.
        
        Pops two operands, applies the operator, and pushes the result.
        I'm using right-to-left evaluation here because stack pop order matters.
        """
        if len(self.stack) < 2:
            raise ValueError(f"Not enough operands for operator '{op}'")
        
        # Order matters: for "5 3 -", we want 5 - 3, not 3 - 5
        right = self.stack.pop()
        left = self.stack.pop()
        
        try:
            result = self.operators[op](left, right)
            self.stack.append(result)
        except ZeroDivisionError:
            raise ValueError(f"Division by zero: {left} {op} {right}")
    
    def evaluate(self, expression: str) -> float:
        """
        Evaluate an RPN expression and return the result.
        
        Args:
            expression: Space-separated RPN expression (e.g., "3 4 + 2 *")
        
        Returns:
            The computed result as a float
        
        Raises:
            ValueError: If the expression is malformed or invalid
        """
        self.stack.clear()
        tokens = expression.split()
        
        if not tokens:
            raise ValueError("Empty expression")
        
        for token in tokens:
            if self._is_number(token):
                # Convert to float to handle both ints and decimals
                self.stack.append(float(token))
            elif token in self.operators:
                self._apply_operator(token)
            else:
                raise ValueError(f"Unknown operator or invalid token: '{token}'")
        
        # After processing all tokens, we should have exactly one value left
        if len(self.stack) != 1:
            raise ValueError(
                f"Malformed expression: stack has {len(self.stack)} values "
                f"instead of 1. Leftover: {self.stack}"
            )
        
        return self.stack[0]
    
    def add_operator(self, symbol: str, func: Callable[[float, float], float]) -> None:
        """
        Add a custom operator to the calculator.
        
        Args:
            symbol: The operator symbol (e.g., "^")
            func: A function that takes two floats and returns a float
        """
        self.operators[symbol] = func


def run_demo():
    """Run a demo showing various RPN calculator capabilities."""
    calc = RPNCalculator()
    
    # Test cases with expected results
    test_cases = [
        ("3 4 +", 7.0),
        ("5 1 2 + 4 * + 3 -", 14.0),  # 5 + ((1 + 2) * 4) - 3
        ("15 7 1 1 + - / 3 * 2 1 1 + + -", 5.0),  # Classic RPN example
        ("10 2 /", 5.0),
        ("2 3 **", 8.0),  # Exponentiation
        ("10 3 %", 1.0),  # Modulo
        ("5.5 2.5 +", 8.0),  # Floats work too
    ]
    
    print("RPN Calculator Demo")
    print("=" * 60)
    
    for expression, expected in test_cases:
        try:
            result = calc.evaluate(expression)
            status = "✓" if abs(result - expected) < 0.0001 else "✗"
            print(f"{status} '{expression}' = {result}")
        except ValueError as e:
            print(f"✗ '{expression}' -> ERROR: {e}")
    
    # Test error cases
    print("\nError Handling:")
    print("-" * 60)
    
    error_cases = [
        "3 4",  # Too many operands
        "3 +",  # Not enough operands
        "5 0 /",  # Division by zero
        "3 4 @",  # Unknown operator
        "",  # Empty expression
    ]
    
    for expression in error_cases:
        try:
            result = calc.evaluate(expression)
            print(f"✗ '{expression}' should have raised an error but got {result}")
        except ValueError as e:
            print(f"✓ '{expression}' -> Caught: {e}")
    
    # Demonstrate custom operator
    print("\nCustom Operator (max):")
    print("-" * 60)
    calc.add_operator("max", lambda a, b: max(a, b))
    result = calc.evaluate("5 10 max 3 +")
    print(f"'5 10 max 3 +' = {result}  (max(5, 10) + 3)")


if __name__ == "__main__":
    run_demo()