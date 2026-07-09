"""
Date: 2026-07-09
Created a collection of modular arithmetic functions including fast modular exponentiation, extended Euclidean algorithm, and modular multiplicative inverse for cryptography and number theory work.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit

A collection of functions for modular arithmetic operations.
Useful for cryptography, number theory, and competitive programming.
"""


def mod_exp(base, exponent, modulus):
    """
    Compute (base^exponent) % modulus efficiently using binary exponentiation.
    
    This is way faster than naive exponentiation for large numbers because
    it reduces intermediate results at each step instead of computing the
    massive power first then taking modulo.
    
    Args:
        base: The base number
        exponent: The power to raise to (non-negative)
        modulus: The modulus to apply
    
    Returns:
        (base^exponent) % modulus
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
        exponent = exponent >> 1  # bit shift right = divide by 2
        base = (base * base) % modulus
    
    return result


def extended_gcd(a, b):
    """
    Extended Euclidean Algorithm.
    
    Finds integers x and y such that: a*x + b*y = gcd(a, b)
    This is the foundation for finding modular multiplicative inverses.
    
    Args:
        a: First integer
        b: Second integer
    
    Returns:
        Tuple (gcd, x, y) where gcd is the greatest common divisor
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
    Calculate the modular multiplicative inverse of a modulo m.
    
    Returns x such that (a * x) % m == 1
    Only exists when gcd(a, m) == 1
    
    Args:
        a: The number to invert
        m: The modulus
    
    Returns:
        The modular inverse, or None if it doesn't exist
    """
    gcd, x, _ = extended_gcd(a, m)
    
    if gcd != 1:
        # Modular inverse doesn't exist
        return None
    
    # Make sure x is positive
    return (x % m + m) % m


def chinese_remainder_theorem(remainders, moduli):
    """
    Solve system of congruences using Chinese Remainder Theorem.
    
    Given x ≡ r1 (mod m1), x ≡ r2 (mod m2), ..., finds x.
    The moduli must be pairwise coprime for a unique solution.
    
    Args:
        remainders: List of remainder values
        moduli: List of modulus values (must be pairwise coprime)
    
    Returns:
        The solution x, or None if no solution exists
    """
    if len(remainders) != len(moduli):
        return None
    
    # Product of all moduli
    total_product = 1
    for m in moduli:
        total_product *= m
    
    result = 0
    
    for r, m in zip(remainders, moduli):
        # Product of all moduli except current one
        partial_product = total_product // m
        
        # Find modular inverse of partial_product mod m
        inverse = mod_inverse(partial_product, m)
        
        if inverse is None:
            return None  # Moduli aren't coprime
        
        result += r * partial_product * inverse
    
    return result % total_product


def is_prime_miller_rabin(n, k=5):
    """
    Miller-Rabin primality test.
    
    Probabilistic test that's way faster than trial division for large numbers.
    The parameter k controls accuracy — higher k means lower false positive rate.
    
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
    
    # Write n-1 as 2^r * d where d is odd
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
    print(f"   Compute 3^100000 mod 1000000007")
    result = mod_exp(3, 100000, 1000000007)
    print(f"   Result: {result}\n")
    
    # Demo 2: Modular multiplicative inverse
    print("2. Modular Multiplicative Inverse")
    a, m = 7, 26
    inv = mod_inverse(a, m)
    if inv:
        print(f"   Inverse of {a} mod {m} = {inv}")
        print(f"   Verification: ({a} * {inv}) mod {m} = {(a * inv) % m}\n")
    else:
        print(f"   No inverse exists for {a} mod {m}\n")
    
    # Demo 3: Chinese Remainder Theorem
    print("3. Chinese Remainder Theorem")
    print("   Solving: x ≡ 2 (mod 3), x ≡ 3 (mod 5), x ≡ 2 (mod 7)")
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    x = chinese_remainder_theorem(remainders, moduli)
    print(f"   Solution: x = {x}")
    print(f"   Verification: {x} mod 3 = {x % 3}, {x} mod 5 = {x % 5}, {x} mod 7 = {x % 7}\n")
    
    # Demo 4: Miller-Rabin primality test
    print("4. Miller-Rabin Primality Test")
    test_numbers = [17, 19, 21, 97, 1000000007, 1000000009]
    for n in test_numbers:
        is_prime = is_prime_miller_rabin(n, k=10)
        print(f"   {n}: {'probably prime' if is_prime else 'composite'}")
    
    print("\n=== All tests completed ===")