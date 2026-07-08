"""
Date: 2026-07-08
Wrote an expression evaluator that parses and computes arithmetic expressions with proper operator precedence using recursive descent parsing.
"""

"""
Simple Expression Evaluator

A recursive descent parser that evaluates arithmetic expressions.
Supports +, -, *, /, parentheses, and respects operator precedence.

Grammar:
    expression := term (('+' | '-') term)*
    term       := factor (('*' | '/') factor)*
    factor     := number | '(' expression ')'
"""

class Token:
    """Represents a single token in the expression."""
    
    def __init__(self, type, value):
        self.type = type  # 'NUMBER', 'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'LPAREN', 'RPAREN', 'EOF'
        self.value = value
    
    def __repr__(self):
        return f"Token({self.type}, {self.value})"


class Lexer:
    """Tokenizes the input string into a stream of tokens."""
    
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
        num_str = ''
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            num_str += self.current_char
            self.advance()
        return float(num_str) if '.' in num_str else int(num_str)
    
    def get_next_token(self):
        """Lexical analyzer - breaks input into tokens."""
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            if self.current_char.isdigit():
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
    """Recursive descent parser that evaluates arithmetic expressions."""
    
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
        """Parse a factor: number or parenthesized expression."""
        token = self.current_token
        
        if token.type == 'NUMBER':
            self.eat('NUMBER')
            return token.value
        elif token.type == 'LPAREN':
            self.eat('LPAREN')
            result = self.expression()
            self.eat('RPAREN')
            return result
        else:
            raise ValueError(f"Unexpected token: {token}")
    
    def term(self):
        """Parse a term: handles * and / with left-to-right associativity."""
        result = self.factor()
        
        while self.current_token.type in ('MULTIPLY', 'DIVIDE'):
            token = self.current_token
            if token.type == 'MULTIPLY':
                self.eat('MULTIPLY')
                result *= self.factor()
            elif token.type == 'DIVIDE':
                self.eat('DIVIDE')
                result /= self.factor()
        
        return result
    
    def expression(self):
        """Parse an expression: handles + and - with left-to-right associativity."""
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
    """
    Evaluate a mathematical expression string.
    
    Args:
        expression: String containing the mathematical expression
    
    Returns:
        The numerical result of evaluating the expression
    """
    lexer = Lexer(expression)
    parser = Parser(lexer)
    return parser.expression()


if __name__ == "__main__":
    # Demo various expressions to show the parser works correctly
    test_expressions = [
        "3 + 5",
        "10 - 2 * 3",
        "(10 - 2) * 3",
        "100 / 4 + 6",
        "2 + 3 * 4 - 5",
        "(2 + 3) * (4 - 5)",
        "15 / (3 + 2)",
        "2.5 + 3.7 * 2",
        "((8 - 2) * 3) + (10 / 5)",
    ]
    
    print("Simple Expression Evaluator Demo")
    print("=" * 50)
    
    for expr in test_expressions:
        try:
            result = evaluate(expr)
            print(f"{expr:30} = {result}")
        except Exception as e:
            print(f"{expr:30} ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("Interactive mode - try your own expressions!")
    print("(Press Ctrl+C or Ctrl+D to exit)\n")
    
    # Simple interactive REPL
    while True:
        try:
            user_input = input(">>> ")
            if user_input.strip():
                result = evaluate(user_input)
                print(f"    {result}")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"    Error: {e}")