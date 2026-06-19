"""
Date: 2026-06-19
Created a collection of modular arithmetic functions I keep needing for Project Euler and CTF challenges, featuring fast modular exponentiation and the extended Euclidean algorithm.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit

A collection of number theory utilities I find myself reimplementing
constantly. Includes modular exponentiation, GCD variants, and modular
inverse calculation using the extended Euclidean algorithm.
"""


def gcd(a, b):
    """
    Compute the greatest common divisor using Euclid's algorithm.
    
    Args:
        a: First integer
        b: Second integer
    
    Returns:
        The GCD of a and b
    """
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a, b):
    """
    Extended Euclidean algorithm - finds gcd(a,b) and coefficients x, y
    such that ax + by = gcd(a, b).
    
    This is the core of computing modular inverses, which is why I needed
    it in the first place (RSA calculations).
    
    Args:
        a: First integer
        b: Second integer
    
    Returns:
        Tuple (gcd, x, y) where gcd is gcd(a,b) and ax + by = gcd
    """
    if b == 0:
        return a, 1, 0
    
    # Recursively compute extended GCD
    gcd_val, x1, y1 = extended_gcd(b, a % b)
    
    # Update x and y using results of recursive call
    x = y1
    y = x1 - (a // b) * y1
    
    return gcd_val, x, y


def mod_inverse(a, m):
    """
    Compute the modular multiplicative inverse of a modulo m.
    
    Returns x such that (a * x) % m == 1.
    Only exists when gcd(a, m) == 1.
    
    Args:
        a: The number to invert
        m: The modulus
    
    Returns:
        The modular inverse of a mod m
    
    Raises:
        ValueError: If the modular inverse doesn't exist
    """
    gcd_val, x, _ = extended_gcd(a, m)
    
    if gcd_val != 1:
        raise ValueError(f"Modular inverse doesn't exist: gcd({a}, {m}) = {gcd_val} ≠ 1")
    
    # Make sure the result is positive
    return x % m


def mod_pow(base, exp, mod):
    """
    Fast modular exponentiation using binary exponentiation.
    
    Computes (base^exp) % mod efficiently without computing base^exp first.
    Uses the square-and-multiply algorithm - way faster than naive approach
    for large exponents.
    
    Args:
        base: The base number
        exp: The exponent (non-negative integer)
        mod: The modulus
    
    Returns:
        (base^exp) % mod
    """
    if mod == 1:
        return 0
    
    result = 1
    base = base % mod
    
    while exp > 0:
        # If exp is odd, multiply base with result
        if exp % 2 == 1:
            result = (result * base) % mod
        
        # Now exp must be even - square the base and halve the exponent
        exp = exp >> 1  # Bit shift is faster than exp // 2
        base = (base * base) % mod
    
    return result


def lcm(a, b):
    """
    Compute the least common multiple of two numbers.
    
    Uses the relationship: lcm(a,b) * gcd(a,b) = a * b
    
    Args:
        a: First integer
        b: Second integer
    
    Returns:
        The LCM of a and b
    """
    return abs(a * b) // gcd(a, b)


def chinese_remainder_theorem(remainders, moduli):
    """
    Solve a system of congruences using the Chinese Remainder Theorem.
    
    Finds x such that:
        x ≡ remainders[0] (mod moduli[0])
        x ≡ remainders[1] (mod moduli[1])
        ...
    
    Moduli must be pairwise coprime for a unique solution to exist.
    
    Args:
        remainders: List of remainders
        moduli: List of moduli (must be pairwise coprime)
    
    Returns:
        The solution x (smallest non-negative value)
    """
    if len(remainders) != len(moduli):
        raise ValueError("Must have same number of remainders and moduli")
    
    # Compute the product of all moduli
    total_mod = 1
    for m in moduli:
        total_mod *= m
    
    result = 0
    
    for remainder, modulus in zip(remainders, moduli):
        # For each congruence, compute the partial product
        partial_mod = total_mod // modulus
        
        # Find the modular inverse
        inverse = mod_inverse(partial_mod, modulus)
        
        # Add this term to the result
        result += remainder * partial_mod * inverse
    
    return result % total_mod


if __name__ == "__main__":
    print("=== Modular Arithmetic Toolkit Demo ===\n")
    
    # Demo GCD and Extended GCD
    print("1. GCD and Extended GCD")
    a, b = 240, 46
    g = gcd(a, b)
    gcd_val, x, y = extended_gcd(a, b)
    print(f"   gcd({a}, {b}) = {g}")
    print(f"   Extended: {a}*{x} + {b}*{y} = {gcd_val}")
    print(f"   Verification: {a*x + b*y} = {gcd_val}\n")
    
    # Demo modular inverse
    print("2. Modular Inverse")
    a, m = 17, 43
    inv = mod_inverse(a, m)
    print(f"   Inverse of {a} mod {m} = {inv}")
    print(f"   Verification: ({a} * {inv}) % {m} = {(a * inv) % m}\n")
    
    # Demo fast modular exponentiation
    print("3. Fast Modular Exponentiation")
    base, exp, mod = 123456, 789012, 1000000007
    result = mod_pow(base, exp, mod)
    print(f"   ({base}^{exp}) mod {mod} = {result}")
    print(f"   (Computing this naively would be impossibly slow!)\n")
    
    # Demo LCM
    print("4. Least Common Multiple")
    a, b = 12, 18
    l = lcm(a, b)
    print(f"   lcm({a}, {b}) = {l}\n")
    
    # Demo Chinese Remainder Theorem
    print("5. Chinese Remainder Theorem")
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    x = chinese_remainder_theorem(remainders, moduli)
    print(f"   Solving system:")
    for r, m in zip(remainders, moduli):
        print(f"      x ≡ {r} (mod {m})")
    print(f"   Solution: x = {x}")
    print(f"   Verification:")
    for r, m in zip(remainders, moduli):
        print(f"      {x} mod {m} = {x % m} (expected {r})")