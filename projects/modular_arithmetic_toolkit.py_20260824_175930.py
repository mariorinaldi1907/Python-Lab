"""
Date: 2026-08-24
Created a collection of modular arithmetic functions I keep reusing for number theory problems and crypto toy projects.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit

A collection of number theory utilities I found myself rewriting constantly.
Includes modular exponentiation, extended GCD, Chinese Remainder Theorem solver,
and modular multiplicative inverse calculation.

Author: Mario
"""


def gcd(a, b):
    """
    Calculate the greatest common divisor using Euclid's algorithm.
    
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
    Extended Euclidean Algorithm — finds gcd(a,b) and coefficients x, y
    such that ax + by = gcd(a, b).
    
    This is the workhorse for modular inverse calculations.
    
    Args:
        a: First integer
        b: Second integer
    
    Returns:
        Tuple (gcd, x, y) where gcd is the GCD and x, y are Bézout coefficients
    """
    if b == 0:
        return a, 1, 0
    
    # Recursively compute extended GCD
    gcd_val, x1, y1 = extended_gcd(b, a % b)
    
    # Update x and y using the relation from Euclidean algorithm
    x = y1
    y = x1 - (a // b) * y1
    
    return gcd_val, x, y


def mod_inverse(a, m):
    """
    Calculate the modular multiplicative inverse of a modulo m.
    
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
        raise ValueError(f"Modular inverse doesn't exist: gcd({a}, {m}) = {gcd_val} != 1")
    
    # Make sure the result is positive
    return x % m


def mod_pow(base, exponent, modulus):
    """
    Fast modular exponentiation using binary exponentiation (square-and-multiply).
    
    Computes (base^exponent) % modulus efficiently, even for huge exponents.
    This is way faster than doing pow(base, exponent) % modulus for large numbers.
    
    Args:
        base: The base number
        exponent: The exponent (must be non-negative)
        modulus: The modulus
    
    Returns:
        (base^exponent) % modulus
    """
    if modulus == 1:
        return 0
    
    result = 1
    base = base % modulus
    
    while exponent > 0:
        # If exponent is odd, multiply base with result
        if exponent % 2 == 1:
            result = (result * base) % modulus
        
        # Square the base and halve the exponent
        exponent = exponent >> 1  # Bit shift is faster than // 2
        base = (base * base) % modulus
    
    return result


def chinese_remainder_theorem(remainders, moduli):
    """
    Solve a system of congruences using the Chinese Remainder Theorem.
    
    Given: x ≡ r1 (mod m1), x ≡ r2 (mod m2), ..., x ≡ rn (mod mn)
    Find: The smallest non-negative x that satisfies all congruences
    
    The moduli must be pairwise coprime (gcd of any pair is 1).
    
    Args:
        remainders: List of remainders [r1, r2, ..., rn]
        moduli: List of moduli [m1, m2, ..., mn]
    
    Returns:
        The solution x (smallest non-negative integer)
    
    Raises:
        ValueError: If moduli are not pairwise coprime or lists have different lengths
    """
    if len(remainders) != len(moduli):
        raise ValueError("Remainders and moduli lists must have the same length")
    
    # Check that moduli are pairwise coprime
    for i in range(len(moduli)):
        for j in range(i + 1, len(moduli)):
            if gcd(moduli[i], moduli[j]) != 1:
                raise ValueError(f"Moduli must be pairwise coprime: gcd({moduli[i]}, {moduli[j]}) != 1")
    
    # Product of all moduli
    M = 1
    for m in moduli:
        M *= m
    
    x = 0
    for r, m in zip(remainders, moduli):
        # M_i is the product of all moduli except m
        M_i = M // m
        
        # Find the modular inverse of M_i mod m
        y_i = mod_inverse(M_i, m)
        
        # Add the contribution of this congruence
        x += r * M_i * y_i
    
    return x % M


if __name__ == "__main__":
    print("=" * 60)
    print("Modular Arithmetic Toolkit Demo")
    print("=" * 60)
    
    # Demo 1: Fast modular exponentiation
    print("\n1. Fast Modular Exponentiation")
    print("-" * 40)
    base, exp, mod = 2, 1000, 13
    result = mod_pow(base, exp, mod)
    print(f"Computing {base}^{exp} mod {mod}")
    print(f"Result: {result}")
    print(f"Verification: {pow(base, exp, mod)}")  # Python's built-in for comparison
    
    # Demo 2: Modular inverse
    print("\n2. Modular Multiplicative Inverse")
    print("-" * 40)
    a, m = 17, 43
    inv = mod_inverse(a, m)
    print(f"Inverse of {a} mod {m} = {inv}")
    print(f"Verification: ({a} * {inv}) mod {m} = {(a * inv) % m}")
    
    # Demo 3: Chinese Remainder Theorem
    print("\n3. Chinese Remainder Theorem")
    print("-" * 40)
    remainders = [2, 3, 1]
    moduli = [3, 4, 5]
    print("Solving system of congruences:")
    for r, m in zip(remainders, moduli):
        print(f"  x ≡ {r} (mod {m})")
    
    solution = chinese_remainder_theorem(remainders, moduli)
    print(f"\nSolution: x = {solution}")
    print("Verification:")
    for r, m in zip(remainders, moduli):
        print(f"  {solution} mod {m} = {solution % m} (expected {r})")
    
    # Demo 4: Extended GCD
    print("\n4. Extended Euclidean Algorithm")
    print("-" * 40)
    a, b = 240, 46
    g, x, y = extended_gcd(a, b)
    print(f"For a={a}, b={b}:")
    print(f"  gcd = {g}")
    print(f"  Bézout coefficients: x={x}, y={y}")
    print(f"  Verification: {a}*{x} + {b}*{y} = {a*x + b*y}")
    
    print("\n" + "=" * 60)