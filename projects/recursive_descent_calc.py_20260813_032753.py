"""
Date: 2026-08-13
Wrote a simple expression evaluator using recursive descent parsing because I wanted to understand how parsers actually work under the hood.
"""

#!/usr/bin/env python3
"""
A simple math expression evaluator using recursive descent parsing.
Supports +, -, *, /, parentheses, and handles operator precedence properly.

Grammar:
    expression  -> term (('+' | '-') term)*
    term        -> factor (('*' | '/') factor)*
    factor      -> NUMBER | '(' expression ')'
"""


class Tokenizer:
    """Breaks an input string into tokens for the parser to consume."""
    
    def __init__(self, text):
        self.text = text.replace(' ', '')  # strip all whitespace for simplicity
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None
    
    def advance(self):
        """Move to the next character in the input."""
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None
    
    def peek_number(self):
        """Extract a full number (integer or float) from current position."""
        num_str = ''
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            num_str += self.current_char
            self.advance()
        return float(num_str)


class Parser:
    """Recursive descent parser that evaluates mathematical expressions."""
    
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
    
    def parse(self):
        """Entry point: parse and evaluate the entire expression."""
        result = self.expression()
        # Make sure we've consumed all input
        if self.tokenizer.current_char is not None:
            raise ValueError(f"Unexpected character: {self.tokenizer.current_char}")
        return result
    
    def expression(self):
        """
        Handle addition and subtraction (lowest precedence).
        expression -> term (('+' | '-') term)*
        """
        result = self.term()
        
        while self.tokenizer.current_char in ('+', '-'):
            op = self.tokenizer.current_char
            self.tokenizer.advance()
            if op == '+':
                result += self.term()
            else:
                result -= self.term()
        
        return result
    
    def term(self):
        """
        Handle multiplication and division (higher precedence than +/-).
        term -> factor (('*' | '/') factor)*
        """
        result = self.factor()
        
        while self.tokenizer.current_char in ('*', '/'):
            op = self.tokenizer.current_char
            self.tokenizer.advance()
            if op == '*':
                result *= self.factor()
            else:
                divisor = self.factor()
                if divisor == 0:
                    raise ZeroDivisionError("Cannot divide by zero")
                result /= divisor
        
        return result
    
    def factor(self):
        """
        Handle numbers and parenthesized expressions (highest precedence).
        factor -> NUMBER | '(' expression ')'
        """
        char = self.tokenizer.current_char
        
        # Handle parentheses
        if char == '(':
            self.tokenizer.advance()  # consume '('
            result = self.expression()  # recursively evaluate inside parens
            if self.tokenizer.current_char != ')':
                raise ValueError("Missing closing parenthesis")
            self.tokenizer.advance()  # consume ')'
            return result
        
        # Handle unary minus
        elif char == '-':
            self.tokenizer.advance()
            return -self.factor()
        
        # Handle unary plus (just ignore it)
        elif char == '+':
            self.tokenizer.advance()
            return self.factor()
        
        # Must be a number
        elif char is not None and (char.isdigit() or char == '.'):
            return self.tokenizer.peek_number()
        
        else:
            raise ValueError(f"Unexpected character in factor: {char}")


def evaluate(expression):
    """
    Main entry point: evaluate a mathematical expression string.
    
    Args:
        expression: String containing a math expression like "3 + 4 * (2 - 1)"
    
    Returns:
        The numeric result of evaluating the expression.
    """
    tokenizer = Tokenizer(expression)
    parser = Parser(tokenizer)
    return parser.parse()


if __name__ == "__main__":
    # Test cases showing various features
    test_expressions = [
        "3 + 4",
        "10 - 2 * 3",
        "(10 - 2) * 3",
        "2 + 3 * 4 - 5",
        "100 / (5 * 2)",
        "((2 + 3) * 4) - 1",
        "-5 + 3",
        "3.14 * 2",
        "-(3 + 4) * 2",
        "1 + 2 + 3 + 4 + 5",
    ]
    
    print("=" * 50)
    print("Recursive Descent Expression Evaluator")
    print("=" * 50)
    print()
    
    for expr in test_expressions:
        try:
            result = evaluate(expr)
            print(f"{expr:25} = {result}")
        except Exception as e:
            print(f"{expr:25} ERROR: {e}")
    
    print()
    print("=" * 50)
    
    # Show that it catches errors properly
    print("\nError handling examples:")
    error_cases = [
        "3 + + 4",
        "5 * (2 + 3",
        "10 / 0",
    ]
    
    for expr in error_cases:
        try:
            result = evaluate(expr)
            print(f"{expr:25} = {result}")
        except Exception as e:
            print(f"{expr:25} ERROR: {type(e).__name__}: {e}")