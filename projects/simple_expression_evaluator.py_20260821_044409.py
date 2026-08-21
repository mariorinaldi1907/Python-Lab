"""
Date: 2026-08-21
Wrote an expression evaluator that parses and evaluates arithmetic with proper operator precedence — wanted to understand how parsers actually work under the hood.
"""

"""
Simple arithmetic expression evaluator using recursive descent parsing.
Handles +, -, *, /, parentheses, and respects operator precedence.
"""

class Tokenizer:
    """
    Breaks an expression string into tokens (numbers, operators, parens).
    """
    def __init__(self, expression):
        self.expression = expression.replace(' ', '')  # strip whitespace
        self.pos = 0
        self.current_token = None
        self.advance()
    
    def advance(self):
        """Move to the next token in the expression."""
        if self.pos >= len(self.expression):
            self.current_token = None
            return
        
        char = self.expression[self.pos]
        
        # Check if it's a number (including decimals)
        if char.isdigit() or char == '.':
            start = self.pos
            while self.pos < len(self.expression) and (
                self.expression[self.pos].isdigit() or self.expression[self.pos] == '.'
            ):
                self.pos += 1
            self.current_token = ('NUMBER', float(self.expression[start:self.pos]))
        
        # Check for operators and parentheses
        elif char in '+-*/()':
            self.current_token = ('OP', char)
            self.pos += 1
        
        else:
            raise ValueError(f"Unexpected character: {char}")


class ExpressionEvaluator:
    """
    Recursive descent parser that evaluates arithmetic expressions.
    Grammar:
        expression := term (('+' | '-') term)*
        term       := factor (('*' | '/') factor)*
        factor     := NUMBER | '(' expression ')'
    """
    def __init__(self, expression):
        self.tokenizer = Tokenizer(expression)
    
    def evaluate(self):
        """Evaluate the entire expression and return the result."""
        result = self.parse_expression()
        if self.tokenizer.current_token is not None:
            raise ValueError("Unexpected tokens at end of expression")
        return result
    
    def parse_expression(self):
        """
        Parse addition and subtraction (lowest precedence).
        This is where we handle left-to-right evaluation of + and -.
        """
        result = self.parse_term()
        
        while self.tokenizer.current_token and self.tokenizer.current_token[0] == 'OP':
            op = self.tokenizer.current_token[1]
            if op not in ('+', '-'):
                break
            
            self.tokenizer.advance()
            right = self.parse_term()
            
            if op == '+':
                result += right
            else:
                result -= right
        
        return result
    
    def parse_term(self):
        """
        Parse multiplication and division (higher precedence than +/-).
        """
        result = self.parse_factor()
        
        while self.tokenizer.current_token and self.tokenizer.current_token[0] == 'OP':
            op = self.tokenizer.current_token[1]
            if op not in ('*', '/'):
                break
            
            self.tokenizer.advance()
            right = self.parse_factor()
            
            if op == '*':
                result *= right
            else:
                if right == 0:
                    raise ZeroDivisionError("Division by zero")
                result /= right
        
        return result
    
    def parse_factor(self):
        """
        Parse a number or a parenthesized expression (highest precedence).
        """
        token = self.tokenizer.current_token
        
        if token is None:
            raise ValueError("Unexpected end of expression")
        
        # Handle numbers
        if token[0] == 'NUMBER':
            self.tokenizer.advance()
            return token[1]
        
        # Handle parentheses
        if token[0] == 'OP' and token[1] == '(':
            self.tokenizer.advance()
            result = self.parse_expression()
            
            if not self.tokenizer.current_token or self.tokenizer.current_token[1] != ')':
                raise ValueError("Missing closing parenthesis")
            
            self.tokenizer.advance()
            return result
        
        raise ValueError(f"Unexpected token: {token}")


def evaluate(expression):
    """
    Convenience function to evaluate an arithmetic expression string.
    Returns the numeric result.
    """
    evaluator = ExpressionEvaluator(expression)
    return evaluator.evaluate()


if __name__ == "__main__":
    # Demo various expressions to show it actually works
    test_cases = [
        "3 + 5",
        "10 - 2 * 3",
        "(10 - 2) * 3",
        "100 / 4 / 5",
        "2 + 3 * 4 - 5",
        "(2 + 3) * (4 - 1)",
        "15.5 + 2.5 * 2",
        "((1 + 2) * (3 + 4)) / 7",
    ]
    
    print("=== Simple Expression Evaluator ===\n")
    
    for expr in test_cases:
        try:
            result = evaluate(expr)
            print(f"{expr:30s} = {result}")
        except Exception as e:
            print(f"{expr:30s} ERROR: {e}")
    
    print("\n--- Edge Cases ---\n")
    
    # Test some error cases
    error_cases = [
        "5 / 0",
        "3 + ",
        "(1 + 2",
        "1 + + 2",
    ]
    
    for expr in error_cases:
        try:
            result = evaluate(expr)
            print(f"{expr:30s} = {result}")
        except Exception as e:
            print(f"{expr:30s} ERROR: {type(e).__name__}")