"""
Date: 2026-07-10
Wrote a tiny interpreter that parses and evaluates s-expressions with basic arithmetic ops and variable bindings — basically a calculator that speaks lisp.
"""

"""
A minimal LISP-style expression evaluator.

This interpreter handles s-expressions with basic arithmetic operations,
variable definitions, and nested expressions. I wanted something that felt
like actually writing an interpreter from scratch without tons of complexity.
"""

import re
from typing import Any, Dict, List, Union


class LispEvaluator:
    """
    Evaluates simple LISP-style expressions with arithmetic and variables.
    
    Supports: +, -, *, /, define (for variables), and nested expressions.
    """
    
    def __init__(self):
        """Initialize with an empty environment for storing variables."""
        self.env: Dict[str, Any] = {}
    
    def tokenize(self, expression: str) -> List[str]:
        """
        Convert a string expression into a list of tokens.
        
        Adds spaces around parens so we can just split on whitespace.
        """
        # Replace parens with space-padded versions for easy splitting
        expression = expression.replace('(', ' ( ').replace(')', ' ) ')
        return expression.split()
    
    def parse(self, tokens: List[str]) -> Union[List, str, float]:
        """
        Parse tokens into nested list structure (AST).
        
        Recursively builds the tree structure from flat token list.
        This is the key step that turns text into something we can evaluate.
        """
        if len(tokens) == 0:
            raise SyntaxError("Unexpected EOF while parsing")
        
        token = tokens.pop(0)
        
        if token == '(':
            # Start of a new list/expression
            ast = []
            while tokens[0] != ')':
                ast.append(self.parse(tokens))
            tokens.pop(0)  # Remove the closing ')'
            return ast
        elif token == ')':
            raise SyntaxError("Unexpected )")
        else:
            # It's an atom (number or symbol)
            return self._parse_atom(token)
    
    def _parse_atom(self, token: str) -> Union[float, str]:
        """
        Convert a token into a number or return it as a symbol.
        
        Tries to parse as float first, otherwise treats as variable/operator name.
        """
        try:
            return float(token)
        except ValueError:
            return token
    
    def evaluate(self, ast: Union[List, str, float]) -> float:
        """
        Evaluate the parsed AST and return the result.
        
        This is where the magic happens — recursively evaluate expressions
        based on their structure and operator.
        """
        # If it's just a number, return it
        if isinstance(ast, (int, float)):
            return ast
        
        # If it's a symbol (variable), look it up in environment
        if isinstance(ast, str):
            if ast in self.env:
                return self.env[ast]
            else:
                raise NameError(f"Undefined variable: {ast}")
        
        # It's a list/expression — first element is the operator
        if not isinstance(ast, list) or len(ast) == 0:
            raise ValueError("Invalid expression")
        
        operator = ast[0]
        
        # Special form: (define var value)
        if operator == 'define':
            if len(ast) != 3:
                raise SyntaxError("define requires exactly 2 arguments")
            var_name = ast[1]
            value = self.evaluate(ast[2])
            self.env[var_name] = value
            return value
        
        # Arithmetic operations
        # Evaluate all arguments first (that's what makes it recursive)
        args = [self.evaluate(arg) for arg in ast[1:]]
        
        if operator == '+':
            return sum(args)
        elif operator == '-':
            if len(args) == 1:
                return -args[0]
            return args[0] - sum(args[1:])
        elif operator == '*':
            result = 1
            for arg in args:
                result *= arg
            return result
        elif operator == '/':
            if len(args) < 2:
                raise ValueError("Division requires at least 2 arguments")
            result = args[0]
            for arg in args[1:]:
                if arg == 0:
                    raise ZeroDivisionError("Division by zero")
                result /= arg
            return result
        else:
            raise ValueError(f"Unknown operator: {operator}")
    
    def run(self, expression: str) -> float:
        """
        Complete pipeline: tokenize, parse, and evaluate an expression.
        
        This is the main entry point for evaluating a string.
        """
        tokens = self.tokenize(expression)
        ast = self.parse(tokens)
        return self.evaluate(ast)


def main():
    """
    Demo the interpreter with various expressions.
    
    Shows basic arithmetic, nested expressions, and variable definition.
    """
    evaluator = LispEvaluator()
    
    test_cases = [
        "(+ 2 3)",
        "(* 4 5)",
        "(- 10 3)",
        "(/ 20 4)",
        "(+ (* 2 3) (- 10 5))",  # Nested: (2*3) + (10-5) = 11
        "(define x 42)",
        "(+ x 8)",  # Should be 50
        "(define y (* x 2))",
        "(/ y 4)",  # Should be 21
        "(+ (- 100 (* 5 10)) (/ 30 3))",  # Complex nested
    ]
    
    print("=== Simple LISP Expression Evaluator ===\n")
    
    for expr in test_cases:
        try:
            result = evaluator.run(expr)
            print(f"{expr:40s} => {result}")
        except Exception as e:
            print(f"{expr:40s} => ERROR: {e}")
    
    print("\n--- Current Environment ---")
    for var, val in evaluator.env.items():
        print(f"  {var} = {val}")


if __name__ == "__main__":
    main()