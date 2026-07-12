"""
Date: 2026-07-12
Wrote an expression evaluator that parses and computes arithmetic expressions with proper operator precedence — no eval() cheating.
"""

"""
Simple arithmetic expression evaluator using recursive descent parsing.
Supports +, -, *, /, parentheses, and proper operator precedence.
"""

class Token:
    """Represents a single token in the expression."""
    def __init__(self, type, value):
        self.type = type  # 'NUMBER', 'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'LPAREN', 'RPAREN', 'EOF'
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"


class Lexer:
    """Tokenizes the input expression string into a stream of tokens."""
    
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None

    def advance(self):
        """Move to the next character in the input."""
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        """Skip over any whitespace characters."""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def read_number(self):
        """Read a multi-digit number (supports decimals)."""
        result = ''
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            result += self.current_char
            self.advance()
        return float(result)

    def get_next_token(self):
        """Return the next token from the input."""
        while self.current_char is not None:
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
                return Token('MULTIPLY', '*')

            if self.current_char == '/':
                self.advance()
                return Token('DIVIDE', '/')

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
        """Parse a factor: NUMBER | ( expr )"""
        token = self.current_token
        
        if token.type == 'NUMBER':
            self.eat('NUMBER')
            return token.value
        elif token.type == 'LPAREN':
            self.eat('LPAREN')
            result = self.expr()
            self.eat('RPAREN')
            return result
        elif token.type == 'MINUS':
            # Handle unary minus
            self.eat('MINUS')
            return -self.factor()
        else:
            raise ValueError(f"Unexpected token: {token}")

    def term(self):
        """Parse a term: factor ((* | /) factor)*"""
        result = self.factor()

        while self.current_token.type in ('MULTIPLY', 'DIVIDE'):
            token = self.current_token
            if token.type == 'MULTIPLY':
                self.eat('MULTIPLY')
                result *= self.factor()
            elif token.type == 'DIVIDE':
                self.eat('DIVIDE')
                divisor = self.factor()
                if divisor == 0:
                    raise ValueError("Division by zero")
                result /= divisor

        return result

    def expr(self):
        """Parse an expression: term ((+ | -) term)*"""
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


def evaluate(expression):
    """Evaluate a mathematical expression string and return the result."""
    lexer = Lexer(expression)
    parser = Parser(lexer)
    return parser.expr()


if __name__ == "__main__":
    print("Simple Expression Evaluator")
    print("=" * 40)
    
    test_cases = [
        "2 + 3 * 4",
        "(2 + 3) * 4",
        "10 / 2 + 3",
        "100 - 50 / 5",
        "2 * (3 + 4) * 5",
        "((15 / (3 - 2)) + 4) * 2",
        "-5 + 3",
        "1.5 * 2 + 3.5",
    ]
    
    for expr in test_cases:
        try:
            result = evaluate(expr)
            print(f"{expr:30} = {result}")
        except Exception as e:
            print(f"{expr:30} ERROR: {e}")
    
    print("\n" + "=" * 40)
    print("Interactive mode (Ctrl+C to exit):")
    
    while True:
        try:
            user_input = input("\n> ")
            if not user_input.strip():
                continue
            result = evaluate(user_input)
            print(f"Result: {result}")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")