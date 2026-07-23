"""
Date: 2026-07-23
Implemented an expression parser that converts infix notation to postfix using Dijkstra's shunting yard algorithm, then evaluates it — wanted something more robust than basic RPN.
"""

#!/usr/bin/env python3
"""
Infix expression evaluator using the Shunting Yard algorithm.

I wanted to build something that could handle actual math expressions
the way humans write them, not just RPN. The shunting yard algorithm
is elegant for this - converts infix to postfix, then evaluates.
"""


class ExpressionEvaluator:
    """
    Evaluates mathematical expressions in standard infix notation.
    
    Supports: +, -, *, /, ^, parentheses, and unary minus.
    Uses Dijkstra's shunting yard algorithm for parsing.
    """
    
    def __init__(self):
        # Operator precedence - higher number means higher precedence
        self.precedence = {
            '+': 1,
            '-': 1,
            '*': 2,
            '/': 2,
            '^': 3,
            'unary-': 4  # Unary minus has highest precedence
        }
        # Right-associative operators (exponentiation)
        self.right_associative = {'^'}
    
    def tokenize(self, expression):
        """
        Convert expression string into tokens (numbers, operators, parens).
        
        This handles multi-digit numbers and detects unary minus by context.
        """
        tokens = []
        i = 0
        expression = expression.replace(' ', '')  # Strip whitespace
        
        while i < len(expression):
            char = expression[i]
            
            # Parse numbers (including decimals)
            if char.isdigit() or char == '.':
                num_str = ''
                while i < len(expression) and (expression[i].isdigit() or expression[i] == '.'):
                    num_str += expression[i]
                    i += 1
                tokens.append(float(num_str))
                continue
            
            # Handle unary minus - it's unary if it appears at start or after an operator/opening paren
            if char == '-':
                if not tokens or tokens[-1] in '(+-*/^':
                    tokens.append('unary-')
                else:
                    tokens.append(char)
            elif char in '+-*/^()':
                tokens.append(char)
            else:
                raise ValueError(f"Invalid character in expression: {char}")
            
            i += 1
        
        return tokens
    
    def infix_to_postfix(self, tokens):
        """
        Convert infix tokens to postfix notation using shunting yard.
        
        This is where the magic happens - operators and parens are managed
        on a stack based on precedence rules.
        """
        output = []
        operator_stack = []
        
        for token in tokens:
            # Numbers go straight to output
            if isinstance(token, (int, float)):
                output.append(token)
            
            # Handle operators
            elif token in self.precedence:
                # Pop operators with higher/equal precedence (considering associativity)
                while operator_stack and operator_stack[-1] != '(':
                    top_op = operator_stack[-1]
                    if top_op in self.precedence:
                        # Right-associative: only pop if strictly greater precedence
                        # Left-associative: pop if greater or equal precedence
                        if token in self.right_associative:
                            if self.precedence[top_op] > self.precedence[token]:
                                output.append(operator_stack.pop())
                            else:
                                break
                        else:
                            if self.precedence[top_op] >= self.precedence[token]:
                                output.append(operator_stack.pop())
                            else:
                                break
                    else:
                        break
                operator_stack.append(token)
            
            # Opening paren goes on stack
            elif token == '(':
                operator_stack.append(token)
            
            # Closing paren: pop until we find matching opening paren
            elif token == ')':
                while operator_stack and operator_stack[-1] != '(':
                    output.append(operator_stack.pop())
                if not operator_stack:
                    raise ValueError("Mismatched parentheses")
                operator_stack.pop()  # Remove the '('
        
        # Pop remaining operators
        while operator_stack:
            if operator_stack[-1] in '()':
                raise ValueError("Mismatched parentheses")
            output.append(operator_stack.pop())
        
        return output
    
    def evaluate_postfix(self, postfix_tokens):
        """
        Evaluate postfix expression using a stack.
        
        This part is straightforward - just process tokens left to right.
        """
        stack = []
        
        for token in postfix_tokens:
            if isinstance(token, (int, float)):
                stack.append(token)
            elif token == 'unary-':
                if not stack:
                    raise ValueError("Invalid expression")
                stack.append(-stack.pop())
            else:
                # Binary operator
                if len(stack) < 2:
                    raise ValueError("Invalid expression")
                right = stack.pop()
                left = stack.pop()
                
                if token == '+':
                    stack.append(left + right)
                elif token == '-':
                    stack.append(left - right)
                elif token == '*':
                    stack.append(left * right)
                elif token == '/':
                    if right == 0:
                        raise ValueError("Division by zero")
                    stack.append(left / right)
                elif token == '^':
                    stack.append(left ** right)
        
        if len(stack) != 1:
            raise ValueError("Invalid expression")
        
        return stack[0]
    
    def evaluate(self, expression):
        """
        Main entry point - evaluate an infix expression string.
        """
        tokens = self.tokenize(expression)
        postfix = self.infix_to_postfix(tokens)
        return self.evaluate_postfix(postfix)


if __name__ == "__main__":
    calc = ExpressionEvaluator()
    
    # Test cases showing various features
    test_expressions = [
        "3 + 4 * 2",
        "(3 + 4) * 2",
        "10 - 2 * 3",
        "2 ^ 3 ^ 2",  # Right associative: 2^(3^2) = 512
        "(2 ^ 3) ^ 2",  # Left to right with parens: 8^2 = 64
        "-5 + 3",
        "10 / (2 + 3)",
        "3.5 * 2 + 1.5",
        "-(3 + 4) * 2",
    ]
    
    print("Expression Evaluator Demo")
    print("=" * 50)
    
    for expr in test_expressions:
        try:
            result = calc.evaluate(expr)
            print(f"{expr:25} = {result}")
        except Exception as e:
            print(f"{expr:25} ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("Interactive mode - enter expressions (or 'quit' to exit):")
    
    while True:
        try:
            user_input = input("\n> ").strip()
            if user_input.lower() in ('quit', 'exit', 'q'):
                break
            if not user_input:
                continue
            result = calc.evaluate(user_input)
            print(f"  = {result}")
        except EOFError:
            break
        except Exception as e:
            print(f"  Error: {e}")