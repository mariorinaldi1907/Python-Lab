"""
Date: 2026-08-10
Built an extended Euclidean algorithm tool because I needed modular inverses for some crypto experiments and wanted a clean implementation with full steps tracking.
"""

#!/usr/bin/env python3
"""
Extended Euclidean Algorithm implementation with modular inverse computation.

This module provides number theory utilities based on the extended Euclidean algorithm,
which finds coefficients (x, y) such that ax + by = gcd(a, b).
"""


def gcd(a, b):
    """
    Compute the greatest common divisor using Euclidean algorithm.
    
    Args:
        a: First integer
        b: Second integer
    
    Returns:
        The GCD of a and b
    """
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a, b):
    """
    Extended Euclidean Algorithm: finds x, y such that ax + by = gcd(a, b).
    
    This is the core algorithm. I'm using the iterative version instead of recursive
    because it's easier to track the steps and doesn't blow the stack on large inputs.
    
    Args:
        a: First integer
        b: Second integer
    
    Returns:
        Tuple (gcd, x, y) where gcd is the greatest common divisor and
        x, y are coefficients satisfying ax + by = gcd
    """
    # Keep track of original signs for the final result
    original_a, original_b = a, b
    a, b = abs(a), abs(b)
    
    # Initialize the sequences
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    
    # Main loop - iterate until remainder is 0
    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    
    # old_r is now the GCD
    # Adjust signs based on original inputs
    if original_a < 0:
        old_s = -old_s
    if original_b < 0:
        old_t = -old_t
    
    return old_r, old_s, old_t


def mod_inverse(a, m):
    """
    Compute the modular multiplicative inverse of a modulo m.
    
    Returns x such that (a * x) % m == 1, if it exists.
    The inverse exists if and only if gcd(a, m) == 1.
    
    Args:
        a: The number to find the inverse of
        m: The modulus
    
    Returns:
        The modular inverse of a modulo m
    
    Raises:
        ValueError: If the modular inverse doesn't exist (gcd(a, m) != 1)
    """
    if m <= 0:
        raise ValueError("Modulus must be positive")
    
    # Normalize a to be in range [0, m)
    a = a % m
    
    g, x, _ = extended_gcd(a, m)
    
    if g != 1:
        raise ValueError(f"Modular inverse doesn't exist: gcd({a}, {m}) = {g} != 1")
    
    # Make sure result is positive
    return x % m


def solve_linear_diophantine(a, b, c):
    """
    Solve the linear Diophantine equation ax + by = c.
    
    Returns one particular solution if it exists. The general solution is:
    x = x0 + (b/gcd)*t
    y = y0 - (a/gcd)*t
    for any integer t.
    
    Args:
        a: Coefficient of x
        b: Coefficient of y
        c: Right-hand side constant
    
    Returns:
        Tuple (x, y) representing one solution, or None if no solution exists
    """
    g, x, y = extended_gcd(a, b)
    
    # Solution exists only if gcd divides c
    if c % g != 0:
        return None
    
    # Scale the solution
    scale = c // g
    return x * scale, y * scale


def bezout_coefficients_verbose(a, b):
    """
    Show the step-by-step computation of Bézout coefficients.
    
    I added this because it's actually pretty cool to see how the algorithm
    works through the iterations.
    
    Args:
        a: First integer
        b: Second integer
    
    Returns:
        List of tuples (r, s, t, q) for each step, where r is remainder,
        s and t are current coefficients, and q is the quotient
    """
    a, b = abs(a), abs(b)
    
    steps = []
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    
    while r != 0:
        quotient = old_r // r
        steps.append((old_r, old_s, old_t, quotient))
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    
    # Add the final step
    steps.append((old_r, old_s, old_t, None))
    
    return steps


if __name__ == "__main__":
    print("=" * 60)
    print("Extended Euclidean Algorithm Demo")
    print("=" * 60)
    
    # Test 1: Basic GCD
    print("\n1. Basic GCD computation:")
    a, b = 48, 18
    print(f"   gcd({a}, {b}) = {gcd(a, b)}")
    
    # Test 2: Extended GCD
    print("\n2. Extended GCD (finding Bézout coefficients):")
    a, b = 240, 46
    g, x, y = extended_gcd(a, b)
    print(f"   For a={a}, b={b}:")
    print(f"   gcd = {g}")
    print(f"   Coefficients: x={x}, y={y}")
    print(f"   Verification: {a}*{x} + {b}*{y} = {a*x + b*y}")
    
    # Test 3: Modular inverse
    print("\n3. Modular inverse computation:")
    a, m = 17, 43
    inv = mod_inverse(a, m)
    print(f"   Inverse of {a} mod {m} = {inv}")
    print(f"   Verification: ({a} * {inv}) mod {m} = {(a * inv) % m}")
    
    # Test 4: Another modular inverse (useful for RSA)
    print("\n4. Another modular inverse (RSA-style):")
    e, phi = 65537, 3220  # phi = (p-1)*(q-1) where p=23, q=140
    try:
        d = mod_inverse(e, phi)
        print(f"   Private exponent d = {d}")
        print(f"   Verification: ({e} * {d}) mod {phi} = {(e * d) % phi}")
    except ValueError as ex:
        print(f"   {ex}")
    
    # Test 5: Linear Diophantine equation
    print("\n5. Solving linear Diophantine equation 14x + 35y = 7:")
    result = solve_linear_diophantine(14, 35, 7)
    if result:
        x, y = result
        print(f"   One solution: x={x}, y={y}")
        print(f"   Verification: 14*{x} + 35*{y} = {14*x + 35*y}")
    else:
        print("   No solution exists")
    
    # Test 6: Verbose step-by-step for educational purposes
    print("\n6. Step-by-step calculation for gcd(252, 105):")
    steps = bezout_coefficients_verbose(252, 105)
    print(f"   {'Step':<6} {'r':<8} {'s':<8} {'t':<8} {'quotient':<10}")
    print("   " + "-" * 50)
    for i, (r, s, t, q) in enumerate(steps):
        q_str = str(q) if q is not None else "final"
        print(f"   {i:<6} {r:<8} {s:<8} {t:<8} {q_str:<10}")
    
    print("\n" + "=" * 60)