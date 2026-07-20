"""
Date: 2026-07-20
Implemented an RPN calculator because I wanted to really understand stack-based evaluation and it's honestly the cleanest way to parse expressions without dealing with precedence nightmares.
"""

#!/usr/bin/env python3
"""
RPN (Reverse Polish Notation) Calculator

A simple stack-based calculator that evaluates expressions in postfix notation.
I built this because RPN is elegant — no parentheses needed, no precedence
ambiguity, and the evaluation algorithm is beautifully straightforward.

Example: "3 4 + 5 *" evaluates to 35 (because (3+4)*5)
"""

import operator
import re
from typing import List, Union


class RPNCalculator:
    """
    Stack-based calculator for Reverse Polish Notation expressions.
    
    Supports basic arithmetic operations and handles floating point numbers.
    The stack approach makes this super clean — just push numbers and apply
    operators when you hit them.
    """
    
    def __init__(self):
        """Initialize the calculator with supported operations."""
        # Using operator module because why reimplement these?
        self.operators = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '//': operator.floordiv,
            '%': operator.mod,
            '^': operator.pow,
            '**': operator.pow,
        }
        self.stack = []
    
    def is_number(self, token: str) -> bool:
        """
        Check if a token is a valid number (int or float).
        
        I'm using a try-except here instead of regex because it's more
        Pythonic and handles edge cases like scientific notation for free.
        """
        try:
            float(token)
            return True
        except ValueError:
            return False
    
    def evaluate(self, expression: str) -> float:
        """
        Evaluate an RPN expression and return the result.
        
        The algorithm is dead simple:
        1. Scan tokens left to right
        2. If number, push to stack
        3. If operator, pop two operands, apply operation, push result
        4. Final stack should have exactly one value — that's your answer
        """
        self.stack = []  # Reset stack for new evaluation
        tokens = expression.split()
        
        if not tokens:
            raise ValueError("Empty expression")
        
        for token in tokens:
            if self.is_number(token):
                # Push numbers onto the stack
                self.stack.append(float(token))
            elif token in self.operators:
                # Need at least two operands for binary operations
                if len(self.stack) < 2:
                    raise ValueError(f"Insufficient operands for operator '{token}'")
                
                # Pop in reverse order because stack is LIFO
                # For "5 3 -" we want 5-3, not 3-5
                right = self.stack.pop()
                left = self.stack.pop()
                
                # Apply the operation and push result back
                result = self.operators[token](left, right)
                self.stack.append(result)
            else:
                raise ValueError(f"Unknown token: '{token}'")
        
        # Should have exactly one value left — the final result
        if len(self.stack) != 1:
            raise ValueError(f"Invalid expression: {len(self.stack)} values remaining on stack")
        
        return self.stack[0]
    
    def get_stack_state(self) -> List[float]:
        """Return current stack state (useful for debugging)."""
        return self.stack.copy()


def infix_to_rpn(expression: str) -> str:
    """
    Convert infix notation to RPN using the Shunting Yard algorithm.
    
    This is Dijkstra's algorithm — super clever use of stacks to handle
    operator precedence. I added this so the demo can show both notations.
    """
    # Operator precedence (higher number = higher precedence)
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '//': 2, '%': 2, '^': 3, '**': 3}
    # Right-associative operators (for exponentiation)
    right_assoc = {'^', '**'}
    
    output = []
    op_stack = []
    
    # Tokenize: split by spaces and operators, keeping operators
    tokens = re.findall(r'\d+\.?\d*|[+\-*/%^()]|\*\*|//', expression.replace(' ', ''))
    
    for token in tokens:
        if re.match(r'\d+\.?\d*', token):
            # Numbers go straight to output
            output.append(token)
        elif token in precedence:
            # Pop operators with higher/equal precedence (respecting associativity)
            while (op_stack and 
                   op_stack[-1] != '(' and
                   op_stack[-1] in precedence and
                   (precedence[op_stack[-1]] > precedence[token] or
                    (precedence[op_stack[-1]] == precedence[token] and token not in right_assoc))):
                output.append(op_stack.pop())
            op_stack.append(token)
        elif token == '(':
            op_stack.append(token)
        elif token == ')':
            # Pop until we find the matching opening paren
            while op_stack and op_stack[-1] != '(':
                output.append(op_stack.pop())
            if not op_stack:
                raise ValueError("Mismatched parentheses")
            op_stack.pop()  # Remove the '('
    
    # Pop any remaining operators
    while op_stack:
        if op_stack[-1] in '()':
            raise ValueError("Mismatched parentheses")
        output.append(op_stack.pop())
    
    return ' '.join(output)


if __name__ == "__main__":
    print("=== RPN Calculator Demo ===\n")
    
    calc = RPNCalculator()
    
    # Test cases with direct RPN input
    test_expressions = [
        "3 4 +",                    # 7
        "3 4 + 5 *",                # 35
        "15 7 1 1 + - / 3 * 2 1 1 + + -",  # Classic example: 5
        "5 1 2 + 4 * + 3 -",        # 14
        "2 3 ^",                    # 8
        "100 10 / 2 /",             # 5
        "10 3 %",                   # 1
    ]
    
    print("Direct RPN Evaluation:")
    print("-" * 50)
    for expr in test_expressions:
        try:
            result = calc.evaluate(expr)
            print(f"Expression: {expr:30} => {result}")
        except Exception as e:
            print(f"Expression: {expr:30} => ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("\nInfix to RPN Conversion + Evaluation:")
    print("-" * 50)
    
    # Test infix conversion
    infix_expressions = [
        "3 + 4",
        "(3 + 4) * 5",
        "3 + 4 * 5",
        "2 ** 3",
        "(1 + 2) * (3 + 4)",
    ]
    
    for infix in infix_expressions:
        try:
            rpn = infix_to_rpn(infix)
            result = calc.evaluate(rpn)
            print(f"Infix:  {infix:20} => RPN: {rpn:25} => {result}")
        except Exception as e:
            print(f"Infix:  {infix:20} => ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("\nError Handling Demo:")
    print("-" * 50)
    
    # Show how errors are handled
    error_cases = [
        "5 +",              # Insufficient operands
        "1 2 3",            # Too many operands
        "5 @ 3",            # Unknown operator
        "",                 # Empty expression
    ]
    
    for expr in error_cases:
        try:
            result = calc.evaluate(expr)
            print(f"'{expr}' => {result}")
        except Exception as e:
            print(f"'{expr}' => Caught error: {e}")