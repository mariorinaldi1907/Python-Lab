"""
Date: 2026-07-06
Implemented a collection of number theory functions I kept needing for Project Euler problems — handles modular exponentiation, bezout coefficients, and CRT solving.
"""

"""
Modular Arithmetic Toolkit

A collection of number theory utilities I found myself rewriting
constantly for competitive programming and crypto puzzles.
Focuses on modular arithmetic operations that come up all the time.
"""


def gcd(a, b):
    """
    Compute the greatest common divisor using Euclid's algorithm.
    
    Classic recursive approach — keeps dividing until we hit zero.
    """
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a, b):
    """
    Extended Euclidean algorithm returning (gcd, x, y) where ax + by = gcd(a, b).
    
    This is the workhorse for modular inverses. We need the Bezout coefficients
    to figure out multiplicative inverses in modular arithmetic.
    """
    if b == 0:
        return a, 1, 0
    
    # Recursively solve for the smaller case
    gcd_val, x1, y1 = extended_gcd(b, a % b)
    
    # Back-substitute to get coefficients for the current level
    x = y1
    y = x1 - (a // b) * y1
    
    return gcd_val, x, y


def mod_inverse(a, m):
    """
    Find the modular multiplicative inverse of a modulo m.
    
    Returns x such that (a * x) % m == 1, or None if no inverse exists.
    An inverse only exists when gcd(a, m) == 1.
    """
    g, x, _ = extended_gcd(a, m)
    
    if g != 1:
        # No modular inverse exists
        return None
    
    # Make sure the result is positive
    return x % m


def mod_power(base, exp, mod):
    """
    Fast modular exponentiation using binary exponentiation.
    
    Computes (base^exp) % mod efficiently in O(log exp) time.
    This is way faster than doing base**exp % mod for large exponents.
    """
    result = 1
    base = base % mod
    
    while exp > 0:
        # If exp is odd, multiply base with result
        if exp % 2 == 1:
            result = (result * base) % mod
        
        # Now exp must be even — square the base and halve the exponent
        exp = exp >> 1  # Bit shift is slightly faster than exp // 2
        base = (base * base) % mod
    
    return result


def chinese_remainder_theorem(remainders, moduli):
    """
    Solve a system of congruences using the Chinese Remainder Theorem.
    
    Given x ≡ remainders[i] (mod moduli[i]) for all i,
    find the unique solution x modulo the product of all moduli.
    
    Assumes all moduli are pairwise coprime — doesn't check this!
    Returns None if the system has no solution.
    """
    if len(remainders) != len(moduli):
        return None
    
    # Product of all moduli
    total_mod = 1
    for m in moduli:
        total_mod *= m
    
    result = 0
    
    for remainder, mod in zip(remainders, moduli):
        # The product of all other moduli
        partial_product = total_mod // mod
        
        # Find the modular inverse of partial_product mod current modulus
        inverse = mod_inverse(partial_product, mod)
        
        if inverse is None:
            # System has no solution (moduli not coprime)
            return None
        
        # Add this term to the result
        result += remainder * partial_product * inverse
    
    return result % total_mod


def is_prime(n, k=5):
    """
    Miller-Rabin primality test — probabilistic but very reliable.
    
    Tests n for primality with k rounds. Higher k means more accuracy.
    For k=5, the probability of a false positive is less than (1/4)^5.
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    # Write n-1 as d * 2^r
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    # Witness loop — test with a few random bases
    import random
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = mod_power(a, d, n)
        
        if x == 1 or x == n - 1:
            continue
        
        for _ in range(r - 1):
            x = mod_power(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    
    return True


if __name__ == "__main__":
    print("=== Modular Arithmetic Toolkit Demo ===\n")
    
    # Test GCD and Extended GCD
    print("1. GCD and Extended GCD")
    a, b = 252, 105
    g = gcd(a, b)
    g_ext, x, y = extended_gcd(a, b)
    print(f"   gcd({a}, {b}) = {g}")
    print(f"   Extended: {a}*{x} + {b}*{y} = {g_ext}")
    print(f"   Verification: {a*x + b*y} = {g_ext}\n")
    
    # Test Modular Inverse
    print("2. Modular Inverse")
    a, m = 17, 43
    inv = mod_inverse(a, m)
    print(f"   Inverse of {a} mod {m} = {inv}")
    print(f"   Verification: ({a} * {inv}) % {m} = {(a * inv) % m}\n")
    
    # Test Fast Modular Exponentiation
    print("3. Fast Modular Exponentiation")
    base, exp, mod = 3, 1000000, 1000000007
    result = mod_power(base, exp, mod)
    print(f"   {base}^{exp} mod {mod} = {result}\n")
    
    # Test Chinese Remainder Theorem
    print("4. Chinese Remainder Theorem")
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    solution = chinese_remainder_theorem(remainders, moduli)
    print(f"   System: x ≡ {remainders[0]} (mod {moduli[0]})")
    for i in range(1, len(remainders)):
        print(f"           x ≡ {remainders[i]} (mod {moduli[i]})")
    print(f"   Solution: x = {solution}")
    print(f"   Verification: {solution} % {moduli[0]} = {solution % moduli[0]}, ", end="")
    print(f"{solution} % {moduli[1]} = {solution % moduli[1]}, ", end="")
    print(f"{solution} % {moduli[2]} = {solution % moduli[2]}\n")
    
    # Test Primality Testing
    print("5. Miller-Rabin Primality Test")
    test_numbers = [17, 91, 104729, 104730]
    for num in test_numbers:
        prime_status = "prime" if is_prime(num) else "composite"
        print(f"   {num} is {prime_status}")