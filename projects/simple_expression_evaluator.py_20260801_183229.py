"""
Date: 2026-08-01
Implemented a simple expression evaluator that parses and computes arithmetic expressions with proper operator precedence using recursive descent parsing.
"""

"""
Simple Expression Evaluator
Parses and evaluates arithmetic expressions like "3 + 4 * (2 - 1)"
Uses recursive descent parsing to handle operator precedence correctly.
"""

class Tokenizer:
    """
    Breaks down an expression string into tokens (numbers, operators, parens).
    I built this as a separate class to keep the parsing logic clean.
    """
    
    def __init__(self, expression):
        self.expression = expression.replace(" ", "")  # Strip whitespace for easier parsing
        self.pos = 0
        
    def peek(self):
        """Look at the current character without consuming it."""
        if self.pos < len(self.expression):
            return self.expression[self.pos]
        return None
    
    def consume(self):
        """Get current character and move to the next position."""
        char = self.peek()
        self.pos += 1
        return char
    
    def get_number(self):
        """
        Extract a complete number (can be multi-digit or decimal).
        I'm supporting floats here because why not.
        """
        num_str = ""
        while self.peek() and (self.peek().isdigit() or self.peek() == '.'):
            num_str += self.consume()
        return float(num_str)


class ExpressionEvaluator:
    """
    Recursive descent parser for arithmetic expressions.
    Grammar I'm using:
      expression -> term (('+' | '-') term)*
      term       -> factor (('*' | '/') factor)*
      factor     -> number | '(' expression ')'
    
    This naturally handles operator precedence since multiplication/division
    are deeper in the parse tree than addition/subtraction.
    """
    
    def __init__(self, expression):
        self.tokenizer = Tokenizer(expression)
    
    def evaluate(self):
        """Entry point for evaluation."""
        result = self.parse_expression()
        # Make sure we consumed the entire expression
        if self.tokenizer.peek() is not None:
            raise ValueError(f"Unexpected character: {self.tokenizer.peek()}")
        return result
    
    def parse_expression(self):
        """
        Handle addition and subtraction (lowest precedence).
        Keep grabbing terms and adding/subtracting them.
        """
        result = self.parse_term()
        
        while self.tokenizer.peek() in ['+', '-']:
            op = self.tokenizer.consume()
            right = self.parse_term()
            if op == '+':
                result += right
            else:
                result -= right
        
        return result
    
    def parse_term(self):
        """
        Handle multiplication and division (higher precedence than +/-).
        This gets called by parse_expression, creating the precedence hierarchy.
        """
        result = self.parse_factor()
        
        while self.tokenizer.peek() in ['*', '/']:
            op = self.tokenizer.consume()
            right = self.parse_factor()
            if op == '*':
                result *= right
            else:
                if right == 0:
                    raise ValueError("Division by zero")
                result /= right
        
        return result
    
    def parse_factor(self):
        """
        Handle numbers and parenthesized expressions (highest precedence).
        Parentheses let us recursively call parse_expression for sub-expressions.
        """
        char = self.tokenizer.peek()
        
        # Handle negative numbers
        if char == '-':
            self.tokenizer.consume()
            return -self.parse_factor()
        
        # Handle parenthesized expressions
        if char == '(':
            self.tokenizer.consume()
            result = self.parse_expression()
            if self.tokenizer.consume() != ')':
                raise ValueError("Mismatched parentheses")
            return result
        
        # Handle numbers
        if char and (char.isdigit() or char == '.'):
            return self.tokenizer.get_number()
        
        raise ValueError(f"Unexpected character: {char}")


def evaluate_expression(expression):
    """
    Convenience function to evaluate an expression string.
    Returns the computed result as a float.
    """
    evaluator = ExpressionEvaluator(expression)
    return evaluator.evaluate()


if __name__ == "__main__":
    # Test cases to show this actually works
    test_expressions = [
        "3 + 4",
        "10 - 2 * 3",
        "(10 - 2) * 3",
        "100 / 4 / 5",
        "2 + 3 * 4 - 5",
        "(2 + 3) * (4 - 1)",
        "-5 + 3",
        "3.5 * 2",
        "((2 + 3) * 4) / 2",
        "1 + 2 + 3 + 4 + 5",
    ]
    
    print("Simple Expression Evaluator")
    print("=" * 50)
    
    for expr in test_expressions:
        try:
            result = evaluate_expression(expr)
            # Clean up the output - show integers when possible
            if result == int(result):
                result = int(result)
            print(f"{expr:25} = {result}")
        except ValueError as e:
            print(f"{expr:25} ERROR: {e}")
    
    # Interactive mode - because it's more fun this way
    print("\n" + "=" * 50)
    print("Try your own expressions (Ctrl+C to exit):")
    print("Supports: +, -, *, /, parentheses, decimals, negative numbers")
    
    try:
        while True:
            user_input = input("\n> ")
            if not user_input.strip():
                continue
            try:
                result = evaluate_expression(user_input)
                if result == int(result):
                    result = int(result)
                print(f"= {result}")
            except ValueError as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")
    except KeyboardInterrupt:
        print("\n\nThanks for calculating!")