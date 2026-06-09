"""
Date: 2026-06-09
Created a number theory utility focused on modular arithmetic operations that I kept needing for Project Euler and AoC problems.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit

A collection of functions for working with modular arithmetic, which I find
myself needing constantly for competitive programming and cryptography problems.
Includes fast modular exponentiation, extended Euclidean algorithm, Chinese
Remainder Theorem solver, and more.
"""


def gcd(a, b):
    """
    Compute the greatest common divisor using Euclidean algorithm.
    
    Classic recursive approach — clean and straightforward.
    """
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a, b):
    """
    Extended Euclidean Algorithm.
    
    Returns (gcd, x, y) such that a*x + b*y = gcd(a, b).
    This is crucial for finding modular inverses.
    """
    if b == 0:
        return a, 1, 0
    
    gcd_val, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    
    return gcd_val, x, y


def mod_inverse(a, m):
    """
    Find modular multiplicative inverse of a modulo m.
    
    Returns x such that (a * x) % m == 1.
    Raises ValueError if inverse doesn't exist (when gcd(a, m) != 1).
    """
    g, x, _ = extended_gcd(a, m)
    
    if g != 1:
        raise ValueError(f"Modular inverse does not exist for {a} mod {m}")
    
    # Make sure the result is positive
    return x % m


def fast_mod_exp(base, exp, mod):
    """
    Fast modular exponentiation using binary exponentiation.
    
    Computes (base^exp) % mod efficiently in O(log exp) time.
    This is way faster than doing pow(base, exp) % mod for large numbers.
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
    Solve system of congruences using Chinese Remainder Theorem.
    
    Given x ≡ remainders[i] (mod moduli[i]) for all i,
    find the smallest positive x that satisfies all congruences.
    
    The moduli must be pairwise coprime for a unique solution to exist.
    """
    if len(remainders) != len(moduli):
        raise ValueError("remainders and moduli must have same length")
    
    # Check that moduli are pairwise coprime
    for i in range(len(moduli)):
        for j in range(i + 1, len(moduli)):
            if gcd(moduli[i], moduli[j]) != 1:
                raise ValueError(f"Moduli {moduli[i]} and {moduli[j]} are not coprime")
    
    # Product of all moduli
    M = 1
    for m in moduli:
        M *= m
    
    result = 0
    
    for i in range(len(remainders)):
        # M_i is the product of all moduli except moduli[i]
        M_i = M // moduli[i]
        
        # Find the modular inverse of M_i mod moduli[i]
        inv = mod_inverse(M_i, moduli[i])
        
        # Add contribution of this congruence
        result += remainders[i] * M_i * inv
    
    return result % M


def is_prime_fermat(n, k=5):
    """
    Probabilistic primality test using Fermat's Little Theorem.
    
    Tests if n is prime with k rounds. Not deterministic but good enough
    for most cases. Returns False if definitely composite, True if probably prime.
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    import random
    
    for _ in range(k):
        a = random.randint(2, n - 1)
        # By Fermat's Little Theorem, if n is prime: a^(n-1) ≡ 1 (mod n)
        if fast_mod_exp(a, n - 1, n) != 1:
            return False
    
    return True


def mod_factorial(n, p):
    """
    Compute n! mod p efficiently.
    
    Useful when you need factorial in modular arithmetic.
    Only practical for relatively small n since it's still O(n).
    """
    result = 1
    for i in range(1, n + 1):
        result = (result * i) % p
    return result


if __name__ == "__main__":
    print("=== Modular Arithmetic Toolkit Demo ===\n")
    
    # Demo 1: Fast modular exponentiation
    print("1. Fast Modular Exponentiation")
    base, exp, mod = 2, 100, 1000000007
    result = fast_mod_exp(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}")
    print()
    
    # Demo 2: Modular inverse
    print("2. Modular Inverse")
    a, m = 3, 11
    inv = mod_inverse(a, m)
    print(f"   Inverse of {a} mod {m} = {inv}")
    print(f"   Verification: ({a} * {inv}) mod {m} = {(a * inv) % m}")
    print()
    
    # Demo 3: Chinese Remainder Theorem
    print("3. Chinese Remainder Theorem")
    print("   Solving system:")
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    for r, m in zip(remainders, moduli):
        print(f"   x ≡ {r} (mod {m})")
    
    x = chinese_remainder_theorem(remainders, moduli)
    print(f"   Solution: x = {x}")
    print(f"   Verification:")
    for r, m in zip(remainders, moduli):
        print(f"     {x} mod {m} = {x % m} (expected {r})")
    print()
    
    # Demo 4: Primality testing
    print("4. Fermat Primality Test")
    test_numbers = [17, 18, 97, 100, 1009]
    for num in test_numbers:
        is_prob_prime = is_prime_fermat(num, k=10)
        print(f"   {num}: {'probably prime' if is_prob_prime else 'composite'}")
    print()
    
    # Demo 5: GCD and Extended GCD
    print("5. GCD and Extended Euclidean Algorithm")
    a, b = 48, 18
    g = gcd(a, b)
    g_ext, x, y = extended_gcd(a, b)
    print(f"   gcd({a}, {b}) = {g}")
    print(f"   Extended: {a}*({x}) + {b}*({y}) = {g_ext}")
    print(f"   Verification: {a*x + b*y} = {g_ext}")