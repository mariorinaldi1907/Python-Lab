"""
Date: 2026-08-29
Created a collection of modular arithmetic functions I keep reusing in Project Euler problems, including modular exponentiation, multiplicative inverse, and Chinese Remainder Theorem solver.
"""

"""
Modular Arithmetic Toolkit
A collection of number theory utilities I find myself rewriting constantly.
Focuses on modular arithmetic operations that come up in crypto and competitive programming.
"""

from typing import List, Tuple
from math import gcd


def mod_exp(base: int, exponent: int, modulus: int) -> int:
    """
    Compute (base^exponent) % modulus efficiently using binary exponentiation.
    
    This is way faster than doing pow(base, exponent) % modulus for large numbers
    because it keeps intermediate results small by applying modulus at each step.
    
    Args:
        base: The base number
        exponent: The power to raise to (non-negative)
        modulus: The modulus to apply
        
    Returns:
        Result of (base^exponent) mod modulus
    """
    if modulus == 1:
        return 0
    
    result = 1
    base = base % modulus
    
    while exponent > 0:
        # If exponent is odd, multiply base with result
        if exponent % 2 == 1:
            result = (result * base) % modulus
        
        # Now exponent must be even, square the base and halve the exponent
        exponent = exponent >> 1  # Bit shift right = divide by 2
        base = (base * base) % modulus
    
    return result


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """
    Extended Euclidean Algorithm.
    
    Finds gcd(a, b) and coefficients x, y such that ax + by = gcd(a, b).
    This is essential for finding modular inverses.
    
    Returns:
        Tuple of (gcd, x, y)
    """
    if a == 0:
        return b, 0, 1
    
    gcd_val, x1, y1 = extended_gcd(b % a, a)
    
    # Update x and y using results of recursive call
    x = y1 - (b // a) * x1
    y = x1
    
    return gcd_val, x, y


def mod_inverse(a: int, m: int) -> int:
    """
    Find the modular multiplicative inverse of a modulo m.
    
    Returns x such that (a * x) % m == 1.
    Only exists when gcd(a, m) == 1.
    
    Args:
        a: Number to find inverse of
        m: Modulus
        
    Returns:
        The modular inverse
        
    Raises:
        ValueError: If inverse doesn't exist
    """
    gcd_val, x, _ = extended_gcd(a, m)
    
    if gcd_val != 1:
        raise ValueError(f"Modular inverse doesn't exist: gcd({a}, {m}) = {gcd_val} != 1")
    
    # x might be negative, so we ensure it's in range [0, m)
    return (x % m + m) % m


def chinese_remainder_theorem(remainders: List[int], moduli: List[int]) -> int:
    """
    Solve a system of congruences using the Chinese Remainder Theorem.
    
    Given: x ≡ remainders[i] (mod moduli[i]) for all i
    Find: x
    
    This assumes all moduli are pairwise coprime (no common factors).
    I use this all the time for crypto problems.
    
    Args:
        remainders: List of remainder values
        moduli: List of moduli (must be pairwise coprime)
        
    Returns:
        The smallest non-negative solution
    """
    if len(remainders) != len(moduli):
        raise ValueError("Must have same number of remainders and moduli")
    
    # Product of all moduli
    total_product = 1
    for m in moduli:
        total_product *= m
    
    result = 0
    
    for remainder, modulus in zip(remainders, moduli):
        # Product of all other moduli
        partial_product = total_product // modulus
        
        # Find modular inverse of partial_product mod modulus
        inverse = mod_inverse(partial_product, modulus)
        
        # Add this term to result
        result += remainder * partial_product * inverse
    
    return result % total_product


def is_prime_miller_rabin(n: int, k: int = 5) -> bool:
    """
    Probabilistic primality test using Miller-Rabin algorithm.
    
    Faster than trial division for large numbers. The accuracy improves
    with more rounds (k), but k=5 is usually good enough for most purposes.
    
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
    
    # Witness loop - test k random witnesses
    import random
    for _ in range(k):
        a = random.randint(2, n - 2)
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
    print("1. Modular Exponentiation")
    base, exp, mod = 3, 1000000, 1000000007
    result = mod_exp(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}")
    print()
    
    # Demo 2: Modular inverse
    print("2. Modular Inverse")
    a, m = 7, 26
    try:
        inv = mod_inverse(a, m)
        print(f"   Inverse of {a} mod {m} = {inv}")
        print(f"   Verification: ({a} * {inv}) mod {m} = {(a * inv) % m}")
    except ValueError as e:
        print(f"   Error: {e}")
    print()
    
    # Demo 3: Chinese Remainder Theorem
    print("3. Chinese Remainder Theorem")
    print("   Solving system:")
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    for r, m in zip(remainders, moduli):
        print(f"   x ≡ {r} (mod {m})")
    
    solution = chinese_remainder_theorem(remainders, moduli)
    print(f"   Solution: x = {solution}")
    print(f"   Verification:")
    for r, m in zip(remainders, moduli):
        print(f"     {solution} mod {m} = {solution % m} (expected {r})")
    print()
    
    # Demo 4: Miller-Rabin primality test
    print("4. Miller-Rabin Primality Test")
    test_numbers = [17, 91, 104729, 104730]
    for num in test_numbers:
        is_prime = is_prime_miller_rabin(num, k=10)
        print(f"   {num}: {'probably prime' if is_prime else 'composite'}")