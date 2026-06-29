"""
Date: 2026-06-29
Wrote a reverse Polish notation calculator that evaluates postfix expressions using a stack — supports basic arithmetic and some useful functions.
"""

#!/usr/bin/env python3
"""
A simple Reverse Polish Notation (RPN) calculator.
Supports basic arithmetic operations and a few mathematical functions.
"""

import math
import operator
from typing import List, Union


class RPNCalculator:
    """
    Stack-based calculator for evaluating RPN expressions.
    
    In RPN, operators come after operands. For example:
    - "3 4 +" means 3 + 4 = 7
    - "5 1 2 + 4 * + 3 -" means 5 + ((1 + 2) * 4) - 3 = 14
    """
    
    def __init__(self):
        """Initialize the calculator with an empty stack and operator mappings."""
        self.stack: List[float] = []
        
        # Binary operators that take two arguments
        self.binary_ops = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '//': operator.floordiv,
            '%': operator.mod,
            '**': operator.pow,
            '^': operator.pow,  # alternative syntax for power
        }
        
        # Unary operators that take one argument
        self.unary_ops = {
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'ln': math.log,
            'log': math.log10,
            'abs': abs,
            'neg': operator.neg,
        }
    
    def push(self, value: float) -> None:
        """Push a numeric value onto the stack."""
        self.stack.append(float(value))
    
    def pop(self) -> float:
        """
        Pop and return the top value from the stack.
        
        Raises:
            IndexError: If the stack is empty.
        """
        if not self.stack:
            raise IndexError("Cannot pop from empty stack")
        return self.stack.pop()
    
    def apply_binary_op(self, op: str) -> None:
        """
        Apply a binary operator to the top two stack values.
        
        The second-to-top value is the left operand, top is the right operand.
        Result is pushed back onto the stack.
        """
        if len(self.stack) < 2:
            raise ValueError(f"Operator '{op}' requires 2 operands, but stack has {len(self.stack)}")
        
        right = self.pop()
        left = self.pop()
        
        if op == '/' and right == 0:
            raise ZeroDivisionError("Division by zero")
        
        result = self.binary_ops[op](left, right)
        self.push(result)
    
    def apply_unary_op(self, op: str) -> None:
        """
        Apply a unary operator to the top stack value.
        
        Result is pushed back onto the stack.
        """
        if len(self.stack) < 1:
            raise ValueError(f"Operator '{op}' requires 1 operand, but stack is empty")
        
        value = self.pop()
        result = self.unary_ops[op](value)
        self.push(result)
    
    def evaluate(self, expression: str) -> float:
        """
        Evaluate an RPN expression and return the result.
        
        Args:
            expression: Space-separated RPN expression (e.g., "3 4 + 2 *")
        
        Returns:
            The final computed value
        
        Raises:
            ValueError: If the expression is malformed or invalid
        """
        self.stack = []  # Reset stack for fresh evaluation
        tokens = expression.split()
        
        if not tokens:
            raise ValueError("Empty expression")
        
        for token in tokens:
            if token in self.binary_ops:
                self.apply_binary_op(token)
            elif token in self.unary_ops:
                self.apply_unary_op(token)
            else:
                # Try to parse as a number
                try:
                    self.push(float(token))
                except ValueError:
                    raise ValueError(f"Unknown token: '{token}'")
        
        # After processing all tokens, stack should have exactly one value
        if len(self.stack) != 1:
            raise ValueError(f"Malformed expression: stack has {len(self.stack)} values instead of 1")
        
        return self.pop()


def demo_expressions():
    """Run a series of demo calculations to show how the RPN calculator works."""
    calc = RPNCalculator()
    
    test_cases = [
        ("3 4 +", "Simple addition: 3 + 4"),
        ("15 7 1 1 + - /", "Complex expression: 15 / (7 - (1 + 1))"),
        ("5 1 2 + 4 * + 3 -", "Mixed operations: 5 + ((1 + 2) * 4) - 3"),
        ("2 3 ^", "Exponentiation: 2^3"),
        ("16 sqrt", "Square root: sqrt(16)"),
        ("3.14159 2 / sin", "Trig function: sin(π/2)"),
        ("100 ln", "Natural log: ln(100)"),
        ("-5 abs 2 **", "Chained: abs(-5)^2"),
    ]
    
    print("=== RPN Calculator Demo ===\n")
    
    for expr, description in test_cases:
        try:
            result = calc.evaluate(expr)
            print(f"{description}")
            print(f"  Expression: {expr}")
            print(f"  Result: {result:.6f}\n")
        except Exception as e:
            print(f"{description}")
            print(f"  Expression: {expr}")
            print(f"  Error: {e}\n")


if __name__ == "__main__":
    demo_expressions()
    
    # Interactive mode example
    print("\n=== Try your own (Ctrl+C to exit) ===")
    print("Examples: '3 4 +' or '10 3 / 2 *'\n")
    
    calc = RPNCalculator()
    
    try:
        while True:
            expr = input("RPN> ").strip()
            if not expr:
                continue
            
            try:
                result = calc.evaluate(expr)
                print(f"  => {result}")
            except Exception as e:
                print(f"  Error: {e}")
    except (KeyboardInterrupt, EOFError):
        print("\n\nBye!")