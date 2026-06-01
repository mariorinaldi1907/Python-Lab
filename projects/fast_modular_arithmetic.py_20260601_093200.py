"""
Date: 2026-06-01
Built a modular arithmetic toolkit with fast exponentiation and matrix operations — wanted something for RSA experiments and Fibonacci tricks.
"""

#!/usr/bin/env python3
"""
Fast modular arithmetic utilities for number theory and cryptography.

I built this because I kept rewriting the same modular exponentiation code
for different projects. Figured I'd make it reusable and throw in matrix
operations since those come up in recurrence relations (Fibonacci, Lucas, etc).
"""


def mod_exp(base, exponent, modulus):
    """
    Compute (base^exponent) % modulus efficiently using binary exponentiation.
    
    This is way faster than doing pow(base, exponent) % modulus for huge numbers
    because it keeps intermediate results small. Essential for RSA and Diffie-Hellman.
    
    Args:
        base: The base number
        exponent: The exponent (must be non-negative)
        modulus: The modulus to reduce by
        
    Returns:
        (base^exponent) % modulus
    """
    if modulus == 1:
        return 0
    
    result = 1
    base = base % modulus
    
    # Binary exponentiation: process each bit of the exponent
    while exponent > 0:
        # If current bit is set, multiply current base into result
        if exponent % 2 == 1:
            result = (result * base) % modulus
        
        # Square the base for the next bit position
        exponent = exponent >> 1
        base = (base * base) % modulus
    
    return result


def mod_inverse(a, m):
    """
    Compute modular multiplicative inverse of a modulo m using extended GCD.
    
    Finds x such that (a * x) % m == 1, if it exists.
    Only exists when gcd(a, m) = 1.
    
    Args:
        a: The number to invert
        m: The modulus
        
    Returns:
        The modular inverse, or None if it doesn't exist
    """
    def extended_gcd(a, b):
        """Extended Euclidean algorithm - returns (gcd, x, y) where ax + by = gcd"""
        if a == 0:
            return b, 0, 1
        
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        
        return gcd, x, y
    
    gcd, x, _ = extended_gcd(a % m, m)
    
    if gcd != 1:
        return None  # Inverse doesn't exist
    
    return (x % m + m) % m


class ModMatrix:
    """
    Matrix class with modular arithmetic operations.
    
    Useful for computing things like Fibonacci numbers efficiently using
    matrix exponentiation. Everything is done modulo some number to keep
    values manageable.
    """
    
    def __init__(self, data, modulus):
        """
        Initialize a matrix with modular arithmetic.
        
        Args:
            data: 2D list representing the matrix
            modulus: All operations are done mod this number
        """
        self.data = [[val % modulus for val in row] for row in data]
        self.rows = len(data)
        self.cols = len(data[0]) if data else 0
        self.modulus = modulus
    
    def __mul__(self, other):
        """
        Matrix multiplication with modular reduction.
        
        This is the expensive operation, but we keep it efficient by
        reducing modulo at each step instead of letting numbers blow up.
        """
        if self.cols != other.rows:
            raise ValueError(f"Incompatible dimensions: {self.cols} != {other.rows}")
        
        result = [[0] * other.cols for _ in range(self.rows)]
        
        for i in range(self.rows):
            for j in range(other.cols):
                for k in range(self.cols):
                    result[i][j] += self.data[i][k] * other.data[k][j]
                    result[i][j] %= self.modulus
        
        return ModMatrix(result, self.modulus)
    
    def __pow__(self, n):
        """
        Fast matrix exponentiation using binary exponentiation.
        
        Same idea as mod_exp but for matrices. Critical for computing
        recurrence relations like Fibonacci in O(log n) time.
        """
        if self.rows != self.cols:
            raise ValueError("Can only exponentiate square matrices")
        
        if n == 0:
            # Return identity matrix
            identity = [[1 if i == j else 0 for j in range(self.cols)] 
                       for i in range(self.rows)]
            return ModMatrix(identity, self.modulus)
        
        if n == 1:
            return ModMatrix([row[:] for row in self.data], self.modulus)
        
        # Binary exponentiation for matrices
        result = ModMatrix([[1 if i == j else 0 for j in range(self.cols)] 
                           for i in range(self.rows)], self.modulus)
        base = ModMatrix([row[:] for row in self.data], self.modulus)
        
        while n > 0:
            if n % 2 == 1:
                result = result * base
            base = base * base
            n //= 2
        
        return result
    
    def __repr__(self):
        """Pretty print the matrix"""
        return '\n'.join([' '.join(map(str, row)) for row in self.data])


def fibonacci_fast(n, modulus=10**9 + 7):
    """
    Compute the nth Fibonacci number modulo some value using matrix exponentiation.
    
    This is a demo of why ModMatrix is useful. Standard approach is O(n),
    this is O(log n). For huge n (like 10^18), this is the only practical way.
    
    Uses the identity: [F(n+1), F(n)] = [[1,1],[1,0]]^n * [1, 0]
    
    Args:
        n: Which Fibonacci number to compute (0-indexed)
        modulus: Return result mod this value
        
    Returns:
        F(n) % modulus
    """
    if n == 0:
        return 0
    if n == 1:
        return 1
    
    # The Fibonacci matrix
    fib_matrix = ModMatrix([[1, 1], [1, 0]], modulus)
    result_matrix = fib_matrix ** (n - 1)
    
    # F(n) is in the top-left corner after exponentiation
    return result_matrix.data[0][0]


if __name__ == "__main__":
    print("=== Fast Modular Arithmetic Demo ===\n")
    
    # Demo 1: Modular exponentiation (useful for RSA)
    print("1. Modular Exponentiation")
    base, exp, mod = 2, 1000, 10**9 + 7
    result = mod_exp(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}")
    print(f"   (This would overflow without modular reduction!)\n")
    
    # Demo 2: Modular inverse (useful for modular division)
    print("2. Modular Inverse")
    a, m = 17, 43
    inv = mod_inverse(a, m)
    if inv:
        print(f"   Inverse of {a} mod {m} = {inv}")
        print(f"   Check: ({a} * {inv}) mod {m} = {(a * inv) % m}\n")
    
    # Demo 3: Matrix exponentiation for Fibonacci
    print("3. Fast Fibonacci using Matrix Exponentiation")
    test_values = [10, 50, 100, 1000]
    for n in test_values:
        fib_n = fibonacci_fast(n)
        print(f"   F({n}) mod 10^9+7 = {fib_n}")
    
    print("\n4. Matrix Multiplication Demo")
    mod = 1000
    m1 = ModMatrix([[1, 2], [3, 4]], mod)
    m2 = ModMatrix([[5, 6], [7, 8]], mod)
    print(f"   Matrix A:\n{m1}\n")
    print(f"   Matrix B:\n{m2}\n")
    print(f"   A * B (mod {mod}):\n{m1 * m2}\n")
    print(f"   A^10 (mod {mod}):\n{m1 ** 10}")