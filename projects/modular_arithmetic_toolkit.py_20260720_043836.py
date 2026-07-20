"""
Date: 2026-07-20
Created a utility for modular arithmetic operations that I keep needing for competitive programming and cryptography experiments — includes all the essentials like fast power, inverse calculations, and CRT solving.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit

A collection of number theory functions for modular arithmetic operations.
I wrote this because I kept reimplementing these for Project Euler problems
and CTF crypto challenges. Now I have them all in one place.
"""


def gcd(a, b):
    """
    Calculate the greatest common divisor using Euclidean algorithm.
    
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
    Extended Euclidean algorithm to find coefficients for Bezout's identity.
    
    Returns x, y, gcd such that ax + by = gcd(a, b).
    This is super useful for finding modular inverses.
    
    Args:
        a: First integer
        b: Second integer
    
    Returns:
        Tuple (x, y, gcd) where ax + by = gcd
    """
    if b == 0:
        return 1, 0, a
    
    x1, y1, gcd_val = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    
    return x, y, gcd_val


def mod_inverse(a, m):
    """
    Find the modular multiplicative inverse of a modulo m.
    
    Returns x such that (a * x) % m == 1.
    Only exists when gcd(a, m) == 1.
    
    Args:
        a: Number to find inverse of
        m: Modulus
    
    Returns:
        The modular inverse, or None if it doesn't exist
    """
    x, _, g = extended_gcd(a, m)
    
    if g != 1:
        return None  # No inverse exists
    
    return x % m


def fast_power(base, exp, mod):
    """
    Fast modular exponentiation using binary exponentiation.
    
    Computes (base^exp) % mod efficiently in O(log exp) time.
    Way faster than doing pow(base, exp) % mod for huge exponents.
    
    Args:
        base: Base number
        exp: Exponent
        mod: Modulus
    
    Returns:
        (base^exp) % mod
    """
    result = 1
    base = base % mod
    
    while exp > 0:
        # If exp is odd, multiply base with result
        if exp % 2 == 1:
            result = (result * base) % mod
        
        # Now exp must be even
        exp = exp >> 1  # Divide exp by 2
        base = (base * base) % mod
    
    return result


def chinese_remainder_theorem(remainders, moduli):
    """
    Solve a system of congruences using the Chinese Remainder Theorem.
    
    Given x ≡ r1 (mod m1), x ≡ r2 (mod m2), ..., find x.
    Assumes all moduli are pairwise coprime (which they should be for CRT).
    
    Args:
        remainders: List of remainders [r1, r2, ...]
        moduli: List of moduli [m1, m2, ...]
    
    Returns:
        The solution x (smallest non-negative integer)
    """
    if len(remainders) != len(moduli):
        raise ValueError("Number of remainders must match number of moduli")
    
    # Calculate the product of all moduli
    total_mod = 1
    for m in moduli:
        total_mod *= m
    
    result = 0
    
    for r, m in zip(remainders, moduli):
        # M_i is the product of all moduli except m
        M_i = total_mod // m
        
        # Find the inverse of M_i modulo m
        inv = mod_inverse(M_i, m)
        
        if inv is None:
            raise ValueError(f"Moduli are not pairwise coprime")
        
        # Add this term to the result
        result += r * M_i * inv
    
    return result % total_mod


def is_prime_miller_rabin(n, k=5):
    """
    Miller-Rabin primality test - probabilistic but fast.
    
    I use this instead of trial division for big numbers.
    With k=5 rounds, the probability of error is less than (1/4)^5.
    
    Args:
        n: Number to test for primality
        k: Number of rounds (more rounds = more accurate)
    
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
        x = fast_power(a, d, n)
        
        if x == 1 or x == n - 1:
            continue
        
        for _ in range(r - 1):
            x = fast_power(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    
    return True


if __name__ == "__main__":
    print("=== Modular Arithmetic Toolkit Demo ===\n")
    
    # GCD and Extended GCD
    print("1. GCD and Extended GCD")
    a, b = 48, 18
    print(f"   gcd({a}, {b}) = {gcd(a, b)}")
    x, y, g = extended_gcd(a, b)
    print(f"   Extended GCD: {a}*{x} + {b}*{y} = {g}")
    print(f"   Verification: {a*x + b*y} = {g}\n")
    
    # Modular Inverse
    print("2. Modular Inverse")
    a, m = 7, 26
    inv = mod_inverse(a, m)
    print(f"   Inverse of {a} mod {m} = {inv}")
    if inv:
        print(f"   Verification: ({a} * {inv}) mod {m} = {(a * inv) % m}\n")
    
    # Fast Exponentiation
    print("3. Fast Modular Exponentiation")
    base, exp, mod = 2, 1000, 999
    result = fast_power(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}\n")
    
    # Chinese Remainder Theorem
    print("4. Chinese Remainder Theorem")
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    x = chinese_remainder_theorem(remainders, moduli)
    print(f"   Solving: x ≡ {remainders[0]} (mod {moduli[0]})")
    for r, m in zip(remainders[1:], moduli[1:]):
        print(f"            x ≡ {r} (mod {m})")
    print(f"   Solution: x = {x}")
    print(f"   Verification: {x} mod {moduli[0]} = {x % moduli[0]}, "
          f"{x} mod {moduli[1]} = {x % moduli[1]}, "
          f"{x} mod {moduli[2]} = {x % moduli[2]}\n")
    
    # Miller-Rabin Primality Test
    print("5. Miller-Rabin Primality Test")
    test_numbers = [97, 100, 1009, 1000]
    for n in test_numbers:
        is_prime = is_prime_miller_rabin(n)
        print(f"   {n} is {'probably prime' if is_prime else 'composite'}")