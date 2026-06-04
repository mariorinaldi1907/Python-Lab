"""
Date: 2026-06-04
Created a collection of modular arithmetic utilities including fast modular exponentiation, extended Euclidean algorithm, and Chinese Remainder Theorem solver since I keep needing these for crypto challenges.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit

A collection of number theory utilities I keep rewriting for various projects.
Includes modular exponentiation, GCD/LCM, modular inverses, and a CRT solver.
"""


def gcd(a, b):
    """
    Compute the greatest common divisor using Euclidean algorithm.
    
    Classic recursive approach — simple and clean.
    """
    while b:
        a, b = b, a % b
    return a


def lcm(a, b):
    """
    Compute the least common multiple.
    
    Uses the relationship: lcm(a,b) * gcd(a,b) = a * b
    """
    return abs(a * b) // gcd(a, b)


def extended_gcd(a, b):
    """
    Extended Euclidean algorithm.
    
    Returns (gcd, x, y) such that a*x + b*y = gcd(a, b).
    This is critical for finding modular inverses.
    """
    if b == 0:
        return a, 1, 0
    
    gcd_val, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    
    return gcd_val, x, y


def mod_inverse(a, m):
    """
    Find the modular multiplicative inverse of a modulo m.
    
    Returns x such that (a * x) % m == 1.
    Raises ValueError if the inverse doesn't exist (when gcd(a, m) != 1).
    """
    g, x, _ = extended_gcd(a, m)
    
    if g != 1:
        raise ValueError(f"Modular inverse doesn't exist: gcd({a}, {m}) = {g} != 1")
    
    # Make sure the result is positive
    return x % m


def fast_mod_exp(base, exp, mod):
    """
    Fast modular exponentiation using binary exponentiation.
    
    Computes (base^exp) % mod efficiently in O(log exp) time.
    This is way faster than doing pow(base, exp) % mod for large numbers.
    """
    result = 1
    base = base % mod
    
    while exp > 0:
        # If exp is odd, multiply base with result
        if exp % 2 == 1:
            result = (result * base) % mod
        
        # Square the base and halve the exponent
        exp = exp >> 1
        base = (base * base) % mod
    
    return result


def chinese_remainder_theorem(remainders, moduli):
    """
    Solve a system of congruences using the Chinese Remainder Theorem.
    
    Given:
        x ≡ remainders[0] (mod moduli[0])
        x ≡ remainders[1] (mod moduli[1])
        ...
    
    Find x (the solution is unique modulo the product of all moduli).
    
    The moduli must be pairwise coprime for this to work correctly.
    """
    if len(remainders) != len(moduli):
        raise ValueError("Number of remainders must match number of moduli")
    
    # Calculate the product of all moduli
    total_product = 1
    for m in moduli:
        total_product *= m
    
    result = 0
    
    for remainder, modulus in zip(remainders, moduli):
        # Calculate the product of all other moduli
        partial_product = total_product // modulus
        
        # Find the modular inverse of partial_product mod modulus
        inverse = mod_inverse(partial_product, modulus)
        
        # Add this term to the result
        result += remainder * partial_product * inverse
    
    return result % total_product


def is_prime_fermat(n, k=5):
    """
    Probabilistic primality test using Fermat's Little Theorem.
    
    Not perfect (Carmichael numbers will fool it), but good enough for demos.
    For production code, I'd use Miller-Rabin instead.
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    import random
    
    for _ in range(k):
        a = random.randint(2, n - 1)
        # Check if a^(n-1) ≡ 1 (mod n)
        if fast_mod_exp(a, n - 1, n) != 1:
            return False
    
    return True


if __name__ == "__main__":
    print("=== Modular Arithmetic Toolkit Demo ===\n")
    
    # GCD and LCM
    print("1. GCD and LCM:")
    a, b = 48, 18
    print(f"   gcd({a}, {b}) = {gcd(a, b)}")
    print(f"   lcm({a}, {b}) = {lcm(a, b)}")
    
    # Extended GCD
    print("\n2. Extended GCD:")
    a, b = 35, 15
    g, x, y = extended_gcd(a, b)
    print(f"   For {a} and {b}:")
    print(f"   gcd = {g}, where {a}*({x}) + {b}*({y}) = {g}")
    print(f"   Verification: {a*x + b*y} = {g}")
    
    # Modular inverse
    print("\n3. Modular Inverse:")
    a, m = 7, 26
    inv = mod_inverse(a, m)
    print(f"   Inverse of {a} mod {m} = {inv}")
    print(f"   Verification: ({a} * {inv}) mod {m} = {(a * inv) % m}")
    
    # Fast modular exponentiation
    print("\n4. Fast Modular Exponentiation:")
    base, exp, mod = 3, 1000000, 1000000007
    result = fast_mod_exp(base, exp, mod)
    print(f"   ({base}^{exp}) mod {mod} = {result}")
    
    # Chinese Remainder Theorem
    print("\n5. Chinese Remainder Theorem:")
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    x = chinese_remainder_theorem(remainders, moduli)
    print(f"   Solving system:")
    for r, m in zip(remainders, moduli):
        print(f"     x ≡ {r} (mod {m})")
    print(f"   Solution: x = {x}")
    print(f"   Verification:")
    for r, m in zip(remainders, moduli):
        print(f"     {x} mod {m} = {x % m} (expected {r})")
    
    # Primality testing
    print("\n6. Primality Testing (Fermat's test):")
    test_numbers = [17, 19, 20, 97, 100, 561]  # 561 is a Carmichael number
    for n in test_numbers:
        result = "probably prime" if is_prime_fermat(n) else "composite"
        print(f"   {n}: {result}")