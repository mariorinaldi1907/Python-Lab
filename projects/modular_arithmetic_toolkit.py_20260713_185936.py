"""
Date: 2026-07-13
Created a collection of modular arithmetic functions I always end up needing for crypto challenges and competitive programming — includes modular inverse, Chinese remainder theorem, and proper fast exponentiation.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit
A collection of number theory utilities I keep reimplementing.
Focused on modular operations because they come up constantly in crypto and competitive programming.
"""

from typing import Tuple, List, Optional


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """
    Extended Euclidean Algorithm.
    Returns (gcd, x, y) such that a*x + b*y = gcd(a, b).
    
    This is the foundation for modular inverses — we need the coefficients,
    not just the gcd itself.
    """
    if b == 0:
        return a, 1, 0
    
    gcd, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    
    return gcd, x, y


def mod_inverse(a: int, m: int) -> Optional[int]:
    """
    Compute modular multiplicative inverse of a modulo m.
    Returns x such that (a * x) % m == 1, or None if no inverse exists.
    
    Inverse only exists when gcd(a, m) = 1, which is why we use extended_gcd.
    """
    gcd, x, _ = extended_gcd(a, m)
    
    if gcd != 1:
        return None  # Inverse doesn't exist
    
    return x % m


def fast_mod_exp(base: int, exp: int, mod: int) -> int:
    """
    Fast modular exponentiation using binary exponentiation.
    Computes (base^exp) % mod efficiently.
    
    Way faster than pow() for very large numbers... actually wait, Python's built-in
    pow(base, exp, mod) does this now. But implementing it anyway because it's elegant
    and I like understanding the algorithm.
    """
    if mod == 1:
        return 0
    
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


def chinese_remainder_theorem(remainders: List[int], moduli: List[int]) -> Optional[int]:
    """
    Solve system of congruences using Chinese Remainder Theorem.
    Given x ≡ remainders[i] (mod moduli[i]), find x.
    
    Returns the solution modulo the product of all moduli, or None if no solution exists.
    This assumes moduli are pairwise coprime — doesn't check for it though.
    """
    if len(remainders) != len(moduli):
        return None
    
    if len(remainders) == 0:
        return None
    
    # Start with the first congruence
    x = remainders[0]
    m = moduli[0]
    
    # Iteratively solve pairs of congruences
    for i in range(1, len(remainders)):
        a1, m1 = x, m
        a2, m2 = remainders[i], moduli[i]
        
        # We need to solve: x ≡ a1 (mod m1) and x ≡ a2 (mod m2)
        gcd, p, q = extended_gcd(m1, m2)
        
        if (a2 - a1) % gcd != 0:
            return None  # No solution exists
        
        # Combine the two congruences
        lcm = m1 * m2 // gcd
        x = (a1 + m1 * ((a2 - a1) // gcd) * p) % lcm
        m = lcm
    
    return x


def is_prime_miller_rabin(n: int, k: int = 5) -> bool:
    """
    Miller-Rabin primality test — probabilistic but fast.
    
    k is the number of rounds. Higher k = more accuracy.
    Returns True if n is probably prime, False if definitely composite.
    
    I chose k=5 as default because it's a good balance for most use cases.
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
        x = fast_mod_exp(a, d, n)
        
        if x == 1 or x == n - 1:
            continue
        
        for _ in range(r - 1):
            x = fast_mod_exp(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    
    return True


def totient(n: int) -> int:
    """
    Euler's totient function φ(n).
    Counts integers from 1 to n that are coprime with n.
    
    Using the formula based on prime factorization because it's faster
    than actually counting coprime numbers.
    """
    result = n
    p = 2
    
    # Find all prime factors and apply formula: φ(n) = n * ∏(1 - 1/p)
    while p * p <= n:
        if n % p == 0:
            # Remove factor p
            while n % p == 0:
                n //= p
            # Apply formula
            result -= result // p
        p += 1
    
    if n > 1:
        result -= result // n
    
    return result


if __name__ == "__main__":
    print("=== Modular Arithmetic Toolkit Demo ===\n")
    
    # Test extended GCD
    print("1. Extended GCD")
    a, b = 240, 46
    gcd, x, y = extended_gcd(a, b)
    print(f"   gcd({a}, {b}) = {gcd}")
    print(f"   {a}*{x} + {b}*{y} = {a*x + b*y} ✓\n")
    
    # Test modular inverse
    print("2. Modular Inverse")
    a, m = 17, 43
    inv = mod_inverse(a, m)
    print(f"   {a}^(-1) mod {m} = {inv}")
    print(f"   Verification: ({a} * {inv}) mod {m} = {(a * inv) % m} ✓\n")
    
    # Test fast modular exponentiation
    print("3. Fast Modular Exponentiation")
    base, exp, mod = 3, 1000000, 1000000007
    result = fast_mod_exp(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}")
    print(f"   (verified with built-in: {pow(base, exp, mod)}) ✓\n")
    
    # Test Chinese Remainder Theorem
    print("4. Chinese Remainder Theorem")
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    solution = chinese_remainder_theorem(remainders, moduli)
    print(f"   Solving system:")
    for r, m in zip(remainders, moduli):
        print(f"     x ≡ {r} (mod {m})")
    print(f"   Solution: x = {solution}")
    for r, m in zip(remainders, moduli):
        print(f"   Verify: {solution} mod {m} = {solution % m} (expected {r}) ✓")
    print()
    
    # Test Miller-Rabin primality
    print("5. Miller-Rabin Primality Test")
    test_numbers = [17, 19, 100, 1009, 1000000007]
    for num in test_numbers:
        is_prime = is_prime_miller_rabin(num, k=10)
        print(f"   {num}: {'probably prime' if is_prime else 'composite'}")
    print()
    
    # Test Euler's totient
    print("6. Euler's Totient Function")
    test_totients = [1, 12, 36, 100]
    for n in test_totients:
        phi = totient(n)
        print(f"   φ({n}) = {phi}")