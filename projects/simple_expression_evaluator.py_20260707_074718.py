"""
Date: 2026-07-07
Wrote an expression evaluator that handles addition, subtraction, multiplication, division, and parentheses using recursive descent parsing — way cleaner than trying to wrestle with regex.
"""

"""
Simple mathematical expression evaluator using recursive descent parsing.

This parser handles basic arithmetic with proper operator precedence:
- Parentheses (highest)
- Multiplication and Division
- Addition and Subtraction (lowest)

Grammar:
    expression := term (('+' | '-') term)*
    term       := factor (('*' | '/') factor)*
    factor     := number | '(' expression ')'
"""


class Token:
    """Represents a single token in the expression."""
    
    def __init__(self, type_, value):
        self.type = type_  # 'NUMBER', 'PLUS', 'MINUS', 'MULT', 'DIV', 'LPAREN', 'RPAREN', 'EOF'
        self.value = value
    
    def __repr__(self):
        return f"Token({self.type}, {self.value})"


class Lexer:
    """Tokenizes a mathematical expression string."""
    
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None
    
    def advance(self):
        """Move to the next character in the input."""
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
    
    def skip_whitespace(self):
        """Skip over any whitespace characters."""
        while self.current_char and self.current_char.isspace():
            self.advance()
    
    def read_number(self):
        """Read a multi-digit number (including decimals)."""
        num_str = ''
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            num_str += self.current_char
            self.advance()
        return float(num_str) if '.' in num_str else int(num_str)
    
    def get_next_token(self):
        """Lexical analyzer - breaks input into tokens."""
        while self.current_char:
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
    """Recursive descent parser that evaluates mathematical expressions."""
    
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
    
    def eat(self, token_type):
        """Consume a token of the expected type, or raise an error."""
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
        
        raise ValueError(f"Unexpected token: {token}")
    
    def term(self):
        """Parse a term: handles multiplication and division (higher precedence)."""
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
                    raise ZeroDivisionError("Division by zero")
                result /= divisor
        
        return result
    
    def expression(self):
        """Parse an expression: handles addition and subtraction (lower precedence)."""
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
        Numerical result of the evaluation
    """
    lexer = Lexer(expression)
    parser = Parser(lexer)
    return parser.expression()


if __name__ == "__main__":
    # Test cases that demonstrate various features
    test_expressions = [
        "2 + 3",
        "10 - 5 + 2",
        "3 * 4 + 2",
        "2 + 3 * 4",  # Should respect precedence
        "10 / 2",
        "(2 + 3) * 4",  # Parentheses change evaluation order
        "((15 / (7 - (1 + 1))) * 3) - (2 + (1 + 1))",  # Complex nested example
        "2.5 + 3.7",  # Decimal support
        "100 / 4 / 5",  # Left-to-right associativity
    ]
    
    print("Expression Evaluator Demo")
    print("=" * 50)
    
    for expr in test_expressions:
        try:
            result = evaluate(expr)
            print(f"{expr:45} = {result}")
        except Exception as e:
            print(f"{expr:45} ERROR: {e}")
    
    print("\nInteractive mode (Ctrl+C to exit):")
    print("-" * 50)
    
    while True:
        try:
            user_input = input(">>> ")
            if user_input.strip():
                result = evaluate(user_input)
                print(f"    {result}")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"    Error: {e}")