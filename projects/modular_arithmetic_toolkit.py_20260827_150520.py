"""
Date: 2026-08-27
Created a collection of number theory functions I keep reusing: modular exponentiation, extended GCD, modular inverse, and a Chinese Remainder Theorem solver.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit

A collection of number theory utilities I find myself needing regularly.
Includes fast modular exponentiation, extended Euclidean algorithm,
modular inverse, and Chinese Remainder Theorem solver.
"""


def gcd(a, b):
    """
    Compute the greatest common divisor of a and b using Euclidean algorithm.
    
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
    Extended Euclidean Algorithm.
    
    Returns (gcd, x, y) such that a*x + b*y = gcd(a, b).
    This is super useful for finding modular inverses.
    
    Args:
        a: First integer
        b: Second integer
    
    Returns:
        Tuple (gcd, x, y) where gcd is the GCD and x, y are Bezout coefficients
    """
    if b == 0:
        return a, 1, 0
    
    gcd_val, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    
    return gcd_val, x, y


def mod_inverse(a, m):
    """
    Compute the modular multiplicative inverse of a modulo m.
    
    Returns x such that (a * x) % m == 1.
    Raises ValueError if the inverse doesn't exist (when gcd(a, m) != 1).
    
    Args:
        a: The number to invert
        m: The modulus
    
    Returns:
        The modular inverse of a mod m
    """
    gcd_val, x, _ = extended_gcd(a, m)
    
    if gcd_val != 1:
        raise ValueError(f"Modular inverse of {a} mod {m} does not exist (gcd != 1)")
    
    # Make sure the result is positive
    return (x % m + m) % m


def fast_mod_exp(base, exp, mod):
    """
    Fast modular exponentiation using binary exponentiation.
    
    Computes (base^exp) % mod efficiently in O(log exp) time.
    This is way faster than doing pow(base, exp) % mod for large numbers.
    
    Args:
        base: Base number
        exp: Exponent (non-negative integer)
        mod: Modulus
    
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
        
        # exp must be even now, so we can divide it by 2
        exp = exp >> 1  # Bit shift is faster than //2
        base = (base * base) % mod
    
    return result


def chinese_remainder_theorem(remainders, moduli):
    """
    Solve a system of congruences using the Chinese Remainder Theorem.
    
    Given x ≡ remainders[i] (mod moduli[i]) for all i,
    finds the smallest non-negative x that satisfies all congruences.
    
    The moduli must be pairwise coprime for a unique solution to exist.
    
    Args:
        remainders: List of remainders
        moduli: List of moduli (must be pairwise coprime)
    
    Returns:
        The solution x
    """
    if len(remainders) != len(moduli):
        raise ValueError("remainders and moduli must have the same length")
    
    # Product of all moduli
    total_mod = 1
    for m in moduli:
        total_mod *= m
    
    solution = 0
    
    for remainder, modulus in zip(remainders, moduli):
        # For each congruence, compute the partial solution
        partial_product = total_mod // modulus
        
        # Find the modular inverse of partial_product mod modulus
        inverse = mod_inverse(partial_product, modulus)
        
        # Add this term to the solution
        solution += remainder * partial_product * inverse
    
    return solution % total_mod


def is_prime_fermat(n, k=5):
    """
    Probabilistic primality test using Fermat's Little Theorem.
    
    Tests if n is probably prime by checking if a^(n-1) ≡ 1 (mod n)
    for k random values of a. Not foolproof (Carmichael numbers fool it),
    but good enough for most cases.
    
    Args:
        n: Number to test
        k: Number of iterations (higher = more accurate)
    
    Returns:
        True if n is probably prime, False if definitely composite
    """
    import random
    
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    for _ in range(k):
        a = random.randint(2, n - 2)
        if fast_mod_exp(a, n - 1, n) != 1:
            return False
    
    return True


if __name__ == "__main__":
    print("=== Modular Arithmetic Toolkit Demo ===\n")
    
    # Demo 1: Fast modular exponentiation
    print("1. Fast Modular Exponentiation")
    base, exp, mod = 3, 100000, 1000000007
    result = fast_mod_exp(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}")
    print()
    
    # Demo 2: Modular inverse
    print("2. Modular Inverse")
    a, m = 7, 26
    inv = mod_inverse(a, m)
    print(f"   Inverse of {a} mod {m} = {inv}")
    print(f"   Verification: ({a} * {inv}) mod {m} = {(a * inv) % m}")
    print()
    
    # Demo 3: Extended GCD
    print("3. Extended Euclidean Algorithm")
    a, b = 240, 46
    g, x, y = extended_gcd(a, b)
    print(f"   For a={a}, b={b}:")
    print(f"   gcd({a}, {b}) = {g}")
    print(f"   Bezout coefficients: x={x}, y={y}")
    print(f"   Verification: {a}*{x} + {b}*{y} = {a*x + b*y}")
    print()
    
    # Demo 4: Chinese Remainder Theorem
    print("4. Chinese Remainder Theorem")
    remainders = [2, 3, 1]
    moduli = [3, 4, 5]
    solution = chinese_remainder_theorem(remainders, moduli)
    print(f"   System of congruences:")
    for r, m in zip(remainders, moduli):
        print(f"     x ≡ {r} (mod {m})")
    print(f"   Solution: x = {solution}")
    print(f"   Verification:")
    for r, m in zip(remainders, moduli):
        print(f"     {solution} mod {m} = {solution % m} (expected {r})")
    print()
    
    # Demo 5: Primality testing
    print("5. Fermat Primality Test")
    test_numbers = [17, 221, 561, 1000000007]
    for n in test_numbers:
        is_prob_prime = is_prime_fermat(n, k=10)
        print(f"   {n}: {'probably prime' if is_prob_prime else 'composite'}")