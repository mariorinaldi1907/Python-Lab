"""
Date: 2026-07-24
Created a collection of number theory functions I kept rewriting for Project Euler problems — figured I'd consolidate them once and for all.
"""

"""
Modular Arithmetic Toolkit

A collection of utilities for modular arithmetic and number theory operations.
I got tired of rewriting these for competitive programming and Project Euler,
so here's a proper implementation with extended GCD and Chinese Remainder Theorem.
"""

from typing import List, Tuple, Optional


def gcd(a: int, b: int) -> int:
    """
    Compute the greatest common divisor using Euclidean algorithm.
    
    Classic recursive approach - keeps going until b hits zero.
    """
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """
    Extended Euclidean algorithm: returns (gcd, x, y) where ax + by = gcd(a, b).
    
    This is the magic behind modular inverses. The idea is to track coefficients
    as we recurse through the regular GCD algorithm.
    """
    if b == 0:
        return a, 1, 0
    
    gcd_val, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    
    return gcd_val, x, y


def mod_inverse(a: int, m: int) -> Optional[int]:
    """
    Find the modular multiplicative inverse of a modulo m.
    
    Returns x such that (a * x) % m == 1, or None if it doesn't exist.
    The inverse only exists when gcd(a, m) == 1.
    """
    g, x, _ = extended_gcd(a, m)
    
    if g != 1:
        # No modular inverse exists
        return None
    
    # Make sure we return a positive result
    return x % m


def fast_power(base: int, exp: int, mod: int) -> int:
    """
    Compute (base^exp) % mod efficiently using binary exponentiation.
    
    This is way faster than doing base**exp % mod for large exponents.
    We square the base and halve the exponent at each step, only multiplying
    into result when the exponent bit is 1.
    """
    result = 1
    base = base % mod
    
    while exp > 0:
        # If exp is odd, multiply base into result
        if exp % 2 == 1:
            result = (result * base) % mod
        
        # Square the base and halve the exponent
        exp = exp >> 1  # Bitshift right = divide by 2
        base = (base * base) % mod
    
    return result


def chinese_remainder_theorem(remainders: List[int], moduli: List[int]) -> Optional[int]:
    """
    Solve a system of congruences using the Chinese Remainder Theorem.
    
    Given x ≡ a₁ (mod m₁), x ≡ a₂ (mod m₂), ..., find x.
    
    This only works when all moduli are pairwise coprime. I'm using the
    constructive approach where we build up the solution incrementally.
    """
    if len(remainders) != len(moduli):
        return None
    
    if not remainders:
        return None
    
    # Start with the first congruence
    x = remainders[0]
    M = moduli[0]
    
    # Add one congruence at a time
    for i in range(1, len(remainders)):
        a = remainders[i]
        m = moduli[i]
        
        # We need to solve: x ≡ a (mod m) and x ≡ x (mod M)
        # This becomes: x + k*M ≡ a (mod m) for some k
        # So: k*M ≡ (a - x) (mod m)
        
        g, p, q = extended_gcd(M, m)
        
        if (a - x) % g != 0:
            # No solution exists
            return None
        
        # Scale the solution
        lcm = M * m // g
        x = (x + M * ((a - x) // g) * p) % lcm
        M = lcm
    
    return x


def is_prime_miller_rabin(n: int, k: int = 5) -> bool:
    """
    Miller-Rabin primality test - probabilistic but very fast.
    
    For k rounds, the probability of a composite passing is at most 4^(-k).
    With k=5, that's about 1 in 1024, which is good enough for most purposes.
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
    
    # Fast exponentiation demo
    print("1. Fast Power: 2^1000 mod 997")
    result = fast_power(2, 1000, 997)
    print(f"   Result: {result}\n")
    
    # Modular inverse demo
    print("2. Modular Inverse: Find x where 3x ≡ 1 (mod 11)")
    inv = mod_inverse(3, 11)
    print(f"   x = {inv}")
    print(f"   Verification: (3 * {inv}) mod 11 = {(3 * inv) % 11}\n")
    
    # Chinese Remainder Theorem demo
    print("3. Chinese Remainder Theorem:")
    print("   Solve: x ≡ 2 (mod 3), x ≡ 3 (mod 5), x ≡ 2 (mod 7)")
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    x = chinese_remainder_theorem(remainders, moduli)
    print(f"   Solution: x = {x}")
    print(f"   Verification: {x} mod 3 = {x % 3}, {x} mod 5 = {x % 5}, {x} mod 7 = {x % 7}\n")
    
    # Miller-Rabin primality test demo
    print("4. Miller-Rabin Primality Test:")
    test_numbers = [17, 1000000007, 1000000008, 1000000009]
    for num in test_numbers:
        is_prime = is_prime_miller_rabin(num)
        print(f"   {num}: {'PRIME' if is_prime else 'COMPOSITE'}")
    
    print("\n=== Demo Complete ===")