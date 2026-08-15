"""
Date: 2026-08-15
Implemented common number theory operations I always end up needing — modular exponentiation, inverse calculation, and Chinese Remainder Theorem solver.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit

A collection of number theory utilities I keep rewriting for Project Euler
and competitive programming problems. Covers the basics: fast modular
exponentiation, modular inverse via extended Euclidean algorithm, and
Chinese Remainder Theorem solving.
"""


def gcd(a, b):
    """
    Compute the greatest common divisor using Euclidean algorithm.
    
    Classic recursive approach — clean and simple.
    """
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a, b):
    """
    Extended Euclidean Algorithm to find gcd and coefficients x, y
    such that a*x + b*y = gcd(a, b).
    
    This is the foundation for computing modular inverses. Returns a tuple
    (gcd, x, y) where the coefficients satisfy Bézout's identity.
    """
    if b == 0:
        return a, 1, 0
    
    # Recursively compute gcd and coefficients
    gcd_val, x1, y1 = extended_gcd(b, a % b)
    
    # Update coefficients based on the recursive relation
    x = y1
    y = x1 - (a // b) * y1
    
    return gcd_val, x, y


def mod_inverse(a, m):
    """
    Compute modular multiplicative inverse of a modulo m.
    
    Returns x such that (a * x) % m == 1.
    Raises ValueError if inverse doesn't exist (when gcd(a, m) != 1).
    
    I use this constantly for division in modular arithmetic, especially
    when working with prime moduli in competitive programming.
    """
    g, x, _ = extended_gcd(a, m)
    
    if g != 1:
        raise ValueError(f"Modular inverse does not exist: gcd({a}, {m}) = {g} != 1")
    
    # Make sure result is positive
    return x % m


def mod_pow(base, exp, mod):
    """
    Fast modular exponentiation using binary exponentiation.
    
    Computes (base^exp) % mod efficiently in O(log exp) time.
    I could use Python's built-in pow(base, exp, mod), but implementing
    this myself helps me remember the algorithm.
    """
    result = 1
    base = base % mod
    
    while exp > 0:
        # If exp is odd, multiply base with result
        if exp % 2 == 1:
            result = (result * base) % mod
        
        # Square the base and halve the exponent
        exp = exp >> 1  # Bit shift is faster than // 2
        base = (base * base) % mod
    
    return result


def chinese_remainder_theorem(remainders, moduli):
    """
    Solve a system of congruences using the Chinese Remainder Theorem.
    
    Given:
        x ≡ remainders[0] (mod moduli[0])
        x ≡ remainders[1] (mod moduli[1])
        ...
    
    Returns the smallest non-negative solution x.
    
    Assumes all moduli are pairwise coprime — that's a requirement for CRT.
    I've used this for RSA-related problems and advent of code puzzles.
    """
    if len(remainders) != len(moduli):
        raise ValueError("remainders and moduli must have the same length")
    
    # Compute the product of all moduli
    total_mod = 1
    for m in moduli:
        total_mod *= m
    
    result = 0
    
    for r, m in zip(remainders, moduli):
        # For each congruence, compute the contribution
        # M_i is the product of all moduli except m
        M_i = total_mod // m
        
        # Find the modular inverse of M_i modulo m
        inv = mod_inverse(M_i, m)
        
        # Add the contribution to result
        result += r * M_i * inv
    
    return result % total_mod


def is_prime_fermat(n, k=5):
    """
    Probabilistic primality test using Fermat's Little Theorem.
    
    Tests k random witnesses. Not perfect (Carmichael numbers fool it),
    but good enough for quick checks. For production I'd use Miller-Rabin,
    but this is simpler to understand.
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
        # Fermat's test: if n is prime, a^(n-1) ≡ 1 (mod n)
        if mod_pow(a, n - 1, n) != 1:
            return False
    
    return True


def main():
    """
    Demo the modular arithmetic toolkit with some examples.
    """
    print("=== Modular Arithmetic Toolkit Demo ===\n")
    
    # Fast exponentiation demo
    print("1. Fast Modular Exponentiation")
    base, exp, mod = 3, 100, 7
    result = mod_pow(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}")
    print(f"   Verification with built-in: {pow(base, exp, mod)}\n")
    
    # Modular inverse demo
    print("2. Modular Multiplicative Inverse")
    a, m = 17, 43
    inv = mod_inverse(a, m)
    print(f"   Inverse of {a} mod {m} = {inv}")
    print(f"   Check: ({a} * {inv}) mod {m} = {(a * inv) % m}\n")
    
    # Chinese Remainder Theorem demo
    print("3. Chinese Remainder Theorem")
    remainders = [2, 3, 1]
    moduli = [3, 4, 5]
    solution = chinese_remainder_theorem(remainders, moduli)
    print(f"   System of congruences:")
    for r, m in zip(remainders, moduli):
        print(f"      x ≡ {r} (mod {m})")
    print(f"   Solution: x = {solution}")
    print(f"   Verification:")
    for r, m in zip(remainders, moduli):
        print(f"      {solution} mod {m} = {solution % m} (expected {r})")
    print()
    
    # Primality testing demo
    print("4. Fermat Primality Test")
    test_numbers = [17, 221, 561, 1009]
    for num in test_numbers:
        is_prime = is_prime_fermat(num, k=10)
        print(f"   {num} is {'probably prime' if is_prime else 'composite'}")
    print()
    
    # Extended GCD demo
    print("5. Extended Euclidean Algorithm")
    a, b = 240, 46
    g, x, y = extended_gcd(a, b)
    print(f"   gcd({a}, {b}) = {g}")
    print(f"   Bézout coefficients: x={x}, y={y}")
    print(f"   Verification: {a}*{x} + {b}*{y} = {a*x + b*y}\n")


if __name__ == "__main__":
    main()