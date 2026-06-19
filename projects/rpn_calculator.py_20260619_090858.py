"""
Date: 2026-06-19
Implemented a reverse Polish notation calculator that parses expressions and evaluates them using a stack — added mod, power, and a few convenience operators for fun.
"""

#!/usr/bin/env python3
"""
RPN (Reverse Polish Notation) Calculator

I wanted to build a simple calculator that uses postfix notation because
it's actually easier to evaluate than infix (no precedence rules to worry about).
This uses a stack-based approach where operands get pushed and operators pop
them off to compute results.
"""

import operator
import re
from typing import List, Union, Callable


class RPNCalculator:
    """
    A simple RPN calculator that evaluates postfix expressions.
    
    Supports basic arithmetic, modulo, power, and a few stack operations.
    Numbers can be integers or floats.
    """
    
    def __init__(self):
        """Initialize the calculator with available operators."""
        # Map operator symbols to their functions
        # I chose operator module for cleanliness, but lambdas would work too
        self.operators = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '//': operator.floordiv,
            '%': operator.mod,
            '**': operator.pow,
            '^': operator.pow,  # alternate power symbol because I like it
        }
        
        # Special single-operand operations
        self.unary_ops = {
            'neg': operator.neg,
            'abs': operator.abs,
        }
        
        # Stack manipulation commands
        self.stack_ops = {
            'dup',   # duplicate top of stack
            'swap',  # swap top two elements
            'drop',  # remove top element
        }
    
    def tokenize(self, expression: str) -> List[str]:
        """
        Break the expression into tokens (numbers and operators).
        
        I'm using a regex to match floats, ints, and operator symbols.
        Whitespace gets stripped out automatically.
        """
        # Match floats, ints, and multi-char operators
        pattern = r'-?\d+\.?\d*|[+\-*/%^()]|//|\*\*|\w+'
        tokens = re.findall(pattern, expression)
        return [t for t in tokens if t.strip()]
    
    def is_number(self, token: str) -> bool:
        """Check if a token represents a number."""
        try:
            float(token)
            return True
        except ValueError:
            return False
    
    def evaluate(self, expression: str) -> Union[int, float]:
        """
        Evaluate an RPN expression and return the result.
        
        The algorithm is simple:
        - If it's a number, push it onto the stack
        - If it's an operator, pop operands, compute, push result
        - At the end, exactly one value should remain
        """
        tokens = self.tokenize(expression)
        stack = []
        
        for token in tokens:
            if self.is_number(token):
                # Push numbers onto the stack
                num = float(token) if '.' in token else int(token)
                stack.append(num)
            
            elif token in self.operators:
                # Binary operators need two operands
                if len(stack) < 2:
                    raise ValueError(f"Not enough operands for operator '{token}'")
                
                b = stack.pop()
                a = stack.pop()
                result = self.operators[token](a, b)
                stack.append(result)
            
            elif token in self.unary_ops:
                # Unary operators need one operand
                if len(stack) < 1:
                    raise ValueError(f"Not enough operands for operator '{token}'")
                
                a = stack.pop()
                result = self.unary_ops[token](a)
                stack.append(result)
            
            elif token in self.stack_ops:
                # Handle stack manipulation
                if token == 'dup':
                    if len(stack) < 1:
                        raise ValueError("Cannot duplicate: stack is empty")
                    stack.append(stack[-1])
                
                elif token == 'swap':
                    if len(stack) < 2:
                        raise ValueError("Cannot swap: need at least 2 elements")
                    stack[-1], stack[-2] = stack[-2], stack[-1]
                
                elif token == 'drop':
                    if len(stack) < 1:
                        raise ValueError("Cannot drop: stack is empty")
                    stack.pop()
            
            else:
                raise ValueError(f"Unknown token: '{token}'")
        
        # After processing all tokens, we should have exactly one result
        if len(stack) != 1:
            raise ValueError(f"Invalid expression: stack has {len(stack)} elements, expected 1")
        
        return stack[0]


def main():
    """Demo the RPN calculator with various expressions."""
    calc = RPNCalculator()
    
    print("RPN Calculator Demo")
    print("=" * 50)
    
    # Test cases showing different features
    test_expressions = [
        ("3 4 +", "Basic addition"),
        ("15 7 1 1 + - /", "Complex expression: (15 / (7 - (1 + 1)))"),
        ("5 1 2 + 4 * + 3 -", "Another complex one: (5 + ((1 + 2) * 4)) - 3"),
        ("2 3 ^", "Power operation: 2^3"),
        ("10 3 %", "Modulo: 10 % 3"),
        ("5 neg", "Negation: -5"),
        ("-12 abs", "Absolute value: |-12|"),
        ("7 dup *", "Duplicate and multiply: 7 * 7"),
        ("10 5 swap /", "Swap and divide: 5 / 10"),
        ("1 2 3 drop +", "Drop 3, then add 1 + 2"),
    ]
    
    for expr, description in test_expressions:
        try:
            result = calc.evaluate(expr)
            print(f"\nExpression: {expr}")
            print(f"Description: {description}")
            print(f"Result: {result}")
        except Exception as e:
            print(f"\nExpression: {expr}")
            print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("\nInteractive mode - enter RPN expressions (or 'quit' to exit):")
    
    # Simple REPL for playing around
    while True:
        try:
            expr = input("\nRPN> ").strip()
            if expr.lower() in ('quit', 'exit', 'q'):
                print("Bye!")
                break
            if not expr:
                continue
            
            result = calc.evaluate(expr)
            print(f"  => {result}")
        
        except ValueError as e:
            print(f"  Error: {e}")
        except KeyboardInterrupt:
            print("\nBye!")
            break


if __name__ == "__main__":
    main()