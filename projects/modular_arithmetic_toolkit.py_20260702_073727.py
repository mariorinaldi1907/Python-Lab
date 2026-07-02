"""
Date: 2026-07-02
Created a collection of modular arithmetic functions I keep reusing in number theory problems, especially for working with RSA and discrete logarithms.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit
A collection of number theory utilities I keep needing for various projects.
Focuses on modular arithmetic operations that come up in cryptography and competitive programming.
"""

import math
from typing import Tuple, Optional


def mod_exp(base: int, exp: int, mod: int) -> int:
    """
    Fast modular exponentiation using binary exponentiation.
    Computes (base^exp) % mod efficiently in O(log exp) time.
    
    This is way faster than doing pow(base, exp) % mod for large numbers
    because we keep the intermediate results small by taking mod at each step.
    """
    if mod == 1:
        return 0
    
    result = 1
    base = base % mod
    
    while exp > 0:
        # If exp is odd, multiply base with result
        if exp % 2 == 1:
            result = (result * base) % mod
        
        # Now exp must be even, so we can divide it by 2
        exp = exp >> 1  # Bit shift is faster than division
        base = (base * base) % mod
    
    return result


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """
    Extended Euclidean Algorithm.
    Returns (gcd, x, y) such that a*x + b*y = gcd(a, b).
    
    This is the foundation for finding modular inverses.
    The regular gcd just gives you the greatest common divisor,
    but this version also gives you the Bézout coefficients.
    """
    if a == 0:
        return b, 0, 1
    
    gcd, x1, y1 = extended_gcd(b % a, a)
    
    # Update x and y using results of recursive call
    x = y1 - (b // a) * x1
    y = x1
    
    return gcd, x, y


def mod_inverse(a: int, m: int) -> Optional[int]:
    """
    Find the modular multiplicative inverse of a modulo m.
    Returns x such that (a * x) % m == 1, or None if no inverse exists.
    
    An inverse only exists if gcd(a, m) = 1 (they're coprime).
    This is super useful for modular division in number theory problems.
    """
    gcd, x, _ = extended_gcd(a, m)
    
    if gcd != 1:
        # No modular inverse exists
        return None
    
    # Make sure the result is positive
    return (x % m + m) % m


def chinese_remainder_theorem(remainders: list, moduli: list) -> Optional[int]:
    """
    Solves system of congruences using the Chinese Remainder Theorem.
    Given x ≡ r1 (mod m1), x ≡ r2 (mod m2), ..., finds x.
    
    This only works when all moduli are pairwise coprime.
    I used this for solving some Advent of Code problems where you had
    to find a number satisfying multiple modular conditions.
    """
    if len(remainders) != len(moduli):
        return None
    
    # Check if all moduli are pairwise coprime
    for i in range(len(moduli)):
        for j in range(i + 1, len(moduli)):
            if math.gcd(moduli[i], moduli[j]) != 1:
                return None  # Not pairwise coprime
    
    total = 0
    prod = math.prod(moduli)
    
    for remainder, modulus in zip(remainders, moduli):
        p = prod // modulus
        inv = mod_inverse(p, modulus)
        if inv is None:
            return None
        total += remainder * p * inv
    
    return total % prod


def is_prime_miller_rabin(n: int, k: int = 5) -> bool:
    """
    Miller-Rabin primality test (probabilistic).
    Tests if n is probably prime with k rounds of testing.
    
    For k=5, the probability of a composite passing is less than (1/4)^5.
    I prefer this over trial division for large numbers because it's much faster.
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


def euler_totient(n: int) -> int:
    """
    Compute Euler's totient function φ(n).
    Returns the count of integers from 1 to n that are coprime with n.
    
    This is crucial for RSA encryption where φ(n) determines the private key.
    """
    result = n
    p = 2
    
    # Check all potential prime factors
    while p * p <= n:
        if n % p == 0:
            # Remove all occurrences of this prime
            while n % p == 0:
                n //= p
            # Apply the formula: φ(n) = n * (1 - 1/p) for each prime p
            result -= result // p
        p += 1
    
    # If n is still greater than 1, then it's a prime factor
    if n > 1:
        result -= result // n
    
    return result


if __name__ == "__main__":
    print("=== Modular Arithmetic Toolkit Demo ===\n")
    
    # Demo 1: Fast modular exponentiation
    print("1. Fast Modular Exponentiation")
    base, exp, mod = 3, 100000, 1000000007
    result = mod_exp(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}\n")
    
    # Demo 2: Modular inverse
    print("2. Modular Inverse")
    a, m = 17, 43
    inv = mod_inverse(a, m)
    print(f"   Inverse of {a} mod {m} = {inv}")
    print(f"   Verification: ({a} * {inv}) mod {m} = {(a * inv) % m}\n")
    
    # Demo 3: Chinese Remainder Theorem
    print("3. Chinese Remainder Theorem")
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    x = chinese_remainder_theorem(remainders, moduli)
    print(f"   System: x ≡ {remainders[0]} (mod {moduli[0]}), x ≡ {remainders[1]} (mod {moduli[1]}), x ≡ {remainders[2]} (mod {moduli[2]})")
    print(f"   Solution: x = {x}")
    print(f"   Verification: {x} mod {moduli[0]} = {x % moduli[0]}, {x} mod {moduli[1]} = {x % moduli[1]}, {x} mod {moduli[2]} = {x % moduli[2]}\n")
    
    # Demo 4: Miller-Rabin primality test
    print("4. Miller-Rabin Primality Test")
    test_numbers = [17, 221, 1000000007, 1000000009]
    for num in test_numbers:
        is_prime = is_prime_miller_rabin(num)
        print(f"   {num}: {'probably prime' if is_prime else 'composite'}")
    print()
    
    # Demo 5: Euler's totient function
    print("5. Euler's Totient Function")
    for n in [1, 9, 10, 36, 100]:
        phi = euler_totient(n)
        print(f"   φ({n}) = {phi}")