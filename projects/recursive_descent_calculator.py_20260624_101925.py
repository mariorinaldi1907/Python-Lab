"""
Date: 2026-06-24
Wrote a simple expression evaluator using recursive descent parsing because I wanted to understand how compilers handle operator precedence without relying on libraries.
"""

"""
Recursive descent calculator for arithmetic expressions.

Supports +, -, *, /, parentheses, and unary minus.
Grammar:
    expression -> term (('+' | '-') term)*
    term       -> factor (('*' | '/') factor)*
    factor     -> number | '-' factor | '(' expression ')'
"""


class Token:
    """Represents a single token in the expression."""
    
    def __init__(self, type_, value):
        self.type = type_  # 'NUMBER', 'PLUS', 'MINUS', 'MULT', 'DIV', 'LPAREN', 'RPAREN', 'EOF'
        self.value = value
    
    def __repr__(self):
        return f"Token({self.type}, {self.value})"


class Lexer:
    """Tokenizes an arithmetic expression string."""
    
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[0] if text else None
    
    def advance(self):
        """Move to the next character in the input."""
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
    
    def skip_whitespace(self):
        """Skip over whitespace characters."""
        while self.current_char and self.current_char.isspace():
            self.advance()
    
    def read_number(self):
        """Read a multi-digit number (supports decimals)."""
        num_str = ''
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            num_str += self.current_char
            self.advance()
        return float(num_str)
    
    def get_next_token(self):
        """Lexical analyzer - breaks input into tokens."""
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            if self.current_char.isdigit() or self.current_char == '.':
                return Token('NUMBER', self.read_number())
            
            if self.current_char == '+':
                self.advance()
                return Token('PLUS', '+')
            
            if self.current_char == '-':
                self.advance()
                return Token('MINUS', '-')
            
            if self.current_char == '*':
                self.advance()
                return Token('MULT', '*')
            
            if self.current_char == '/':
                self.advance()
                return Token('DIV', '/')
            
            if self.current_char == '(':
                self.advance()
                return Token('LPAREN', '(')
            
            if self.current_char == ')':
                self.advance()
                return Token('RPAREN', ')')
            
            raise ValueError(f"Invalid character: {self.current_char}")
        
        return Token('EOF', None)


class Parser:
    """Recursive descent parser for arithmetic expressions."""
    
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
    
    def eat(self, token_type):
        """Consume the current token if it matches the expected type."""
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise ValueError(f"Expected {token_type}, got {self.current_token.type}")
    
    def factor(self):
        """Parse a factor: number | -factor | (expression)."""
        token = self.current_token
        
        if token.type == 'NUMBER':
            self.eat('NUMBER')
            return token.value
        elif token.type == 'MINUS':
            # Unary minus
            self.eat('MINUS')
            return -self.factor()
        elif token.type == 'LPAREN':
            self.eat('LPAREN')
            result = self.expression()
            self.eat('RPAREN')
            return result
        
        raise ValueError(f"Unexpected token: {token}")
    
    def term(self):
        """Parse a term: factor ((* | /) factor)*."""
        result = self.factor()
        
        while self.current_token.type in ('MULT', 'DIV'):
            token = self.current_token
            if token.type == 'MULT':
                self.eat('MULT')
                result *= self.factor()
            elif token.type == 'DIV':
                self.eat('DIV')
                divisor = self.factor()
                if divisor == 0:
                    raise ValueError("Division by zero")
                result /= divisor
        
        return result
    
    def expression(self):
        """Parse an expression: term ((+ | -) term)*."""
        result = self.term()
        
        while self.current_token.type in ('PLUS', 'MINUS'):
            token = self.current_token
            if token.type == 'PLUS':
                self.eat('PLUS')
                result += self.term()
            elif token.type == 'MINUS':
                self.eat('MINUS')
                result -= self.term()
        
        return result
    
    def parse(self):
        """Start parsing and return the result."""
        result = self.expression()
        if self.current_token.type != 'EOF':
            raise ValueError("Unexpected characters after expression")
        return result


def evaluate(expression):
    """Evaluate an arithmetic expression string and return the result."""
    lexer = Lexer(expression)
    parser = Parser(lexer)
    return parser.parse()


if __name__ == "__main__":
    # Demo with various expressions to show off the parser
    test_expressions = [
        "3 + 5 * 2",
        "(3 + 5) * 2",
        "10 - 2 * 3",
        "100 / (10 + 5)",
        "-5 + 3",
        "2 * -3 + 10",
        "(2 + 3) * (4 - 1)",
        "10 / 2 / 5",
        "1.5 * 2.0 + 3.14",
    ]
    
    print("Recursive Descent Calculator Demo")
    print("=" * 50)
    
    for expr in test_expressions:
        try:
            result = evaluate(expr)
            print(f"{expr:30} = {result}")
        except Exception as e:
            print(f"{expr:30} ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("Interactive mode - enter expressions (or 'quit' to exit):")
    
    while True:
        try:
            user_input = input("\n> ").strip()
            if user_input.lower() in ('quit', 'exit', 'q'):
                print("Goodbye!")
                break
            if user_input:
                result = evaluate(user_input)
                print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")