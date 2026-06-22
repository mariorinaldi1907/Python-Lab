"""
Date: 2026-06-22
Created a number theory utility for competitive programming practice — includes modular exponentiation, inverse, and Chinese Remainder Theorem solver.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit
A collection of number theory functions I keep using in competitive programming.
Covers modular exponentiation, inverses, and the Chinese Remainder Theorem.
"""


def mod_exp(base, exp, mod):
    """
    Fast modular exponentiation using binary exponentiation.
    
    Computes (base^exp) % mod efficiently in O(log exp) time.
    This is way faster than doing pow(base, exp) % mod for large numbers
    because we keep intermediate results small.
    
    Args:
        base: The base number
        exp: The exponent (non-negative integer)
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
        
        # Now exp must be even, so we can divide it by 2
        exp = exp >> 1  # Right shift is faster than division
        base = (base * base) % mod
    
    return result


def gcd_extended(a, b):
    """
    Extended Euclidean Algorithm.
    
    Finds gcd(a, b) and coefficients x, y such that ax + by = gcd(a, b).
    This is crucial for finding modular inverses.
    
    Args:
        a, b: Two integers
    
    Returns:
        Tuple (gcd, x, y) where ax + by = gcd
    """
    if a == 0:
        return b, 0, 1
    
    gcd, x1, y1 = gcd_extended(b % a, a)
    
    # Update x and y using results of recursive call
    x = y1 - (b // a) * x1
    y = x1
    
    return gcd, x, y


def mod_inverse(a, mod):
    """
    Find the modular multiplicative inverse of a modulo mod.
    
    Returns x such that (a * x) % mod == 1.
    Only exists when gcd(a, mod) == 1.
    
    Args:
        a: The number to invert
        mod: The modulus
    
    Returns:
        The modular inverse, or None if it doesn't exist
    """
    gcd, x, _ = gcd_extended(a, mod)
    
    if gcd != 1:
        # Modular inverse doesn't exist
        return None
    
    # Make sure the result is positive
    return (x % mod + mod) % mod


def chinese_remainder_theorem(remainders, moduli):
    """
    Solve a system of congruences using the Chinese Remainder Theorem.
    
    Given: x ≡ r1 (mod m1), x ≡ r2 (mod m2), ..., x ≡ rn (mod mn)
    Find: The unique solution x modulo M = m1 * m2 * ... * mn
    
    This assumes all moduli are pairwise coprime (which I should probably check
    but skipping for now since I usually know my inputs).
    
    Args:
        remainders: List of remainders [r1, r2, ..., rn]
        moduli: List of moduli [m1, m2, ..., mn]
    
    Returns:
        The solution x, or None if no solution exists
    """
    if len(remainders) != len(moduli):
        return None
    
    # Calculate the product of all moduli
    M = 1
    for m in moduli:
        M *= m
    
    x = 0
    
    for ri, mi in zip(remainders, moduli):
        # Mi is the product of all moduli except mi
        Mi = M // mi
        
        # Find the modular inverse of Mi modulo mi
        yi = mod_inverse(Mi, mi)
        
        if yi is None:
            # Moduli aren't coprime, CRT doesn't apply
            return None
        
        # Add this term to the solution
        x += ri * Mi * yi
    
    # Return the smallest positive solution
    return x % M


def is_prime_mr(n, k=5):
    """
    Miller-Rabin primality test.
    
    Probabilistic primality test that's much faster than trial division
    for large numbers. The more rounds (k), the more confident we can be.
    
    Args:
        n: Number to test for primality
        k: Number of rounds (higher = more accurate)
    
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
    base, exp, mod = 2, 100, 1000000007
    result = mod_exp(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}")
    print(f"   (That's 2^100 mod 10^9+7, calculated instantly!)\n")
    
    # Demo 2: Modular inverse
    print("2. Modular Inverse")
    a, m = 3, 11
    inv = mod_inverse(a, m)
    if inv:
        print(f"   Inverse of {a} mod {m} = {inv}")
        print(f"   Verification: ({a} * {inv}) mod {m} = {(a * inv) % m}\n")
    
    # Demo 3: Chinese Remainder Theorem
    print("3. Chinese Remainder Theorem")
    print("   Solving the system:")
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    for r, m in zip(remainders, moduli):
        print(f"      x ≡ {r} (mod {m})")
    
    x = chinese_remainder_theorem(remainders, moduli)
    print(f"   Solution: x = {x}")
    print(f"   Verification:")
    for r, m in zip(remainders, moduli):
        print(f"      {x} mod {m} = {x % m} (should be {r})")
    print()
    
    # Demo 4: Miller-Rabin primality test
    print("4. Miller-Rabin Primality Test")
    test_numbers = [17, 1000000007, 1000000008, 982451653]
    for num in test_numbers:
        is_prime = is_prime_mr(num, k=10)
        print(f"   {num}: {'probably prime' if is_prime else 'composite'}")
    print()
    
    # Demo 5: Real-world scenario - RSA-like calculation
    print("5. Mini RSA-like Demo")
    p, q = 61, 53
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 17
    d = mod_inverse(e, phi)
    
    message = 42
    encrypted = mod_exp(message, e, n)
    decrypted = mod_exp(encrypted, d, n)
    
    print(f"   Public key: (e={e}, n={n})")
    print(f"   Original message: {message}")
    print(f"   Encrypted: {encrypted}")
    print(f"   Decrypted: {decrypted}")
    print(f"   Success: {message == decrypted}")