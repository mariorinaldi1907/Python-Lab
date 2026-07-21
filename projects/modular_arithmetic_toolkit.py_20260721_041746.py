"""
Date: 2026-07-21
Created a modular arithmetic utility that handles fast modular exponentiation, multiplicative inverses, and solves systems using the Chinese Remainder Theorem — been wanting this for Project Euler problems.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit

A collection of number theory utilities I keep needing for competitive programming
and Project Euler. Focuses on modular arithmetic operations that need to be efficient.
"""


def mod_exp(base, exp, mod):
    """
    Fast modular exponentiation using binary exponentiation.
    
    Computes (base^exp) % mod efficiently in O(log exp) time.
    This is way faster than doing pow(base, exp) % mod for large numbers
    because we keep intermediate results small.
    
    Args:
        base: The base number
        exp: The exponent (non-negative)
        mod: The modulus
        
    Returns:
        (base^exp) % mod
    """
    if mod == 1:
        return 0
    
    result = 1
    base = base % mod
    
    while exp > 0:
        # If exp is odd, multiply base with result
        if exp % 2 == 1:
            result = (result * base) % mod
        
        # Now exp must be even, so we can halve it
        exp = exp >> 1  # Bit shift is faster than exp // 2
        base = (base * base) % mod
    
    return result


def gcd(a, b):
    """
    Euclidean algorithm for greatest common divisor.
    
    Classic recursive implementation. Could use math.gcd but I like
    having it here for completeness.
    """
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a, b):
    """
    Extended Euclidean algorithm.
    
    Finds integers x, y such that ax + by = gcd(a, b).
    This is crucial for finding modular inverses.
    
    Returns:
        Tuple (gcd, x, y) where ax + by = gcd
    """
    if a == 0:
        return b, 0, 1
    
    gcd_val, x1, y1 = extended_gcd(b % a, a)
    
    # Update x and y using results of recursive call
    x = y1 - (b // a) * x1
    y = x1
    
    return gcd_val, x, y


def mod_inverse(a, m):
    """
    Find modular multiplicative inverse of a under modulo m.
    
    Returns x such that (a * x) % m == 1.
    Only exists if gcd(a, m) == 1.
    
    Args:
        a: Number to find inverse of
        m: Modulus
        
    Returns:
        Modular inverse of a mod m
        
    Raises:
        ValueError: If inverse doesn't exist
    """
    gcd_val, x, _ = extended_gcd(a, m)
    
    if gcd_val != 1:
        raise ValueError(f"Modular inverse doesn't exist: gcd({a}, {m}) = {gcd_val}")
    
    # x might be negative, so we make sure it's in range [0, m)
    return (x % m + m) % m


def chinese_remainder_theorem(remainders, moduli):
    """
    Solve system of congruences using Chinese Remainder Theorem.
    
    Given: x ≡ r1 (mod m1), x ≡ r2 (mod m2), ..., x ≡ rn (mod mn)
    Find: x
    
    All moduli must be pairwise coprime for unique solution to exist.
    
    Args:
        remainders: List of remainders [r1, r2, ..., rn]
        moduli: List of moduli [m1, m2, ..., mn]
        
    Returns:
        The smallest non-negative solution x
    """
    if len(remainders) != len(moduli):
        raise ValueError("remainders and moduli must have same length")
    
    # Check pairwise coprimality (not the most efficient but clear)
    for i in range(len(moduli)):
        for j in range(i + 1, len(moduli)):
            if gcd(moduli[i], moduli[j]) != 1:
                raise ValueError(f"Moduli must be pairwise coprime: gcd({moduli[i]}, {moduli[j]}) != 1")
    
    # Product of all moduli
    total_mod = 1
    for m in moduli:
        total_mod *= m
    
    result = 0
    
    for r, m in zip(remainders, moduli):
        # For each congruence, compute contribution to final result
        # M_i is the product of all moduli except m
        M_i = total_mod // m
        
        # Find inverse of M_i mod m
        inv = mod_inverse(M_i, m)
        
        # Add this term's contribution
        result += r * M_i * inv
    
    return result % total_mod


def is_prime_fermat(n, k=5):
    """
    Probabilistic primality test using Fermat's Little Theorem.
    
    Not perfect (fails for Carmichael numbers) but fast and good enough
    for most purposes. For deterministic test, use Miller-Rabin.
    
    Args:
        n: Number to test
        k: Number of iterations (higher = more confident)
        
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
    
    # Test k random witnesses
    for _ in range(k):
        a = random.randint(2, n - 2)
        # If a^(n-1) ≢ 1 (mod n), then n is composite
        if mod_exp(a, n - 1, n) != 1:
            return False
    
    return True


if __name__ == "__main__":
    print("=== Modular Arithmetic Toolkit Demo ===\n")
    
    # Demo 1: Fast modular exponentiation
    print("1. Fast Modular Exponentiation")
    base, exp, mod = 2, 1000, 10**9 + 7
    result = mod_exp(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}")
    print()
    
    # Demo 2: Modular inverse
    print("2. Modular Multiplicative Inverse")
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
        print(f"     x ≡ {r} (mod {m})")
    
    x = chinese_remainder_theorem(remainders, moduli)
    print(f"   Solution: x = {x}")
    print(f"   Verification:")
    for r, m in zip(remainders, moduli):
        print(f"     {x} mod {m} = {x % m} (should be {r})")
    print()
    
    # Demo 4: Primality testing
    print("4. Fermat Primality Test")
    test_numbers = [17, 221, 561, 1009]
    for n in test_numbers:
        is_prob_prime = is_prime_fermat(n, k=10)
        print(f"   {n}: {'probably prime' if is_prob_prime else 'composite'}")