"""
Date: 2026-08-28
Created a collection of modular arithmetic functions I've been wanting for Project Euler problems, handles cryptographic-sized integers efficiently.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit

A collection of number theory utilities for working with modular arithmetic.
I kept running into these problems on Project Euler and Codeforces, so I
finally sat down and wrote proper implementations.

Includes:
- Fast modular exponentiation (for RSA-sized numbers)
- Extended Euclidean algorithm
- Modular multiplicative inverse
- Chinese Remainder Theorem solver
- Basic primality testing
"""

import math
from typing import Tuple, List, Optional


def mod_exp(base: int, exponent: int, modulus: int) -> int:
    """
    Compute (base^exponent) % modulus efficiently using binary exponentiation.
    
    This is way faster than pow() for huge numbers because we keep intermediate
    results small by taking mod at each step. Critical for crypto operations.
    
    Args:
        base: The base number
        exponent: The power to raise to (must be non-negative)
        modulus: The modulus to reduce by
    
    Returns:
        Result of (base^exponent) mod modulus
    """
    if modulus == 1:
        return 0
    
    result = 1
    base = base % modulus
    
    # Process exponent bit by bit from right to left
    while exponent > 0:
        # If current bit is set, multiply result by current base
        if exponent % 2 == 1:
            result = (result * base) % modulus
        
        # Square the base for the next bit position
        exponent = exponent >> 1
        base = (base * base) % modulus
    
    return result


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """
    Extended Euclidean algorithm - finds gcd(a,b) and Bézout coefficients.
    
    Returns (gcd, x, y) such that a*x + b*y = gcd(a, b)
    This is the foundation for computing modular inverses.
    
    Args:
        a: First integer
        b: Second integer
    
    Returns:
        Tuple of (gcd, x, y) where gcd is the greatest common divisor
    """
    if a == 0:
        return b, 0, 1
    
    gcd, x1, y1 = extended_gcd(b % a, a)
    
    # Update x and y using results from recursive call
    x = y1 - (b // a) * x1
    y = x1
    
    return gcd, x, y


def mod_inverse(a: int, m: int) -> Optional[int]:
    """
    Compute the modular multiplicative inverse of a modulo m.
    
    Returns x such that (a * x) % m == 1
    Only exists when gcd(a, m) == 1
    
    I use this constantly for division in modular arithmetic - instead of
    dividing by a, multiply by its inverse.
    
    Args:
        a: Number to find inverse of
        m: The modulus
    
    Returns:
        Modular inverse if it exists, None otherwise
    """
    gcd, x, _ = extended_gcd(a, m)
    
    if gcd != 1:
        # Inverse doesn't exist
        return None
    
    # Make sure result is positive
    return (x % m + m) % m


def chinese_remainder_theorem(remainders: List[int], moduli: List[int]) -> Optional[int]:
    """
    Solve system of congruences using Chinese Remainder Theorem.
    
    Given x ≡ r1 (mod m1), x ≡ r2 (mod m2), ..., finds x.
    The moduli must be pairwise coprime for a unique solution to exist.
    
    This came up when I was solving a synced-cycles problem - had to find
    when multiple periodic events aligned.
    
    Args:
        remainders: List of remainders [r1, r2, ...]
        moduli: List of moduli [m1, m2, ...]
    
    Returns:
        Solution x if it exists, None if moduli aren't coprime
    """
    if len(remainders) != len(moduli):
        return None
    
    # Product of all moduli
    M = math.prod(moduli)
    result = 0
    
    for remainder, modulus in zip(remainders, moduli):
        Mi = M // modulus
        # Find modular inverse of Mi mod modulus
        inv = mod_inverse(Mi, modulus)
        
        if inv is None:
            # Moduli aren't coprime
            return None
        
        result += remainder * Mi * inv
    
    return result % M


def is_prime_miller_rabin(n: int, k: int = 5) -> bool:
    """
    Miller-Rabin primality test - probabilistic but fast for large numbers.
    
    With k=5, probability of false positive is less than (1/4)^5 ≈ 0.1%
    Good enough for most purposes and way faster than trial division.
    
    Args:
        n: Number to test for primality
        k: Number of rounds (higher = more accurate but slower)
    
    Returns:
        True if n is probably prime, False if definitely composite
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    # Write n-1 as 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    # Witness loop - test k random witnesses
    import random
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = mod_exp(a, d, n)
        
        if x == 1 or x == n - 1:
            continue
        
        for _ in range(r - 1):
            x = mod_exp(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    
    return True


if __name__ == "__main__":
    print("=== Modular Arithmetic Toolkit Demo ===\n")
    
    # Fast exponentiation - useful for RSA
    print("1. Fast Modular Exponentiation")
    base, exp, mod = 123456789, 987654321, 1000000007
    result = mod_exp(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}")
    print()
    
    # Extended GCD
    print("2. Extended Euclidean Algorithm")
    a, b = 240, 46
    gcd, x, y = extended_gcd(a, b)
    print(f"   gcd({a}, {b}) = {gcd}")
    print(f"   Bézout coefficients: {a}*{x} + {b}*{y} = {gcd}")
    print(f"   Verification: {a*x + b*y} = {gcd}")
    print()
    
    # Modular inverse
    print("3. Modular Multiplicative Inverse")
    num, modulus = 17, 43
    inv = mod_inverse(num, modulus)
    print(f"   Inverse of {num} mod {modulus} = {inv}")
    print(f"   Verification: ({num} * {inv}) mod {modulus} = {(num * inv) % modulus}")
    print()
    
    # Chinese Remainder Theorem
    print("4. Chinese Remainder Theorem")
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    solution = chinese_remainder_theorem(remainders, moduli)
    print(f"   Solving system:")
    for r, m in zip(remainders, moduli):
        print(f"     x ≡ {r} (mod {m})")
    print(f"   Solution: x = {solution}")
    print(f"   Verification: {solution} mod 3 = {solution % 3}, "
          f"{solution} mod 5 = {solution % 5}, {solution} mod 7 = {solution % 7}")
    print()
    
    # Primality testing
    print("5. Miller-Rabin Primality Test")
    test_numbers = [17, 221, 1000000007, 1000000009]
    for n in test_numbers:
        is_prime = is_prime_miller_rabin(n)
        print(f"   {n}: {'probably prime' if is_prime else 'composite'}")