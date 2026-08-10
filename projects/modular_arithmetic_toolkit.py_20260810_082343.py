"""
Date: 2026-08-10
Implemented common number theory operations I kept rewriting for competitive programming problems — modular exponentiation, inverse via extended Euclidean, and Chinese Remainder Theorem solver.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit

A collection of number theory utilities I found myself needing
over and over for various math problems and competitive programming.
Focuses on modular arithmetic operations that are fast and correct.
"""


def gcd(a, b):
    """
    Compute the greatest common divisor using Euclidean algorithm.
    
    Args:
        a: First integer
        b: Second integer
    
    Returns:
        GCD of a and b
    """
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a, b):
    """
    Extended Euclidean algorithm.
    
    Returns (gcd, x, y) such that a*x + b*y = gcd(a, b).
    This is crucial for computing modular inverses.
    
    Args:
        a: First integer
        b: Second integer
    
    Returns:
        Tuple (gcd, x, y) where gcd is GCD and x, y are Bézout coefficients
    """
    if b == 0:
        return a, 1, 0
    
    gcd_val, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    
    return gcd_val, x, y


def mod_inverse(a, m):
    """
    Compute modular inverse of a modulo m.
    
    The modular inverse exists only if gcd(a, m) = 1.
    Uses extended Euclidean algorithm rather than Fermat's little theorem
    because it works for non-prime moduli too.
    
    Args:
        a: Number to invert
        m: Modulus
    
    Returns:
        Modular inverse of a mod m
    
    Raises:
        ValueError: If inverse doesn't exist (gcd(a,m) != 1)
    """
    g, x, _ = extended_gcd(a % m, m)
    
    if g != 1:
        raise ValueError(f"Modular inverse doesn't exist: gcd({a}, {m}) = {g}")
    
    return x % m


def fast_power(base, exp, mod=None):
    """
    Fast exponentiation using binary exponentiation (exponentiation by squaring).
    
    Computes base^exp in O(log exp) time instead of O(exp).
    If mod is provided, computes (base^exp) % mod efficiently.
    
    Args:
        base: Base number
        exp: Exponent (non-negative integer)
        mod: Optional modulus for modular exponentiation
    
    Returns:
        base^exp, or (base^exp) % mod if mod is provided
    """
    if exp < 0:
        raise ValueError("Exponent must be non-negative")
    
    result = 1
    base = base if mod is None else base % mod
    
    while exp > 0:
        # If exp is odd, multiply current base into result
        if exp % 2 == 1:
            result = result * base if mod is None else (result * base) % mod
        
        # Square the base and halve the exponent
        exp //= 2
        base = base * base if mod is None else (base * base) % mod
    
    return result


def chinese_remainder_theorem(remainders, moduli):
    """
    Solve system of congruences using Chinese Remainder Theorem.
    
    Given: x ≡ r1 (mod m1), x ≡ r2 (mod m2), ..., x ≡ rn (mod mn)
    Find: x such that all congruences hold
    
    Requires moduli to be pairwise coprime.
    
    Args:
        remainders: List of remainders [r1, r2, ..., rn]
        moduli: List of moduli [m1, m2, ..., mn]
    
    Returns:
        Solution x (smallest non-negative integer)
    
    Raises:
        ValueError: If moduli aren't pairwise coprime
    """
    if len(remainders) != len(moduli):
        raise ValueError("Number of remainders must match number of moduli")
    
    # Check pairwise coprimality
    for i in range(len(moduli)):
        for j in range(i + 1, len(moduli)):
            if gcd(moduli[i], moduli[j]) != 1:
                raise ValueError(f"Moduli {moduli[i]} and {moduli[j]} are not coprime")
    
    # Product of all moduli
    M = 1
    for m in moduli:
        M *= m
    
    # Apply CRT formula
    x = 0
    for r, m in zip(remainders, moduli):
        M_i = M // m  # Product of all moduli except m
        y_i = mod_inverse(M_i, m)  # Modular inverse of M_i mod m
        x += r * M_i * y_i
    
    return x % M


def is_prime_simple(n):
    """
    Simple primality test for demonstration purposes.
    
    This is not the most efficient algorithm, but it's clear and works
    fine for smallish numbers. For serious use, I'd implement Miller-Rabin.
    
    Args:
        n: Integer to test
    
    Returns:
        True if n is prime, False otherwise
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    # Check odd divisors up to sqrt(n)
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    
    return True


if __name__ == "__main__":
    print("=== Modular Arithmetic Toolkit Demo ===\n")
    
    # Demo 1: Fast exponentiation
    print("1. Fast Exponentiation")
    base, exp, mod = 2, 1000, 10**9 + 7
    result = fast_power(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}")
    print(f"   (Computing this naively would take forever!)\n")
    
    # Demo 2: Modular inverse
    print("2. Modular Inverse")
    a, m = 42, 97
    inv = mod_inverse(a, m)
    print(f"   Inverse of {a} mod {m} = {inv}")
    print(f"   Verification: ({a} * {inv}) mod {m} = {(a * inv) % m}\n")
    
    # Demo 3: Chinese Remainder Theorem
    print("3. Chinese Remainder Theorem")
    print("   Solving system:")
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    for r, m in zip(remainders, moduli):
        print(f"     x ≡ {r} (mod {m})")
    
    solution = chinese_remainder_theorem(remainders, moduli)
    print(f"   Solution: x = {solution}")
    print("   Verification:")
    for r, m in zip(remainders, moduli):
        print(f"     {solution} mod {m} = {solution % m} (expected {r})")
    print()
    
    # Demo 4: Extended GCD
    print("4. Extended Euclidean Algorithm")
    a, b = 240, 46
    g, x, y = extended_gcd(a, b)
    print(f"   For a={a}, b={b}:")
    print(f"   GCD = {g}")
    print(f"   Bézout coefficients: x={x}, y={y}")
    print(f"   Verification: {a}*{x} + {b}*{y} = {a*x + b*y}\n")
    
    # Demo 5: Primality testing
    print("5. Primality Testing")
    test_numbers = [17, 91, 97, 1000000007]
    for n in test_numbers:
        result = "prime" if is_prime_simple(n) else "composite"
        print(f"   {n:>10} is {result}")