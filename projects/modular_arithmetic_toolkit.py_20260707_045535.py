"""
Date: 2026-07-07
Created a collection of modular arithmetic utilities including fast modular exponentiation, extended Euclidean algorithm, and Chinese Remainder Theorem solver because I kept rewriting these for competitive programming.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit

A collection of number theory utilities I use frequently for competitive
programming and math problems. Implements fast modular exponentiation,
extended GCD, modular inverse, and Chinese Remainder Theorem.

Author: Mario
"""


def mod_exp(base, exp, mod):
    """
    Fast modular exponentiation using binary exponentiation.
    
    Computes (base^exp) % mod efficiently in O(log exp) time.
    This is way faster than doing pow(base, exp) % mod for large numbers.
    
    Args:
        base: The base number
        exp: The exponent (must be non-negative)
        mod: The modulus
    
    Returns:
        Result of (base^exp) % mod
    """
    if mod == 1:
        return 0
    
    result = 1
    base = base % mod
    
    while exp > 0:
        # If exp is odd, multiply base with result
        if exp % 2 == 1:
            result = (result * base) % mod
        
        # Now exp must be even, so we can square the base
        exp = exp >> 1  # Divide by 2
        base = (base * base) % mod
    
    return result


def extended_gcd(a, b):
    """
    Extended Euclidean Algorithm.
    
    Finds integers x and y such that a*x + b*y = gcd(a, b).
    This is crucial for finding modular inverses.
    
    Args:
        a: First integer
        b: Second integer
    
    Returns:
        Tuple (gcd, x, y) where gcd is the GCD of a and b,
        and x, y satisfy a*x + b*y = gcd
    """
    if a == 0:
        return b, 0, 1
    
    gcd, x1, y1 = extended_gcd(b % a, a)
    
    # Update x and y using results of recursive call
    x = y1 - (b // a) * x1
    y = x1
    
    return gcd, x, y


def mod_inverse(a, m):
    """
    Computes the modular multiplicative inverse of a modulo m.
    
    Returns x such that (a * x) % m == 1.
    Only exists when gcd(a, m) = 1.
    
    Args:
        a: The number to find the inverse of
        m: The modulus
    
    Returns:
        The modular inverse of a mod m
    
    Raises:
        ValueError: If the modular inverse doesn't exist
    """
    gcd, x, _ = extended_gcd(a, m)
    
    if gcd != 1:
        raise ValueError(f"Modular inverse doesn't exist: gcd({a}, {m}) = {gcd}")
    
    # Make sure the result is positive
    return (x % m + m) % m


def chinese_remainder_theorem(remainders, moduli):
    """
    Solves a system of congruences using the Chinese Remainder Theorem.
    
    Given x ≡ r1 (mod m1), x ≡ r2 (mod m2), ..., x ≡ rn (mod mn),
    finds the unique solution modulo M = m1 * m2 * ... * mn.
    
    I use this a lot in advent of code and similar problems where you need
    to find cycles that align across different periods.
    
    Args:
        remainders: List of remainders [r1, r2, ..., rn]
        moduli: List of moduli [m1, m2, ..., mn] (must be pairwise coprime)
    
    Returns:
        The unique solution x modulo the product of all moduli
    
    Raises:
        ValueError: If moduli are not pairwise coprime
    """
    if len(remainders) != len(moduli):
        raise ValueError("Number of remainders must match number of moduli")
    
    # Calculate the product of all moduli
    total_mod = 1
    for m in moduli:
        total_mod *= m
    
    result = 0
    
    for remainder, modulus in zip(remainders, moduli):
        # M_i is the product of all moduli except the current one
        Mi = total_mod // modulus
        
        # Find the modular inverse of M_i modulo the current modulus
        # This will raise an error if they're not coprime
        yi = mod_inverse(Mi, modulus)
        
        # Add this term to the result
        result += remainder * Mi * yi
    
    return result % total_mod


def is_prime_miller_rabin(n, k=5):
    """
    Miller-Rabin primality test - probabilistic but very accurate.
    
    Tests whether n is probably prime. The probability of a composite
    number passing k rounds is at most 4^(-k), so k=5 gives us
    pretty much certainty for practical purposes.
    
    Args:
        n: Number to test for primality
        k: Number of rounds (higher = more accurate but slower)
    
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


if __name__ == "__main__":
    print("=== Modular Arithmetic Toolkit Demo ===\n")
    
    # Demo 1: Fast modular exponentiation
    print("1. Fast Modular Exponentiation")
    base, exp, mod = 2, 1000, 1000000007
    result = mod_exp(base, exp, mod)
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
    print("   Solving the system:")
    remainders = [2, 3, 1]
    moduli = [3, 4, 5]
    for r, m in zip(remainders, moduli):
        print(f"   x ≡ {r} (mod {m})")
    
    solution = chinese_remainder_theorem(remainders, moduli)
    print(f"   Solution: x = {solution} (mod {3 * 4 * 5})")
    
    # Verify the solution
    print("   Verification:")
    for r, m in zip(remainders, moduli):
        print(f"   {solution} mod {m} = {solution % m} (expected {r})")
    print()
    
    # Demo 4: Miller-Rabin primality testing
    print("4. Miller-Rabin Primality Test")
    test_numbers = [17, 221, 561, 1000000007]
    for num in test_numbers:
        is_prime = is_prime_miller_rabin(num)
        print(f"   {num}: {'probably prime' if is_prime else 'composite'}")