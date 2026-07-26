"""
Date: 2026-07-26
Created a number theory utility library for modular arithmetic operations since I keep needing these for Project Euler and cryptography experiments.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit

A collection of number theory functions I find myself needing repeatedly
for competitive programming and cryptography work. Includes extended GCD,
modular inverse, Chinese Remainder Theorem, and fast modular exponentiation.

Author: Mario
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
    Extended Euclidean Algorithm - finds gcd(a,b) and coefficients x,y
    such that ax + by = gcd(a,b).
    
    This is the backbone for modular inverse calculation.
    
    Args:
        a: First integer
        b: Second integer
    
    Returns:
        Tuple (gcd, x, y) where gcd = ax + by
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
    Only exists if gcd(a, m) == 1.
    
    Args:
        a: The number to invert
        m: The modulus
    
    Returns:
        The modular inverse of a mod m
    
    Raises:
        ValueError: If inverse doesn't exist (when gcd(a,m) != 1)
    """
    g, x, _ = extended_gcd(a, m)
    
    if g != 1:
        raise ValueError(f"Modular inverse doesn't exist: gcd({a}, {m}) = {g} != 1")
    
    # Make sure result is positive
    return x % m


def fast_pow_mod(base, exp, mod):
    """
    Fast modular exponentiation using binary exponentiation.
    
    Computes (base^exp) % mod efficiently in O(log exp) time.
    Much faster than doing pow(base, exp) % mod for large exponents.
    
    Args:
        base: The base number
        exp: The exponent
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
        
        # exp must be even now
        exp = exp >> 1  # Divide exp by 2
        base = (base * base) % mod
    
    return result


def chinese_remainder_theorem(remainders, moduli):
    """
    Solve system of congruences using Chinese Remainder Theorem.
    
    Given x ≡ a1 (mod m1), x ≡ a2 (mod m2), ..., x ≡ an (mod mn),
    finds the unique solution modulo M = m1 * m2 * ... * mn.
    
    Assumes all moduli are pairwise coprime (gcd(mi, mj) = 1 for i != j).
    
    Args:
        remainders: List of remainders [a1, a2, ..., an]
        moduli: List of moduli [m1, m2, ..., mn]
    
    Returns:
        The solution x (mod M) where M is the product of all moduli
    
    Raises:
        ValueError: If moduli are not pairwise coprime
    """
    if len(remainders) != len(moduli):
        raise ValueError("Number of remainders must equal number of moduli")
    
    # Check pairwise coprimality
    for i in range(len(moduli)):
        for j in range(i + 1, len(moduli)):
            if gcd(moduli[i], moduli[j]) != 1:
                raise ValueError(f"Moduli {moduli[i]} and {moduli[j]} are not coprime")
    
    # Calculate M = product of all moduli
    M = 1
    for m in moduli:
        M *= m
    
    # Apply CRT formula
    x = 0
    for i in range(len(remainders)):
        Mi = M // moduli[i]
        yi = mod_inverse(Mi, moduli[i])
        x += remainders[i] * Mi * yi
    
    return x % M


def is_prime_miller_rabin(n, k=5):
    """
    Miller-Rabin primality test - probabilistic algorithm.
    
    Tests if n is probably prime with k rounds of testing.
    The probability of a composite passing is at most 4^(-k).
    
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
        x = fast_pow_mod(a, d, n)
        
        if x == 1 or x == n - 1:
            continue
        
        for _ in range(r - 1):
            x = fast_pow_mod(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    
    return True


if __name__ == "__main__":
    print("=== Modular Arithmetic Toolkit Demo ===\n")
    
    # Test GCD and Extended GCD
    print("1. GCD and Extended GCD")
    a, b = 240, 46
    g = gcd(a, b)
    eg, x, y = extended_gcd(a, b)
    print(f"   gcd({a}, {b}) = {g}")
    print(f"   Extended: {a}*{x} + {b}*{y} = {eg}")
    print(f"   Verification: {a*x + b*y} = {eg}\n")
    
    # Test modular inverse
    print("2. Modular Inverse")
    a, m = 7, 26
    inv = mod_inverse(a, m)
    print(f"   {a}^(-1) mod {m} = {inv}")
    print(f"   Verification: ({a} * {inv}) mod {m} = {(a * inv) % m}\n")
    
    # Test fast modular exponentiation
    print("3. Fast Modular Exponentiation")
    base, exp, mod = 3, 1000000, 1000000007
    result = fast_pow_mod(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}\n")
    
    # Test Chinese Remainder Theorem
    print("4. Chinese Remainder Theorem")
    remainders = [2, 3, 1]
    moduli = [3, 4, 5]
    solution = chinese_remainder_theorem(remainders, moduli)
    print(f"   System: x ≡ {remainders[0]} (mod {moduli[0]})")
    for i in range(1, len(remainders)):
        print(f"           x ≡ {remainders[i]} (mod {moduli[i]})")
    print(f"   Solution: x ≡ {solution} (mod {moduli[0] * moduli[1] * moduli[2]})")
    print(f"   Verification: {solution} mod {moduli[0]} = {solution % moduli[0]},", end=" ")
    print(f"{solution} mod {moduli[1]} = {solution % moduli[1]},", end=" ")
    print(f"{solution} mod {moduli[2]} = {solution % moduli[2]}\n")
    
    # Test primality testing
    print("5. Miller-Rabin Primality Test")
    test_numbers = [17, 561, 104729, 104730]
    for num in test_numbers:
        is_prime = is_prime_miller_rabin(num)
        print(f"   {num}: {'probably prime' if is_prime else 'composite'}")