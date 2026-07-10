"""
Date: 2026-07-10
Created a collection of modular arithmetic functions I kept rewriting for project euler problems, including Chinese Remainder Theorem and extended Euclidean algorithm.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit
A collection of number theory utilities I got tired of rewriting.
Focuses on modular arithmetic operations that come up in competitive programming
and cryptography exercises.
"""


def extended_gcd(a, b):
    """
    Extended Euclidean Algorithm - finds gcd(a, b) and coefficients x, y
    such that ax + by = gcd(a, b).
    
    This is the foundation for a lot of modular arithmetic operations.
    Returns: (gcd, x, y)
    """
    if b == 0:
        return a, 1, 0
    
    gcd, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    
    return gcd, x, y


def mod_inverse(a, m):
    """
    Compute modular multiplicative inverse of a modulo m.
    Returns x such that (a * x) % m == 1.
    
    Only exists when gcd(a, m) = 1. Raises ValueError otherwise.
    I use this constantly for division in modular arithmetic.
    """
    gcd, x, _ = extended_gcd(a, m)
    
    if gcd != 1:
        raise ValueError(f"Modular inverse doesn't exist: gcd({a}, {m}) = {gcd}")
    
    return x % m


def fast_mod_exp(base, exp, mod):
    """
    Fast modular exponentiation using binary exponentiation.
    Computes (base^exp) % mod efficiently.
    
    Way faster than pow() for huge numbers, though Python's built-in pow(base, exp, mod)
    actually does this already. I wrote it to understand the algorithm better.
    """
    result = 1
    base = base % mod
    
    while exp > 0:
        # If exp is odd, multiply base with result
        if exp % 2 == 1:
            result = (result * base) % mod
        
        # Square the base and halve the exponent
        exp = exp >> 1  # bit shift is faster than // 2
        base = (base * base) % mod
    
    return result


def chinese_remainder_theorem(remainders, moduli):
    """
    Solve system of congruences using Chinese Remainder Theorem.
    
    Given: x ≡ remainders[i] (mod moduli[i]) for all i
    Find: x (the unique solution modulo product of all moduli)
    
    Assumes all moduli are pairwise coprime. This comes up surprisingly often
    in encryption and some combinatorics problems.
    """
    if len(remainders) != len(moduli):
        raise ValueError("Need same number of remainders and moduli")
    
    # Product of all moduli
    M = 1
    for m in moduli:
        M *= m
    
    result = 0
    
    for i in range(len(moduli)):
        # M_i is the product of all moduli except moduli[i]
        Mi = M // moduli[i]
        
        # Find modular inverse of M_i mod moduli[i]
        yi = mod_inverse(Mi, moduli[i])
        
        # Add this term to result
        result += remainders[i] * Mi * yi
    
    return result % M


def euler_totient(n):
    """
    Compute Euler's totient function φ(n).
    Returns count of positive integers <= n that are coprime to n.
    
    Using the formula based on prime factorization:
    φ(n) = n * ∏(1 - 1/p) for all prime factors p of n
    """
    result = n
    p = 2
    
    # Check all potential prime factors
    while p * p <= n:
        if n % p == 0:
            # Remove all factors of p
            while n % p == 0:
                n //= p
            # Apply formula: multiply by (1 - 1/p) = (p-1)/p
            result -= result // p
        p += 1
    
    # If n > 1 after above, it's a prime factor
    if n > 1:
        result -= result // n
    
    return result


def is_prime_miller_rabin(n, k=5):
    """
    Miller-Rabin primality test - probabilistic but super fast.
    
    With k rounds, probability of false positive is at most 4^(-k).
    So k=5 gives us < 0.1% false positive rate, which is fine for most uses.
    
    I prefer this over trial division for anything above ~10^6.
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


if __name__ == "__main__":
    print("=== Modular Arithmetic Toolkit Demo ===\n")
    
    # Demo 1: Extended GCD
    print("1. Extended GCD")
    a, b = 240, 46
    gcd, x, y = extended_gcd(a, b)
    print(f"   gcd({a}, {b}) = {gcd}")
    print(f"   {a}*{x} + {b}*{y} = {a*x + b*y} ✓\n")
    
    # Demo 2: Modular Inverse
    print("2. Modular Inverse")
    a, m = 3, 11
    inv = mod_inverse(a, m)
    print(f"   Inverse of {a} mod {m} = {inv}")
    print(f"   Verification: ({a} * {inv}) mod {m} = {(a * inv) % m} ✓\n")
    
    # Demo 3: Fast Modular Exponentiation
    print("3. Fast Modular Exponentiation")
    base, exp, mod = 2, 1000, 1000000007
    result = fast_mod_exp(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}")
    print(f"   (Compare to built-in pow: {pow(base, exp, mod)}) ✓\n")
    
    # Demo 4: Chinese Remainder Theorem
    print("4. Chinese Remainder Theorem")
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    x = chinese_remainder_theorem(remainders, moduli)
    print(f"   Solving system:")
    for r, m in zip(remainders, moduli):
        print(f"     x ≡ {r} (mod {m})")
    print(f"   Solution: x = {x}")
    print(f"   Verification: ", end="")
    for r, m in zip(remainders, moduli):
        print(f"{x % m}≡{r}(mod {m}) ", end="")
    print("✓\n")
    
    # Demo 5: Euler's Totient Function
    print("5. Euler's Totient Function")
    n = 36
    phi = euler_totient(n)
    print(f"   φ({n}) = {phi}")
    print(f"   (Numbers coprime to {n}: ", end="")
    coprimes = [i for i in range(1, n+1) if extended_gcd(i, n)[0] == 1]
    print(f"{len(coprimes)} total) ✓\n")
    
    # Demo 6: Miller-Rabin Primality Test
    print("6. Miller-Rabin Primality Test")
    test_numbers = [17, 100, 1000000007, 1000000009]
    for num in test_numbers:
        is_p = is_prime_miller_rabin(num)
        print(f"   {num}: {'PRIME' if is_p else 'COMPOSITE'}")
    print()