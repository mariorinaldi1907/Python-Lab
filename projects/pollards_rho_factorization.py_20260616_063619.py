"""
Date: 2026-06-16
Built a fast integer factorization tool using Pollard's rho algorithm because I was curious how RSA-style problems get cracked — includes primality testing with Miller-Rabin.
"""

#!/usr/bin/env python3
"""
Pollard's Rho Integer Factorization

I got interested in how large numbers get factored after reading about
cryptography challenges. This implements Pollard's rho algorithm, which
is way faster than trial division for semi-primes (products of two large primes).

The algorithm uses a pseudo-random cycle detection technique — it's beautiful
because it leverages the birthday paradox to find factors surprisingly quickly.
"""

import math
import random
from typing import List, Tuple


def gcd(a: int, b: int) -> int:
    """
    Euclidean algorithm for greatest common divisor.
    
    Classic recursion — keeps dividing until we hit the GCD.
    """
    while b:
        a, b = b, a % b
    return a


def miller_rabin(n: int, k: int = 5) -> bool:
    """
    Miller-Rabin primality test.
    
    Probabilistic test — runs k rounds to minimize false positives.
    For k=5, the probability of a composite passing is less than 1/1024.
    
    I use this to verify if we've found a prime factor or need to keep going.
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
    
    # Run k rounds of testing
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)  # modular exponentiation
        
        if x == 1 or x == n - 1:
            continue
        
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    
    return True


def pollards_rho(n: int, max_iterations: int = 100000) -> int:
    """
    Pollard's rho algorithm for finding a non-trivial factor of n.
    
    Uses Floyd's cycle detection (tortoise and hare) on a polynomial sequence.
    The function f(x) = (x^2 + c) mod n generates a pseudo-random sequence
    that eventually cycles. When the cycle overlaps in a certain way, we find factors.
    
    Returns a factor if found, otherwise returns n (failed to factor).
    """
    if n % 2 == 0:
        return 2
    
    # Random starting point and constant — sometimes we need to retry
    # with different values if we get unlucky
    x = random.randint(2, n - 1)
    y = x
    c = random.randint(1, n - 1)
    d = 1
    
    # Define the polynomial function
    def f(val):
        return (val * val + c) % n
    
    iteration = 0
    while d == 1 and iteration < max_iterations:
        x = f(x)          # tortoise moves one step
        y = f(f(y))       # hare moves two steps
        d = gcd(abs(x - y), n)
        iteration += 1
    
    # If d == n, we failed (the algorithm can occasionally get stuck)
    return d if d != n else n


def factor(n: int) -> List[int]:
    """
    Complete factorization of n into prime factors.
    
    Combines trial division for small factors with Pollard's rho for larger ones.
    Returns a list of prime factors (with repetition for powers).
    """
    if n < 2:
        return []
    
    factors = []
    
    # Trial division for small primes — this is fast and catches common cases
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
        while n % p == 0:
            factors.append(p)
            n //= p
    
    # If n is now 1, we're done
    if n == 1:
        return factors
    
    # If n is prime, we're also done
    if miller_rabin(n):
        factors.append(n)
        return factors
    
    # Use Pollard's rho for the remaining composite
    stack = [n]
    while stack:
        current = stack.pop()
        
        if current == 1:
            continue
        
        if miller_rabin(current):
            factors.append(current)
            continue
        
        # Try to find a factor
        factor_found = pollards_rho(current)
        
        if factor_found == current:
            # Pollard's rho failed, fall back to trial division
            # This is slow but guaranteed to work
            for i in range(37, int(math.sqrt(current)) + 1, 2):
                if current % i == 0:
                    factor_found = i
                    break
        
        if factor_found == current:
            # Still couldn't factor — treat as prime (shouldn't happen often)
            factors.append(current)
        else:
            # Add both the factor and the quotient back to the stack
            stack.append(factor_found)
            stack.append(current // factor_found)
    
    return sorted(factors)


def format_factorization(n: int, factors: List[int]) -> str:
    """
    Pretty-print factorization with exponents.
    
    Converts [2, 2, 3, 5, 5] into "2^2 × 3 × 5^2"
    """
    if not factors:
        return "1"
    
    from collections import Counter
    counts = Counter(factors)
    
    terms = []
    for prime in sorted(counts.keys()):
        count = counts[prime]
        if count == 1:
            terms.append(str(prime))
        else:
            terms.append(f"{prime}^{count}")
    
    return " × ".join(terms)


if __name__ == "__main__":
    print("Pollard's Rho Integer Factorization\n" + "=" * 40)
    
    # Test cases — mix of easy and harder examples
    test_numbers = [
        100,
        1234567,
        999983 * 999979,  # product of two large primes
        2**16 + 1,        # Fermat number F4 (known to be composite)
        8675309,
        1000000007,       # large prime
    ]
    
    for n in test_numbers:
        print(f"\nFactoring {n:,}...")
        factors = factor(n)
        factorization = format_factorization(n, factors)
        print(f"  {n:,} = {factorization}")
        
        # Verify the factorization is correct
        product = 1
        for f in factors:
            product *= f
        assert product == n, f"Verification failed for {n}"
        
        # Check if it's prime
        if len(factors) == 1:
            print(f"  → Prime number!")
    
    print("\n" + "=" * 40)
    print("All factorizations verified successfully!")