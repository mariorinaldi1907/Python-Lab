"""
Date: 2026-05-29
I wanted a clean implementation of modular arithmetic operations I keep reusing, so I bundled modular exponentiation, extended GCD, and the Chinese Remainder Theorem into one script.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit
A collection of number theory functions I find myself needing over and over.
Includes fast modular exponentiation, extended Euclidean algorithm, and CRT.
"""


def mod_exp(base, exp, mod):
    """
    Compute (base^exp) % mod efficiently using binary exponentiation.
    
    This is way faster than doing pow(base, exp) % mod for large numbers
    because we keep intermediate results small by taking mod at each step.
    
    Args:
        base: The base number
        exp: The exponent (must be non-negative)
        mod: The modulus
    
    Returns:
        Result of (base^exp) mod mod
    """
    if mod == 1:
        return 0
    
    result = 1
    base = base % mod
    
    while exp > 0:
        # If exp is odd, multiply base with result
        if exp % 2 == 1:
            result = (result * base) % mod
        
        # Now exp must be even, so we can divide it by 2
        exp = exp >> 1  # Bit shift is faster than exp // 2
        base = (base * base) % mod
    
    return result


def extended_gcd(a, b):
    """
    Extended Euclidean Algorithm - finds gcd(a,b) and coefficients x, y
    such that a*x + b*y = gcd(a,b).
    
    This is super useful for finding modular inverses and solving
    linear Diophantine equations.
    
    Args:
        a, b: Two integers
    
    Returns:
        Tuple (gcd, x, y) where gcd = a*x + b*y
    """
    if a == 0:
        return b, 0, 1
    
    gcd, x1, y1 = extended_gcd(b % a, a)
    
    # Update x and y using results of recursive call
    x = y1 - (b // a) * x1
    y = x1
    
    return gcd, x, y


def mod_inverse(a, m):
    """
    Find the modular multiplicative inverse of a modulo m.
    
    Returns x such that (a * x) % m == 1.
    Only exists if gcd(a, m) == 1.
    
    Args:
        a: The number to invert
        m: The modulus
    
    Returns:
        The modular inverse, or None if it doesn't exist
    """
    gcd, x, _ = extended_gcd(a, m)
    
    if gcd != 1:
        return None  # Modular inverse doesn't exist
    
    # Make sure result is positive
    return (x % m + m) % m


def chinese_remainder_theorem(remainders, moduli):
    """
    Solve a system of congruences using the Chinese Remainder Theorem.
    
    Given: x ≡ r1 (mod m1), x ≡ r2 (mod m2), ..., x ≡ rn (mod mn)
    Find: The unique solution x modulo (m1 * m2 * ... * mn)
    
    This assumes all moduli are pairwise coprime. I'm not checking that
    here because in most of my use cases I know they are.
    
    Args:
        remainders: List of remainders [r1, r2, ..., rn]
        moduli: List of moduli [m1, m2, ..., mn]
    
    Returns:
        The solution x, or None if no solution exists
    """
    if len(remainders) != len(moduli):
        return None
    
    # Product of all moduli
    total_mod = 1
    for m in moduli:
        total_mod *= m
    
    result = 0
    
    for ri, mi in zip(remainders, moduli):
        # Mi is the product of all moduli except mi
        Mi = total_mod // mi
        
        # Find the modular inverse of Mi with respect to mi
        yi = mod_inverse(Mi, mi)
        
        if yi is None:
            return None  # No solution exists
        
        # Add this term to the result
        result += ri * Mi * yi
    
    return result % total_mod


def is_prime_fermat(n, k=5):
    """
    Probabilistic primality test using Fermat's Little Theorem.
    
    Not perfect (fails for Carmichael numbers) but fast and good enough
    for most cases. For k trials, probability of error is at most (1/2)^k.
    
    Args:
        n: Number to test
        k: Number of test iterations (higher = more accurate)
    
    Returns:
        True if n is probably prime, False if definitely composite
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    import random
    
    for _ in range(k):
        # Pick a random number in [2, n-2]
        a = random.randint(2, n - 2)
        
        # Check if a^(n-1) ≡ 1 (mod n)
        if mod_exp(a, n - 1, n) != 1:
            return False
    
    return True


if __name__ == "__main__":
    print("=== Modular Arithmetic Toolkit Demo ===\n")
    
    # Demo 1: Fast modular exponentiation
    print("1. Modular Exponentiation")
    base, exp, mod = 3, 1000000, 7
    result = mod_exp(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}")
    print(f"   (Python's built-in pow gives: {pow(base, exp, mod)})")
    print()
    
    # Demo 2: Extended GCD
    print("2. Extended Euclidean Algorithm")
    a, b = 240, 46
    gcd, x, y = extended_gcd(a, b)
    print(f"   gcd({a}, {b}) = {gcd}")
    print(f"   Bézout coefficients: {a}*({x}) + {b}*({y}) = {gcd}")
    print(f"   Verification: {a*x + b*y} = {gcd}")
    print()
    
    # Demo 3: Modular inverse
    print("3. Modular Inverse")
    a, m = 17, 43
    inv = mod_inverse(a, m)
    if inv:
        print(f"   Inverse of {a} mod {m} = {inv}")
        print(f"   Verification: ({a} * {inv}) mod {m} = {(a * inv) % m}")
    print()
    
    # Demo 4: Chinese Remainder Theorem
    print("4. Chinese Remainder Theorem")
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    solution = chinese_remainder_theorem(remainders, moduli)
    print(f"   System: x ≡ {remainders[0]} (mod {moduli[0]})")
    for i in range(1, len(remainders)):
        print(f"           x ≡ {remainders[i]} (mod {moduli[i]})")
    print(f"   Solution: x = {solution}")
    print(f"   Verification: {solution} mod {moduli[0]} = {solution % moduli[0]}")
    print(f"                 {solution} mod {moduli[1]} = {solution % moduli[1]}")
    print(f"                 {solution} mod {moduli[2]} = {solution % moduli[2]}")
    print()
    
    # Demo 5: Primality testing
    print("5. Fermat Primality Test")
    test_numbers = [17, 561, 997, 1000]
    for num in test_numbers:
        is_prob_prime = is_prime_fermat(num, k=10)
        print(f"   {num}: {'probably prime' if is_prob_prime else 'composite'}")