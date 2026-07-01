"""
Date: 2026-07-01
Created a collection of modular arithmetic utilities including fast exponentiation, modular inverse, and Chinese Remainder Theorem solver since I keep needing these for project euler problems.
"""

"""
Modular Arithmetic Toolkit

A collection of number theory utilities I keep rewriting for different projects.
Includes fast modular exponentiation, extended GCD, modular inverse, and a
Chinese Remainder Theorem solver.
"""


def mod_exp(base, exp, mod):
    """
    Fast modular exponentiation using binary exponentiation.
    
    Computes (base^exp) % mod efficiently in O(log exp) time.
    This is way faster than doing pow(base, exp) % mod for large numbers
    because we keep intermediate results small.
    
    Args:
        base: The base number
        exp: The exponent (must be non-negative)
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
        exp = exp >> 1  # bit shift is faster than division
        base = (base * base) % mod
    
    return result


def extended_gcd(a, b):
    """
    Extended Euclidean Algorithm.
    
    Finds gcd(a, b) and also the coefficients x, y such that:
    a*x + b*y = gcd(a, b)
    
    This is essential for computing modular inverses and solving
    linear Diophantine equations.
    
    Args:
        a, b: Two integers
    
    Returns:
        Tuple (gcd, x, y) where gcd = a*x + b*y
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
    Computes the modular multiplicative inverse of a modulo m.
    
    Returns x such that (a * x) % m == 1.
    Only exists when gcd(a, m) = 1.
    
    Args:
        a: The number to invert
        m: The modulus
    
    Returns:
        The modular inverse of a mod m
    
    Raises:
        ValueError: If the inverse doesn't exist (when gcd(a, m) != 1)
    """
    gcd, x, _ = extended_gcd(a % m, m)
    
    if gcd != 1:
        raise ValueError(f"Modular inverse doesn't exist: gcd({a}, {m}) = {gcd}")
    
    return (x % m + m) % m


def chinese_remainder_theorem(remainders, moduli):
    """
    Solves a system of congruences using the Chinese Remainder Theorem.
    
    Given:
        x ≡ r1 (mod m1)
        x ≡ r2 (mod m2)
        ...
        x ≡ rn (mod mn)
    
    Finds the smallest non-negative x that satisfies all congruences.
    The moduli must be pairwise coprime (gcd(mi, mj) = 1 for i != j).
    
    Args:
        remainders: List of remainders [r1, r2, ..., rn]
        moduli: List of moduli [m1, m2, ..., mn]
    
    Returns:
        The solution x (smallest non-negative integer)
    
    Raises:
        ValueError: If moduli aren't pairwise coprime or lists have different lengths
    """
    if len(remainders) != len(moduli):
        raise ValueError("remainders and moduli must have the same length")
    
    # Calculate the product of all moduli
    M = 1
    for m in moduli:
        M *= m
    
    result = 0
    
    for r, m in zip(remainders, moduli):
        # M_i is the product of all moduli except m
        M_i = M // m
        
        # Find the modular inverse of M_i mod m
        # This is the key step that requires moduli to be coprime
        try:
            inv = mod_inverse(M_i, m)
        except ValueError:
            raise ValueError(f"Moduli are not pairwise coprime")
        
        # Add this term to the result
        result += r * M_i * inv
    
    return result % M


def is_prime_fermat(n, k=5):
    """
    Probabilistic primality test using Fermat's Little Theorem.
    
    Tests if n is probably prime by checking if a^(n-1) ≡ 1 (mod n)
    for k random values of a. Not perfect (fails for Carmichael numbers)
    but good enough for most purposes.
    
    Args:
        n: Number to test for primality
        k: Number of rounds (higher = more accurate)
    
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
    
    # Test with k random bases
    for _ in range(k):
        a = random.randint(2, n - 2)
        if mod_exp(a, n - 1, n) != 1:
            return False
    
    return True


if __name__ == "__main__":
    print("=== Modular Arithmetic Toolkit Demo ===\n")
    
    # Demo 1: Fast modular exponentiation
    print("1. Fast Modular Exponentiation")
    base, exp, mod = 3, 1000000, 1000000007
    result = mod_exp(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}")
    print()
    
    # Demo 2: Extended GCD
    print("2. Extended GCD")
    a, b = 240, 46
    gcd, x, y = extended_gcd(a, b)
    print(f"   gcd({a}, {b}) = {gcd}")
    print(f"   Coefficients: {a}*{x} + {b}*{y} = {gcd}")
    print(f"   Verification: {a*x + b*y} = {gcd}")
    print()
    
    # Demo 3: Modular inverse
    print("3. Modular Inverse")
    a, m = 7, 26
    inv = mod_inverse(a, m)
    print(f"   Inverse of {a} mod {m} = {inv}")
    print(f"   Verification: ({a} * {inv}) mod {m} = {(a * inv) % m}")
    print()
    
    # Demo 4: Chinese Remainder Theorem
    print("4. Chinese Remainder Theorem")
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    solution = chinese_remainder_theorem(remainders, moduli)
    print(f"   System of congruences:")
    for r, m in zip(remainders, moduli):
        print(f"      x ≡ {r} (mod {m})")
    print(f"   Solution: x = {solution}")
    print(f"   Verification:")
    for r, m in zip(remainders, moduli):
        print(f"      {solution} mod {m} = {solution % m} (should be {r})")
    print()
    
    # Demo 5: Primality testing
    print("5. Fermat Primality Test")
    test_numbers = [17, 561, 1009, 1024]
    for n in test_numbers:
        is_prob_prime = is_prime_fermat(n, k=10)
        print(f"   {n} is {'probably prime' if is_prob_prime else 'composite'}")