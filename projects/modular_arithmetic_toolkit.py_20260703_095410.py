"""
Date: 2026-07-03
Created a collection of modular arithmetic utilities I keep needing for competitive programming and crypto experiments — includes fast modular exponentiation, extended GCD, and Chinese Remainder Theorem solver.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit

A collection of number theory utilities I find myself rewriting constantly.
Focuses on modular arithmetic operations that are useful for crypto, competitive
programming, and general number theory exploration.
"""


def gcd(a, b):
    """
    Compute the greatest common divisor using Euclid's algorithm.
    
    Classic recursive approach — clean and simple.
    """
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a, b):
    """
    Extended Euclidean algorithm.
    
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
    Raises ValueError if inverse doesn't exist (when gcd(a,m) != 1).
    """
    g, x, _ = extended_gcd(a, m)
    
    if g != 1:
        raise ValueError(f"Modular inverse doesn't exist: gcd({a}, {m}) = {g} != 1")
    
    # Make sure the result is positive
    return (x % m + m) % m


def fast_power(base, exp, mod):
    """
    Fast modular exponentiation using binary exponentiation.
    
    Computes (base^exp) % mod efficiently in O(log exp) time.
    This is way faster than pow(base, exp) % mod for large numbers
    (though Python's built-in pow(base, exp, mod) actually uses this too).
    """
    result = 1
    base = base % mod
    
    while exp > 0:
        # If exp is odd, multiply base with result
        if exp % 2 == 1:
            result = (result * base) % mod
        
        # Now exp must be even
        exp = exp >> 1  # Divide by 2
        base = (base * base) % mod
    
    return result


def chinese_remainder_theorem(remainders, moduli):
    """
    Solve system of congruences using Chinese Remainder Theorem.
    
    Given: x ≡ remainders[i] (mod moduli[i]) for all i
    Returns: x that satisfies all congruences
    
    The moduli should be pairwise coprime for a unique solution.
    This comes up surprisingly often in competitive programming.
    """
    if len(remainders) != len(moduli):
        raise ValueError("Number of remainders must match number of moduli")
    
    # Product of all moduli
    total_product = 1
    for mod in moduli:
        total_product *= mod
    
    result = 0
    
    for remainder, mod in zip(remainders, moduli):
        # Product of all moduli except current one
        partial_product = total_product // mod
        
        # Find modular inverse of partial_product mod mod
        inv = mod_inverse(partial_product, mod)
        
        # Add contribution from this congruence
        result += remainder * partial_product * inv
    
    return result % total_product


def is_prime_fermat(n, k=5):
    """
    Probabilistic primality test using Fermat's Little Theorem.
    
    Tests k random witnesses. Not perfect (fails for Carmichael numbers)
    but good enough for most purposes and way faster than trial division.
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    import random
    
    for _ in range(k):
        # Pick random witness in range [2, n-1]
        a = random.randint(2, n - 1)
        
        # Check if a^(n-1) ≡ 1 (mod n)
        if fast_power(a, n - 1, n) != 1:
            return False
    
    return True


def totient(n):
    """
    Euler's totient function φ(n).
    
    Counts integers from 1 to n that are coprime with n.
    Used everywhere in number theory and cryptography.
    """
    result = n
    p = 2
    
    # Check all potential prime factors
    while p * p <= n:
        if n % p == 0:
            # Remove factor p
            while n % p == 0:
                n //= p
            # Apply formula: φ(n) = n * (1 - 1/p) for each prime p
            result -= result // p
        p += 1
    
    # If n > 1, then it's a prime factor
    if n > 1:
        result -= result // n
    
    return result


if __name__ == "__main__":
    print("=== Modular Arithmetic Toolkit Demo ===\n")
    
    # Fast exponentiation
    print("1. Fast Modular Exponentiation")
    base, exp, mod = 3, 100, 7
    result = fast_power(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}")
    print(f"   (Verification: {pow(base, exp, mod)})\n")
    
    # Modular inverse
    print("2. Modular Multiplicative Inverse")
    a, m = 3, 11
    inv = mod_inverse(a, m)
    print(f"   Inverse of {a} mod {m} = {inv}")
    print(f"   Verification: ({a} * {inv}) mod {m} = {(a * inv) % m}\n")
    
    # Chinese Remainder Theorem
    print("3. Chinese Remainder Theorem")
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    x = chinese_remainder_theorem(remainders, moduli)
    print(f"   Solving system:")
    for r, m in zip(remainders, moduli):
        print(f"     x ≡ {r} (mod {m})")
    print(f"   Solution: x = {x}")
    print(f"   Verification: {x} mod 3={x%3}, mod 5={x%5}, mod 7={x%7}\n")
    
    # Euler's totient
    print("4. Euler's Totient Function")
    n = 36
    phi = totient(n)
    print(f"   φ({n}) = {phi}")
    print(f"   (Numbers from 1 to {n} that are coprime with {n})\n")
    
    # Primality testing
    print("5. Fermat Primality Test")
    test_numbers = [17, 221, 561, 104729]
    for num in test_numbers:
        is_prime = is_prime_fermat(num, k=10)
        print(f"   {num}: {'probably prime' if is_prime else 'composite'}")