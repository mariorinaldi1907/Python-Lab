"""
Date: 2026-07-05
Built a number theory toolkit centered around prime generation and factorization because I got tired of rewriting this logic every time I need it.
"""

#!/usr/bin/env python3
"""
Prime number utilities using Sieve of Eratosthenes and related algorithms.

This module provides efficient prime generation, primality testing,
and prime factorization. I built this because I was solving Project Euler
problems and kept needing these primitives over and over.
"""

import random
from typing import List, Dict, Tuple


def sieve_of_eratosthenes(limit: int) -> List[int]:
    """
    Generate all primes up to limit using the Sieve of Eratosthenes.
    
    Args:
        limit: Upper bound (inclusive) for prime generation
        
    Returns:
        List of all primes <= limit
        
    Time complexity: O(n log log n)
    Space complexity: O(n)
    """
    if limit < 2:
        return []
    
    # I'm using a boolean array where True means "is prime"
    # Starting with the assumption that all numbers are prime
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    
    # Only need to check up to sqrt(limit) because any composite
    # number must have a factor <= its square root
    p = 2
    while p * p <= limit:
        if is_prime[p]:
            # Mark all multiples of p as composite
            # Start at p*p because smaller multiples were already marked
            for multiple in range(p * p, limit + 1, p):
                is_prime[multiple] = False
        p += 1
    
    # Collect all indices that remained True
    return [num for num in range(limit + 1) if is_prime[num]]


def prime_factorization(n: int) -> Dict[int, int]:
    """
    Find the prime factorization of n.
    
    Args:
        n: Integer to factorize (must be >= 2)
        
    Returns:
        Dictionary mapping prime factors to their exponents
        
    Example:
        prime_factorization(60) returns {2: 2, 3: 1, 5: 1}
        because 60 = 2^2 * 3^1 * 5^1
    """
    if n < 2:
        return {}
    
    factors = {}
    
    # Handle factors of 2 separately to avoid checking even numbers later
    while n % 2 == 0:
        factors[2] = factors.get(2, 0) + 1
        n //= 2
    
    # Now n is odd, so we can skip even numbers
    divisor = 3
    while divisor * divisor <= n:
        while n % divisor == 0:
            factors[divisor] = factors.get(divisor, 0) + 1
            n //= divisor
        divisor += 2
    
    # If n > 1 at this point, it's a prime factor itself
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    
    return factors


def miller_rabin_test(n: int, k: int = 5) -> bool:
    """
    Probabilistic primality test using Miller-Rabin algorithm.
    
    This is useful for testing very large numbers where trial division
    would be too slow. The probability of a false positive is at most 4^(-k).
    
    Args:
        n: Number to test for primality
        k: Number of rounds (more rounds = higher confidence)
        
    Returns:
        False if definitely composite, True if probably prime
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
    
    # Witness loop - run k rounds of testing
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)  # a^d mod n (built-in fast modular exponentiation)
        
        if x == 1 or x == n - 1:
            continue
        
        # Square x repeatedly r-1 times
        composite = True
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                composite = False
                break
        
        if composite:
            return False
    
    return True


def get_divisors(n: int) -> List[int]:
    """
    Find all divisors of n using its prime factorization.
    
    This is more efficient than trial division for finding all divisors
    because we can construct them from the prime factors.
    
    Args:
        n: Integer to find divisors for
        
    Returns:
        Sorted list of all divisors of n
    """
    if n < 1:
        return []
    
    factors = prime_factorization(n)
    divisors = [1]
    
    # For each prime factor p^e, multiply existing divisors by p^0, p^1, ..., p^e
    for prime, exponent in factors.items():
        new_divisors = []
        power = 1
        for _ in range(exponent + 1):
            for div in divisors:
                new_divisors.append(div * power)
            power *= prime
        divisors = new_divisors
    
    return sorted(divisors)


if __name__ == "__main__":
    print("=== Prime Number Utilities Demo ===\n")
    
    # Demo 1: Generate primes using sieve
    print("1. Generating primes up to 100:")
    primes = sieve_of_eratosthenes(100)
    print(f"   Found {len(primes)} primes: {primes}\n")
    
    # Demo 2: Prime factorization
    print("2. Prime factorization examples:")
    test_numbers = [60, 128, 315, 1001, 2023]
    for num in test_numbers:
        factors = prime_factorization(num)
        # Reconstruct the factorization string
        factor_str = " × ".join(
            f"{p}^{e}" if e > 1 else str(p) 
            for p, e in sorted(factors.items())
        )
        print(f"   {num} = {factor_str}")
    print()
    
    # Demo 3: Miller-Rabin primality test
    print("3. Testing large numbers for primality (Miller-Rabin):")
    large_numbers = [
        (15485863, True),   # Actually prime
        (15485864, False),  # Even, so composite
        (179424691, True),  # Large prime
        (179424692, False), # Composite
    ]
    for num, expected in large_numbers:
        result = miller_rabin_test(num, k=10)
        status = "PRIME" if result else "COMPOSITE"
        check = "✓" if result == expected else "✗"
        print(f"   {num}: {status} {check}")
    print()
    
    # Demo 4: Find all divisors
    print("4. Finding all divisors:")
    for num in [24, 100, 144]:
        divisors = get_divisors(num)
        print(f"   {num}: {divisors} (count: {len(divisors)})")
```