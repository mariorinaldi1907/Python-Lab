"""
Date: 2026-07-30
Wrote a simple expression evaluator using recursive descent parsing because I wanted to understand how parsers actually work under the hood.
"""

#!/usr/bin/env python3
"""
Recursive descent calculator that parses and evaluates arithmetic expressions.
Supports +, -, *, /, parentheses, and respects operator precedence.
"""

import re


class Tokenizer:
    """Breaks up an input string into tokens (numbers, operators, parentheses)."""
    
    def __init__(self, text):
        """
        Initialize tokenizer with input text.
        
        Args:
            text: String containing the arithmetic expression
        """
        self.text = text
        self.pos = 0
        self.current_token = None
        
    def tokenize(self):
        """
        Generator that yields tokens one at a time.
        Skips whitespace and recognizes numbers, operators, and parens.
        """
        # Regex pattern: matches floats/ints, operators, or parentheses
        pattern = r'\d+\.?\d*|[+\-*/()]'
        tokens = re.findall(pattern, self.text.replace(' ', ''))
        
        for token in tokens:
            if re.match(r'\d+\.?\d*', token):
                yield ('NUMBER', float(token))
            else:
                yield ('OP', token)
        
        yield ('EOF', None)


class Parser:
    """
    Recursive descent parser for arithmetic expressions.
    Grammar:
        expression → term (('+' | '-') term)*
        term → factor (('*' | '/') factor)*
        factor → NUMBER | '(' expression ')'
    """
    
    def __init__(self, tokenizer):
        """
        Initialize parser with a tokenizer.
        
        Args:
            tokenizer: Tokenizer instance that provides tokens
        """
        self.tokenizer = tokenizer
        self.tokens = list(self.tokenizer.tokenize())
        self.pos = 0
        self.current_token = self.tokens[0] if self.tokens else ('EOF', None)
    
    def advance(self):
        """Move to the next token in the stream."""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = ('EOF', None)
    
    def parse_expression(self):
        """
        Parse an expression (handles addition and subtraction).
        This is the top-level parsing function.
        """
        result = self.parse_term()
        
        # Keep consuming + and - operators (left-associative)
        while self.current_token[0] == 'OP' and self.current_token[1] in ['+', '-']:
            op = self.current_token[1]
            self.advance()
            right = self.parse_term()
            
            if op == '+':
                result += right
            else:
                result -= right
        
        return result
    
    def parse_term(self):
        """
        Parse a term (handles multiplication and division).
        Higher precedence than expression, so it's called by parse_expression.
        """
        result = self.parse_factor()
        
        # Keep consuming * and / operators (left-associative)
        while self.current_token[0] == 'OP' and self.current_token[1] in ['*', '/']:
            op = self.current_token[1]
            self.advance()
            right = self.parse_factor()
            
            if op == '*':
                result *= right
            else:
                if right == 0:
                    raise ValueError("Division by zero")
                result /= right
        
        return result
    
    def parse_factor(self):
        """
        Parse a factor (either a number or a parenthesized expression).
        This is the highest precedence level.
        """
        token_type, token_value = self.current_token
        
        if token_type == 'NUMBER':
            self.advance()
            return token_value
        elif token_type == 'OP' and token_value == '(':
            self.advance()  # consume '('
            result = self.parse_expression()  # recursively parse what's inside
            
            if self.current_token[1] != ')':
                raise SyntaxError("Expected closing parenthesis")
            
            self.advance()  # consume ')'
            return result
        else:
            raise SyntaxError(f"Unexpected token: {token_value}")


def evaluate(expression):
    """
    Main entry point: tokenize and parse an arithmetic expression.
    
    Args:
        expression: String containing the arithmetic expression
        
    Returns:
        Numerical result of evaluating the expression
    """
    tokenizer = Tokenizer(expression)
    parser = Parser(tokenizer)
    return parser.parse_expression()


if __name__ == "__main__":
    # Demo expressions showing various features
    test_cases = [
        "3 + 5",
        "10 - 2 * 3",
        "(10 - 2) * 3",
        "100 / 4 / 5",
        "2 + 3 * 4 - 5",
        "(2 + 3) * (4 - 1)",
        "15.5 + 2.5 * 4",
        "((5 + 3) * 2) / 4",
    ]
    
    print("=== Recursive Descent Calculator ===\n")
    
    for expr in test_cases:
        try:
            result = evaluate(expr)
            print(f"{expr:25} = {result}")
        except Exception as e:
            print(f"{expr:25} ERROR: {e}")
    
    # Interactive mode hint
    print("\n--- Try it yourself ---")
    print("Example: evaluate('(10 + 5) * 2 - 3')")