"""
Date: 2026-06-15
Implemented common modular arithmetic operations I kept rewriting for Project Euler problems — includes fast modular exponentiation, modular inverse via extended GCD, and Chinese Remainder Theorem solver.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit

A collection of number theory functions I use for competitive programming
and cryptography stuff. Includes modular exponentiation, modular inverse,
extended GCD, and a solver for the Chinese Remainder Theorem.
"""


def gcd(a, b):
    """
    Compute the greatest common divisor using Euclidean algorithm.
    
    I know math.gcd exists, but implementing this myself because I need
    the extended version below anyway.
    """
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a, b):
    """
    Extended Euclidean Algorithm.
    
    Returns (gcd, x, y) such that a*x + b*y = gcd(a, b).
    This is crucial for computing modular inverses.
    """
    if b == 0:
        return a, 1, 0
    
    gcd_val, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    
    return gcd_val, x, y


def mod_inverse(a, m):
    """
    Compute modular multiplicative inverse of a modulo m.
    
    Returns x such that (a * x) % m == 1.
    Raises ValueError if inverse doesn't exist (when gcd(a, m) != 1).
    
    I use this constantly for modular division in number theory problems.
    """
    g, x, _ = extended_gcd(a, m)
    
    if g != 1:
        raise ValueError(f"Modular inverse doesn't exist: gcd({a}, {m}) = {g} != 1")
    
    # Make sure result is positive
    return x % m


def mod_pow(base, exp, mod):
    """
    Fast modular exponentiation using binary exponentiation.
    
    Computes (base^exp) % mod efficiently in O(log exp) time.
    Way faster than doing pow(base, exp) % mod for large numbers
    because we keep intermediate results small.
    """
    if mod == 1:
        return 0
    
    result = 1
    base = base % mod
    
    while exp > 0:
        # If exp is odd, multiply base with result
        if exp % 2 == 1:
            result = (result * base) % mod
        
        # exp must be even now
        exp = exp >> 1  # divide by 2
        base = (base * base) % mod
    
    return result


def chinese_remainder_theorem(remainders, moduli):
    """
    Solve system of congruences using Chinese Remainder Theorem.
    
    Given: x ≡ r1 (mod m1), x ≡ r2 (mod m2), ..., x ≡ rn (mod mn)
    Find: x (the unique solution modulo M = m1*m2*...*mn)
    
    Assumes all moduli are pairwise coprime. This assumption is critical
    for CRT to work — if violated, there might be no solution or infinitely many.
    """
    if len(remainders) != len(moduli):
        raise ValueError("remainders and moduli must have same length")
    
    # Total modulus
    M = 1
    for m in moduli:
        M *= m
    
    x = 0
    
    for r_i, m_i in zip(remainders, moduli):
        # M_i is the product of all moduli except m_i
        M_i = M // m_i
        
        # Find the modular inverse of M_i modulo m_i
        # This is the key step that makes CRT work
        y_i = mod_inverse(M_i, m_i)
        
        # Add this term to the solution
        x += r_i * M_i * y_i
    
    # Return smallest positive solution
    return x % M


def is_prime_miller_rabin(n, k=5):
    """
    Miller-Rabin primality test.
    
    Probabilistic test that's right with very high probability.
    k is the number of rounds — higher k means more accurate but slower.
    For k=5, error probability is less than (1/4)^5 = 1/1024.
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
        x = mod_pow(a, d, n)
        
        if x == 1 or x == n - 1:
            continue
        
        for _ in range(r - 1):
            x = mod_pow(x, 2, n)
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
    result = mod_pow(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}")
    print(f"   (Computing this naively would overflow!)\n")
    
    # Demo 2: Modular inverse
    print("2. Modular Inverse")
    a, m = 7, 26
    inv = mod_inverse(a, m)
    print(f"   Inverse of {a} mod {m} = {inv}")
    print(f"   Verification: ({a} * {inv}) mod {m} = {(a * inv) % m}\n")
    
    # Demo 3: Chinese Remainder Theorem
    print("3. Chinese Remainder Theorem")
    print("   Solving system:")
    remainders = [2, 3, 1]
    moduli = [3, 4, 5]
    for r, m in zip(remainders, moduli):
        print(f"     x ≡ {r} (mod {m})")
    
    solution = chinese_remainder_theorem(remainders, moduli)
    print(f"   Solution: x = {solution}")
    print(f"   Verification:")
    for r, m in zip(remainders, moduli):
        print(f"     {solution} mod {m} = {solution % m} (expected {r})")
    print()
    
    # Demo 4: Miller-Rabin primality test
    print("4. Miller-Rabin Primality Test")
    test_numbers = [17, 221, 1000000007, 1000000009]
    for n in test_numbers:
        is_prime = is_prime_miller_rabin(n)
        print(f"   {n}: {'PRIME' if is_prime else 'COMPOSITE'}")
    print()
    
    # Demo 5: Extended GCD
    print("5. Extended GCD (Bézout's Identity)")
    a, b = 240, 46
    g, x, y = extended_gcd(a, b)
    print(f"   gcd({a}, {b}) = {g}")
    print(f"   Bézout coefficients: x={x}, y={y}")
    print(f"   Verification: {a}*{x} + {b}*{y} = {a*x + b*y}")