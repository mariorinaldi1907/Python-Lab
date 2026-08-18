"""
Date: 2026-08-18
Created a collection of modular arithmetic utilities I always end up rewriting — includes fast modular exponentiation, extended GCD, and Chinese Remainder Theorem solver.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit

A collection of number theory utilities I got tired of reimplementing.
Focuses on modular arithmetic operations that come up in competitive programming
and cryptography exercises.
"""

from typing import Tuple, List, Optional


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """
    Extended Euclidean Algorithm.
    
    Returns (gcd, x, y) such that a*x + b*y = gcd(a, b).
    This is super useful for finding modular inverses.
    
    Args:
        a: First integer
        b: Second integer
    
    Returns:
        Tuple of (gcd, x, y) where gcd = a*x + b*y
    """
    if b == 0:
        return a, 1, 0
    
    gcd, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    
    return gcd, x, y


def mod_inverse(a: int, m: int) -> Optional[int]:
    """
    Compute modular multiplicative inverse of a modulo m.
    
    Returns x such that (a * x) % m == 1, or None if inverse doesn't exist.
    The inverse exists only when gcd(a, m) == 1.
    
    Args:
        a: Number to find inverse of
        m: Modulus
    
    Returns:
        Modular inverse or None if it doesn't exist
    """
    gcd, x, _ = extended_gcd(a, m)
    
    if gcd != 1:
        return None  # Inverse doesn't exist
    
    return x % m


def fast_power(base: int, exp: int, mod: int) -> int:
    """
    Fast modular exponentiation using binary exponentiation.
    
    Computes (base^exp) % mod efficiently in O(log exp) time.
    Way faster than pow(base, exp) % mod for huge exponents.
    
    Args:
        base: Base number
        exp: Exponent (must be non-negative)
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
        exp = exp >> 1  # Bit shift is faster than // 2
        base = (base * base) % mod
    
    return result


def chinese_remainder_theorem(remainders: List[int], moduli: List[int]) -> Optional[int]:
    """
    Solve system of congruences using Chinese Remainder Theorem.
    
    Given x ≡ r1 (mod m1), x ≡ r2 (mod m2), ..., finds x.
    Works when all moduli are pairwise coprime.
    
    Args:
        remainders: List of remainders [r1, r2, ...]
        moduli: List of moduli [m1, m2, ...]
    
    Returns:
        Solution x, or None if no solution exists
    """
    if len(remainders) != len(moduli):
        return None
    
    if len(remainders) == 0:
        return None
    
    # Product of all moduli
    M = 1
    for m in moduli:
        M *= m
    
    x = 0
    
    for i in range(len(remainders)):
        Mi = M // moduli[i]
        
        # Find modular inverse of Mi with respect to moduli[i]
        inv = mod_inverse(Mi, moduli[i])
        if inv is None:
            return None  # Moduli aren't coprime
        
        x += remainders[i] * Mi * inv
    
    return x % M


def is_prime_fermat(n: int, k: int = 5) -> bool:
    """
    Probabilistic primality test using Fermat's Little Theorem.
    
    Not perfect (Carmichael numbers fool it), but good enough for most cases.
    For serious crypto work, use Miller-Rabin instead.
    
    Args:
        n: Number to test
        k: Number of test iterations (higher = more accurate)
    
    Returns:
        True if probably prime, False if definitely composite
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    import random
    
    # Test with k random bases
    for _ in range(k):
        a = random.randint(2, n - 2)
        # Fermat's test: a^(n-1) should be ≡ 1 (mod n) if n is prime
        if fast_power(a, n - 1, n) != 1:
            return False
    
    return True


def factorial_mod(n: int, mod: int) -> int:
    """
    Compute n! mod m efficiently.
    
    Naive approach would overflow for large n, so we take mod at each step.
    
    Args:
        n: Factorial input
        mod: Modulus
    
    Returns:
        n! % mod
    """
    result = 1
    for i in range(2, n + 1):
        result = (result * i) % mod
    return result


if __name__ == "__main__":
    print("=== Modular Arithmetic Toolkit Demo ===\n")
    
    # Demo 1: Extended GCD
    print("1. Extended GCD")
    a, b = 240, 46
    gcd, x, y = extended_gcd(a, b)
    print(f"   gcd({a}, {b}) = {gcd}")
    print(f"   {a}*{x} + {b}*{y} = {gcd}")
    print(f"   Verification: {a*x + b*y} == {gcd}\n")
    
    # Demo 2: Modular Inverse
    print("2. Modular Inverse")
    a, m = 3, 11
    inv = mod_inverse(a, m)
    print(f"   Inverse of {a} mod {m} = {inv}")
    print(f"   Verification: ({a} * {inv}) mod {m} = {(a * inv) % m}\n")
    
    # Demo 3: Fast Exponentiation
    print("3. Fast Modular Exponentiation")
    base, exp, mod = 2, 1000, 997
    result = fast_power(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}")
    print(f"   (Compare with Python's pow: {pow(base, exp, mod)})\n")
    
    # Demo 4: Chinese Remainder Theorem
    print("4. Chinese Remainder Theorem")
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    print(f"   Solving: x ≡ {remainders[0]} (mod {moduli[0]})")
    print(f"            x ≡ {remainders[1]} (mod {moduli[1]})")
    print(f"            x ≡ {remainders[2]} (mod {moduli[2]})")
    solution = chinese_remainder_theorem(remainders, moduli)
    print(f"   Solution: x = {solution}")
    print(f"   Verification: {solution} mod {moduli[0]} = {solution % moduli[0]}")
    print(f"                 {solution} mod {moduli[1]} = {solution % moduli[1]}")
    print(f"                 {solution} mod {moduli[2]} = {solution % moduli[2]}\n")
    
    # Demo 5: Primality Testing
    print("5. Fermat Primality Test")
    test_numbers = [17, 97, 100, 561]  # 561 is a Carmichael number
    for num in test_numbers:
        is_prime = is_prime_fermat(num, k=10)
        print(f"   {num}: {'probably prime' if is_prime else 'composite'}")
    
    print("\n6. Factorial Modulo")
    n, mod = 10, 13
    fact_mod = factorial_mod(n, mod)
    print(f"   {n}! mod {mod} = {fact_mod}")