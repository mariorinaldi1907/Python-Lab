"""
Date: 2026-08-01
Implemented core number theory algorithms I keep needing for cryptography problems and competitive programming — proper handling of edge cases included.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit

A collection of number theory utilities I find myself needing constantly.
Implements extended Euclidean algorithm, modular inverse, Chinese Remainder Theorem,
and fast modular exponentiation.

Author: Mario
"""


def gcd(a, b):
    """
    Compute the greatest common divisor using Euclidean algorithm.
    
    Args:
        a: First integer
        b: Second integer
    
    Returns:
        Greatest common divisor of a and b
    """
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a, b):
    """
    Extended Euclidean Algorithm.
    
    Finds integers x, y such that a*x + b*y = gcd(a, b).
    This is crucial for finding modular inverses.
    
    Args:
        a: First integer
        b: Second integer
    
    Returns:
        Tuple (gcd, x, y) where gcd is gcd(a,b) and a*x + b*y = gcd
    """
    if b == 0:
        return a, 1, 0
    
    # Recursive case: work backwards from the base case
    gcd_val, x1, y1 = extended_gcd(b, a % b)
    
    # Update x and y using results from recursive call
    x = y1
    y = x1 - (a // b) * y1
    
    return gcd_val, x, y


def mod_inverse(a, m):
    """
    Compute modular multiplicative inverse of a modulo m.
    
    Returns x such that (a * x) % m == 1.
    Only exists if gcd(a, m) == 1.
    
    Args:
        a: Number to find inverse of
        m: Modulus
    
    Returns:
        Modular inverse of a mod m
    
    Raises:
        ValueError: If inverse doesn't exist (gcd(a, m) != 1)
    """
    gcd_val, x, _ = extended_gcd(a, m)
    
    if gcd_val != 1:
        raise ValueError(f"Modular inverse doesn't exist: gcd({a}, {m}) = {gcd_val} != 1")
    
    # Make sure result is positive
    return (x % m + m) % m


def fast_mod_exp(base, exp, mod):
    """
    Fast modular exponentiation using binary exponentiation.
    
    Computes (base^exp) % mod efficiently in O(log exp) time.
    Way faster than doing pow(base, exp) % mod for large exponents.
    
    Args:
        base: Base number
        exp: Exponent (non-negative)
        mod: Modulus
    
    Returns:
        (base^exp) % mod
    """
    if exp < 0:
        raise ValueError("Exponent must be non-negative")
    
    result = 1
    base = base % mod
    
    while exp > 0:
        # If exp is odd, multiply base with result
        if exp % 2 == 1:
            result = (result * base) % mod
        
        # Square the base and halve the exponent
        exp = exp >> 1  # Bit shift right = divide by 2
        base = (base * base) % mod
    
    return result


def chinese_remainder_theorem(remainders, moduli):
    """
    Solve system of congruences using Chinese Remainder Theorem.
    
    Given x ≡ remainders[i] (mod moduli[i]) for all i,
    finds the unique solution modulo the product of all moduli.
    
    Requires all moduli to be pairwise coprime.
    
    Args:
        remainders: List of remainders
        moduli: List of moduli (must be pairwise coprime)
    
    Returns:
        Solution x that satisfies all congruences
    
    Raises:
        ValueError: If moduli are not pairwise coprime
    """
    if len(remainders) != len(moduli):
        raise ValueError("Number of remainders must equal number of moduli")
    
    # Check pairwise coprimality
    for i in range(len(moduli)):
        for j in range(i + 1, len(moduli)):
            if gcd(moduli[i], moduli[j]) != 1:
                raise ValueError(f"Moduli must be pairwise coprime: gcd({moduli[i]}, {moduli[j]}) != 1")
    
    # Product of all moduli
    total_mod = 1
    for m in moduli:
        total_mod *= m
    
    result = 0
    
    # For each congruence
    for remainder, modulus in zip(remainders, moduli):
        # M_i = product of all moduli except current one
        partial_product = total_mod // modulus
        
        # Find modular inverse of partial_product mod current modulus
        inverse = mod_inverse(partial_product, modulus)
        
        # Add this term to result
        result += remainder * partial_product * inverse
    
    return result % total_mod


if __name__ == "__main__":
    print("=== Modular Arithmetic Toolkit Demo ===\n")
    
    # Demo 1: Extended GCD
    print("1. Extended GCD")
    a, b = 240, 46
    g, x, y = extended_gcd(a, b)
    print(f"   gcd({a}, {b}) = {g}")
    print(f"   {a}*({x}) + {b}*({y}) = {a*x + b*y}")
    print(f"   Verification: {a}*{x} + {b}*{y} = {a*x + b*y}\n")
    
    # Demo 2: Modular Inverse
    print("2. Modular Inverse")
    a, m = 7, 26
    inv = mod_inverse(a, m)
    print(f"   Inverse of {a} mod {m} = {inv}")
    print(f"   Verification: ({a} * {inv}) mod {m} = {(a * inv) % m}\n")
    
    # Demo 3: Fast Modular Exponentiation
    print("3. Fast Modular Exponentiation")
    base, exp, mod = 3, 1000000, 1000000007
    result = fast_mod_exp(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}")
    print(f"   (Would take forever with regular pow and mod!)\n")
    
    # Demo 4: Chinese Remainder Theorem
    print("4. Chinese Remainder Theorem")
    # Solving: x ≡ 2 (mod 3), x ≡ 3 (mod 5), x ≡ 2 (mod 7)
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    solution = chinese_remainder_theorem(remainders, moduli)
    print(f"   System of congruences:")
    for r, m in zip(remainders, moduli):
        print(f"      x ≡ {r} (mod {m})")
    print(f"   Solution: x = {solution}")
    print(f"   Verification:")
    for r, m in zip(remainders, moduli):
        print(f"      {solution} mod {m} = {solution % m} (should be {r})")