"""
Date: 2026-08-30
Implemented a reverse Polish notation calculator that supports arithmetic, variables, and stack manipulation — been wanting to build one of these for a while.
"""

#!/usr/bin/env python3
"""
A Reverse Polish Notation (RPN) calculator with variables and stack operations.
Supports basic arithmetic, variable assignment, and stack manipulation commands.
"""

import operator
import re
from typing import List, Dict, Union


class RPNCalculator:
    """
    An RPN calculator that processes expressions in postfix notation.
    Maintains a stack and supports variables for storing intermediate results.
    """
    
    def __init__(self):
        """Initialize the calculator with an empty stack and variable store."""
        self.stack: List[float] = []
        self.variables: Dict[str, float] = {}
        
        # Map operators to their functions - makes it easy to extend later
        self.operators = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '**': operator.pow,
            '%': operator.mod,
        }
    
    def push(self, value: Union[float, str]) -> None:
        """
        Push a value onto the stack.
        If it's a variable name, push its stored value instead.
        """
        if isinstance(value, str) and value in self.variables:
            self.stack.append(self.variables[value])
        else:
            self.stack.append(float(value))
    
    def pop(self) -> float:
        """Pop and return the top value from the stack."""
        if not self.stack:
            raise ValueError("Stack underflow - not enough values on stack")
        return self.stack.pop()
    
    def peek(self) -> float:
        """Return the top value without removing it."""
        if not self.stack:
            raise ValueError("Stack is empty")
        return self.stack[-1]
    
    def apply_operator(self, op: str) -> None:
        """
        Apply a binary operator to the top two stack values.
        The second-to-top is the left operand, top is the right operand.
        """
        if len(self.stack) < 2:
            raise ValueError(f"Operator '{op}' needs two operands")
        
        right = self.pop()
        left = self.pop()
        
        if op == '/' and right == 0:
            raise ValueError("Division by zero")
        
        result = self.operators[op](left, right)
        self.stack.append(result)
    
    def store_variable(self, name: str) -> None:
        """Store the top stack value in a variable without popping it."""
        if not self.stack:
            raise ValueError("Cannot store from empty stack")
        self.variables[name] = self.peek()
    
    def duplicate(self) -> None:
        """Duplicate the top stack value."""
        if not self.stack:
            raise ValueError("Cannot duplicate from empty stack")
        self.stack.append(self.peek())
    
    def swap(self) -> None:
        """Swap the top two stack values."""
        if len(self.stack) < 2:
            raise ValueError("Need at least two values to swap")
        self.stack[-1], self.stack[-2] = self.stack[-2], self.stack[-1]
    
    def clear(self) -> None:
        """Clear the entire stack."""
        self.stack.clear()
    
    def evaluate(self, expression: str) -> float:
        """
        Evaluate an RPN expression and return the result.
        
        Supports:
        - Numbers (integers and floats)
        - Operators: +, -, *, /, **, %
        - Variable assignment: =var (stores top of stack in 'var')
        - Stack commands: dup (duplicate), swap, clear, drop
        """
        tokens = expression.split()
        
        for token in tokens:
            # Check if it's a variable assignment (=varname)
            if token.startswith('=') and len(token) > 1:
                var_name = token[1:]
                if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', var_name):
                    raise ValueError(f"Invalid variable name: {var_name}")
                self.store_variable(var_name)
            
            # Check if it's an operator
            elif token in self.operators:
                self.apply_operator(token)
            
            # Stack manipulation commands
            elif token == 'dup':
                self.duplicate()
            elif token == 'swap':
                self.swap()
            elif token == 'drop':
                self.pop()
            elif token == 'clear':
                self.clear()
            
            # Otherwise try to parse as number or variable reference
            else:
                try:
                    self.push(float(token))
                except ValueError:
                    # Maybe it's a variable reference
                    if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', token):
                        if token not in self.variables:
                            raise ValueError(f"Undefined variable: {token}")
                        self.push(token)
                    else:
                        raise ValueError(f"Invalid token: {token}")
        
        # Return the top of stack as the result
        if not self.stack:
            raise ValueError("Expression resulted in empty stack")
        
        return self.peek()
    
    def get_stack(self) -> List[float]:
        """Return a copy of the current stack state."""
        return self.stack.copy()


def demo():
    """Run some example calculations to show off the RPN calculator."""
    calc = RPNCalculator()
    
    print("=== RPN Calculator Demo ===\n")
    
    # Basic arithmetic
    examples = [
        ("3 4 +", "Simple addition"),
        ("15 7 1 1 + - /", "Complex expression: (15 / (7 - (1 + 1)))"),
        ("5 2 **", "Exponentiation: 5^2"),
        ("10 3 %", "Modulo: 10 % 3"),
    ]
    
    for expr, desc in examples:
        result = calc.evaluate(expr)
        print(f"{desc}")
        print(f"  Expression: {expr}")
        print(f"  Result: {result}")
        print(f"  Stack after: {calc.get_stack()}\n")
        calc.clear()
    
    # Variable storage and reuse
    print("--- Variables Example ---")
    calc.evaluate("5 =x")
    print(f"Stored 5 in 'x': {calc.variables}")
    calc.evaluate("3 =y")
    print(f"Stored 3 in 'y': {calc.variables}")
    result = calc.evaluate("x y *")
    print(f"x * y = {result}\n")
    calc.clear()
    
    # Stack operations
    print("--- Stack Operations ---")
    calc.evaluate("10 20 dup")
    print(f"After '10 20 dup': {calc.get_stack()}")
    calc.evaluate("swap")
    print(f"After 'swap': {calc.get_stack()}")
    calc.evaluate("drop")
    print(f"After 'drop': {calc.get_stack()}")


if __name__ == "__main__":
    demo()