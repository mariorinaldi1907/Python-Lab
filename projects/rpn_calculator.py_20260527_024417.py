"""
Date: 2026-05-27
Implemented a reverse polish notation calculator that handles basic arithmetic and variable assignment — wanted something cleaner than infix parsing for quick calculations.
"""

#!/usr/bin/env python3
"""
RPN (Reverse Polish Notation) Calculator
Evaluates expressions in postfix notation where operators come after operands.
Example: "3 4 +" evaluates to 7
"""

import re
from typing import Union, Dict


class RPNCalculator:
    """
    Stack-based calculator for evaluating RPN expressions.
    Supports basic arithmetic operations and variable storage.
    """
    
    def __init__(self):
        """Initialize the calculator with an empty variable store."""
        self.variables: Dict[str, float] = {}
        self.operators = {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            '*': lambda a, b: a * b,
            '/': lambda a, b: a / b,
            '**': lambda a, b: a ** b,
            '%': lambda a, b: a % b,
        }
    
    def tokenize(self, expression: str) -> list:
        """
        Split expression into tokens, handling numbers, operators, and variables.
        Uses regex to properly parse negative numbers and multi-char operators.
        """
        # Match: floats (including negative), operators, or alphanumeric variable names
        pattern = r'-?\d+\.?\d*|[+\-*/%()]|\*\*|[a-zA-Z_]\w*|='
        tokens = re.findall(pattern, expression)
        return [t for t in tokens if t.strip()]  # Filter out empty strings
    
    def is_number(self, token: str) -> bool:
        """Check if a token can be parsed as a number."""
        try:
            float(token)
            return True
        except ValueError:
            return False
    
    def evaluate(self, expression: str) -> Union[float, None]:
        """
        Evaluate an RPN expression and return the result.
        Supports variable assignment with '=' operator.
        
        Examples:
            "3 4 +" -> 7
            "5 x =" -> stores 5 in variable x
            "x 2 *" -> retrieves x and multiplies by 2
        """
        tokens = self.tokenize(expression)
        stack = []
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            # Handle variable assignment: "value varname ="
            if i + 1 < len(tokens) and tokens[i + 1] == '=':
                if len(stack) == 0:
                    raise ValueError("Assignment requires a value on the stack")
                value = stack.pop()
                var_name = token
                self.variables[var_name] = value
                stack.append(value)  # Push back for chaining
                i += 2  # Skip both varname and '='
                continue
            
            # Number: push to stack
            if self.is_number(token):
                stack.append(float(token))
            
            # Operator: pop operands, apply operation, push result
            elif token in self.operators:
                if len(stack) < 2:
                    raise ValueError(f"Not enough operands for operator '{token}'")
                b = stack.pop()  # Second operand
                a = stack.pop()  # First operand
                result = self.operators[token](a, b)
                stack.append(result)
            
            # Variable: retrieve from store
            elif token.isidentifier():
                if token not in self.variables:
                    raise ValueError(f"Undefined variable: '{token}'")
                stack.append(self.variables[token])
            
            else:
                raise ValueError(f"Unknown token: '{token}'")
            
            i += 1
        
        # After processing all tokens, stack should have exactly one value
        if len(stack) != 1:
            raise ValueError(f"Invalid expression: {len(stack)} values left on stack")
        
        return stack[0]


def demo():
    """
    Run a series of example calculations to demonstrate the RPN calculator.
    Shows basic arithmetic, operator precedence, variables, and error handling.
    """
    calc = RPNCalculator()
    
    # Test cases: (expression, description)
    test_cases = [
        ("3 4 +", "Simple addition"),
        ("10 5 -", "Subtraction"),
        ("6 7 *", "Multiplication"),
        ("20 4 /", "Division"),
        ("2 3 **", "Exponentiation"),
        ("15 2 + 3 *", "Multiple operations: (15+2)*3"),
        ("100 radius =", "Store value in variable"),
        ("radius 2 *", "Use stored variable"),
        ("radius radius * 3.14159 *", "Calculate area: π*r²"),
        ("10 0.5 + price =", "Chain assignment"),
        ("price 1.08 * total =", "Tax calculation"),
        ("total", "Retrieve final total"),
    ]
    
    print("=" * 60)
    print("RPN Calculator Demo")
    print("=" * 60)
    
    for expression, description in test_cases:
        try:
            result = calc.evaluate(expression)
            print(f"\n{description}")
            print(f"  Expression: {expression}")
            print(f"  Result: {result:.4f}" if result is not None else "  Result: None")
        except Exception as e:
            print(f"\n{description}")
            print(f"  Expression: {expression}")
            print(f"  Error: {e}")
    
    # Show error handling
    print("\n" + "=" * 60)
    print("Error Handling Examples")
    print("=" * 60)
    
    error_cases = [
        ("3 +", "Not enough operands"),
        ("foo", "Undefined variable"),
        ("5 5 5 +", "Too many values on stack"),
    ]
    
    for expression, description in error_cases:
        try:
            result = calc.evaluate(expression)
            print(f"\n{description}: {expression} = {result}")
        except Exception as e:
            print(f"\n{description}: {expression}")
            print(f"  Caught: {e}")


if __name__ == "__main__":
    demo()