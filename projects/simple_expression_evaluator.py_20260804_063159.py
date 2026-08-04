"""
Date: 2026-08-04
Wrote a simple expression evaluator that parses and computes arithmetic expressions with proper operator precedence, because I wanted to understand how parsers actually work under the hood.
"""

"""
Simple expression evaluator using recursive descent parsing.
Supports +, -, *, /, parentheses, and respects operator precedence.

Grammar:
    expression  -> term (('+' | '-') term)*
    term        -> factor (('*' | '/') factor)*
    factor      -> NUMBER | '(' expression ')'
"""


class Tokenizer:
    """
    Breaks up an input string into tokens for parsing.
    Handles numbers, operators, and parentheses.
    """
    
    def __init__(self, text):
        self.text = text.replace(' ', '')  # strip whitespace for simplicity
        self.pos = 0
        self.current_token = None
        self.current_value = None
    
    def peek_char(self):
        """Return the current character without advancing, or None if at end."""
        if self.pos < len(self.text):
            return self.text[self.pos]
        return None
    
    def advance(self):
        """Move to the next character in the input."""
        self.pos += 1
    
    def next_token(self):
        """
        Get the next token from the input.
        Returns token type: 'NUMBER', 'PLUS', 'MINUS', 'MULT', 'DIV', 'LPAREN', 'RPAREN', 'EOF'
        """
        if self.pos >= len(self.text):
            self.current_token = 'EOF'
            return self.current_token
        
        char = self.peek_char()
        
        # Check for numbers (including decimals)
        if char.isdigit() or char == '.':
            num_str = ''
            while self.peek_char() and (self.peek_char().isdigit() or self.peek_char() == '.'):
                num_str += self.peek_char()
                self.advance()
            self.current_token = 'NUMBER'
            self.current_value = float(num_str)
            return self.current_token
        
        # Single character tokens
        token_map = {
            '+': 'PLUS',
            '-': 'MINUS',
            '*': 'MULT',
            '/': 'DIV',
            '(': 'LPAREN',
            ')': 'RPAREN',
        }
        
        if char in token_map:
            self.current_token = token_map[char]
            self.advance()
            return self.current_token
        
        raise ValueError(f"Unexpected character: {char}")


class ExpressionEvaluator:
    """
    Recursive descent parser and evaluator for arithmetic expressions.
    Respects standard operator precedence (*, / before +, -).
    """
    
    def __init__(self, text):
        self.tokenizer = Tokenizer(text)
        self.tokenizer.next_token()  # initialize first token
    
    def eat(self, token_type):
        """
        Consume a token of the expected type, or raise an error.
        This is how we enforce the grammar rules.
        """
        if self.tokenizer.current_token == token_type:
            self.tokenizer.next_token()
        else:
            raise SyntaxError(f"Expected {token_type}, got {self.tokenizer.current_token}")
    
    def factor(self):
        """
        Parse a factor: either a number or a parenthesized expression.
        This is the highest precedence level in our grammar.
        """
        token = self.tokenizer.current_token
        
        if token == 'NUMBER':
            value = self.tokenizer.current_value
            self.eat('NUMBER')
            return value
        elif token == 'LPAREN':
            self.eat('LPAREN')
            result = self.expression()
            self.eat('RPAREN')
            return result
        else:
            raise SyntaxError(f"Unexpected token in factor: {token}")
    
    def term(self):
        """
        Parse a term: factors connected by * or /.
        This handles multiplication and division, which bind tighter than +/-.
        """
        result = self.factor()
        
        while self.tokenizer.current_token in ('MULT', 'DIV'):
            op = self.tokenizer.current_token
            self.eat(op)
            if op == 'MULT':
                result *= self.factor()
            elif op == 'DIV':
                divisor = self.factor()
                if divisor == 0:
                    raise ZeroDivisionError("Division by zero")
                result /= divisor
        
        return result
    
    def expression(self):
        """
        Parse an expression: terms connected by + or -.
        This is the entry point for parsing, lowest precedence.
        """
        result = self.term()
        
        while self.tokenizer.current_token in ('PLUS', 'MINUS'):
            op = self.tokenizer.current_token
            self.eat(op)
            if op == 'PLUS':
                result += self.term()
            elif op == 'MINUS':
                result -= self.term()
        
        return result
    
    def evaluate(self):
        """
        Evaluate the entire expression and ensure we've consumed all input.
        Returns the numeric result.
        """
        result = self.expression()
        if self.tokenizer.current_token != 'EOF':
            raise SyntaxError(f"Unexpected token after expression: {self.tokenizer.current_token}")
        return result


def eval_expression(expression_str):
    """
    Convenience function to evaluate an expression string.
    Returns the computed value or raises an error if parsing fails.
    """
    evaluator = ExpressionEvaluator(expression_str)
    return evaluator.evaluate()


if __name__ == "__main__":
    # Demo with various expressions showing operator precedence and parens
    test_expressions = [
        "3 + 5 * 2",           # should be 13 (not 16)
        "20 / 4 + 2",          # should be 7
        "(3 + 5) * 2",         # should be 16
        "10 - 2 * 3",          # should be 4
        "100 / (5 + 5)",       # should be 10
        "2.5 * 4 + 1.5",       # should be 11.5
        "((2 + 3) * 4) / 2",   # should be 10
    ]
    
    print("Simple Expression Evaluator Demo")
    print("=" * 40)
    
    for expr in test_expressions:
        try:
            result = eval_expression(expr)
            print(f"{expr:25} = {result}")
        except Exception as e:
            print(f"{expr:25} -> ERROR: {e}")
    
    print("\n" + "=" * 40)
    print("Interactive mode: enter expressions (or 'quit' to exit)")
    
    # Simple REPL for playing around
    while True:
        try:
            user_input = input("\n> ").strip()
            if user_input.lower() in ('quit', 'exit', 'q'):
                print("Bye!")
                break
            if not user_input:
                continue
            
            result = eval_expression(user_input)
            print(f"Result: {result}")
        except EOFError:
            print("\nBye!")
            break
        except Exception as e:
            print(f"Error: {e}")