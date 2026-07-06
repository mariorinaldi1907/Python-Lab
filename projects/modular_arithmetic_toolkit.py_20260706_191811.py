"""
Date: 2026-07-06
Built a collection of modular arithmetic functions I keep needing for competitive programming and crypto exercises — includes extended Euclidean algorithm and Chinese Remainder Theorem solver.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit

A collection of number theory functions I use frequently for competitive
programming problems and exploring cryptographic primitives. Focuses on
modular arithmetic operations that come up surprisingly often.
"""


def gcd(a, b):
    """
    Compute the greatest common divisor using Euclidean algorithm.
    
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
    Extended Euclidean algorithm — finds x, y such that ax + by = gcd(a, b).
    
    This is the workhorse behind modular inverses. I originally learned this
    from a cryptography course and it's become one of my favorite algorithms.
    
    Args:
        a: First integer
        b: Second integer
    
    Returns:
        Tuple (gcd, x, y) where gcd is GCD(a,b) and ax + by = gcd
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
    
    Returns x such that (a * x) % m == 1, or None if no inverse exists.
    An inverse exists if and only if gcd(a, m) == 1.
    
    Args:
        a: The number to invert
        m: The modulus
    
    Returns:
        The modular inverse, or None if it doesn't exist
    """
    gcd_val, x, _ = extended_gcd(a, m)
    
    if gcd_val != 1:
        return None  # No inverse exists
    
    return x % m


def fast_power(base, exp, mod):
    """
    Compute (base^exp) % mod efficiently using binary exponentiation.
    
    This is way faster than pow(base, exp) % mod for huge exponents because
    it's O(log exp) instead of O(exp). Essential for RSA and Diffie-Hellman.
    
    Args:
        base: The base number
        exp: The exponent (must be non-negative)
        mod: The modulus
    
    Returns:
        (base^exp) % mod
    """
    result = 1
    base = base % mod
    
    while exp > 0:
        # If exp is odd, multiply base with result
        if exp % 2 == 1:
            result = (result * base) % mod
        
        # Now exp is even, so we can square the base and halve the exponent
        exp = exp >> 1  # Equivalent to exp // 2
        base = (base * base) % mod
    
    return result


def chinese_remainder_theorem(remainders, moduli):
    """
    Solve a system of linear congruences using the Chinese Remainder Theorem.
    
    Given x ≡ r1 (mod m1), x ≡ r2 (mod m2), ..., find x.
    The moduli must be pairwise coprime for a unique solution to exist.
    
    I needed this for an Advent of Code problem involving bus schedules and
    it was super satisfying to implement from scratch.
    
    Args:
        remainders: List of remainders [r1, r2, ...]
        moduli: List of moduli [m1, m2, ...]
    
    Returns:
        The solution x, or None if the moduli aren't pairwise coprime
    """
    if len(remainders) != len(moduli):
        return None
    
    # Check that moduli are pairwise coprime
    for i in range(len(moduli)):
        for j in range(i + 1, len(moduli)):
            if gcd(moduli[i], moduli[j]) != 1:
                return None
    
    # Product of all moduli
    M = 1
    for m in moduli:
        M *= m
    
    x = 0
    for i in range(len(remainders)):
        Mi = M // moduli[i]
        # Find the modular inverse of Mi modulo moduli[i]
        yi = mod_inverse(Mi, moduli[i])
        if yi is None:
            return None
        x += remainders[i] * Mi * yi
    
    return x % M


def is_prime(n, k=5):
    """
    Miller-Rabin primality test — probabilistic but very accurate.
    
    This is faster than trial division for large numbers. With k=5 rounds,
    the probability of a false positive is astronomically low.
    
    Args:
        n: The number to test
        k: Number of test rounds (higher = more accurate)
    
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
    
    # Import random here since we only need it for this function
    import random
    
    # Witness loop
    for _ in range(k):
        a = random.randint(2, n - 2)
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
    
    # Demo 1: Fast exponentiation
    print("1. Fast Exponentiation")
    base, exp, mod = 2, 1000, 1000000007
    result = fast_power(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}\n")
    
    # Demo 2: Modular inverse
    print("2. Modular Inverse")
    a, m = 3, 11
    inv = mod_inverse(a, m)
    if inv:
        print(f"   Inverse of {a} mod {m} = {inv}")
        print(f"   Verification: ({a} * {inv}) mod {m} = {(a * inv) % m}\n")
    
    # Demo 3: Chinese Remainder Theorem
    print("3. Chinese Remainder Theorem")
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    solution = chinese_remainder_theorem(remainders, moduli)
    print(f"   Solving: x ≡ {remainders[0]} (mod {moduli[0]}), "
          f"x ≡ {remainders[1]} (mod {moduli[1]}), "
          f"x ≡ {remainders[2]} (mod {moduli[2]})")
    print(f"   Solution: x = {solution}")
    print(f"   Verification: {solution} mod {moduli[0]} = {solution % moduli[0]}, "
          f"{solution} mod {moduli[1]} = {solution % moduli[1]}, "
          f"{solution} mod {moduli[2]} = {solution % moduli[2]}\n")
    
    # Demo 4: Primality testing
    print("4. Miller-Rabin Primality Test")
    test_numbers = [97, 100, 1009, 1024, 104729]
    for n in test_numbers:
        result = is_prime(n)
        print(f"   {n} is {'probably prime' if result else 'composite'}")