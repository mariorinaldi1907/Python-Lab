"""
Date: 2026-06-26
Implemented modular arithmetic utilities including fast modular exponentiation and Chinese Remainder Theorem solver because I keep needing these for cryptography puzzles and competitive programming.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit

A collection of number theory utilities I keep rewriting for various projects.
Includes fast modular exponentiation, extended Euclidean algorithm, modular
inverse, and Chinese Remainder Theorem solver.

Mostly built this because I got tired of looking up the CRT every time I needed
it for Advent of Code or Project Euler problems.
"""

from typing import List, Tuple, Optional


def gcd(a: int, b: int) -> int:
    """
    Compute the greatest common divisor using Euclidean algorithm.
    
    Classic recursive implementation - clean and simple.
    """
    if b == 0:
        return a
    return gcd(b, a % b)


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """
    Extended Euclidean Algorithm.
    
    Returns (gcd, x, y) such that a*x + b*y = gcd(a, b).
    This is crucial for finding modular inverses.
    
    I always forget the iterative version, so going with the recursive one
    that matches the textbook definition more closely.
    """
    if b == 0:
        return a, 1, 0
    
    gcd_val, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    
    return gcd_val, x, y


def mod_inverse(a: int, m: int) -> Optional[int]:
    """
    Find modular multiplicative inverse of a modulo m.
    
    Returns x such that (a * x) % m = 1, or None if no inverse exists.
    An inverse exists if and only if gcd(a, m) = 1.
    """
    gcd_val, x, _ = extended_gcd(a, m)
    
    if gcd_val != 1:
        # No inverse exists
        return None
    
    # Make sure result is positive
    return x % m


def fast_mod_exp(base: int, exp: int, mod: int) -> int:
    """
    Fast modular exponentiation using binary exponentiation.
    
    Computes (base^exp) % mod efficiently in O(log exp) time.
    This is way faster than doing pow(base, exp) % mod for large exponents
    because we keep the intermediate results small.
    """
    if mod == 1:
        return 0
    
    result = 1
    base = base % mod
    
    while exp > 0:
        # If exp is odd, multiply base with result
        if exp % 2 == 1:
            result = (result * base) % mod
        
        # Square the base and halve the exponent
        exp = exp >> 1  # Bit shift right is faster than // 2
        base = (base * base) % mod
    
    return result


def chinese_remainder_theorem(remainders: List[int], moduli: List[int]) -> Optional[int]:
    """
    Solve system of congruences using Chinese Remainder Theorem.
    
    Given: x ≡ remainders[i] (mod moduli[i]) for all i
    Find: x
    
    Returns the smallest positive solution, or None if no solution exists.
    
    The moduli must be pairwise coprime for a unique solution to exist.
    I'm not checking that here because sometimes you just want to see what happens.
    """
    if len(remainders) != len(moduli):
        return None
    
    if len(remainders) == 0:
        return None
    
    # Start with the first congruence
    x = remainders[0]
    m = moduli[0]
    
    # Iteratively combine congruences
    for i in range(1, len(remainders)):
        r = remainders[i]
        n = moduli[i]
        
        # We need to solve: x ≡ r (mod n) and x ≡ current_x (mod m)
        # Using the formula: x = x + m * k where k satisfies m*k ≡ (r - x) (mod n)
        
        gcd_val, inv, _ = extended_gcd(m, n)
        
        if (r - x) % gcd_val != 0:
            # No solution exists
            return None
        
        # Find k
        k = ((r - x) // gcd_val * inv) % n
        x = x + m * k
        
        # Update modulus to lcm(m, n) = m * n / gcd(m, n)
        m = m * n // gcd_val
    
    return x % m


def is_prime_fermat(n: int, k: int = 5) -> bool:
    """
    Probabilistic primality test using Fermat's Little Theorem.
    
    Not as robust as Miller-Rabin, but simpler and good enough for most cases.
    Tests k random witnesses. Higher k = more confident.
    
    Note: This can be fooled by Carmichael numbers, but they're rare enough
    that I'm not worried for my use cases.
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    import random
    
    for _ in range(k):
        a = random.randint(2, n - 2)
        if fast_mod_exp(a, n - 1, n) != 1:
            return False
    
    return True


if __name__ == "__main__":
    print("=== Modular Arithmetic Toolkit Demo ===\n")
    
    # Demo 1: Fast modular exponentiation
    print("1. Fast Modular Exponentiation")
    base, exp, mod = 3, 1000000, 1000000007
    result = fast_mod_exp(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}")
    print(f"   (This would overflow with regular exponentiation)\n")
    
    # Demo 2: Modular inverse
    print("2. Modular Inverse")
    a, m = 7, 26
    inv = mod_inverse(a, m)
    if inv:
        print(f"   Inverse of {a} mod {m} = {inv}")
        print(f"   Verification: ({a} * {inv}) mod {m} = {(a * inv) % m}\n")
    
    # Demo 3: Chinese Remainder Theorem
    print("3. Chinese Remainder Theorem")
    print("   Solving system:")
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    for r, m in zip(remainders, moduli):
        print(f"   x ≡ {r} (mod {m})")
    
    solution = chinese_remainder_theorem(remainders, moduli)
    print(f"   Solution: x = {solution}")
    print(f"   Verification:")
    for r, m in zip(remainders, moduli):
        print(f"   {solution} mod {m} = {solution % m} (expected {r})")
    print()
    
    # Demo 4: Primality testing
    print("4. Fermat Primality Test")
    test_numbers = [17, 221, 561, 1009]  # Mix of primes and composites
    for n in test_numbers:
        is_prime = is_prime_fermat(n, k=10)
        print(f"   {n}: {'probably prime' if is_prime else 'composite'}")
    print()
    
    # Demo 5: Extended GCD
    print("5. Extended GCD")
    a, b = 240, 46
    g, x, y = extended_gcd(a, b)
    print(f"   gcd({a}, {b}) = {g}")
    print(f"   Bézout coefficients: {x}, {y}")
    print(f"   Verification: {a}*({x}) + {b}*({y}) = {a*x + b*y}")
```