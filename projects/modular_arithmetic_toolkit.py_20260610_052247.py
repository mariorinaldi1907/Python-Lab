"""
Date: 2026-06-10
Created a collection of modular arithmetic functions including fast exponentiation, modular inverse, and Chinese Remainder Theorem solver for number theory problems.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit
A collection of functions for modular arithmetic and number theory operations.
Useful for cryptography, competitive programming, and general math problems.
"""

from math import gcd
from typing import List, Tuple, Optional


def mod_exp(base: int, exponent: int, modulus: int) -> int:
    """
    Fast modular exponentiation using binary exponentiation.
    Computes (base^exponent) % modulus efficiently.
    
    This is way faster than doing pow(base, exponent) % modulus for large numbers
    because it keeps intermediate results small by taking mod at each step.
    """
    if modulus == 1:
        return 0
    
    result = 1
    base = base % modulus
    
    while exponent > 0:
        # If exponent is odd, multiply base with result
        if exponent % 2 == 1:
            result = (result * base) % modulus
        
        # Now exponent must be even, so we can divide it by 2
        exponent = exponent >> 1  # bit shift is faster than division
        base = (base * base) % modulus
    
    return result


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """
    Extended Euclidean Algorithm.
    Returns (gcd, x, y) such that a*x + b*y = gcd(a, b).
    
    This is the foundation for computing modular inverses.
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
    Computes modular multiplicative inverse of a modulo m.
    Returns x such that (a * x) % m == 1.
    
    Returns None if the inverse doesn't exist (when gcd(a, m) != 1).
    """
    g, x, _ = extended_gcd(a % m, m)
    
    if g != 1:
        # Modular inverse doesn't exist
        return None
    
    # Make sure the result is positive
    return (x % m + m) % m


def chinese_remainder_theorem(remainders: List[int], moduli: List[int]) -> Optional[int]:
    """
    Solves a system of congruences using the Chinese Remainder Theorem.
    
    Given: x ≡ r1 (mod m1), x ≡ r2 (mod m2), ..., x ≡ rn (mod mn)
    Returns: x (the smallest positive solution)
    
    This only works when all moduli are pairwise coprime.
    I use this for solving problems where you need to find a number
    that has specific remainders when divided by different moduli.
    """
    if len(remainders) != len(moduli):
        return None
    
    # Check that all moduli are pairwise coprime
    for i in range(len(moduli)):
        for j in range(i + 1, len(moduli)):
            if gcd(moduli[i], moduli[j]) != 1:
                return None  # CRT doesn't apply
    
    # Calculate the product of all moduli
    total_mod = 1
    for m in moduli:
        total_mod *= m
    
    result = 0
    
    for i in range(len(moduli)):
        # M_i is the product of all moduli except moduli[i]
        M_i = total_mod // moduli[i]
        
        # Find the modular inverse of M_i mod moduli[i]
        inv = mod_inverse(M_i, moduli[i])
        if inv is None:
            return None
        
        # Add this term to the result
        result += remainders[i] * M_i * inv
    
    # Return the smallest positive solution
    return result % total_mod


def is_prime_fermat(n: int, k: int = 5) -> bool:
    """
    Probabilistic primality test using Fermat's Little Theorem.
    
    Tests if n is prime by checking if a^(n-1) ≡ 1 (mod n) for k random bases.
    Not perfect (Carmichael numbers can fool it), but fast and good enough
    for most use cases. For serious crypto, use Miller-Rabin instead.
    """
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False
    
    # Test with the first k primes as witnesses
    test_bases = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    
    for a in test_bases[:min(k, len(test_bases))]:
        if a >= n:
            continue
        if mod_exp(a, n - 1, n) != 1:
            return False
    
    return True


def totient(n: int) -> int:
    """
    Euler's totient function φ(n).
    Returns the count of numbers from 1 to n that are coprime with n.
    
    I'm using the formula based on prime factorization:
    φ(n) = n * ∏(1 - 1/p) for all prime factors p of n
    """
    result = n
    p = 2
    
    # Find all prime factors
    while p * p <= n:
        if n % p == 0:
            # Remove all occurrences of this prime factor
            while n % p == 0:
                n //= p
            # Apply the formula: result *= (1 - 1/p) = (p - 1)/p
            result -= result // p
        p += 1
    
    # If n is still greater than 1, then it's a prime factor
    if n > 1:
        result -= result // n
    
    return result


if __name__ == "__main__":
    print("=== Modular Arithmetic Toolkit Demo ===\n")
    
    # Fast modular exponentiation
    print("1. Fast Modular Exponentiation")
    base, exp, mod = 3, 100000, 1000000007
    result = mod_exp(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}\n")
    
    # Modular inverse
    print("2. Modular Inverse")
    a, m = 7, 26
    inv = mod_inverse(a, m)
    if inv:
        print(f"   Inverse of {a} mod {m} = {inv}")
        print(f"   Verification: ({a} * {inv}) mod {m} = {(a * inv) % m}\n")
    
    # Chinese Remainder Theorem
    print("3. Chinese Remainder Theorem")
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    print(f"   Solving system:")
    for r, m in zip(remainders, moduli):
        print(f"   x ≡ {r} (mod {m})")
    solution = chinese_remainder_theorem(remainders, moduli)
    print(f"   Solution: x = {solution}")
    print(f"   Verification: {solution} mod {moduli[0]} = {solution % moduli[0]}, "
          f"{solution} mod {moduli[1]} = {solution % moduli[1]}, "
          f"{solution} mod {moduli[2]} = {solution % moduli[2]}\n")
    
    # Primality testing
    print("4. Primality Testing (Fermat)")
    test_numbers = [17, 101, 561, 1000000007]
    for num in test_numbers:
        is_p = is_prime_fermat(num)
        print(f"   {num}: {'probably prime' if is_p else 'composite'}")
    print()
    
    # Euler's totient
    print("5. Euler's Totient Function")
    test_ns = [9, 10, 36, 100]
    for n in test_ns:
        phi = totient(n)
        print(f"   φ({n}) = {phi} (numbers from 1 to {n} that are coprime with {n})")