"""
Date: 2026-07-06
Built a modular arithmetic library with extended GCD, Chinese Remainder Theorem solver, and modular exponentiation because I kept rewriting these for Project Euler problems.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit

A collection of number theory utilities I keep needing for competitive programming
and cryptography experiments. Includes modular exponentiation, inverse, and CRT.

Author: Mario
"""

from typing import Tuple, List, Optional


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """
    Extended Euclidean Algorithm.
    
    Returns (gcd, x, y) such that a*x + b*y = gcd(a, b).
    This is useful for finding modular inverses and solving linear Diophantine equations.
    
    Args:
        a: First integer
        b: Second integer
    
    Returns:
        Tuple of (gcd, x, y) where gcd is the greatest common divisor
    """
    if b == 0:
        return (a, 1, 0)
    
    gcd, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    
    return (gcd, x, y)


def mod_inverse(a: int, m: int) -> Optional[int]:
    """
    Compute modular multiplicative inverse of a modulo m.
    
    Returns x such that (a * x) % m == 1, or None if inverse doesn't exist.
    The inverse exists if and only if gcd(a, m) = 1.
    
    Args:
        a: Number to find inverse of
        m: Modulus
    
    Returns:
        Modular inverse or None if it doesn't exist
    """
    gcd, x, _ = extended_gcd(a, m)
    
    if gcd != 1:
        return None  # Inverse doesn't exist
    
    # Make sure result is positive
    return x % m


def fast_mod_exp(base: int, exp: int, mod: int) -> int:
    """
    Fast modular exponentiation using binary exponentiation.
    
    Computes (base^exp) % mod efficiently in O(log exp) time.
    This is way faster than doing pow(base, exp) % mod for large exponents
    because we keep the intermediate results small.
    
    Args:
        base: Base number
        exp: Exponent (must be non-negative)
        mod: Modulus
    
    Returns:
        Result of (base^exp) % mod
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
        exp = exp >> 1  # Bit shift is faster than division
        base = (base * base) % mod
    
    return result


def chinese_remainder_theorem(remainders: List[int], moduli: List[int]) -> Optional[int]:
    """
    Solve system of congruences using Chinese Remainder Theorem.
    
    Given x ≡ r1 (mod m1), x ≡ r2 (mod m2), ..., finds x.
    Assumes all moduli are pairwise coprime (which I should probably validate but eh).
    
    Args:
        remainders: List of remainders [r1, r2, ...]
        moduli: List of moduli [m1, m2, ...]
    
    Returns:
        Solution x, or None if no solution exists
    """
    if len(remainders) != len(moduli):
        raise ValueError("Must have same number of remainders and moduli")
    
    if len(remainders) == 0:
        return None
    
    # Product of all moduli
    total_mod = 1
    for m in moduli:
        total_mod *= m
    
    result = 0
    
    for r, m in zip(remainders, moduli):
        # M_i = product of all moduli except m_i
        M_i = total_mod // m
        
        # Find modular inverse of M_i mod m_i
        inv = mod_inverse(M_i, m)
        if inv is None:
            return None  # Moduli aren't coprime
        
        # Add contribution of this congruence
        result += r * M_i * inv
    
    return result % total_mod


def is_prime_miller_rabin(n: int, k: int = 5) -> bool:
    """
    Miller-Rabin probabilistic primality test.
    
    Not 100% accurate but good enough for most purposes. The probability of
    a composite number passing k rounds is at most 4^(-k).
    
    Args:
        n: Number to test
        k: Number of rounds (higher = more accurate)
    
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
    
    # Witness loop
    import random
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = fast_mod_exp(a, d, n)
        
        if x == 1 or x == n - 1:
            continue
        
        for _ in range(r - 1):
            x = fast_mod_exp(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    
    return True


if __name__ == "__main__":
    print("=== Modular Arithmetic Toolkit Demo ===\n")
    
    # Extended GCD demo
    print("1. Extended GCD")
    a, b = 240, 46
    gcd, x, y = extended_gcd(a, b)
    print(f"   gcd({a}, {b}) = {gcd}")
    print(f"   {a}*{x} + {b}*{y} = {gcd}")
    print(f"   Verification: {a*x + b*y} = {gcd}\n")
    
    # Modular inverse demo
    print("2. Modular Inverse")
    a, m = 7, 26
    inv = mod_inverse(a, m)
    if inv:
        print(f"   {a}^(-1) mod {m} = {inv}")
        print(f"   Verification: ({a} * {inv}) mod {m} = {(a * inv) % m}\n")
    
    # Fast modular exponentiation demo
    print("3. Fast Modular Exponentiation")
    base, exp, mod = 3, 1000000, 1000000007
    result = fast_mod_exp(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}\n")
    
    # Chinese Remainder Theorem demo
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
    print(f"                 {solution} mod {moduli[2]} = {solution % moduli[2]}\n")
    
    # Miller-Rabin primality test demo
    print("5. Miller-Rabin Primality Test")
    test_numbers = [17, 221, 561, 1000000007]
    for n in test_numbers:
        result = is_prime_miller_rabin(n, k=10)
        print(f"   {n} is {'probably prime' if result else 'composite'}")