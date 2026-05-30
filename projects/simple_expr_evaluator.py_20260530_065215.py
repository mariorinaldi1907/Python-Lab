"""
Date: 2026-05-30
Wrote an expression evaluator that parses and computes arithmetic with proper precedence — way cleaner than regex hacks.
"""

"""
Simple arithmetic expression evaluator using recursive descent parsing.

Supports +, -, *, /, parentheses, and respects standard operator precedence.
I wanted something that actually understands expression structure rather than
just regex matching or eval() cheating.
"""


class ExpressionEvaluator:
    """
    A recursive descent parser for simple arithmetic expressions.
    
    Grammar:
        expression := term (('+' | '-') term)*
        term       := factor (('*' | '/') factor)*
        factor     := number | '(' expression ')'
    """
    
    def __init__(self, text):
        """Initialize with the expression string to parse."""
        self.text = text.replace(" ", "")  # strip whitespace for easier parsing
        self.pos = 0
        self.current_char = self.text[0] if self.text else None
    
    def advance(self):
        """Move to the next character in the input."""
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None
    
    def parse_number(self):
        """
        Parse a number (integer or float).
        
        I'm handling decimals here because why not — makes it more useful.
        """
        num_str = ""
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            num_str += self.current_char
            self.advance()
        
        # Convert to int if no decimal, otherwise float
        if '.' in num_str:
            return float(num_str)
        return int(num_str)
    
    def parse_factor(self):
        """
        Parse a factor: either a number or a parenthesized expression.
        
        This is where we handle nested expressions recursively.
        """
        # Handle negative numbers with unary minus
        if self.current_char == '-':
            self.advance()
            return -self.parse_factor()
        
        # Handle parentheses
        if self.current_char == '(':
            self.advance()  # skip '('
            result = self.parse_expression()
            if self.current_char == ')':
                self.advance()  # skip ')'
            else:
                raise ValueError(f"Expected ')' at position {self.pos}")
            return result
        
        # Otherwise it's a number
        if self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            return self.parse_number()
        
        raise ValueError(f"Unexpected character '{self.current_char}' at position {self.pos}")
    
    def parse_term(self):
        """
        Parse a term: handles multiplication and division.
        
        These have higher precedence than addition/subtraction, so we handle them
        in a separate layer of the recursive descent.
        """
        result = self.parse_factor()
        
        while self.current_char in ('*', '/'):
            op = self.current_char
            self.advance()
            right = self.parse_factor()
            
            if op == '*':
                result *= right
            elif op == '/':
                if right == 0:
                    raise ZeroDivisionError("Division by zero")
                result /= right
        
        return result
    
    def parse_expression(self):
        """
        Parse a full expression: handles addition and subtraction.
        
        This is the entry point for parsing since these operators have the
        lowest precedence.
        """
        result = self.parse_term()
        
        while self.current_char in ('+', '-'):
            op = self.current_char
            self.advance()
            right = self.parse_term()
            
            if op == '+':
                result += right
            elif op == '-':
                result -= right
        
        return result
    
    def evaluate(self):
        """
        Evaluate the expression and return the result.
        
        Main public method — call this after constructing the evaluator.
        """
        if not self.text:
            raise ValueError("Empty expression")
        
        result = self.parse_expression()
        
        # Make sure we consumed the entire input
        if self.current_char is not None:
            raise ValueError(f"Unexpected character '{self.current_char}' at position {self.pos}")
        
        return result


def evaluate(expression):
    """
    Convenience function to evaluate an expression string.
    
    Just wraps the class for simpler usage in the demo.
    """
    evaluator = ExpressionEvaluator(expression)
    return evaluator.evaluate()


if __name__ == "__main__":
    print("=== Simple Expression Evaluator ===\n")
    
    # Test cases covering different features
    test_expressions = [
        "2 + 3",
        "10 - 5 * 2",
        "(10 - 5) * 2",
        "100 / 4 / 5",
        "3.14 * 2",
        "-5 + 10",
        "2 * (3 + 4) - 1",
        "((2 + 3) * 4) / 2",
        "1 + 2 * 3 - 4 / 2",
        "10 / (2 + 3)",
    ]
    
    for expr in test_expressions:
        try:
            result = evaluate(expr)
            print(f"{expr:25} = {result}")
        except Exception as e:
            print(f"{expr:25} ERROR: {e}")
    
    print("\n--- Edge Cases ---")
    
    # Test error handling
    error_cases = [
        ("5 / 0", "Division by zero"),
        ("2 + + 3", "Invalid syntax"),
        ("(2 + 3", "Missing closing paren"),
    ]
    
    for expr, expected_error in error_cases:
        try:
            result = evaluate(expr)
            print(f"{expr:25} = {result} (expected error!)")
        except Exception as e:
            print(f"{expr:25} ERROR (expected): {type(e).__name__}")