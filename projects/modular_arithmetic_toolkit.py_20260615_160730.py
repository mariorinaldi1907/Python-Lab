"""
Date: 2026-06-15
Implemented modular exponentiation, multiplicative inverse, and Chinese Remainder Theorem solver because I kept needing these for crypto puzzles and Project Euler problems.
"""

"""
Modular Arithmetic Toolkit

A collection of utilities for modular arithmetic operations.
I got tired of rewriting these every time I hit a number theory problem,
so here's a proper toolkit with the core operations I always need.
"""


def mod_exp(base, exp, mod):
    """
    Fast modular exponentiation using square-and-multiply.
    
    Computes (base^exp) % mod efficiently in O(log exp) time.
    This is way faster than naive pow() for large exponents.
    
    Args:
        base: The base number
        exp: The exponent (must be non-negative)
        mod: The modulus
    
    Returns:
        (base^exp) % mod
    """
    if mod == 1:
        return 0
    
    result = 1
    base = base % mod
    
    # Square and multiply algorithm - classic binary exponentiation
    while exp > 0:
        # If exp is odd, multiply base with result
        if exp % 2 == 1:
            result = (result * base) % mod
        
        # Now exp must be even, square the base and halve exp
        exp = exp >> 1  # Bit shift is faster than // 2
        base = (base * base) % mod
    
    return result


def extended_gcd(a, b):
    """
    Extended Euclidean Algorithm.
    
    Finds gcd(a, b) and coefficients x, y such that ax + by = gcd(a, b).
    This is the foundation for finding modular inverses.
    
    Args:
        a, b: Two integers
    
    Returns:
        Tuple (gcd, x, y) where gcd is the GCD and x, y satisfy Bézout's identity
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
    Compute modular multiplicative inverse of a modulo m.
    
    Finds x such that (a * x) % m == 1.
    Only exists when gcd(a, m) == 1.
    
    Args:
        a: The number to invert
        m: The modulus
    
    Returns:
        The modular inverse, or None if it doesn't exist
    """
    gcd, x, _ = extended_gcd(a, m)
    
    if gcd != 1:
        # Inverse doesn't exist - a and m aren't coprime
        return None
    
    # Make sure result is positive
    return (x % m + m) % m


def chinese_remainder_theorem(remainders, moduli):
    """
    Solve system of congruences using Chinese Remainder Theorem.
    
    Given x ≡ r1 (mod m1), x ≡ r2 (mod m2), ..., finds x.
    Assumes all moduli are pairwise coprime (otherwise CRT doesn't apply cleanly).
    
    Args:
        remainders: List of remainder values [r1, r2, ...]
        moduli: List of modulus values [m1, m2, ...]
    
    Returns:
        The solution x modulo the product of all moduli
    """
    if len(remainders) != len(moduli):
        raise ValueError("Need same number of remainders and moduli")
    
    # Product of all moduli
    total_mod = 1
    for m in moduli:
        total_mod *= m
    
    result = 0
    
    for r, m in zip(remainders, moduli):
        # For each congruence, compute its contribution
        # M_i is the product of all moduli except m
        M_i = total_mod // m
        
        # Find the inverse of M_i modulo m
        inv = mod_inverse(M_i, m)
        if inv is None:
            raise ValueError(f"Moduli are not pairwise coprime (failed at {m})")
        
        # Add this congruence's contribution
        result += r * M_i * inv
    
    return result % total_mod


def is_prime_miller_rabin(n, k=5):
    """
    Miller-Rabin primality test (probabilistic).
    
    Tests if n is probably prime. With k rounds, the probability
    of a composite passing is at most 4^(-k).
    
    Args:
        n: Number to test
        k: Number of rounds (more = more accurate)
    
    Returns:
        True if n is probably prime, False if definitely composite
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    # Write n-1 as 2^r * d where d is odd
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    # Witness loop - test k times with different bases
    import random
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = mod_exp(a, d, n)
        
        if x == 1 or x == n - 1:
            continue
        
        # Square x repeatedly r-1 times
        for _ in range(r - 1):
            x = mod_exp(x, 2, n)
            if x == n - 1:
                break
        else:
            # If we never hit n-1, n is composite
            return False
    
    return True


if __name__ == "__main__":
    print("=== Modular Arithmetic Toolkit Demo ===\n")
    
    # Demo 1: Fast modular exponentiation
    print("1. Fast Modular Exponentiation")
    base, exp, mod = 3, 1000000, 1000000007
    result = mod_exp(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}")
    print()
    
    # Demo 2: Modular inverse
    print("2. Modular Multiplicative Inverse")
    a, m = 7, 26
    inv = mod_inverse(a, m)
    if inv:
        print(f"   Inverse of {a} mod {m} = {inv}")
        print(f"   Verification: ({a} * {inv}) mod {m} = {(a * inv) % m}")
    print()
    
    # Demo 3: Chinese Remainder Theorem
    print("3. Chinese Remainder Theorem")
    print("   Solving: x ≡ 2 (mod 3), x ≡ 3 (mod 5), x ≡ 2 (mod 7)")
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    x = chinese_remainder_theorem(remainders, moduli)
    print(f"   Solution: x = {x}")
    print(f"   Verification: {x} mod 3 = {x % 3}, {x} mod 5 = {x % 5}, {x} mod 7 = {x % 7}")
    print()
    
    # Demo 4: Primality testing
    print("4. Miller-Rabin Primality Test")
    test_numbers = [97, 100, 1000000007, 1000000009]
    for n in test_numbers:
        is_prime = is_prime_miller_rabin(n, k=10)
        print(f"   {n}: {'probably prime' if is_prime else 'composite'}")