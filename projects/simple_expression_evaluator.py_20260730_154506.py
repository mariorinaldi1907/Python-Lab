"""
Date: 2026-07-30
Wrote an expression evaluator that parses and computes arithmetic expressions with proper operator precedence — felt like building a mini compiler.
"""

"""
Simple arithmetic expression evaluator using recursive descent parsing.
Supports +, -, *, /, parentheses, and unary negation.
"""

import re


class Token:
    """Represents a token in the expression."""
    
    def __init__(self, token_type, value):
        self.type = token_type
        self.value = value
    
    def __repr__(self):
        return f"Token({self.type}, {self.value})"


class Lexer:
    """Tokenizes an arithmetic expression string."""
    
    def __init__(self, text):
        self.text = text
        self.pos = 0
    
    def tokenize(self):
        """
        Break the input into tokens.
        Returns a list of Token objects.
        """
        tokens = []
        # Regex to match numbers (including decimals), operators, and parens
        pattern = r'\d+\.?\d*|[+\-*/()]'
        
        for match in re.finditer(pattern, self.text):
            token_str = match.group()
            
            if re.match(r'\d+\.?\d*', token_str):
                tokens.append(Token('NUMBER', float(token_str)))
            elif token_str in '+-*/':
                tokens.append(Token('OPERATOR', token_str))
            elif token_str == '(':
                tokens.append(Token('LPAREN', token_str))
            elif token_str == ')':
                tokens.append(Token('RPAREN', token_str))
        
        tokens.append(Token('EOF', None))
        return tokens


class Parser:
    """
    Recursive descent parser for arithmetic expressions.
    Grammar:
        expression -> term (('+' | '-') term)*
        term -> factor (('*' | '/') factor)*
        factor -> NUMBER | '(' expression ')' | '-' factor
    """
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos]
    
    def advance(self):
        """Move to the next token."""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
    
    def parse(self):
        """Parse and evaluate the entire expression."""
        result = self.expression()
        if self.current_token.type != 'EOF':
            raise SyntaxError(f"Unexpected token: {self.current_token}")
        return result
    
    def expression(self):
        """
        Handle addition and subtraction (lowest precedence).
        This is where the expression evaluation happens recursively.
        """
        result = self.term()
        
        while self.current_token.type == 'OPERATOR' and self.current_token.value in '+-':
            op = self.current_token.value
            self.advance()
            right = self.term()
            
            if op == '+':
                result += right
            else:
                result -= right
        
        return result
    
    def term(self):
        """
        Handle multiplication and division (higher precedence than +/-).
        """
        result = self.factor()
        
        while self.current_token.type == 'OPERATOR' and self.current_token.value in '*/':
            op = self.current_token.value
            self.advance()
            right = self.factor()
            
            if op == '*':
                result *= right
            else:
                if right == 0:
                    raise ZeroDivisionError("Division by zero")
                result /= right
        
        return result
    
    def factor(self):
        """
        Handle numbers, parentheses, and unary negation.
        This is the highest precedence level.
        """
        token = self.current_token
        
        # Handle unary negation
        if token.type == 'OPERATOR' and token.value == '-':
            self.advance()
            return -self.factor()
        
        # Handle parentheses
        if token.type == 'LPAREN':
            self.advance()
            result = self.expression()
            if self.current_token.type != 'RPAREN':
                raise SyntaxError("Expected ')'")
            self.advance()
            return result
        
        # Handle numbers
        if token.type == 'NUMBER':
            self.advance()
            return token.value
        
        raise SyntaxError(f"Unexpected token: {token}")


def evaluate(expression):
    """
    Main entry point to evaluate an arithmetic expression.
    Returns the computed result as a float.
    """
    lexer = Lexer(expression)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()


if __name__ == "__main__":
    # Demo with various test cases
    test_expressions = [
        "3 + 5 * 2",
        "(3 + 5) * 2",
        "10 / 2 - 3",
        "2 + 3 * (4 - 1)",
        "-5 + 3",
        "((2 + 3) * 4) / 5",
        "100 - 50 / 2 + 10 * 3",
    ]
    
    print("=== Simple Expression Evaluator Demo ===\n")
    
    for expr in test_expressions:
        try:
            result = evaluate(expr)
            print(f"{expr:30s} = {result}")
        except Exception as e:
            print(f"{expr:30s} ERROR: {e}")
    
    print("\n=== Interactive Mode (type 'quit' to exit) ===")
    while True:
        try:
            user_input = input("\nEnter expression: ").strip()
            if user_input.lower() in ('quit', 'exit', 'q'):
                print("Goodbye!")
                break
            if not user_input:
                continue
            
            result = evaluate(user_input)
            print(f"Result: {result}")
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")