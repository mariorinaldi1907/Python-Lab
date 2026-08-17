"""
Date: 2026-08-17
Implemented core number theory primitives I always end up needing for cryptography experiments and competitive programming — includes modular inverse, Chinese remainder theorem, and some primality testing.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit
A collection of number theory utilities I keep rewriting in different projects.
Finally putting them all in one place.
"""

from typing import Tuple, List, Optional


def gcd(a: int, b: int) -> int:
    """
    Compute the greatest common divisor using Euclidean algorithm.
    Classic recursive implementation because it's cleaner than the iterative version.
    """
    if b == 0:
        return a
    return gcd(b, a % b)


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """
    Extended Euclidean Algorithm.
    Returns (gcd, x, y) such that a*x + b*y = gcd(a, b).
    
    This is the backbone for computing modular inverses.
    I always forget the coefficient update rules, so keeping this well-documented.
    """
    if b == 0:
        return (a, 1, 0)
    
    gcd_val, x1, y1 = extended_gcd(b, a % b)
    
    # Update coefficients based on the recursive relation
    # a = b * q + r where r = a % b
    # So: gcd = b*x1 + (a%b)*y1 = b*x1 + (a - b*q)*y1
    #         = a*y1 + b*(x1 - q*y1)
    x = y1
    y = x1 - (a // b) * y1
    
    return (gcd_val, x, y)


def mod_inverse(a: int, m: int) -> Optional[int]:
    """
    Compute modular inverse of a modulo m.
    Returns x such that (a * x) % m == 1, or None if inverse doesn't exist.
    
    The inverse exists iff gcd(a, m) == 1.
    """
    g, x, _ = extended_gcd(a, m)
    
    if g != 1:
        return None  # Inverse doesn't exist
    
    # x might be negative, so we normalize it to [0, m)
    return x % m


def fast_power(base: int, exp: int, mod: int) -> int:
    """
    Fast modular exponentiation using binary exponentiation.
    Computes (base^exp) % mod in O(log exp) time.
    
    This is way faster than pow() for huge numbers... just kidding, Python's
    built-in pow(base, exp, mod) actually uses this algorithm. But implementing
    it myself helps me understand the bit-shifting magic.
    """
    result = 1
    base = base % mod
    
    while exp > 0:
        # If exp is odd, multiply base with result
        if exp % 2 == 1:
            result = (result * base) % mod
        
        # Now exp must be even, so we square the base and halve the exponent
        exp = exp // 2
        base = (base * base) % mod
    
    return result


def chinese_remainder_theorem(remainders: List[int], moduli: List[int]) -> Optional[int]:
    """
    Solve system of congruences using the Chinese Remainder Theorem.
    
    Given x ≡ remainders[i] (mod moduli[i]) for all i,
    finds the unique solution modulo the product of all moduli.
    
    Returns None if the moduli aren't pairwise coprime (CRT doesn't apply).
    
    I needed this for a CTF challenge once and had to derive it from scratch.
    Never again — keeping this implementation handy.
    """
    if len(remainders) != len(moduli):
        return None
    
    # Check if moduli are pairwise coprime
    for i in range(len(moduli)):
        for j in range(i + 1, len(moduli)):
            if gcd(moduli[i], moduli[j]) != 1:
                return None
    
    # Product of all moduli
    M = 1
    for m in moduli:
        M *= m
    
    result = 0
    
    for i in range(len(moduli)):
        Mi = M // moduli[i]  # Product of all moduli except moduli[i]
        
        # Find the modular inverse of Mi mod moduli[i]
        yi = mod_inverse(Mi, moduli[i])
        
        if yi is None:
            return None  # This shouldn't happen if moduli are coprime, but just in case
        
        # Add this term to the result
        result += remainders[i] * Mi * yi
    
    return result % M


def is_prime_miller_rabin(n: int, k: int = 5) -> bool:
    """
    Miller-Rabin primality test.
    Probabilistic test that's correct with high probability.
    
    k is the number of rounds — higher k means higher confidence.
    For k=5, the error probability is at most (1/4)^5 ≈ 0.001.
    
    Using this instead of trial division for large numbers.
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
    
    # Import random here since we only use it in this function
    import random
    
    # Witness loop
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = fast_power(a, d, n)
        
        if x == 1 or x == n - 1:
            continue
        
        # Square x repeatedly r-1 times
        for _ in range(r - 1):
            x = fast_power(x, 2, n)
            if x == n - 1:
                break
        else:
            # If we never hit n-1, n is composite
            return False
    
    return True


if __name__ == "__main__":
    print("=== Modular Arithmetic Toolkit Demo ===\n")
    
    # GCD and Extended GCD
    print("1. GCD and Extended GCD:")
    a, b = 48, 18
    g = gcd(a, b)
    print(f"   gcd({a}, {b}) = {g}")
    
    g, x, y = extended_gcd(a, b)
    print(f"   Extended: {a}*{x} + {b}*{y} = {g}")
    print(f"   Verification: {a*x + b*y} = {g}\n")
    
    # Modular Inverse
    print("2. Modular Inverse:")
    a, m = 7, 26
    inv = mod_inverse(a, m)
    if inv:
        print(f"   {a}^(-1) mod {m} = {inv}")
        print(f"   Verification: ({a} * {inv}) mod {m} = {(a * inv) % m}\n")
    else:
        print(f"   No inverse exists for {a} mod {m}\n")
    
    # Fast Exponentiation
    print("3. Fast Modular Exponentiation:")
    base, exp, mod = 2, 100, 1000000007
    result = fast_power(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}")
    print(f"   Built-in pow: {pow(base, exp, mod)}\n")
    
    # Chinese Remainder Theorem
    print("4. Chinese Remainder Theorem:")
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    solution = chinese_remainder_theorem(remainders, moduli)
    print(f"   System: x ≡ {remainders[0]} (mod {moduli[0]})")
    print(f"           x ≡ {remainders[1]} (mod {moduli[1]})")
    print(f"           x ≡ {remainders[2]} (mod {moduli[2]})")
    print(f"   Solution: x ≡ {solution} (mod {moduli[0] * moduli[1] * moduli[2]})")
    
    # Verify the solution
    print(f"   Verification:")
    for i in range(len(remainders)):
        print(f"      {solution} mod {moduli[i]} = {solution % moduli[i]} (expected {remainders[i]})")
    print()
    
    # Miller-Rabin Primality Test
    print("5. Miller-Rabin Primality Test:")
    test_numbers = [17, 221, 1009, 1000000007]
    for num in test_numbers:
        is_p = is_prime_miller_rabin(num)
        print(f"   {num}: {'probably prime' if is_p else 'composite'}")