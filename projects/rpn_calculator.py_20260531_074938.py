"""
Date: 2026-05-31
Implemented an RPN calculator that handles basic arithmetic, variables, and stack operations — spent way too much time getting the error messages right.
"""

#!/usr/bin/env python3
"""
Simple Reverse Polish Notation (RPN) Calculator
Supports basic arithmetic operations, variables, and stack manipulation.
"""


class RPNCalculator:
    """
    A stack-based calculator that evaluates expressions in Reverse Polish Notation.
    
    Supports operations: +, -, *, /, %, ** (power), and sqrt
    Also supports variables (store with '=' and retrieve by name)
    """
    
    def __init__(self):
        """Initialize the calculator with an empty stack and variable storage."""
        self.stack = []
        self.variables = {}
    
    def push(self, value):
        """Push a numeric value onto the stack."""
        self.stack.append(float(value))
    
    def pop(self):
        """
        Pop and return the top value from the stack.
        
        Raises:
            IndexError: If the stack is empty
        """
        if not self.stack:
            raise IndexError("Cannot pop from empty stack")
        return self.stack.pop()
    
    def peek(self):
        """Return the top value without removing it."""
        if not self.stack:
            raise IndexError("Stack is empty")
        return self.stack[-1]
    
    def execute_operation(self, operator):
        """
        Execute a binary or unary operation on stack values.
        
        Binary ops need 2 operands, unary ops need 1.
        Result is pushed back onto the stack.
        """
        if operator in ['+', '-', '*', '/', '%', '**']:
            # Binary operations need two operands
            if len(self.stack) < 2:
                raise ValueError(f"Operation '{operator}' requires 2 operands")
            b = self.pop()
            a = self.pop()
            
            if operator == '+':
                result = a + b
            elif operator == '-':
                result = a - b
            elif operator == '*':
                result = a * b
            elif operator == '/':
                if b == 0:
                    raise ZeroDivisionError("Division by zero")
                result = a / b
            elif operator == '%':
                result = a % b
            elif operator == '**':
                result = a ** b
            
            self.push(result)
        
        elif operator == 'sqrt':
            # Unary operation
            if len(self.stack) < 1:
                raise ValueError("Operation 'sqrt' requires 1 operand")
            a = self.pop()
            if a < 0:
                raise ValueError("Cannot take square root of negative number")
            result = a ** 0.5
            self.push(result)
        
        else:
            raise ValueError(f"Unknown operator: {operator}")
    
    def evaluate(self, expression):
        """
        Evaluate an RPN expression given as a string.
        
        The expression is split by whitespace. Each token is either:
        - A number (pushed to stack)
        - An operator (executes operation)
        - A variable name (pushes its value)
        - An assignment (var_name =)
        
        Returns:
            The final value on top of the stack
        """
        tokens = expression.split()
        
        for i, token in enumerate(tokens):
            # Check if this is a variable assignment (next token is '=')
            if i + 1 < len(tokens) and tokens[i + 1] == '=':
                continue  # Skip the variable name, handle on '='
            
            if token == '=':
                # Assignment: previous token is variable name
                if i == 0:
                    raise ValueError("Assignment needs a variable name")
                var_name = tokens[i - 1]
                if len(self.stack) < 1:
                    raise ValueError("Assignment requires a value on stack")
                self.variables[var_name] = self.peek()
            
            elif token in ['+', '-', '*', '/', '%', '**', 'sqrt']:
                self.execute_operation(token)
            
            else:
                # Try to parse as number first, then check variables
                try:
                    value = float(token)
                    self.push(value)
                except ValueError:
                    # Must be a variable reference
                    if token in self.variables:
                        self.push(self.variables[token])
                    else:
                        raise ValueError(f"Unknown variable or invalid token: {token}")
        
        if not self.stack:
            raise ValueError("No result on stack")
        
        return self.peek()
    
    def clear(self):
        """Clear the stack and all variables."""
        self.stack.clear()
        self.variables.clear()


if __name__ == "__main__":
    calc = RPNCalculator()
    
    print("=== RPN Calculator Demo ===\n")
    
    # Example 1: Simple arithmetic
    expr1 = "3 4 +"
    result1 = calc.evaluate(expr1)
    print(f"Expression: {expr1}")
    print(f"Result: {result1}")
    print(f"Explanation: 3 + 4 = {result1}\n")
    
    # Example 2: More complex expression
    calc.clear()
    expr2 = "15 7 1 1 + - / 3 * 2 1 1 + + -"
    result2 = calc.evaluate(expr2)
    print(f"Expression: {expr2}")
    print(f"Result: {result2}")
    print(f"Explanation: ((15 / (7 - (1 + 1))) * 3) - (2 + (1 + 1)) = {result2}\n")
    
    # Example 3: Variables
    calc.clear()
    expr3 = "5 x = x x * sqrt"
    result3 = calc.evaluate(expr3)
    print(f"Expression: {expr3}")
    print(f"Result: {result3}")
    print(f"Explanation: x = 5, then sqrt(x * x) = {result3}\n")
    
    # Example 4: Power and modulo
    calc.clear()
    expr4 = "2 10 ** 7 %"
    result4 = calc.evaluate(expr4)
    print(f"Expression: {expr4}")
    print(f"Result: {result4}")
    print(f"Explanation: (2 ** 10) % 7 = 1024 % 7 = {result4}\n")
    
    # Example 5: Using stored variables
    calc.clear()
    expr5 = "10 a = 20 b = a b + a b * /"
    result5 = calc.evaluate(expr5)
    print(f"Expression: {expr5}")
    print(f"Result: {result5}")
    print(f"Explanation: a=10, b=20, then (a+b)/(a*b) = 30/200 = {result5}\n")
    
    print("=== Error Handling Demo ===\n")
    
    # Show how errors are handled
    calc.clear()
    try:
        calc.evaluate("5 0 /")
    except ZeroDivisionError as e:
        print(f"Caught expected error: {e}")
    
    calc.clear()
    try:
        calc.evaluate("+")
    except ValueError as e:
        print(f"Caught expected error: {e}")