"""
Date: 2026-06-30
Wrote a number theory utility for competitive programming practice — handles modular exponentiation, multiplicative inverses, and Chinese Remainder Theorem since I keep rewriting these.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit
A collection of number theory utilities I keep needing for project euler
and competitive programming problems. Includes fast modular exponentiation,
modular inverse (using extended Euclidean algorithm), and Chinese Remainder
Theorem solver.
"""

from math import gcd
from typing import List, Tuple, Optional


def mod_exp(base: int, exponent: int, modulus: int) -> int:
    """
    Compute (base^exponent) % modulus efficiently using binary exponentiation.
    
    This is way faster than pow() for huge numbers, though Python's built-in
    pow(base, exp, mod) actually does the same thing. I implemented it myself
    to understand the algorithm better.
    
    Args:
        base: The base number
        exponent: The power to raise to
        modulus: Take result modulo this
    
    Returns:
        (base^exponent) % modulus
    """
    if modulus == 1:
        return 0
    
    result = 1
    base = base % modulus
    
    # Process exponent bit by bit
    while exponent > 0:
        # If current bit is set, multiply base with result
        if exponent % 2 == 1:
            result = (result * base) % modulus
        
        # Square the base for next bit position
        exponent = exponent >> 1
        base = (base * base) % modulus
    
    return result


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """
    Extended Euclidean Algorithm - finds gcd and Bezout coefficients.
    
    Returns gcd(a,b) and integers x, y such that ax + by = gcd(a,b).
    This is crucial for computing modular inverses.
    
    Args:
        a: First integer
        b: Second integer
    
    Returns:
        Tuple of (gcd, x, y) where ax + by = gcd
    """
    if a == 0:
        return b, 0, 1
    
    gcd_val, x1, y1 = extended_gcd(b % a, a)
    
    # Update x and y using results of recursive call
    x = y1 - (b // a) * x1
    y = x1
    
    return gcd_val, x, y


def mod_inverse(a: int, m: int) -> Optional[int]:
    """
    Find modular multiplicative inverse of a modulo m.
    
    Returns x such that (a * x) % m == 1, or None if inverse doesn't exist.
    Inverse exists iff gcd(a, m) == 1.
    
    Args:
        a: Number to find inverse of
        m: Modulus
    
    Returns:
        Modular inverse, or None if it doesn't exist
    """
    g, x, _ = extended_gcd(a % m, m)
    
    if g != 1:
        # Inverse doesn't exist - a and m aren't coprime
        return None
    
    return (x % m + m) % m


def chinese_remainder_theorem(remainders: List[int], moduli: List[int]) -> Optional[int]:
    """
    Solve system of congruences using Chinese Remainder Theorem.
    
    Given: x ≡ r1 (mod m1), x ≡ r2 (mod m2), ...
    Find: x that satisfies all congruences
    
    This only works when all moduli are pairwise coprime. I check for that
    because getting wrong answers silently would be annoying.
    
    Args:
        remainders: List of remainders [r1, r2, ...]
        moduli: List of moduli [m1, m2, ...]
    
    Returns:
        Solution x, or None if no solution exists
    """
    if len(remainders) != len(moduli):
        return None
    
    # Check if moduli are pairwise coprime
    for i in range(len(moduli)):
        for j in range(i + 1, len(moduli)):
            if gcd(moduli[i], moduli[j]) != 1:
                return None
    
    # Product of all moduli
    M = 1
    for m in moduli:
        M *= m
    
    result = 0
    
    for i in range(len(moduli)):
        # M_i = M / moduli[i]
        Mi = M // moduli[i]
        
        # Find inverse of Mi modulo moduli[i]
        inv = mod_inverse(Mi, moduli[i])
        if inv is None:
            return None
        
        # Add contribution of this congruence
        result += remainders[i] * Mi * inv
    
    return result % M


def is_prime_fermat(n: int, k: int = 5) -> bool:
    """
    Probabilistic primality test using Fermat's Little Theorem.
    
    Not perfect (fails for Carmichael numbers) but good enough for most cases.
    Runs k rounds with different bases to reduce false positive rate.
    
    Args:
        n: Number to test
        k: Number of test rounds (higher = more accurate)
    
    Returns:
        True if probably prime, False if definitely composite
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    # Test with first k primes as bases
    test_bases = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29][:k]
    
    for a in test_bases:
        if a >= n:
            continue
        # Check if a^(n-1) ≡ 1 (mod n)
        if mod_exp(a, n - 1, n) != 1:
            return False
    
    return True


if __name__ == "__main__":
    print("=== Modular Arithmetic Toolkit Demo ===\n")
    
    # Demo 1: Fast modular exponentiation
    print("1. Modular Exponentiation:")
    base, exp, mod = 123456, 789012, 1000000007
    result = mod_exp(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}")
    print(f"   Verification with built-in pow: {pow(base, exp, mod)}\n")
    
    # Demo 2: Modular inverse
    print("2. Modular Inverse:")
    a, m = 7, 26
    inv = mod_inverse(a, m)
    if inv:
        print(f"   Inverse of {a} mod {m} = {inv}")
        print(f"   Check: {a} * {inv} mod {m} = {(a * inv) % m}\n")
    
    # Demo 3: Chinese Remainder Theorem
    print("3. Chinese Remainder Theorem:")
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    print(f"   System: x ≡ {remainders[0]} (mod {moduli[0]})")
    print(f"           x ≡ {remainders[1]} (mod {moduli[1]})")
    print(f"           x ≡ {remainders[2]} (mod {moduli[2]})")
    
    solution = chinese_remainder_theorem(remainders, moduli)
    if solution:
        print(f"   Solution: x = {solution}")
        print(f"   Verification: {solution} mod {moduli[0]} = {solution % moduli[0]}")
        print(f"                 {solution} mod {moduli[1]} = {solution % moduli[1]}")
        print(f"                 {solution} mod {moduli[2]} = {solution % moduli[2]}\n")
    
    # Demo 4: Primality testing
    print("4. Fermat Primality Test:")
    test_numbers = [17, 561, 1000000007]
    for num in test_numbers:
        is_prob_prime = is_prime_fermat(num, k=5)
        print(f"   {num}: {'probably prime' if is_prob_prime else 'composite'}")