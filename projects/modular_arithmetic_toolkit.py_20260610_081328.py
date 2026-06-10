"""
Date: 2026-06-10
Implemented core modular arithmetic operations I always end up needing for competitive programming and cryptography experiments — includes modular exponentiation, inverse via extended Euclidean algorithm, and Chinese Remainder Theorem solver.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit

A collection of number theory utilities I keep rewriting for various projects.
Implements fast modular exponentiation, modular inverse, extended GCD, and 
Chinese Remainder Theorem solver.

Author: Mario
"""


def gcd(a, b):
    """
    Compute the greatest common divisor using Euclidean algorithm.
    
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
    Extended Euclidean algorithm to find coefficients x, y such that:
    ax + by = gcd(a, b)
    
    This is essential for computing modular inverses.
    
    Args:
        a: First integer
        b: Second integer
    
    Returns:
        Tuple (gcd, x, y) where gcd is the GCD and x, y are the coefficients
    """
    if b == 0:
        return a, 1, 0
    
    gcd_val, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    
    return gcd_val, x, y


def mod_inverse(a, m):
    """
    Compute the modular multiplicative inverse of a modulo m.
    
    Finds x such that (a * x) % m == 1.
    Only exists when gcd(a, m) == 1.
    
    Args:
        a: The number to find the inverse of
        m: The modulus
    
    Returns:
        The modular inverse of a mod m
    
    Raises:
        ValueError: If the modular inverse doesn't exist
    """
    gcd_val, x, _ = extended_gcd(a, m)
    
    if gcd_val != 1:
        raise ValueError(f"Modular inverse doesn't exist: gcd({a}, {m}) = {gcd_val}")
    
    # Make sure the result is positive
    return (x % m + m) % m


def mod_exp(base, exponent, modulus):
    """
    Fast modular exponentiation using binary exponentiation (square-and-multiply).
    
    Computes (base^exponent) % modulus efficiently in O(log exponent) time.
    Way faster than doing pow(base, exponent) % modulus for large numbers.
    
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
        
        # Now exponent must be even, square the base and halve the exponent
        exponent = exponent >> 1  # Bit shift is faster than // 2
        base = (base * base) % modulus
    
    return result


def chinese_remainder_theorem(remainders, moduli):
    """
    Solve a system of congruences using the Chinese Remainder Theorem.
    
    Given:
        x ≡ r1 (mod m1)
        x ≡ r2 (mod m2)
        ...
        x ≡ rn (mod mn)
    
    Find x (the solution is unique modulo M = m1 * m2 * ... * mn).
    
    This assumes all moduli are pairwise coprime. I should probably add a check
    for that, but for now I'm just documenting the requirement.
    
    Args:
        remainders: List of remainders [r1, r2, ..., rn]
        moduli: List of moduli [m1, m2, ..., mn]
    
    Returns:
        The solution x in the range [0, M) where M is the product of all moduli
    
    Raises:
        ValueError: If the input lists have different lengths
    """
    if len(remainders) != len(moduli):
        raise ValueError("Number of remainders must match number of moduli")
    
    # Calculate the product of all moduli
    M = 1
    for m in moduli:
        M *= m
    
    x = 0
    
    for remainder, modulus in zip(remainders, moduli):
        # M_i is the product of all moduli except the current one
        M_i = M // modulus
        
        # Find the modular inverse of M_i mod modulus
        # This is the key step that makes CRT work
        inv = mod_inverse(M_i, modulus)
        
        # Add the contribution of this congruence
        x += remainder * M_i * inv
    
    # Return result in canonical form [0, M)
    return x % M


if __name__ == "__main__":
    print("=== Modular Arithmetic Toolkit Demo ===\n")
    
    # Demo 1: Fast modular exponentiation
    print("1. Fast Modular Exponentiation")
    base, exp, mod = 3, 1000000, 1000000007
    result = mod_exp(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}")
    print()
    
    # Demo 2: Modular inverse
    print("2. Modular Inverse")
    a, m = 17, 43
    inv = mod_inverse(a, m)
    print(f"   Inverse of {a} mod {m} = {inv}")
    print(f"   Verification: ({a} * {inv}) mod {m} = {(a * inv) % m}")
    print()
    
    # Demo 3: Chinese Remainder Theorem
    print("3. Chinese Remainder Theorem")
    print("   Solving the system:")
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    for r, m in zip(remainders, moduli):
        print(f"   x ≡ {r} (mod {m})")
    
    solution = chinese_remainder_theorem(remainders, moduli)
    print(f"   Solution: x = {solution}")
    
    # Verify the solution
    print("   Verification:")
    for r, m in zip(remainders, moduli):
        print(f"   {solution} mod {m} = {solution % m} (expected {r})")
    print()
    
    # Demo 4: RSA toy example
    print("4. Toy RSA Encryption/Decryption")
    # Using small primes for demo (don't do this in real crypto!)
    p, q = 61, 53
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 17  # Public exponent
    d = mod_inverse(e, phi)  # Private exponent
    
    message = 42
    encrypted = mod_exp(message, e, n)
    decrypted = mod_exp(encrypted, d, n)
    
    print(f"   Message: {message}")
    print(f"   Encrypted: {encrypted}")
    print(f"   Decrypted: {decrypted}")
    print()