"""
Date: 2026-07-28
Wrote a simple expression evaluator that parses and evaluates mathematical expressions with proper operator precedence — wanted to understand how parsers actually work under the hood.
"""

"""
Simple arithmetic expression evaluator using recursive descent parsing.

Supports +, -, *, /, parentheses, and unary minus.
Uses proper operator precedence (multiplication/division before addition/subtraction).
"""

import re


class Tokenizer:
    """
    Breaks an input string into tokens (numbers, operators, parentheses).
    
    I built this to handle the lexical analysis phase — splitting the raw input
    into meaningful chunks before we try to parse the structure.
    """
    
    TOKEN_PATTERN = r'\d+\.?\d*|[+\-*/()]'
    
    def __init__(self, expression):
        """Initialize with an expression string."""
        self.tokens = re.findall(self.TOKEN_PATTERN, expression.replace(' ', ''))
        self.position = 0
    
    def peek(self):
        """Look at the current token without consuming it."""
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None
    
    def consume(self):
        """Get the current token and move to the next one."""
        token = self.peek()
        self.position += 1
        return token
    
    def has_more(self):
        """Check if there are more tokens to process."""
        return self.position < len(self.tokens)


class ExpressionEvaluator:
    """
    Recursive descent parser and evaluator for arithmetic expressions.
    
    Grammar (in order of precedence, lowest to highest):
      expression := term (('+' | '-') term)*
      term       := factor (('*' | '/') factor)*
      factor     := number | '(' expression ')' | '-' factor
    
    The recursive structure naturally handles operator precedence because
    we parse higher-precedence operations deeper in the recursion tree.
    """
    
    def __init__(self, tokenizer):
        """Initialize with a tokenizer instance."""
        self.tokenizer = tokenizer
    
    def parse_expression(self):
        """
        Parse an expression: handles addition and subtraction.
        
        This is the lowest precedence level, so it gets evaluated last
        (after multiplication/division are already resolved).
        """
        result = self.parse_term()
        
        while self.tokenizer.peek() in ('+', '-'):
            operator = self.tokenizer.consume()
            right = self.parse_term()
            if operator == '+':
                result += right
            else:
                result -= right
        
        return result
    
    def parse_term(self):
        """
        Parse a term: handles multiplication and division.
        
        Higher precedence than addition/subtraction, so we recurse here
        before returning to parse_expression.
        """
        result = self.parse_factor()
        
        while self.tokenizer.peek() in ('*', '/'):
            operator = self.tokenizer.consume()
            right = self.parse_factor()
            if operator == '*':
                result *= right
            else:
                # Handle division by zero gracefully
                if right == 0:
                    raise ValueError("Division by zero")
                result /= right
        
        return result
    
    def parse_factor(self):
        """
        Parse a factor: handles numbers, parentheses, and unary minus.
        
        This is the highest precedence level — we handle atomic values
        and grouping here.
        """
        token = self.tokenizer.peek()
        
        # Handle parentheses — recursively parse the inside as a new expression
        if token == '(':
            self.tokenizer.consume()
            result = self.parse_expression()
            if self.tokenizer.peek() != ')':
                raise ValueError("Mismatched parentheses")
            self.tokenizer.consume()
            return result
        
        # Handle unary minus
        if token == '-':
            self.tokenizer.consume()
            return -self.parse_factor()
        
        # Must be a number at this point
        if token and token not in ('+', '-', '*', '/', '(', ')'):
            self.tokenizer.consume()
            try:
                # Support both integers and floats
                return float(token)
            except ValueError:
                raise ValueError(f"Invalid token: {token}")
        
        raise ValueError(f"Unexpected token: {token}")


def evaluate(expression):
    """
    Main entry point: evaluate an arithmetic expression string.
    
    Returns the numerical result as a float.
    """
    if not expression or not expression.strip():
        raise ValueError("Empty expression")
    
    tokenizer = Tokenizer(expression)
    evaluator = ExpressionEvaluator(tokenizer)
    result = evaluator.parse_expression()
    
    # Make sure we consumed all tokens (detect trailing garbage)
    if tokenizer.has_more():
        raise ValueError(f"Unexpected token at end: {tokenizer.peek()}")
    
    return result


if __name__ == "__main__":
    # Demo with various test cases to show it actually works
    test_expressions = [
        "3 + 4 * 2",           # Should be 11 (not 14)
        "(3 + 4) * 2",         # Should be 14
        "10 / 2 - 3",          # Should be 2
        "-5 + 3",              # Should be -2
        "2 * -3",              # Should be -6
        "100 / (2 + 3) / 2",   # Should be 10
        "1 + 2 * 3 - 4 / 2",   # Should be 5
        "((2 + 3) * 4) - 5",   # Should be 15
    ]
    
    print("=== Simple Expression Evaluator Demo ===\n")
    
    for expr in test_expressions:
        try:
            result = evaluate(expr)
            print(f"{expr:25} = {result}")
        except Exception as e:
            print(f"{expr:25} ERROR: {e}")
    
    print("\n=== Error Handling Demo ===\n")
    
    error_cases = [
        "3 + + 4",       # Double operator
        "5 * (2 + 3",    # Mismatched parens
        "10 / 0",        # Division by zero
    ]
    
    for expr in error_cases:
        try:
            result = evaluate(expr)
            print(f"{expr:25} = {result}")
        except Exception as e:
            print(f"{expr:25} ERROR: {e}")