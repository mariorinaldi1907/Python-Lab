"""
Date: 2026-08-21
Created a collection of modular arithmetic utilities I keep needing for Project Euler and advent of code problems, especially the Chinese Remainder Theorem solver.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit

A collection of number theory functions I find myself needing over and over.
Includes fast modular exponentiation, extended GCD, modular inverse, and
a Chinese Remainder Theorem solver that actually works.

Author: Mario
"""


def gcd(a, b):
    """
    Compute the greatest common divisor using Euclidean algorithm.
    
    Classic recursive approach — clean and simple.
    """
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a, b):
    """
    Extended Euclidean algorithm.
    
    Returns (gcd, x, y) such that a*x + b*y = gcd(a, b).
    This is the magic behind modular inverses.
    """
    if b == 0:
        return a, 1, 0
    
    gcd_val, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    
    return gcd_val, x, y


def mod_inverse(a, m):
    """
    Find the modular multiplicative inverse of a modulo m.
    
    Returns x where (a * x) % m == 1.
    Raises ValueError if inverse doesn't exist (when gcd(a,m) != 1).
    
    I used to implement this wrong all the time until I really
    understood the extended GCD connection.
    """
    g, x, _ = extended_gcd(a, m)
    
    if g != 1:
        raise ValueError(f"Modular inverse does not exist: gcd({a}, {m}) = {g}")
    
    # Make sure the result is positive
    return x % m


def fast_mod_exp(base, exp, mod):
    """
    Fast modular exponentiation using binary exponentiation.
    
    Computes (base^exp) % mod efficiently in O(log exp) time.
    This is way faster than doing pow(base, exp) % mod for large numbers.
    
    The trick: repeatedly square and multiply only when the bit is set.
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
    
    Args:
        remainders: list of remainder values
        moduli: list of moduli (must be pairwise coprime)
    
    Returns:
        The unique solution modulo the product of all moduli
    
    This implementation assumes moduli are pairwise coprime.
    I should probably add a check for that, but for my use cases
    it's always true.
    """
    if len(remainders) != len(moduli):
        raise ValueError("remainders and moduli must have the same length")
    
    # Product of all moduli
    total_mod = 1
    for m in moduli:
        total_mod *= m
    
    result = 0
    
    for remainder, modulus in zip(remainders, moduli):
        # M_i is the product of all moduli except the current one
        Mi = total_mod // modulus
        
        # Find the modular inverse of Mi with respect to modulus
        yi = mod_inverse(Mi, modulus)
        
        # Add this term to the result
        result += remainder * Mi * yi
    
    return result % total_mod


def is_prime_fermat(n, k=5):
    """
    Probabilistic primality test using Fermat's Little Theorem.
    
    Not as robust as Miller-Rabin, but simpler and good enough
    for most of my needs. Returns False if definitely composite,
    True if probably prime.
    
    Args:
        n: number to test
        k: number of iterations (higher = more accurate)
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    import random
    
    for _ in range(k):
        # Pick a random base between 2 and n-2
        a = random.randint(2, n - 2)
        
        # If a^(n-1) is not congruent to 1 mod n, then n is composite
        if fast_mod_exp(a, n - 1, n) != 1:
            return False
    
    return True


def totient(n):
    """
    Euler's totient function φ(n).
    
    Counts integers from 1 to n that are coprime with n.
    This is a simple O(n) implementation — there are faster ways
    using prime factorization, but this works fine for small n.
    """
    count = 0
    for i in range(1, n + 1):
        if gcd(i, n) == 1:
            count += 1
    return count


if __name__ == "__main__":
    print("=== Modular Arithmetic Toolkit Demo ===\n")
    
    # Demo 1: Fast modular exponentiation
    print("1. Fast Modular Exponentiation")
    base, exp, mod = 3, 1000000, 1000000007
    result = fast_mod_exp(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}\n")
    
    # Demo 2: Modular inverse
    print("2. Modular Multiplicative Inverse")
    a, m = 7, 26
    try:
        inv = mod_inverse(a, m)
        print(f"   Inverse of {a} mod {m} = {inv}")
        print(f"   Verification: ({a} * {inv}) mod {m} = {(a * inv) % m}\n")
    except ValueError as e:
        print(f"   Error: {e}\n")
    
    # Demo 3: Chinese Remainder Theorem
    print("3. Chinese Remainder Theorem")
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    solution = chinese_remainder_theorem(remainders, moduli)
    print(f"   System of congruences:")
    for r, m in zip(remainders, moduli):
        print(f"     x ≡ {r} (mod {m})")
    print(f"   Solution: x = {solution}")
    print(f"   Verification:")
    for r, m in zip(remainders, moduli):
        print(f"     {solution} mod {m} = {solution % m} (expected {r})")
    print()
    
    # Demo 4: Primality testing
    print("4. Fermat Primality Test")
    test_numbers = [17, 25, 97, 100, 561]  # 561 is a Carmichael number!
    for num in test_numbers:
        is_prob_prime = is_prime_fermat(num, k=10)
        print(f"   {num}: {'probably prime' if is_prob_prime else 'composite'}")
    print()
    
    # Demo 5: Euler's totient
    print("5. Euler's Totient Function")
    for n in [1, 9, 10, 12, 36]:
        phi = totient(n)
        print(f"   φ({n}) = {phi}")