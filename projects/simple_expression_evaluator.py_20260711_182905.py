"""
Date: 2026-07-11
Wrote an expression evaluator that parses and calculates arithmetic expressions with proper precedence rules — way more elegant than RPN for this use case.
"""

"""
Simple arithmetic expression evaluator using recursive descent parsing.
Handles +, -, *, /, parentheses, and respects operator precedence.

Grammar:
    expression  -> term (('+' | '-') term)*
    term        -> factor (('*' | '/') factor)*
    factor      -> NUMBER | '(' expression ')'
"""

class Token:
    """Represents a single token from the input expression."""
    
    def __init__(self, type, value):
        self.type = type  # 'NUMBER', 'PLUS', 'MINUS', 'MUL', 'DIV', 'LPAREN', 'RPAREN', 'EOF'
        self.value = value
    
    def __repr__(self):
        return f'Token({self.type}, {self.value})'


class Lexer:
    """Tokenizes an arithmetic expression string."""
    
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
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
    
    def read_number(self):
        """Read a multi-digit number (including decimals)."""
        num_str = ''
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            num_str += self.current_char
            self.advance()
        return float(num_str) if '.' in num_str else int(num_str)
    
    def get_next_token(self):
        """
        Lexical analyzer - breaks input into tokens.
        This is where we decide what each character means.
        """
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
                return Token('MUL', '*')
            
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
    """
    Recursive descent parser for arithmetic expressions.
    Implements operator precedence by using separate methods for each precedence level.
    """
    
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
    
    def eat(self, token_type):
        """Consume a token if it matches the expected type, otherwise raise an error."""
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise ValueError(f"Expected {token_type}, got {self.current_token.type}")
    
    def factor(self):
        """
        Parse a factor: either a number or a parenthesized expression.
        This is the highest precedence level.
        """
        token = self.current_token
        
        if token.type == 'NUMBER':
            self.eat('NUMBER')
            return token.value
        elif token.type == 'LPAREN':
            self.eat('LPAREN')
            result = self.expression()  # Recursively parse the inner expression
            self.eat('RPAREN')
            return result
        
        raise ValueError(f"Unexpected token: {token}")
    
    def term(self):
        """
        Parse a term: factors connected by * or /.
        Handles multiplication and division with left-to-right associativity.
        """
        result = self.factor()
        
        while self.current_token.type in ('MUL', 'DIV'):
            op = self.current_token
            if op.type == 'MUL':
                self.eat('MUL')
                result *= self.factor()
            elif op.type == 'DIV':
                self.eat('DIV')
                divisor = self.factor()
                if divisor == 0:
                    raise ValueError("Division by zero")
                result /= divisor
        
        return result
    
    def expression(self):
        """
        Parse an expression: terms connected by + or -.
        This is the lowest precedence level (evaluated last).
        """
        result = self.term()
        
        while self.current_token.type in ('PLUS', 'MINUS'):
            op = self.current_token
            if op.type == 'PLUS':
                self.eat('PLUS')
                result += self.term()
            elif op.type == 'MINUS':
                self.eat('MINUS')
                result -= self.term()
        
        return result


def evaluate(expression):
    """
    Main entry point - evaluate an arithmetic expression string.
    Returns the computed result as a number.
    """
    lexer = Lexer(expression)
    parser = Parser(lexer)
    return parser.expression()


if __name__ == "__main__":
    # Demo with various expressions to show it actually works
    test_expressions = [
        "2 + 3",
        "10 - 4 * 2",
        "(10 - 4) * 2",
        "3.5 + 2.5 * 4",
        "100 / (5 + 5)",
        "2 + 3 * 4 - 6 / 2",
        "((15 + 3) * 2) / 6",
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
    print("Testing edge cases:")
    print("=" * 50)
    
    # Show it handles errors gracefully
    try:
        evaluate("5 / 0")
    except ValueError as e:
        print(f"5 / 0                          ERROR: {e}")
    
    try:
        evaluate("2 + + 3")
    except ValueError as e:
        print(f"2 + + 3                        ERROR: {e}")