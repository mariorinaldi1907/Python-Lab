"""
Date: 2026-06-01
Created a collection of number theory functions I keep needing for cryptography experiments and competitive programming — handles modular exponentiation, multiplicative inverse, and Chinese Remainder Theorem.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit
A collection of number theory utilities I find myself reaching for constantly.
Focused on modular arithmetic operations that come up in cryptography and competitive programming.
"""


def mod_exp(base, exponent, modulus):
    """
    Fast modular exponentiation using binary exponentiation.
    Computes (base^exponent) % modulus efficiently in O(log exponent) time.
    
    This is way faster than doing pow(base, exponent) % modulus for large numbers
    because we keep the intermediate results small by taking mod at each step.
    """
    if modulus == 1:
        return 0
    
    result = 1
    base = base % modulus
    
    while exponent > 0:
        # If exponent is odd, multiply base with result
        if exponent % 2 == 1:
            result = (result * base) % modulus
        
        # Square the base and halve the exponent
        exponent = exponent >> 1  # bit shift is faster than // 2
        base = (base * base) % modulus
    
    return result


def extended_gcd(a, b):
    """
    Extended Euclidean Algorithm.
    Returns (gcd, x, y) such that a*x + b*y = gcd(a, b).
    
    The coefficients x and y are what make this "extended" — we can use them
    to find modular inverses and solve linear Diophantine equations.
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
    Finds the modular multiplicative inverse of a modulo m.
    Returns x such that (a * x) % m == 1.
    
    Only exists if gcd(a, m) = 1. Raises ValueError if no inverse exists.
    This is crucial for modular division and RSA cryptography.
    """
    gcd, x, _ = extended_gcd(a, m)
    
    if gcd != 1:
        raise ValueError(f"Modular inverse does not exist: gcd({a}, {m}) = {gcd} != 1")
    
    # Make sure the result is positive
    return (x % m + m) % m


def chinese_remainder_theorem(remainders, moduli):
    """
    Solves a system of congruences using the Chinese Remainder Theorem.
    
    Given: x ≡ r1 (mod m1), x ≡ r2 (mod m2), ..., x ≡ rn (mod mn)
    Finds: x such that all congruences are satisfied
    
    Requires that all moduli are pairwise coprime (gcd(mi, mj) = 1 for i != j).
    Returns the smallest non-negative solution.
    """
    if len(remainders) != len(moduli):
        raise ValueError("Number of remainders must match number of moduli")
    
    # Product of all moduli
    total_product = 1
    for m in moduli:
        total_product *= m
    
    result = 0
    
    for remainder, modulus in zip(remainders, moduli):
        # Product of all moduli except the current one
        partial_product = total_product // modulus
        
        # Find the modular inverse of partial_product mod modulus
        inverse = mod_inverse(partial_product, modulus)
        
        # Add this term to the result
        result += remainder * partial_product * inverse
    
    return result % total_product


def is_prime(n, k=5):
    """
    Miller-Rabin primality test.
    Probabilistic algorithm to check if n is prime with k rounds of testing.
    
    Not 100% certain for composite numbers, but the probability of error is at most 4^(-k).
    With k=5, error probability is less than 0.1%. Good enough for most purposes.
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
    
    # Witnesses to test against
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


def factorial_mod(n, p):
    """
    Computes n! mod p efficiently.
    Useful when you need factorial under modular arithmetic but n is too large
    for regular factorial calculation.
    """
    if n >= p:
        return 0  # By Wilson's theorem, if n >= p then n! ≡ 0 (mod p)
    
    result = 1
    for i in range(1, n + 1):
        result = (result * i) % p
    
    return result


if __name__ == "__main__":
    print("=== Modular Arithmetic Toolkit Demo ===\n")
    
    # Fast modular exponentiation
    print("1. Fast Modular Exponentiation")
    base, exp, mod = 3, 100000, 1000000007
    result = mod_exp(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}")
    print(f"   (Computing this naively would overflow!)\n")
    
    # Modular inverse
    print("2. Modular Multiplicative Inverse")
    a, m = 7, 26
    inv = mod_inverse(a, m)
    print(f"   Inverse of {a} mod {m} = {inv}")
    print(f"   Verification: ({a} * {inv}) mod {m} = {(a * inv) % m}\n")
    
    # Chinese Remainder Theorem
    print("3. Chinese Remainder Theorem")
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    x = chinese_remainder_theorem(remainders, moduli)
    print(f"   Solving system:")
    for r, m in zip(remainders, moduli):
        print(f"     x ≡ {r} (mod {m})")
    print(f"   Solution: x = {x}")
    print(f"   Verification: x mod 3 = {x % 3}, x mod 5 = {x % 5}, x mod 7 = {x % 7}\n")
    
    # Primality testing
    print("4. Miller-Rabin Primality Test")
    test_numbers = [17, 1009, 1024, 15485863]
    for num in test_numbers:
        prime = is_prime(num)
        print(f"   {num} is {'prime' if prime else 'composite'}")
    print()
    
    # Factorial modulo
    print("5. Factorial Modulo Prime")
    n, p = 10, 13
    fact = factorial_mod(n, p)
    print(f"   {n}! mod {p} = {fact}")
    print(f"   (Regular {n}! = {3628800})")