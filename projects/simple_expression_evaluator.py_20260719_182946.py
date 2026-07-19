"""
Date: 2026-07-19
Wrote an expression evaluator that parses and computes arithmetic with proper operator precedence — way more elegant than RPN for this use case.
"""

#!/usr/bin/env python3
"""
Simple expression evaluator using recursive descent parsing.
Supports +, -, *, /, parentheses, and respects operator precedence.
"""

import re


class Tokenizer:
    """
    Breaks an input string into tokens (numbers, operators, parens).
    """
    
    def __init__(self, expression):
        """Initialize with an expression string."""
        self.expression = expression.replace(' ', '')  # strip whitespace
        self.tokens = []
        self.position = 0
        self._tokenize()
    
    def _tokenize(self):
        """
        Convert the expression into a list of tokens.
        Uses regex to match numbers (including decimals) and single-char operators.
        """
        # Match numbers (int or float) or single characters (operators/parens)
        token_pattern = r'\d+\.?\d*|[+\-*/()]'
        self.tokens = re.findall(token_pattern, self.expression)
    
    def peek(self):
        """Look at the current token without consuming it."""
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None
    
    def consume(self):
        """Return the current token and move to the next one."""
        token = self.peek()
        self.position += 1
        return token


class ExpressionEvaluator:
    """
    Recursive descent parser for arithmetic expressions.
    Grammar:
        expression := term (('+' | '-') term)*
        term := factor (('*' | '/') factor)*
        factor := number | '(' expression ')'
    """
    
    def __init__(self, tokenizer):
        """Initialize with a tokenizer instance."""
        self.tokenizer = tokenizer
    
    def parse(self):
        """Entry point for parsing — returns the evaluated result."""
        return self._expression()
    
    def _expression(self):
        """
        Parse addition and subtraction (lowest precedence).
        Handles chains like: 1 + 2 - 3 + 4
        """
        result = self._term()
        
        while self.tokenizer.peek() in ('+', '-'):
            op = self.tokenizer.consume()
            right = self._term()
            if op == '+':
                result += right
            else:
                result -= right
        
        return result
    
    def _term(self):
        """
        Parse multiplication and division (higher precedence than +/-).
        Handles chains like: 2 * 3 / 4 * 5
        """
        result = self._factor()
        
        while self.tokenizer.peek() in ('*', '/'):
            op = self.tokenizer.consume()
            right = self._factor()
            if op == '*':
                result *= right
            else:
                # Avoid integer division — keep as float
                result /= right
        
        return result
    
    def _factor(self):
        """
        Parse numbers or parenthesized expressions (highest precedence).
        Recursively calls _expression() for anything in parens.
        """
        token = self.tokenizer.peek()
        
        if token == '(':
            self.tokenizer.consume()  # eat the '('
            result = self._expression()  # recursively parse what's inside
            self.tokenizer.consume()  # eat the ')'
            return result
        else:
            # It's a number
            self.tokenizer.consume()
            return float(token)


def evaluate(expression):
    """
    Main function to evaluate a mathematical expression string.
    Returns the computed result as a float.
    """
    tokenizer = Tokenizer(expression)
    evaluator = ExpressionEvaluator(tokenizer)
    return evaluator.parse()


if __name__ == "__main__":
    # Demo: test a bunch of expressions to show off precedence and parentheses
    test_cases = [
        "3 + 5",
        "10 - 2 * 3",
        "(10 - 2) * 3",
        "100 / 4 / 5",
        "2 + 3 * 4 - 5",
        "(2 + 3) * (4 - 5)",
        "7 + (6 * 5 - 3) / 2",
        "3.5 + 2.5 * 2",
        "((1 + 2) * (3 + 4)) / 5",
    ]
    
    print("Expression Evaluator Demo")
    print("=" * 50)
    
    for expr in test_cases:
        result = evaluate(expr)
        print(f"{expr:30s} = {result}")
    
    print("\n" + "=" * 50)
    print("All tests completed successfully!")