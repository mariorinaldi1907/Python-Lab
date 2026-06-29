"""
Date: 2026-06-29
Built a modular arithmetic library because I got tired of reimplementing modpow and CRT every time I solve number theory problems.
"""

#!/usr/bin/env python3
"""
Modular Arithmetic Toolkit
A collection of number theory utilities I use frequently.
Includes modular exponentiation, extended Euclidean algorithm, and Chinese Remainder Theorem solver.
"""


def mod_exp(base, exp, mod):
    """
    Fast modular exponentiation using binary exponentiation.
    Computes (base^exp) % mod efficiently in O(log exp) time.
    
    This is way faster than doing pow(base, exp) % mod for large numbers
    because we keep the intermediate results small by taking mod at each step.
    """
    if mod == 1:
        return 0
    
    result = 1
    base = base % mod
    
    while exp > 0:
        # If exp is odd, multiply base with result
        if exp % 2 == 1:
            result = (result * base) % mod
        
        # Square the base and halve the exponent
        exp = exp >> 1  # Bit shift is faster than division by 2
        base = (base * base) % mod
    
    return result


def extended_gcd(a, b):
    """
    Extended Euclidean Algorithm.
    Returns (gcd, x, y) such that a*x + b*y = gcd(a, b).
    
    This is super useful for finding modular inverses and solving linear Diophantine equations.
    The algorithm works by keeping track of the coefficients while doing regular GCD.
    """
    if a == 0:
        return b, 0, 1
    
    gcd, x1, y1 = extended_gcd(b % a, a)
    
    # Update x and y using results from recursive call
    x = y1 - (b // a) * x1
    y = x1
    
    return gcd, x, y


def mod_inverse(a, m):
    """
    Find modular multiplicative inverse of a under modulo m.
    Returns x such that (a * x) % m = 1.
    
    Only exists if gcd(a, m) = 1. I use this constantly for modular division.
    """
    gcd, x, _ = extended_gcd(a, m)
    
    if gcd != 1:
        raise ValueError(f"Modular inverse doesn't exist: gcd({a}, {m}) = {gcd} != 1")
    
    # x might be negative, so we make sure it's in range [0, m)
    return (x % m + m) % m


def chinese_remainder_theorem(remainders, moduli):
    """
    Solve system of congruences using Chinese Remainder Theorem.
    Given x ≡ remainders[i] (mod moduli[i]), find x.
    
    This assumes all moduli are pairwise coprime — I should add a check for that
    but usually when I use this I've already verified it.
    
    Returns the unique solution modulo the product of all moduli.
    """
    if len(remainders) != len(moduli):
        raise ValueError("Number of remainders must match number of moduli")
    
    # Total modulus is the product of all individual moduli
    total_mod = 1
    for m in moduli:
        total_mod *= m
    
    result = 0
    
    for i, (remainder, modulus) in enumerate(zip(remainders, moduli)):
        # M_i is the product of all moduli except the current one
        M_i = total_mod // modulus
        
        # Find the modular inverse of M_i under modulus
        inv = mod_inverse(M_i, modulus)
        
        # Add this term to the result
        result += remainder * M_i * inv
    
    return result % total_mod


def is_prime_fermat(n, k=5):
    """
    Probabilistic primality test using Fermat's Little Theorem.
    Tests k random witnesses — if any fails, n is definitely composite.
    
    Not perfect (Carmichael numbers can fool it) but good enough for most cases.
    For production code I'd use Miller-Rabin instead.
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    import random
    
    for _ in range(k):
        a = random.randint(2, n - 1)
        # Check if a^(n-1) ≡ 1 (mod n)
        if mod_exp(a, n - 1, n) != 1:
            return False
    
    return True


def solve_linear_congruence(a, b, m):
    """
    Solve linear congruence: a*x ≡ b (mod m).
    Returns all solutions in range [0, m).
    
    There can be multiple solutions if gcd(a,m) > 1.
    """
    gcd, x0, _ = extended_gcd(a, m)
    
    if b % gcd != 0:
        # No solution exists
        return []
    
    # Reduce to simpler congruence
    a_reduced = a // gcd
    b_reduced = b // gcd
    m_reduced = m // gcd
    
    # Find one solution
    inv = mod_inverse(a_reduced, m_reduced)
    x = (inv * b_reduced) % m_reduced
    
    # Generate all solutions (there are gcd of them)
    solutions = []
    for i in range(gcd):
        solutions.append((x + i * m_reduced) % m)
    
    return sorted(solutions)


if __name__ == "__main__":
    print("=== Modular Arithmetic Toolkit Demo ===\n")
    
    # Demo 1: Fast modular exponentiation
    print("1. Fast Modular Exponentiation")
    base, exp, mod = 3, 100000, 1000000007
    result = mod_exp(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}")
    print(f"   (Computing this directly would overflow!)\n")
    
    # Demo 2: Modular inverse
    print("2. Modular Inverse")
    a, m = 17, 43
    inv = mod_inverse(a, m)
    print(f"   Inverse of {a} mod {m} = {inv}")
    print(f"   Verification: ({a} * {inv}) mod {m} = {(a * inv) % m}\n")
    
    # Demo 3: Chinese Remainder Theorem
    print("3. Chinese Remainder Theorem")
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    solution = chinese_remainder_theorem(remainders, moduli)
    print(f"   Solving system:")
    for r, m in zip(remainders, moduli):
        print(f"   x ≡ {r} (mod {m})")
    print(f"   Solution: x = {solution}")
    print(f"   Verification: {solution} mod 3 = {solution % 3}, mod 5 = {solution % 5}, mod 7 = {solution % 7}\n")
    
    # Demo 4: Primality testing
    print("4. Fermat Primality Test")
    test_numbers = [97, 100, 561, 1009]  # 561 is a Carmichael number!
    for n in test_numbers:
        is_prob_prime = is_prime_fermat(n, k=10)
        print(f"   {n}: {'probably prime' if is_prob_prime else 'composite'}")
    print()
    
    # Demo 5: Linear congruence
    print("5. Solving Linear Congruence")
    a, b, m = 6, 9, 15
    solutions = solve_linear_congruence(a, b, m)
    print(f"   Solving {a}*x ≡ {b} (mod {m})")
    print(f"   Solutions: {solutions}")
    if solutions:
        print(f"   Verification for x={solutions[0]}: ({a}*{solutions[0]}) mod {m} = {(a*solutions[0]) % m}")