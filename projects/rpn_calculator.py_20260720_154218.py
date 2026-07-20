"""
Date: 2026-07-20
Implemented an RPN calculator that evaluates postfix expressions using a stack — supports basic arithmetic, trig functions, and custom operations.
"""

#!/usr/bin/env python3
"""
RPN (Reverse Polish Notation) Calculator
A stack-based expression evaluator that processes postfix notation.
"""

import math
import operator
from typing import Union, List


class RPNCalculator:
    """
    A simple Reverse Polish Notation calculator.
    
    Uses a stack to evaluate expressions written in postfix notation.
    Example: "3 4 +" evaluates to 7
    """
    
    def __init__(self):
        """Initialize the calculator with an empty stack and operation mappings."""
        self.stack: List[float] = []
        
        # Binary operations that take two operands
        self.binary_ops = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '**': operator.pow,
            '%': operator.mod,
            '^': operator.pow,  # Alternative power syntax
        }
        
        # Unary operations that take one operand
        self.unary_ops = {
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'sqrt': math.sqrt,
            'abs': abs,
            'ln': math.log,
            'log': math.log10,
            'neg': operator.neg,  # Negation
        }
    
    def push(self, value: float) -> None:
        """Push a value onto the stack."""
        self.stack.append(value)
    
    def pop(self) -> float:
        """Pop and return the top value from the stack."""
        if not self.stack:
            raise ValueError("Stack underflow: not enough operands")
        return self.stack.pop()
    
    def evaluate(self, expression: str) -> float:
        """
        Evaluate an RPN expression and return the result.
        
        The expression should be a string with tokens separated by spaces.
        Numbers are pushed onto the stack, operators consume operands from the stack.
        
        Args:
            expression: RPN expression string (e.g., "3 4 + 2 *")
        
        Returns:
            The computed result as a float
        """
        self.stack.clear()  # Start fresh for each evaluation
        tokens = expression.split()
        
        for token in tokens:
            if token in self.binary_ops:
                # Binary operation: pop two operands
                if len(self.stack) < 2:
                    raise ValueError(f"Not enough operands for '{token}'")
                b = self.pop()
                a = self.pop()
                result = self.binary_ops[token](a, b)
                self.push(result)
                
            elif token in self.unary_ops:
                # Unary operation: pop one operand
                if len(self.stack) < 1:
                    raise ValueError(f"Not enough operands for '{token}'")
                a = self.pop()
                result = self.unary_ops[token](a)
                self.push(result)
                
            else:
                # Try to parse as a number
                try:
                    value = float(token)
                    self.push(value)
                except ValueError:
                    raise ValueError(f"Unknown token: '{token}'")
        
        # After processing all tokens, should have exactly one value left
        if len(self.stack) != 1:
            raise ValueError(f"Invalid expression: {len(self.stack)} values remain on stack")
        
        return self.pop()
    
    def get_stack_state(self) -> List[float]:
        """Return a copy of the current stack state."""
        return self.stack.copy()


def interactive_mode():
    """
    Run the calculator in interactive mode where user can input expressions.
    Type 'quit' or 'exit' to leave.
    """
    calc = RPNCalculator()
    print("RPN Calculator - Interactive Mode")
    print("Example: '3 4 +' evaluates to 7")
    print("Type 'quit' to exit\n")
    
    while True:
        try:
            expr = input("rpn> ").strip()
            if expr.lower() in ('quit', 'exit', 'q'):
                break
            if not expr:
                continue
            
            result = calc.evaluate(expr)
            print(f"  = {result}")
            
        except ValueError as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("\nExiting...")
            break


if __name__ == "__main__":
    # Demo mode: evaluate a bunch of example expressions
    calc = RPNCalculator()
    
    examples = [
        ("3 4 +", "Simple addition"),
        ("15 7 1 1 + - /", "Complex expression: 15/(7-(1+1))"),
        ("5 1 2 + 4 * + 3 -", "(5 + ((1+2)*4)) - 3"),
        ("2 3 ^", "Exponentiation: 2^3"),
        ("9 sqrt", "Square root of 9"),
        ("0 sin", "Sine of 0"),
        ("3.14159 2 / cos", "Cosine of π/2 (approx)"),
        ("100 ln", "Natural log of 100"),
        ("5 neg", "Negate 5"),
        ("10 3 % 2 +", "Modulo: (10 % 3) + 2"),
    ]
    
    print("=== RPN Calculator Demo ===\n")
    
    for expression, description in examples:
        try:
            result = calc.evaluate(expression)
            print(f"{description}")
            print(f"  Expression: {expression}")
            print(f"  Result: {result}\n")
        except Exception as e:
            print(f"Error evaluating '{expression}': {e}\n")
    
    print("\n--- Starting interactive mode ---\n")
    interactive_mode()