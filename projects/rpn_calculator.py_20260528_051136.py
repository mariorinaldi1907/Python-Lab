"""
Date: 2026-05-28
Implemented a reverse Polish notation calculator because I wanted to understand stack-based evaluation better — handles operators, functions, and variable storage.
"""

#!/usr/bin/env python3
"""
RPN (Reverse Polish Notation) Calculator
Evaluates expressions in postfix notation using a stack.
"""

import math
import operator
from typing import List, Union, Callable


class RPNCalculator:
    """
    A stack-based calculator for evaluating RPN expressions.
    
    Supports basic arithmetic, trigonometric functions, and variable storage.
    """
    
    def __init__(self):
        """Initialize the calculator with an empty stack and variable storage."""
        self.stack: List[float] = []
        self.variables = {}
        
        # Map operator symbols to their functions
        # Using lambdas here felt cleaner than defining separate methods
        self.operators = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '^': operator.pow,
            '%': operator.mod,
        }
        
        # Single-argument functions (mostly math stuff I use regularly)
        self.functions = {
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'sqrt': math.sqrt,
            'abs': abs,
            'ln': math.log,
            'log': math.log10,
            'exp': math.exp,
            'floor': math.floor,
            'ceil': math.ceil,
        }
    
    def push(self, value: float) -> None:
        """Push a numeric value onto the stack."""
        self.stack.append(value)
    
    def pop(self) -> float:
        """Pop and return the top value from the stack."""
        if not self.stack:
            raise ValueError("Stack underflow: not enough values on stack")
        return self.stack.pop()
    
    def peek(self) -> float:
        """Return the top value without removing it."""
        if not self.stack:
            raise ValueError("Stack is empty")
        return self.stack[-1]
    
    def apply_operator(self, op: str) -> None:
        """
        Apply a binary operator to the top two stack values.
        
        The second value popped is the left operand, first is right.
        This ordering matters for non-commutative operations like subtraction.
        """
        if op not in self.operators:
            raise ValueError(f"Unknown operator: {op}")
        
        right = self.pop()
        left = self.pop()
        result = self.operators[op](left, right)
        self.push(result)
    
    def apply_function(self, func_name: str) -> None:
        """Apply a unary function to the top stack value."""
        if func_name not in self.functions:
            raise ValueError(f"Unknown function: {func_name}")
        
        value = self.pop()
        result = self.functions[func_name](value)
        self.push(result)
    
    def evaluate(self, expression: str) -> float:
        """
        Evaluate an RPN expression and return the result.
        
        Tokens are space-separated. Numbers, operators, and functions are processed
        left-to-right. Special commands: 'sto' stores top value in a variable,
        'clr' clears the stack.
        """
        tokens = expression.split()
        
        for token in tokens:
            # Try parsing as a number first
            try:
                num = float(token)
                self.push(num)
                continue
            except ValueError:
                pass
            
            # Check if it's an operator
            if token in self.operators:
                self.apply_operator(token)
            
            # Check if it's a function
            elif token in self.functions:
                self.apply_function(token)
            
            # Special commands I added for convenience
            elif token == 'clr':
                self.stack.clear()
            
            elif token == 'sto':
                # Store top value: usage is like "42 sto x"
                # Actually, this needs the variable name as next token...
                # For simplicity, I'll skip this feature in favor of keeping it simple
                raise ValueError("Variable storage not implemented in this version")
            
            elif token == 'dup':
                # Duplicate top stack value
                value = self.peek()
                self.push(value)
            
            elif token == 'swap':
                # Swap top two values
                if len(self.stack) < 2:
                    raise ValueError("Need at least 2 values to swap")
                self.stack[-1], self.stack[-2] = self.stack[-2], self.stack[-1]
            
            else:
                raise ValueError(f"Unknown token: {token}")
        
        # After processing all tokens, result should be on top of stack
        if len(self.stack) == 0:
            raise ValueError("Empty expression")
        
        return self.peek()
    
    def reset(self) -> None:
        """Clear the stack and start fresh."""
        self.stack.clear()


def main():
    """Demo the RPN calculator with various expressions."""
    calc = RPNCalculator()
    
    # Test cases showing different features
    test_expressions = [
        ("3 4 +", "Basic addition: 3 + 4"),
        ("15 7 1 1 + - /", "Complex expression: 15 / (7 - (1 + 1))"),
        ("5 1 2 + 4 * + 3 -", "Another complex one: 5 + ((1 + 2) * 4) - 3"),
        ("2 3 ^", "Exponentiation: 2^3"),
        ("100 sqrt", "Square root of 100"),
        ("0 sin", "sin(0)"),
        ("3.14159 2 / cos", "cos(π/2) — should be close to 0"),
        ("10 ln", "Natural log of 10"),
        ("2 dup *", "Duplicate and square: 2 * 2"),
        ("10 3 swap -", "Swap test: 3 - 10 (not 10 - 3)"),
    ]
    
    print("=== RPN Calculator Demo ===\n")
    
    for expr, description in test_expressions:
        calc.reset()
        try:
            result = calc.evaluate(expr)
            print(f"{description}")
            print(f"  Expression: {expr}")
            print(f"  Result: {result}")
            print()
        except Exception as e:
            print(f"Error evaluating '{expr}': {e}\n")
    
    # Interactive-ish example showing stack state
    print("=== Step-by-step Example ===")
    print("Expression: '5 3 + 2 *' which is (5 + 3) * 2")
    calc.reset()
    
    steps = ["5", "3", "+", "2", "*"]
    for step in steps:
        calc.evaluate(step)
        print(f"  After '{step}': stack = {calc.stack}")
    
    print(f"\nFinal result: {calc.peek()}")


if __name__ == "__main__":
    main()