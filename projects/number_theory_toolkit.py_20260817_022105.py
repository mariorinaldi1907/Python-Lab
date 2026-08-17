"""
Date: 2026-08-17
Implemented core number theory operations I got tired of Googling every time I need them for competitive programming or crypto stuff.
"""

#!/usr/bin/env python3
"""
Number Theory Toolkit
A collection of fundamental number theory algorithms that I use way too often.
Includes prime generation, modular arithmetic, and GCD operations.
"""

from typing import List, Tuple
import math


def sieve_of_eratosthenes(limit: int) -> List[int]:
    """
    Generate all primes up to and including limit using the Sieve of Eratosthenes.
    
    I'm using the classic algorithm here — mark multiples of each prime as composite.
    Returns a sorted list of primes, which is handy for iteration.
    
    Args:
        limit: Upper bound (inclusive) for prime generation
        
    Returns:
        List of all primes <= limit
    """
    if limit < 2:
        return []
    
    # Start with all numbers marked as potentially prime
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    
    # Only need to check up to sqrt(limit) because any composite number
    # must have a factor <= its square root
    for num in range(2, int(math.sqrt(limit)) + 1):
        if is_prime[num]:
            # Mark all multiples as composite, starting from num^2
            # (smaller multiples already marked by smaller primes)
            for multiple in range(num * num, limit + 1, num):
                is_prime[multiple] = False
    
    return [num for num in range(len(is_prime)) if is_prime[num]]


def mod_exp(base: int, exponent: int, modulus: int) -> int:
    """
    Compute (base^exponent) % modulus efficiently using binary exponentiation.
    
    This is crucial for cryptography and competitive programming. The naive approach
    of computing base^exponent then taking mod would overflow instantly for large values.
    Binary exponentiation keeps everything under control by doing mod at each step.
    
    Args:
        base: The base number
        exponent: The power to raise base to
        modulus: The modulus to apply
        
    Returns:
        (base^exponent) mod modulus
    """
    if modulus == 1:
        return 0
    
    result = 1
    base = base % modulus
    
    # Process exponent bit by bit from right to left
    while exponent > 0:
        # If current bit is 1, multiply current base into result
        if exponent & 1:
            result = (result * base) % modulus
        
        # Square the base for next bit position
        exponent >>= 1
        base = (base * base) % modulus
    
    return result


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """
    Extended Euclidean algorithm to find gcd and Bézout coefficients.
    
    Returns (gcd, x, y) such that ax + by = gcd(a, b).
    This is super useful for finding modular inverses and solving linear Diophantine equations.
    
    Args:
        a: First integer
        b: Second integer
        
    Returns:
        Tuple of (gcd, x, y) where ax + by = gcd
    """
    if b == 0:
        return (a, 1, 0)
    
    # Recursively find gcd and coefficients for b and a%b
    gcd, x1, y1 = extended_gcd(b, a % b)
    
    # Update coefficients based on the recurrence relation
    # From: b*x1 + (a%b)*y1 = gcd
    # To:   a*x + b*y = gcd
    x = y1
    y = x1 - (a // b) * y1
    
    return (gcd, x, y)


def mod_inverse(a: int, m: int) -> int:
    """
    Find the modular multiplicative inverse of a modulo m.
    
    Returns x such that (a * x) % m == 1.
    Only exists when gcd(a, m) == 1.
    
    Args:
        a: Number to find inverse of
        m: Modulus
        
    Returns:
        Modular inverse of a mod m
        
    Raises:
        ValueError: If inverse doesn't exist (gcd(a,m) != 1)
    """
    gcd, x, _ = extended_gcd(a, m)
    
    if gcd != 1:
        raise ValueError(f"Modular inverse doesn't exist: gcd({a}, {m}) = {gcd} != 1")
    
    # Make sure result is positive
    return x % m


def is_prime(n: int) -> bool:
    """
    Check if a number is prime using trial division.
    
    Not the fastest method for huge numbers, but good enough for most cases
    and doesn't require preprocessing like a sieve.
    
    Args:
        n: Number to check
        
    Returns:
        True if n is prime, False otherwise
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    # Only check odd divisors up to sqrt(n)
    for divisor in range(3, int(math.sqrt(n)) + 1, 2):
        if n % divisor == 0:
            return False
    
    return True


def prime_factorization(n: int) -> List[Tuple[int, int]]:
    """
    Find the prime factorization of n.
    
    Returns list of (prime, exponent) tuples representing the factorization.
    For example, 12 = 2^2 * 3^1 returns [(2, 2), (3, 1)].
    
    Args:
        n: Number to factorize (must be >= 2)
        
    Returns:
        List of (prime, exponent) tuples in ascending order
    """
    if n < 2:
        return []
    
    factors = []
    
    # Handle factor of 2 separately
    if n % 2 == 0:
        count = 0
        while n % 2 == 0:
            count += 1
            n //= 2
        factors.append((2, count))
    
    # Check odd factors up to sqrt(n)
    divisor = 3
    while divisor * divisor <= n:
        if n % divisor == 0:
            count = 0
            while n % divisor == 0:
                count += 1
                n //= divisor
            factors.append((divisor, count))
        divisor += 2
    
    # If n > 1 at this point, it's a prime factor
    if n > 1:
        factors.append((n, 1))
    
    return factors


if __name__ == "__main__":
    print("=== Number Theory Toolkit Demo ===\n")
    
    # Demo 1: Prime generation
    print("1. Generating primes up to 50:")
    primes = sieve_of_eratosthenes(50)
    print(f"   Found {len(primes)} primes: {primes}\n")
    
    # Demo 2: Modular exponentiation
    base, exp, mod = 3, 1000, 7
    result = mod_exp(base, exp, mod)
    print(f"2. Modular exponentiation:")
    print(f"   ({base}^{exp}) mod {mod} = {result}")
    print(f"   (useful for RSA and other crypto operations)\n")
    
    # Demo 3: GCD and Bézout coefficients
    a, b = 240, 46
    gcd, x, y = extended_gcd(a, b)
    print(f"3. Extended GCD:")
    print(f"   gcd({a}, {b}) = {gcd}")
    print(f"   Bézout coefficients: {a}*({x}) + {b}*({y}) = {gcd}")
    print(f"   Verification: {a*x + b*y} = {gcd}\n")
    
    # Demo 4: Modular inverse
    num, modulus = 17, 43
    inverse = mod_inverse(num, modulus)
    print(f"4. Modular inverse:")
    print(f"   Inverse of {num} mod {modulus} = {inverse}")
    print(f"   Verification: ({num} * {inverse}) mod {modulus} = {(num * inverse) % modulus}\n")
    
    # Demo 5: Prime checking
    test_nums = [17, 18, 97, 100]
    print("5. Prime checking:")
    for n in test_nums:
        print(f"   {n} is {'prime' if is_prime(n) else 'composite'}")
    print()
    
    # Demo 6: Prime factorization
    numbers = [60, 128, 97]
    print("6. Prime factorization:")
    for n in numbers:
        factors = prime_factorization(n)
        factor_str = " * ".join([f"{p}^{e}" if e > 1 else str(p) for p, e in factors])
        print(f"   {n} = {factor_str}")