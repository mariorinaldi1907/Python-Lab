"""
Date: 2026-07-18
Wrote a simple expression evaluator that parses and computes arithmetic expressions with proper operator precedence — wanted to understand how parsers actually work under the hood.
"""

"""
Simple expression evaluator using recursive descent parsing.

Supports:
- Basic arithmetic: +, -, *, /, ** (power)
- Parentheses for grouping
- Unary minus
- Proper operator precedence

Grammar:
    expression := term (('+' | '-') term)*
    term       := factor (('*' | '/') factor)*
    factor     := power (('**') power)*
    power      := unary
    unary      := ('-')? atom
    atom       := NUMBER | '(' expression ')'
"""

import re
from typing import Union


class Token:
    """Represents a single token in the expression."""
    
    def __init__(self, type_: str, value: Union[str, float]):
        self.type = type_
        self.value = value
    
    def __repr__(self):
        return f"Token({self.type}, {self.value})"


class Lexer:
    """Tokenizes mathematical expressions into a stream of tokens."""
    
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
    
    def tokenize(self) -> list[Token]:
        """Break the input string into tokens for parsing."""
        tokens = []
        # Pattern matches numbers (including decimals) and operators
        pattern = r'\d+\.?\d*|[+\-*/()^]|\*\*'
        
        for match in re.finditer(pattern, self.text):
            value = match.group()
            
            if re.match(r'\d+\.?\d*', value):
                tokens.append(Token('NUMBER', float(value)))
            elif value == '**':
                tokens.append(Token('POWER', value))
            elif value in '+-*/()':
                tokens.append(Token(value, value))
        
        tokens.append(Token('EOF', None))
        return tokens


class Parser:
    """Recursive descent parser for arithmetic expressions."""
    
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = tokens[0]
    
    def advance(self):
        """Move to the next token in the stream."""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
    
    def parse(self) -> float:
        """Entry point for parsing — returns the evaluated result."""
        result = self.expression()
        if self.current_token.type != 'EOF':
            raise SyntaxError(f"Unexpected token: {self.current_token}")
        return result
    
    def expression(self) -> float:
        """Handle addition and subtraction (lowest precedence)."""
        result = self.term()
        
        while self.current_token.type in ('+', '-'):
            op = self.current_token.type
            self.advance()
            if op == '+':
                result += self.term()
            else:
                result -= self.term()
        
        return result
    
    def term(self) -> float:
        """Handle multiplication and division."""
        result = self.factor()
        
        while self.current_token.type in ('*', '/'):
            op = self.current_token.type
            self.advance()
            if op == '*':
                result *= self.factor()
            else:
                divisor = self.factor()
                if divisor == 0:
                    raise ZeroDivisionError("Cannot divide by zero")
                result /= divisor
        
        return result
    
    def factor(self) -> float:
        """Handle exponentiation (right-associative, so we use recursion differently)."""
        result = self.unary()
        
        if self.current_token.type == 'POWER':
            self.advance()
            # Right-associative: 2**3**2 = 2**(3**2) = 512
            result = result ** self.factor()
        
        return result
    
    def unary(self) -> float:
        """Handle unary minus."""
        if self.current_token.type == '-':
            self.advance()
            return -self.unary()
        return self.atom()
    
    def atom(self) -> float:
        """Handle numbers and parenthesized expressions."""
        token = self.current_token
        
        if token.type == 'NUMBER':
            self.advance()
            return token.value
        elif token.type == '(':
            self.advance()
            result = self.expression()
            if self.current_token.type != ')':
                raise SyntaxError("Expected closing parenthesis")
            self.advance()
            return result
        else:
            raise SyntaxError(f"Unexpected token: {token}")


def evaluate(expression: str) -> float:
    """
    Evaluate a mathematical expression and return the result.
    
    This is the main entry point — tokenize, parse, and compute.
    """
    lexer = Lexer(expression)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()


if __name__ == "__main__":
    # Test cases showing various features
    test_expressions = [
        "3 + 5 * 2",
        "(3 + 5) * 2",
        "10 / 2 - 3",
        "2 ** 3",
        "2 ** 3 ** 2",  # Should be 2^(3^2) = 512
        "-5 + 3",
        "-(10 - 4) * 2",
        "3.14 * 2",
        "100 / (5 * 2)",
        "((2 + 3) * 4) ** 2",
    ]
    
    print("=== Simple Expression Evaluator ===\n")
    
    for expr in test_expressions:
        try:
            result = evaluate(expr)
            print(f"{expr:25} = {result}")
        except Exception as e:
            print(f"{expr:25} ERROR: {e}")
    
    # Interactive mode demo
    print("\n--- Interactive mode (enter 'quit' to exit) ---")
    print("Try: 2 + 2 * 3, (10 - 5) ** 2, etc.\n")
    
    while True:
        try:
            user_input = input(">>> ").strip()
            if user_input.lower() in ('quit', 'exit', 'q'):
                break
            if not user_input:
                continue
            result = evaluate(user_input)
            print(f"  = {result}\n")
        except EOFError:
            break
        except Exception as e:
            print(f"  Error: {e}\n")