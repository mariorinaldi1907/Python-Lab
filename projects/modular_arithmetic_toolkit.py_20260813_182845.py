"""
Date: 2026-08-13
Created a collection of number theory utilities for modular arithmetic operations that I keep reusing in various projects, especially when messing around with RSA and discrete log problems.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit

A collection of number theory utilities I keep rewriting for different projects.
Focused on modular arithmetic operations — the bread and butter of cryptography
and competitive programming.
"""

import math
from typing import Tuple, Optional


def gcd(a: int, b: int) -> int:
    """
    Compute the greatest common divisor using Euclidean algorithm.
    
    Classic recursive implementation because it's elegant and fast enough
    for most practical purposes.
    """
    if b == 0:
        return abs(a)
    return gcd(b, a % b)


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """
    Extended Euclidean algorithm: returns (gcd, x, y) where gcd = ax + by.
    
    This is crucial for finding modular inverses. The coefficients x and y
    are what make it "extended" — we're tracking how to express the GCD
    as a linear combination of a and b.
    """
    if b == 0:
        return (abs(a), 1 if a >= 0 else -1, 0)
    
    gcd_val, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    
    return (gcd_val, x, y)


def mod_inverse(a: int, m: int) -> Optional[int]:
    """
    Find the modular multiplicative inverse of a modulo m.
    
    Returns x such that (a * x) % m == 1, or None if no inverse exists.
    An inverse only exists when gcd(a, m) == 1.
    """
    g, x, _ = extended_gcd(a, m)
    
    if g != 1:
        # No inverse exists when a and m aren't coprime
        return None
    
    # Make sure the result is positive and in range [0, m)
    return x % m


def fast_pow_mod(base: int, exp: int, mod: int) -> int:
    """
    Fast modular exponentiation using binary exponentiation.
    
    Computes (base^exp) % mod efficiently in O(log exp) time.
    This is way faster than doing pow(base, exp) % mod for large exponents
    because we keep the intermediate values small.
    """
    if mod == 1:
        return 0
    
    result = 1
    base = base % mod
    
    # Process each bit of the exponent
    while exp > 0:
        # If current bit is set, multiply current base into result
        if exp & 1:
            result = (result * base) % mod
        
        # Square the base for the next bit position
        exp >>= 1
        base = (base * base) % mod
    
    return result


def is_prime_trial_division(n: int) -> bool:
    """
    Check primality using trial division up to sqrt(n).
    
    Simple but effective for small to medium numbers. Not suitable for
    huge numbers where you'd want Miller-Rabin or similar.
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    # Only check odd divisors up to sqrt(n)
    sqrt_n = int(math.sqrt(n))
    for i in range(3, sqrt_n + 1, 2):
        if n % i == 0:
            return False
    
    return True


def lcm(a: int, b: int) -> int:
    """
    Compute least common multiple using the GCD.
    
    Using the identity: lcm(a,b) = |a*b| / gcd(a,b)
    """
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // gcd(a, b)


def chinese_remainder_theorem(remainders: list, moduli: list) -> Optional[int]:
    """
    Solve system of congruences using Chinese Remainder Theorem.
    
    Given x ≡ remainders[i] (mod moduli[i]) for all i, find x.
    Only works when all moduli are pairwise coprime.
    
    This is super useful in crypto and when you need to reconstruct
    a number from its remainders in different modular systems.
    """
    if len(remainders) != len(moduli):
        return None
    
    # Check that moduli are pairwise coprime
    for i in range(len(moduli)):
        for j in range(i + 1, len(moduli)):
            if gcd(moduli[i], moduli[j]) != 1:
                return None
    
    total = 0
    prod = 1
    for m in moduli:
        prod *= m
    
    for remainder, modulus in zip(remainders, moduli):
        p = prod // modulus
        # Find the modular inverse of p with respect to modulus
        inv = mod_inverse(p, modulus)
        if inv is None:
            return None
        total += remainder * p * inv
    
    return total % prod


def euler_phi(n: int) -> int:
    """
    Compute Euler's totient function φ(n).
    
    Returns the count of integers from 1 to n that are coprime with n.
    Using the formula based on prime factorization.
    """
    result = n
    p = 2
    
    # Find all prime factors and apply formula
    while p * p <= n:
        if n % p == 0:
            # Remove factor p
            while n % p == 0:
                n //= p
            # Multiply result by (1 - 1/p)
            result -= result // p
        p += 1
    
    # If n > 1, then it's a prime factor
    if n > 1:
        result -= result // n
    
    return result


if __name__ == "__main__":
    print("=== Modular Arithmetic Toolkit Demo ===\n")
    
    # GCD and Extended GCD
    print("1. GCD and Extended GCD:")
    a, b = 48, 18
    g = gcd(a, b)
    print(f"   gcd({a}, {b}) = {g}")
    g, x, y = extended_gcd(a, b)
    print(f"   Extended: {g} = {a}*{x} + {b}*{y}")
    print(f"   Verify: {a*x + b*y} = {g}")
    print()
    
    # Modular inverse
    print("2. Modular Inverse:")
    a, m = 7, 26
    inv = mod_inverse(a, m)
    if inv:
        print(f"   {a}^-1 ≡ {inv} (mod {m})")
        print(f"   Verify: ({a} * {inv}) mod {m} = {(a * inv) % m}")
    print()
    
    # Fast modular exponentiation
    print("3. Fast Modular Exponentiation:")
    base, exp, mod = 3, 100000, 1000000007
    result = fast_pow_mod(base, exp, mod)
    print(f"   {base}^{exp} ≡ {result} (mod {mod})")
    print()
    
    # Primality testing
    print("4. Primality Testing:")
    test_nums = [17, 24, 97, 100, 541]
    for n in test_nums:
        print(f"   {n} is {'prime' if is_prime_trial_division(n) else 'composite'}")
    print()
    
    # LCM
    print("5. Least Common Multiple:")
    a, b = 12, 18
    print(f"   lcm({a}, {b}) = {lcm(a, b)}")
    print()
    
    # Chinese Remainder Theorem
    print("6. Chinese Remainder Theorem:")
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    solution = chinese_remainder_theorem(remainders, moduli)
    print(f"   Solving: x ≡ {remainders[0]} (mod {moduli[0]})")
    for i in range(1, len(remainders)):
        print(f"            x ≡ {remainders[i]} (mod {moduli[i]})")
    print(f"   Solution: x = {solution}")
    print(f"   Verify: {solution} mod {moduli[0]} = {solution % moduli[0]}")
    print()
    
    # Euler's totient
    print("7. Euler's Totient Function:")
    test_vals = [10, 12, 17, 36, 100]
    for n in test_vals:
        phi = euler_phi(n)
        print(f"   φ({n}) = {phi}")