"""
Date: 2026-08-26
Wrote an expression evaluator that parses and computes arithmetic expressions with proper operator precedence — something I always wanted to understand deeply.
"""

"""
Simple expression evaluator using recursive descent parsing.
Supports +, -, *, /, parentheses, and unary minus.
"""

import re
from typing import List, Union


class Token:
    """Represents a single token in the expression."""
    
    def __init__(self, token_type: str, value: Union[str, float]):
        self.type = token_type  # 'NUMBER', 'PLUS', 'MINUS', 'MULT', 'DIV', 'LPAREN', 'RPAREN', 'EOF'
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"


class Lexer:
    """Tokenizes an input expression string into a list of tokens."""
    
    def __init__(self, text: str):
        self.text = text.replace(' ', '')  # Remove whitespace for simplicity
        self.pos = 0
    
    def tokenize(self) -> List[Token]:
        """Break the input into tokens we can parse."""
        tokens = []
        
        while self.pos < len(self.text):
            char = self.text[self.pos]
            
            # Check if it's a number (including decimals)
            if char.isdigit() or char == '.':
                tokens.append(self._read_number())
            elif char == '+':
                tokens.append(Token('PLUS', char))
                self.pos += 1
            elif char == '-':
                tokens.append(Token('MINUS', char))
                self.pos += 1
            elif char == '*':
                tokens.append(Token('MULT', char))
                self.pos += 1
            elif char == '/':
                tokens.append(Token('DIV', char))
                self.pos += 1
            elif char == '(':
                tokens.append(Token('LPAREN', char))
                self.pos += 1
            elif char == ')':
                tokens.append(Token('RPAREN', char))
                self.pos += 1
            else:
                raise ValueError(f"Unknown character: {char}")
        
        tokens.append(Token('EOF', None))
        return tokens
    
    def _read_number(self) -> Token:
        """Read a full number including decimals."""
        num_str = ''
        while self.pos < len(self.text) and (self.text[self.pos].isdigit() or self.text[self.pos] == '.'):
            num_str += self.text[self.pos]
            self.pos += 1
        return Token('NUMBER', float(num_str))


class Parser:
    """
    Recursive descent parser for arithmetic expressions.
    Grammar (from lowest to highest precedence):
        expression: term ((PLUS | MINUS) term)*
        term: factor ((MULT | DIV) factor)*
        factor: (PLUS | MINUS) factor | NUMBER | LPAREN expression RPAREN
    """
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos]
    
    def advance(self):
        """Move to the next token."""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
    
    def parse(self) -> float:
        """Entry point for parsing — returns the computed result."""
        result = self.expression()
        if self.current_token.type != 'EOF':
            raise ValueError(f"Unexpected token: {self.current_token}")
        return result
    
    def expression(self) -> float:
        """Handle addition and subtraction (lowest precedence)."""
        result = self.term()
        
        while self.current_token.type in ('PLUS', 'MINUS'):
            op = self.current_token.type
            self.advance()
            if op == 'PLUS':
                result += self.term()
            else:
                result -= self.term()
        
        return result
    
    def term(self) -> float:
        """Handle multiplication and division (higher precedence)."""
        result = self.factor()
        
        while self.current_token.type in ('MULT', 'DIV'):
            op = self.current_token.type
            self.advance()
            if op == 'MULT':
                result *= self.factor()
            else:
                divisor = self.factor()
                if divisor == 0:
                    raise ValueError("Division by zero")
                result /= divisor
        
        return result
    
    def factor(self) -> float:
        """Handle unary operators, numbers, and parentheses (highest precedence)."""
        token = self.current_token
        
        # Unary plus or minus
        if token.type == 'PLUS':
            self.advance()
            return +self.factor()
        elif token.type == 'MINUS':
            self.advance()
            return -self.factor()
        elif token.type == 'NUMBER':
            self.advance()
            return token.value
        elif token.type == 'LPAREN':
            self.advance()
            result = self.expression()  # Recursively parse the expression inside parens
            if self.current_token.type != 'RPAREN':
                raise ValueError("Expected closing parenthesis")
            self.advance()
            return result
        else:
            raise ValueError(f"Unexpected token: {token}")


def evaluate(expression: str) -> float:
    """
    Main function to evaluate an arithmetic expression.
    This is what you'd actually call from outside.
    """
    lexer = Lexer(expression)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()


if __name__ == "__main__":
    # Demo expressions to show it works
    test_cases = [
        "3 + 5",
        "10 - 2 * 3",
        "(10 - 2) * 3",
        "100 / (5 + 5)",
        "-3 + 5",
        "2 * (3 + 4) * 5",
        "3.14 * 2",
        "((2 + 3) * 4) / (5 - 3)",
    ]
    
    print("Simple Expression Evaluator")
    print("=" * 40)
    
    for expr in test_cases:
        try:
            result = evaluate(expr)
            print(f"{expr:30s} = {result}")
        except Exception as e:
            print(f"{expr:30s} ERROR: {e}")
    
    print("\nTry it yourself:")
    while True:
        try:
            user_input = input(">>> ")
            if user_input.lower() in ('quit', 'exit', 'q'):
                break
            result = evaluate(user_input)
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")