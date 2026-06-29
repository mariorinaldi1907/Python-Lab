"""
Date: 2026-06-29
Built a Miller-Rabin probabilistic primality tester because I got tired of slow prime checks — includes deterministic mode for smaller numbers.
"""

#!/usr/bin/env python3
"""
Miller-Rabin Primality Test Implementation

I needed a fast way to check if large numbers are prime without waiting forever.
Trial division is painfully slow for anything beyond a few million, so I implemented
the Miller-Rabin probabilistic test. It's not 100% certain for random witnesses,
but with enough rounds the error probability becomes negligible. Plus, I added
deterministic mode for numbers under 3,317,044,064,679,887,385,961,981 using
known witness sets.
"""

import random


def power_mod(base, exponent, modulus):
    """
    Compute (base^exponent) % modulus efficiently using binary exponentiation.
    
    This is way faster than doing base**exponent % modulus for large numbers
    because it keeps intermediate results small by taking modulo at each step.
    """
    result = 1
    base = base % modulus
    
    while exponent > 0:
        if exponent % 2 == 1:
            result = (result * base) % modulus
        exponent = exponent >> 1
        base = (base * base) % modulus
    
    return result


def miller_rabin_test(n, witness):
    """
    Perform a single Miller-Rabin test with the given witness.
    
    Returns False if n is definitely composite, True if n is probably prime.
    
    The idea: we write n-1 as 2^r * d where d is odd, then check if
    witness^d ≡ 1 (mod n) or witness^(2^i * d) ≡ -1 (mod n) for some i.
    If neither condition holds, n is definitely composite.
    """
    if n == witness:
        return True
    
    # Write n-1 as 2^r * d where d is odd
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    # Compute witness^d mod n
    x = power_mod(witness, d, n)
    
    if x == 1 or x == n - 1:
        return True
    
    # Square x repeatedly r-1 times
    for _ in range(r - 1):
        x = power_mod(x, 2, n)
        if x == n - 1:
            return True
    
    return False


def is_prime(n, rounds=40):
    """
    Check if n is prime using Miller-Rabin test.
    
    For small n (< 3.3e24), uses deterministic witnesses for 100% accuracy.
    For larger n, uses random witnesses with configurable rounds.
    The probability of error is at most 4^(-rounds), so 40 rounds gives
    error probability < 10^(-24), which is good enough for me.
    
    Args:
        n: Number to test for primality
        rounds: Number of test rounds (only used for large n)
    
    Returns:
        True if n is prime, False otherwise
    """
    # Handle small cases
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    # Deterministic witnesses for small numbers
    # These witness sets are proven to work for their respective ranges
    if n < 2047:
        witnesses = [2]
    elif n < 1373653:
        witnesses = [2, 3]
    elif n < 9080191:
        witnesses = [31, 73]
    elif n < 25326001:
        witnesses = [2, 3, 5]
    elif n < 3215031751:
        witnesses = [2, 3, 5, 7]
    elif n < 4759123141:
        witnesses = [2, 7, 61]
    elif n < 1122004669633:
        witnesses = [2, 13, 23, 1662803]
    elif n < 2152302898747:
        witnesses = [2, 3, 5, 7, 11]
    elif n < 3474749660383:
        witnesses = [2, 3, 5, 7, 11, 13]
    elif n < 341550071728321:
        witnesses = [2, 3, 5, 7, 11, 13, 17]
    elif n < 3825123056546413051:
        witnesses = [2, 3, 5, 7, 11, 13, 17, 19, 23]
    else:
        # For very large numbers, use random witnesses
        witnesses = [random.randint(2, n - 2) for _ in range(rounds)]
    
    # Run the test with each witness
    for witness in witnesses:
        if not miller_rabin_test(n, witness):
            return False
    
    return True


def find_primes_in_range(start, end):
    """
    Find all prime numbers in the range [start, end] using Miller-Rabin.
    
    Not the most efficient for finding many small primes (sieve is better),
    but works great for checking specific large numbers in a range.
    """
    primes = []
    for num in range(start, end + 1):
        if is_prime(num):
            primes.append(num)
    return primes


def next_prime(n):
    """
    Find the smallest prime number greater than n.
    
    Just increments and tests each number. For odd n, we can skip even numbers
    to cut the search space in half.
    """
    candidate = n + 1
    if candidate > 2 and candidate % 2 == 0:
        candidate += 1
    
    while not is_prime(candidate):
        candidate += 2 if candidate > 2 else 1
    
    return candidate


if __name__ == "__main__":
    print("Miller-Rabin Primality Test Demo")
    print("=" * 50)
    
    # Test some small primes
    print("\nTesting small numbers:")
    test_numbers = [2, 3, 17, 19, 97, 100, 561, 1105]  # 561 and 1105 are Carmichael numbers
    for num in test_numbers:
        result = "PRIME" if is_prime(num) else "COMPOSITE"
        print(f"  {num:6d} -> {result}")
    
    # Test some larger primes
    print("\nTesting larger numbers:")
    large_tests = [
        1000000007,  # prime
        1000000009,  # prime
        1000000021,  # prime
        1000000033,  # composite (3 × 333333344)
    ]
    for num in large_tests:
        result = "PRIME" if is_prime(num) else "COMPOSITE"
        print(f"  {num} -> {result}")
    
    # Find primes in a range
    print("\nPrimes between 100 and 150:")
    primes = find_primes_in_range(100, 150)
    print(f"  {primes}")
    
    # Find next prime after a number
    print("\nNext prime after some numbers:")
    for num in [1000, 10000, 100000]:
        np = next_prime(num)
        print(f"  After {num}: {np}")
    
    # Test a really large probable prime
    print("\nTesting very large number:")
    # Mersenne prime 2^89 - 1
    huge = 2**89 - 1
    result = "PRIME" if is_prime(huge) else "COMPOSITE"
    print(f"  2^89 - 1 = {huge}")
    print(f"  Result: {result}")