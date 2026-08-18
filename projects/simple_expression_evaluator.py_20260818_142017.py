"""
Date: 2026-08-18
Wrote an expression evaluator that parses and computes arithmetic with proper operator precedence using recursive descent — way cleaner than RPN for this use case.
"""

"""
Simple expression evaluator using recursive descent parsing.
Handles +, -, *, /, parentheses, and respects operator precedence.
I wanted to understand how parsers work under the hood without using eval().
"""

class Lexer:
    """
    Tokenizes an input string into numbers and operators.
    Strips whitespace and validates characters along the way.
    """
    def __init__(self, text):
        self.text = text.replace(' ', '')  # removing spaces makes life easier
        self.pos = 0
        
    def peek(self):
        """Look at current character without consuming it."""
        if self.pos < len(self.text):
            return self.text[self.pos]
        return None
    
    def advance(self):
        """Move to the next character."""
        self.pos += 1
    
    def get_number(self):
        """Extract a complete number (supports decimals)."""
        num_str = ''
        while self.peek() and (self.peek().isdigit() or self.peek() == '.'):
            num_str += self.peek()
            self.advance()
        return float(num_str)


class Parser:
    """
    Recursive descent parser that evaluates expressions.
    Grammar:
        expression := term (('+' | '-') term)*
        term := factor (('*' | '/') factor)*
        factor := number | '(' expression ')'
    """
    def __init__(self, lexer):
        self.lexer = lexer
    
    def parse(self):
        """Entry point for parsing — returns the computed result."""
        result = self.expression()
        # Make sure we consumed everything
        if self.lexer.peek() is not None:
            raise SyntaxError(f"Unexpected character: {self.lexer.peek()}")
        return result
    
    def expression(self):
        """
        Handle addition and subtraction (lowest precedence).
        Keeps consuming terms separated by + or -.
        """
        result = self.term()
        
        while self.lexer.peek() in ('+', '-'):
            op = self.lexer.peek()
            self.lexer.advance()
            right = self.term()
            if op == '+':
                result += right
            else:
                result -= right
        
        return result
    
    def term(self):
        """
        Handle multiplication and division (higher precedence than +/-).
        Keeps consuming factors separated by * or /.
        """
        result = self.factor()
        
        while self.lexer.peek() in ('*', '/'):
            op = self.lexer.peek()
            self.lexer.advance()
            right = self.factor()
            if op == '*':
                result *= right
            else:
                if right == 0:
                    raise ZeroDivisionError("Cannot divide by zero")
                result /= right
        
        return result
    
    def factor(self):
        """
        Handle numbers and parenthesized expressions.
        This is where recursion happens for nested expressions.
        """
        char = self.lexer.peek()
        
        # Handle negative numbers
        if char == '-':
            self.lexer.advance()
            return -self.factor()
        
        # Handle parentheses — recurse into a new expression
        if char == '(':
            self.lexer.advance()
            result = self.expression()
            if self.lexer.peek() != ')':
                raise SyntaxError("Missing closing parenthesis")
            self.lexer.advance()
            return result
        
        # Must be a number at this point
        if char and (char.isdigit() or char == '.'):
            return self.lexer.get_number()
        
        raise SyntaxError(f"Unexpected character: {char}")


def evaluate(expression):
    """
    Main interface function — takes a string expression and returns the result.
    Wraps the lexer and parser for convenience.
    """
    lexer = Lexer(expression)
    parser = Parser(lexer)
    return parser.parse()


if __name__ == "__main__":
    # Testing various expressions to make sure everything works
    test_cases = [
        "2 + 3 * 4",           # Should be 14 (precedence matters)
        "(2 + 3) * 4",         # Should be 20 (parentheses override)
        "10 / 2 - 3",          # Should be 2.0
        "100 / (5 * 2)",       # Should be 10.0
        "-5 + 3",              # Should be -2 (negative numbers)
        "2.5 * 4",             # Should be 10.0 (decimals)
        "((2 + 3) * (4 - 1))", # Should be 15 (nested parens)
        "7 - 3 - 2",           # Should be 2 (left-to-right)
    ]
    
    print("Simple Expression Evaluator Demo")
    print("=" * 40)
    
    for expr in test_cases:
        try:
            result = evaluate(expr)
            print(f"{expr:25} = {result}")
        except Exception as e:
            print(f"{expr:25} -> ERROR: {e}")
    
    print("\n" + "=" * 40)
    print("Interactive mode - try your own expressions:")
    print("(Press Ctrl+C or Ctrl+D to exit)\n")
    
    # Simple REPL for interactive testing
    while True:
        try:
            user_input = input(">>> ")
            if not user_input.strip():
                continue
            result = evaluate(user_input)
            print(f"    {result}")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"    Error: {e}")