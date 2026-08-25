"""
Date: 2026-08-25
Built a complete integer factorization toolkit using Pollard's rho algorithm paired with Miller-Rabin primality testing — wanted something faster than trial division for my Project Euler solutions.
"""

#!/usr/bin/env python3
"""
Pollard's Rho Integer Factorization
====================================
A practical implementation of Pollard's rho algorithm for factoring large integers.
Includes Miller-Rabin primality testing to speed things up by identifying primes early.

I got tired of waiting for trial division on big numbers, so I finally sat down
and implemented this properly. The rho algorithm uses a pseudo-random walk to find
non-trivial factors — it's probabilistic but usually way faster than deterministic methods.
"""

import random
from math import gcd
from typing import List, Tuple


def miller_rabin(n: int, k: int = 5) -> bool:
    """
    Miller-Rabin primality test.
    
    Returns True if n is *probably* prime, False if definitely composite.
    The parameter k controls accuracy — higher k means lower false positive rate.
    
    I'm using k=5 as default because it gives negligible error for practical purposes
    while keeping the test fast.
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
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)  # a^d mod n
        
        if x == 1 or x == n - 1:
            continue
        
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    
    return True


def pollard_rho(n: int) -> int:
    """
    Pollard's rho algorithm for finding a non-trivial factor of n.
    
    This uses Floyd's cycle detection with the polynomial f(x) = x^2 + c.
    If it returns n, the algorithm failed (try again with different random seed).
    
    The "rho" name comes from the shape of the cycle when you graph the sequence.
    """
    if n % 2 == 0:
        return 2
    
    # Random starting values — sometimes we need to retry with different values
    x = random.randint(2, n - 1)
    y = x
    c = random.randint(1, n - 1)
    d = 1
    
    # Floyd's cycle detection: tortoise and hare
    while d == 1:
        # Tortoise moves one step
        x = (x * x + c) % n
        
        # Hare moves two steps
        y = (y * y + c) % n
        y = (y * y + c) % n
        
        d = gcd(abs(x - y), n)
    
    return d if d != n else pollard_rho(n)  # Retry if we failed


def factor(n: int) -> List[int]:
    """
    Complete factorization of n into prime factors.
    
    Returns a list of prime factors (with repetition) in ascending order.
    Combines Miller-Rabin testing with Pollard's rho to avoid unnecessary work.
    """
    if n <= 1:
        return []
    
    if miller_rabin(n):
        return [n]
    
    # Handle small factors quickly
    if n % 2 == 0:
        return [2] + factor(n // 2)
    
    # Use Pollard's rho to find a factor
    divisor = pollard_rho(n)
    
    # Recursively factor both parts
    return sorted(factor(divisor) + factor(n // divisor))


def prime_factorization(n: int) -> List[Tuple[int, int]]:
    """
    Returns prime factorization as list of (prime, exponent) tuples.
    
    Example: 360 -> [(2, 3), (3, 2), (5, 1)] because 360 = 2^3 * 3^2 * 5
    
    This is usually more useful than just a list of factors when you need
    to work with divisors or do number theory stuff.
    """
    factors = factor(n)
    
    if not factors:
        return []
    
    result = []
    current_prime = factors[0]
    count = 1
    
    for i in range(1, len(factors)):
        if factors[i] == current_prime:
            count += 1
        else:
            result.append((current_prime, count))
            current_prime = factors[i]
            count = 1
    
    result.append((current_prime, count))
    return result


def count_divisors(n: int) -> int:
    """
    Count the number of divisors of n using prime factorization.
    
    If n = p1^a1 * p2^a2 * ... * pk^ak, then the number of divisors is
    (a1+1) * (a2+1) * ... * (ak+1). Way faster than enumerating them all.
    """
    factorization = prime_factorization(n)
    result = 1
    
    for prime, exponent in factorization:
        result *= (exponent + 1)
    
    return result


def is_perfect_power(n: int) -> Tuple[bool, int, int]:
    """
    Check if n is a perfect power (n = a^b for integers a, b where b > 1).
    
    Returns (is_power, base, exponent).
    Example: 64 -> (True, 2, 6) because 64 = 2^6
             65 -> (False, 0, 0)
    
    Uses the factorization to find the GCD of all exponents.
    """
    if n <= 1:
        return (False, 0, 0)
    
    factorization = prime_factorization(n)
    
    if not factorization:
        return (False, 0, 0)
    
    # Find GCD of all exponents
    exp_gcd = factorization[0][1]
    for _, exp in factorization[1:]:
        exp_gcd = gcd(exp_gcd, exp)
    
    if exp_gcd == 1:
        return (False, 0, 0)
    
    # Reconstruct the base
    base = 1
    for prime, exp in factorization:
        base *= prime ** (exp // exp_gcd)
    
    return (True, base, exp_gcd)


if __name__ == "__main__":
    print("Pollard's Rho Factorization Demo")
    print("=" * 50)
    
    # Test some interesting numbers
    test_numbers = [
        1234567,
        9999991,  # Prime
        1000000007,  # Prime
        123456789012345,
        2**31 - 1,  # Mersenne prime
        2**32 - 5,  # Large composite
    ]
    
    for num in test_numbers:
        print(f"\nn = {num:,}")
        
        if miller_rabin(num):
            print(f"  → PRIME (verified with Miller-Rabin)")
        else:
            factors = factor(num)
            fact_str = prime_factorization(num)
            
            print(f"  → Factors: {factors}")
            print(f"  → Prime factorization: {fact_str}")
            print(f"  → Number of divisors: {count_divisors(num)}")
            
            is_power, base, exp = is_perfect_power(num)
            if is_power:
                print(f"  → Perfect power: {base}^{exp}")
    
    # Demonstrate perfect power detection
    print("\n" + "=" * 50)
    print("Perfect Power Detection:")
    powers = [64, 128, 1000, 15625, 1024]
    for n in powers:
        is_power, base, exp = is_perfect_power(n)
        if is_power:
            print(f"  {n} = {base}^{exp}")
        else:
            print(f"  {n} is not a perfect power")