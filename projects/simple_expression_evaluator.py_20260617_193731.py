"""
Date: 2026-06-17
Wrote a simple expression evaluator that parses and computes arithmetic expressions with proper operator precedence — wanted something cleaner than eval().
"""

#!/usr/bin/env python3
"""
A simple recursive descent parser for arithmetic expressions.
Supports +, -, *, /, parentheses, and handles operator precedence properly.
I built this because I wanted to understand how parsers work without regex hacks.
"""


class Tokenizer:
    """Breaks an input string into tokens for the parser to consume."""
    
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_token = None
        self.advance()
    
    def advance(self):
        """Move to the next token in the input stream."""
        # Skip whitespace
        while self.pos < len(self.text) and self.text[self.pos].isspace():
            self.pos += 1
        
        if self.pos >= len(self.text):
            self.current_token = None
            return
        
        char = self.text[self.pos]
        
        # Check for numbers (including decimals)
        if char.isdigit() or char == '.':
            start = self.pos
            has_dot = False
            while self.pos < len(self.text):
                c = self.text[self.pos]
                if c.isdigit():
                    self.pos += 1
                elif c == '.' and not has_dot:
                    has_dot = True
                    self.pos += 1
                else:
                    break
            self.current_token = ('NUMBER', float(self.text[start:self.pos]))
        
        # Check for operators and parentheses
        elif char in '+-*/()':
            self.current_token = (char, char)
            self.pos += 1
        
        else:
            raise ValueError(f"Unexpected character: {char}")


class ExpressionEvaluator:
    """
    Recursive descent parser for arithmetic expressions.
    Grammar:
        expression -> term (('+' | '-') term)*
        term       -> factor (('*' | '/') factor)*
        factor     -> NUMBER | '(' expression ')'
    """
    
    def __init__(self, text):
        self.tokenizer = Tokenizer(text)
    
    def parse(self):
        """Parse and evaluate the entire expression."""
        result = self.expression()
        # Make sure we consumed all tokens
        if self.tokenizer.current_token is not None:
            raise ValueError("Unexpected tokens after expression")
        return result
    
    def expression(self):
        """Handle addition and subtraction (lowest precedence)."""
        result = self.term()
        
        while self.tokenizer.current_token is not None:
            token_type, token_value = self.tokenizer.current_token
            
            if token_type == '+':
                self.tokenizer.advance()
                result += self.term()
            elif token_type == '-':
                self.tokenizer.advance()
                result -= self.term()
            else:
                break
        
        return result
    
    def term(self):
        """Handle multiplication and division (higher precedence than +/-)."""
        result = self.factor()
        
        while self.tokenizer.current_token is not None:
            token_type, token_value = self.tokenizer.current_token
            
            if token_type == '*':
                self.tokenizer.advance()
                result *= self.factor()
            elif token_type == '/':
                self.tokenizer.advance()
                divisor = self.factor()
                if divisor == 0:
                    raise ValueError("Division by zero")
                result /= divisor
            else:
                break
        
        return result
    
    def factor(self):
        """Handle numbers and parenthesized expressions (highest precedence)."""
        token = self.tokenizer.current_token
        
        if token is None:
            raise ValueError("Unexpected end of expression")
        
        token_type, token_value = token
        
        if token_type == 'NUMBER':
            self.tokenizer.advance()
            return token_value
        
        elif token_type == '(':
            self.tokenizer.advance()
            result = self.expression()
            
            # Expect closing parenthesis
            if self.tokenizer.current_token is None or self.tokenizer.current_token[0] != ')':
                raise ValueError("Missing closing parenthesis")
            
            self.tokenizer.advance()
            return result
        
        else:
            raise ValueError(f"Unexpected token: {token_type}")


def evaluate(expression):
    """
    Main interface function to evaluate an arithmetic expression.
    Returns the computed result as a float.
    """
    evaluator = ExpressionEvaluator(expression)
    return evaluator.parse()


if __name__ == "__main__":
    # Demo with various test cases to show it actually works
    test_expressions = [
        "2 + 3",
        "10 - 5 * 2",
        "(10 - 5) * 2",
        "3.5 + 2.5 * 4",
        "100 / (5 + 5)",
        "2 + 3 * 4 - 1",
        "((2 + 3) * (4 - 1)) / 3",
    ]
    
    print("Simple Expression Evaluator Demo")
    print("=" * 50)
    
    for expr in test_expressions:
        try:
            result = evaluate(expr)
            print(f"{expr:30s} = {result}")
        except Exception as e:
            print(f"{expr:30s} ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("Testing error handling:")
    
    error_cases = [
        "5 / 0",
        "2 + (3 * 4",
        "2 + + 3",
    ]
    
    for expr in error_cases:
        try:
            result = evaluate(expr)
            print(f"{expr:30s} = {result}")
        except Exception as e:
            print(f"{expr:30s} ERROR: {e}")