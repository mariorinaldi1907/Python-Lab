"""
Date: 2026-06-24
Implemented a reverse polish notation calculator that supports basic arithmetic and a few math functions — wanted something lightweight for quick calculations without dealing with operator precedence parsing.
"""

#!/usr/bin/env python3
"""
RPN (Reverse Polish Notation) Calculator

Evaluates expressions written in postfix notation where operators follow operands.
Example: "3 4 +" evaluates to 7, "5 1 2 + 4 * + 3 -" evaluates to 14

Supports basic arithmetic (+, -, *, /), power (^), and some math functions.
"""

import math
import operator
from typing import List, Union


class RPNCalculator:
    """
    A simple stack-based calculator for evaluating RPN expressions.
    
    I chose RPN because it's easier to parse than infix notation — no need
    to worry about operator precedence or parentheses. Everything just flows
    left to right onto the stack.
    """
    
    def __init__(self):
        """Initialize the calculator with operator mappings."""
        # Maps operator symbols to their actual functions
        self.operators = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '^': operator.pow,
            '**': operator.pow,  # Alternative power syntax
        }
        
        # Single-argument functions (unary operations)
        self.functions = {
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log,
            'ln': math.log,
            'abs': abs,
            'neg': operator.neg,
        }
    
    def evaluate(self, expression: str) -> float:
        """
        Evaluate an RPN expression and return the result.
        
        Args:
            expression: Space-separated tokens in RPN format
            
        Returns:
            The computed result as a float
            
        Raises:
            ValueError: If the expression is malformed or invalid
        """
        stack: List[float] = []
        tokens = expression.split()
        
        if not tokens:
            raise ValueError("Empty expression")
        
        for token in tokens:
            if self._is_number(token):
                # Push numbers onto the stack
                stack.append(float(token))
            
            elif token in self.operators:
                # Binary operators need two operands
                if len(stack) < 2:
                    raise ValueError(f"Insufficient operands for operator '{token}'")
                
                b = stack.pop()  # Right operand
                a = stack.pop()  # Left operand
                
                try:
                    result = self.operators[token](a, b)
                    stack.append(result)
                except ZeroDivisionError:
                    raise ValueError("Division by zero")
            
            elif token in self.functions:
                # Unary functions need one operand
                if len(stack) < 1:
                    raise ValueError(f"Insufficient operands for function '{token}'")
                
                a = stack.pop()
                try:
                    result = self.functions[token](a)
                    stack.append(result)
                except (ValueError, OverflowError) as e:
                    raise ValueError(f"Math error in '{token}': {e}")
            
            else:
                raise ValueError(f"Unknown token: '{token}'")
        
        # After processing all tokens, we should have exactly one result
        if len(stack) != 1:
            raise ValueError(f"Malformed expression: {len(stack)} values remain on stack")
        
        return stack[0]
    
    @staticmethod
    def _is_number(token: str) -> bool:
        """
        Check if a token represents a valid number.
        
        Handles integers, floats, and negative numbers.
        """
        try:
            float(token)
            return True
        except ValueError:
            return False


def infix_to_rpn(expression: str) -> str:
    """
    Convert a simple infix expression to RPN using the Shunting Yard algorithm.
    
    This is a bonus feature — lets users type normal math expressions.
    Only supports +, -, *, /, ^ and parentheses. No functions yet.
    """
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3, '**': 3}
    right_associative = {'^', '**'}
    
    output = []
    operator_stack = []
    
    # Simple tokenization — splits on spaces and preserves parentheses
    tokens = expression.replace('(', ' ( ').replace(')', ' ) ').split()
    
    for token in tokens:
        if RPNCalculator._is_number(token):
            output.append(token)
        elif token == '(':
            operator_stack.append(token)
        elif token == ')':
            # Pop operators until we find the matching '('
            while operator_stack and operator_stack[-1] != '(':
                output.append(operator_stack.pop())
            if not operator_stack:
                raise ValueError("Mismatched parentheses")
            operator_stack.pop()  # Remove the '('
        elif token in precedence:
            # Pop operators with higher or equal precedence
            while (operator_stack and 
                   operator_stack[-1] != '(' and
                   operator_stack[-1] in precedence and
                   (precedence[operator_stack[-1]] > precedence[token] or
                    (precedence[operator_stack[-1]] == precedence[token] and 
                     token not in right_associative))):
                output.append(operator_stack.pop())
            operator_stack.append(token)
    
    # Pop remaining operators
    while operator_stack:
        op = operator_stack.pop()
        if op == '(':
            raise ValueError("Mismatched parentheses")
        output.append(op)
    
    return ' '.join(output)


if __name__ == "__main__":
    calc = RPNCalculator()
    
    print("=== RPN Calculator Demo ===\n")
    
    # Test cases showing various features
    test_expressions = [
        "3 4 +",
        "15 7 1 1 + - /",  # ((15) / (7 - (1 + 1))) = 3.0
        "5 1 2 + 4 * + 3 -",  # 5 + ((1 + 2) * 4) - 3 = 14
        "2 3 ^",
        "9 sqrt",
        "3.14159 2 / sin",
        "100 ln",
        "-5 abs",
        "10 3 / 2 *",
    ]
    
    for expr in test_expressions:
        try:
            result = calc.evaluate(expr)
            print(f"RPN: {expr:25} => {result:.6f}")
        except ValueError as e:
            print(f"RPN: {expr:25} => ERROR: {e}")
    
    print("\n=== Infix to RPN Conversion ===\n")
    
    infix_tests = [
        "3 + 4",
        "3 + 4 * 2",
        "( 3 + 4 ) * 2",
        "2 ^ 3 ^ 2",  # Right associative: 2^(3^2) = 512
    ]
    
    for infix in infix_tests:
        try:
            rpn = infix_to_rpn(infix)
            result = calc.evaluate(rpn)
            print(f"Infix: {infix:20} => RPN: {rpn:20} => {result:.6f}")
        except ValueError as e:
            print(f"Infix: {infix:20} => ERROR: {e}")