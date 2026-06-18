"""
Date: 2026-06-18
Built a prime number toolkit with both basic and segmented sieves because I got tired of writing the same logic in CTF challenges.
"""

#!/usr/bin/env python3
"""
Prime number utilities using the Sieve of Eratosthenes.
Includes both basic and segmented sieves, plus prime factorization.
"""

import math


def sieve_of_eratosthenes(limit):
    """
    Generate all primes up to `limit` using the classic sieve algorithm.
    
    Args:
        limit: Upper bound (inclusive) for prime search
        
    Returns:
        List of all primes <= limit
    
    Time: O(n log log n), Space: O(n)
    """
    if limit < 2:
        return []
    
    # Start assuming all numbers are prime
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    
    # Only need to check up to sqrt(limit) because any composite number
    # must have at least one factor <= its square root
    for i in range(2, int(math.sqrt(limit)) + 1):
        if is_prime[i]:
            # Mark all multiples of i as composite
            # Start at i*i because smaller multiples were already marked
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    
    return [num for num in range(limit + 1) if is_prime[num]]


def segmented_sieve(low, high):
    """
    Find all primes in range [low, high] using segmented sieve.
    
    This is way more memory-efficient for large ranges since we only need
    to allocate space for the segment, not all numbers from 0 to high.
    
    Args:
        low: Lower bound (inclusive)
        high: Upper bound (inclusive)
        
    Returns:
        List of primes in [low, high]
    """
    if high < 2:
        return []
    
    # Need primes up to sqrt(high) to mark composites in our segment
    limit = int(math.sqrt(high)) + 1
    base_primes = sieve_of_eratosthenes(limit)
    
    # Adjust low to at least 2
    low = max(low, 2)
    
    # Create boolean array for the segment [low, high]
    segment_size = high - low + 1
    is_prime = [True] * segment_size
    
    for prime in base_primes:
        # Find the first multiple of prime in [low, high]
        # This is either low rounded up to next multiple, or prime^2
        start = max(prime * prime, ((low + prime - 1) // prime) * prime)
        
        # Mark all multiples in the segment as composite
        for j in range(start, high + 1, prime):
            is_prime[j - low] = False
    
    # Handle edge case: if low <= 2 <= high, make sure 2 is included
    primes = []
    for i in range(segment_size):
        if is_prime[i] and (low + i >= 2):
            primes.append(low + i)
    
    return primes


def prime_factorization(n):
    """
    Compute the prime factorization of n.
    
    Returns a dictionary mapping prime factors to their exponents.
    For example: 60 -> {2: 2, 3: 1, 5: 1} because 60 = 2^2 * 3 * 5
    
    Args:
        n: Positive integer to factorize
        
    Returns:
        Dict mapping prime -> exponent
    """
    if n < 2:
        return {}
    
    factors = {}
    
    # Check for factor of 2 separately to optimize the loop
    # (so we can skip even numbers afterwards)
    while n % 2 == 0:
        factors[2] = factors.get(2, 0) + 1
        n //= 2
    
    # Now n is odd, so we only need to check odd divisors
    divisor = 3
    while divisor * divisor <= n:
        while n % divisor == 0:
            factors[divisor] = factors.get(divisor, 0) + 1
            n //= divisor
        divisor += 2
    
    # If n > 1 at this point, it's a prime factor itself
    if n > 1:
        factors[n] = 1
    
    return factors


def is_prime(n):
    """
    Simple primality test. Not the fastest but works fine for small numbers.
    
    Args:
        n: Number to test
        
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
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


if __name__ == "__main__":
    print("=== Prime Sieve Toolkit Demo ===\n")
    
    # Demo 1: Basic sieve for small range
    print("1. Basic Sieve of Eratosthenes (primes up to 50):")
    primes_50 = sieve_of_eratosthenes(50)
    print(f"   Found {len(primes_50)} primes: {primes_50}\n")
    
    # Demo 2: Segmented sieve for large range
    print("2. Segmented Sieve (primes between 1,000,000 and 1,000,100):")
    large_primes = segmented_sieve(1_000_000, 1_000_100)
    print(f"   Found {len(large_primes)} primes in this range:")
    print(f"   {large_primes}\n")
    
    # Demo 3: Prime factorization
    test_numbers = [60, 2024, 1024, 97]
    print("3. Prime Factorization:")
    for num in test_numbers:
        factors = prime_factorization(num)
        if factors:
            # Build a nice representation like "60 = 2^2 * 3 * 5"
            factor_strs = [f"{p}^{e}" if e > 1 else str(p) 
                          for p, e in sorted(factors.items())]
            print(f"   {num} = {' * '.join(factor_strs)}")
        else:
            print(f"   {num} has no prime factors (< 2)")
    print()
    
    # Demo 4: Primality testing
    print("4. Primality Tests:")
    test_primes = [2, 17, 97, 100, 541, 1000]
    for n in test_primes:
        result = "PRIME" if is_prime(n) else "composite"
        print(f"   {n}: {result}")
```