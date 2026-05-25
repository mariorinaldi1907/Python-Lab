"""
Date: 2026-05-25
Wrote an expression evaluator that parses and computes arithmetic expressions using a recursive descent parser — wanted to really understand how precedence and associativity work under the hood.
"""

"""
Simple expression evaluator using recursive descent parsing.
Supports: +, -, *, /, ^ (power), parentheses
Respects standard operator precedence and associativity.
"""


class Tokenizer:
    """Breaks input string into tokens for parsing."""
    
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_token = None
        self.current_value = None
    
    def advance(self):
        """Move to the next token in the input."""
        # Skip whitespace
        while self.pos < len(self.text) and self.text[self.pos].isspace():
            self.pos += 1
        
        # End of input
        if self.pos >= len(self.text):
            self.current_token = 'EOF'
            return
        
        char = self.text[self.pos]
        
        # Check for numbers (including decimals)
        if char.isdigit() or char == '.':
            start = self.pos
            has_dot = char == '.'
            self.pos += 1
            while self.pos < len(self.text):
                char = self.text[self.pos]
                if char.isdigit():
                    self.pos += 1
                elif char == '.' and not has_dot:
                    has_dot = True
                    self.pos += 1
                else:
                    break
            self.current_value = float(self.text[start:self.pos])
            self.current_token = 'NUMBER'
        # Operators and parentheses
        elif char in '+-*/^()':
            self.current_token = char
            self.current_value = char
            self.pos += 1
        else:
            raise ValueError(f"Unexpected character: {char}")


class ExpressionEvaluator:
    """
    Recursive descent parser for arithmetic expressions.
    Grammar (in order of precedence, lowest to highest):
      expr   -> term (('+' | '-') term)*
      term   -> factor (('*' | '/') factor)*
      factor -> power ('^' power)*     # right-associative
      power  -> NUMBER | '(' expr ')'
    """
    
    def __init__(self, text):
        self.tokenizer = Tokenizer(text)
        self.tokenizer.advance()  # Load first token
    
    def parse(self):
        """Entry point: parse and evaluate the expression."""
        result = self.expr()
        if self.tokenizer.current_token != 'EOF':
            raise ValueError("Unexpected tokens after expression")
        return result
    
    def expr(self):
        """Handle addition and subtraction (lowest precedence)."""
        result = self.term()
        
        while self.tokenizer.current_token in ('+', '-'):
            op = self.tokenizer.current_token
            self.tokenizer.advance()
            right = self.term()
            if op == '+':
                result += right
            else:
                result -= right
        
        return result
    
    def term(self):
        """Handle multiplication and division."""
        result = self.factor()
        
        while self.tokenizer.current_token in ('*', '/'):
            op = self.tokenizer.current_token
            self.tokenizer.advance()
            right = self.factor()
            if op == '*':
                result *= right
            else:
                if right == 0:
                    raise ValueError("Division by zero")
                result /= right
        
        return result
    
    def factor(self):
        """Handle exponentiation (right-associative, so we recurse on the right)."""
        result = self.power()
        
        # Right associativity: 2^3^2 = 2^(3^2) = 2^9 = 512
        if self.tokenizer.current_token == '^':
            self.tokenizer.advance()
            right = self.factor()  # Recursive call for right associativity
            result = result ** right
        
        return result
    
    def power(self):
        """Handle numbers and parenthesized expressions (highest precedence)."""
        token = self.tokenizer.current_token
        
        if token == 'NUMBER':
            value = self.tokenizer.current_value
            self.tokenizer.advance()
            return value
        elif token == '(':
            self.tokenizer.advance()
            result = self.expr()  # Recursively parse the sub-expression
            if self.tokenizer.current_token != ')':
                raise ValueError("Missing closing parenthesis")
            self.tokenizer.advance()
            return result
        elif token in ('+', '-'):
            # Handle unary plus/minus
            self.tokenizer.advance()
            value = self.power()
            return -value if token == '-' else value
        else:
            raise ValueError(f"Unexpected token: {token}")


def evaluate(expression):
    """
    Parse and evaluate a mathematical expression string.
    Returns the numeric result.
    """
    evaluator = ExpressionEvaluator(expression)
    return evaluator.parse()


if __name__ == "__main__":
    # Demo with various test cases
    test_cases = [
        "3 + 5 * 2",
        "(3 + 5) * 2",
        "10 / 2 - 3",
        "2 ^ 3 ^ 2",  # Should be 512 (right-associative)
        "100 / (5 * 2)",
        "-5 + 3",
        "2.5 * 4 + 1.5",
        "(2 + 3) * (4 - 1)",
        "10 - 2 - 3",  # Left-associative: (10-2)-3 = 5
    ]
    
    print("Expression Evaluator Demo")
    print("=" * 50)
    
    for expr in test_cases:
        try:
            result = evaluate(expr)
            print(f"{expr:25} = {result}")
        except Exception as e:
            print(f"{expr:25} ERROR: {e}")
    
    print("\nInteractive mode (Ctrl+C to exit):")
    print("-" * 50)
    
    # Simple REPL for interactive testing
    try:
        while True:
            user_input = input(">>> ").strip()
            if not user_input:
                continue
            try:
                result = evaluate(user_input)
                print(f"    {result}")
            except Exception as e:
                print(f"    Error: {e}")
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")