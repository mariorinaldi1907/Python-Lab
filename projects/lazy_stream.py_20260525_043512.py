# A lazy evaluation stream class that lets you work with infinite sequences without blowing up your memory.
# written: 2026-05-25

"""
Lazy Stream implementation - basically infinite lists that compute values on demand.
Playing around with functional programming concepts in Python.
"""

from typing import Callable, Any, Optional
from functools import wraps


class Stream:
    """
    Lazy evaluated stream. Only computes values when you actually need them.
    Think Haskell's lazy lists but in Python.
    """
    
    def __init__(self, head: Any, tail_func: Callable[[], 'Stream']):
        """
        Create a stream with a head value and a function that generates the tail.
        
        Args:
            head: The first element of the stream
            tail_func: A function that returns the rest of the stream (called lazily)
        """
        self._head = head
        self._tail_func = tail_func
        self._tail_cached = None
    
    @property
    def head(self) -> Any:
        """Get the first element."""
        return self._head
    
    @property
    def tail(self) -> 'Stream':
        """Get the rest of the stream (memoized so we don't recompute)."""
        if self._tail_cached is None:
            self._tail_cached = self._tail_func()
        return self._tail_cached
    
    def take(self, n: int) -> list:
        """
        Take the first n elements from the stream.
        This is where the magic happens - forces evaluation.
        """
        if n <= 0:
            return []
        return [self.head] + self.tail.take(n - 1)
    
    def map(self, func: Callable[[Any], Any]) -> 'Stream':
        """Apply a function to every element (lazily, of course)."""
        return Stream(
            func(self.head),
            lambda: self.tail.map(func)
        )
    
    def filter(self, predicate: Callable[[Any], bool]) -> 'Stream':
        """Filter elements based on a predicate. Skips elements that don't match."""
        if predicate(self.head):
            return Stream(
                self.head,
                lambda: self.tail.filter(predicate)
            )
        else:
            # this is the tricky part - skip the head and keep filtering the tail
            return self.tail.filter(predicate)
    
    def zip_with(self, other: 'Stream', func: Callable[[Any, Any], Any]) -> 'Stream':
        """Combine two streams element-wise using a function."""
        return Stream(
            func(self.head, other.head),
            lambda: self.tail.zip_with(other.tail, func)
        )


def stream_from(start: int, step: int = 1) -> Stream:
    """
    Create an infinite stream of integers starting from 'start'.
    Classic example: stream_from(1) gives you 1, 2, 3, 4, ...
    """
    return Stream(start, lambda: stream_from(start + step, step))


def iterate(func: Callable[[Any], Any], initial: Any) -> Stream:
    """
    Create a stream by repeatedly applying a function.
    iterate(f, x) generates: x, f(x), f(f(x)), f(f(f(x))), ...
    """
    return Stream(initial, lambda: iterate(func, func(initial)))


def fibonacci_stream() -> Stream:
    """
    The classic Fibonacci sequence as an infinite stream.
    Uses a neat trick with zip_with to define fibs in terms of itself.
    """
    def fib_helper(a: int, b: int) -> Stream:
        return Stream(a, lambda: fib_helper(b, a + b))
    
    return fib_helper(0, 1)


def sieve_of_eratosthenes(s: Stream) -> Stream:
    """
    Prime number sieve using streams. Pretty elegant if you ask me.
    Takes a stream of integers and filters out composites.
    """
    return Stream(
        s.head,
        lambda: sieve_of_eratosthenes(
            s.tail.filter(lambda x: x % s.head != 0)
        )
    )


if __name__ == "__main__":
    print("=== Lazy Stream Demo ===\n")
    
    # Basic infinite sequence
    print("First 10 natural numbers:")
    naturals = stream_from(1)
    print(naturals.take(10))
    
    # Map operation
    print("\nFirst 10 squares:")
    squares = naturals.map(lambda x: x * x)
    print(squares.take(10))
    
    # Filter operation
    print("\nFirst 10 even numbers:")
    evens = naturals.filter(lambda x: x % 2 == 0)
    print(evens.take(10))
    
    # Fibonacci sequence
    print("\nFirst 15 Fibonacci numbers:")
    fibs = fibonacci_stream()
    print(fibs.take(15))
    
    # Iterate function
    print("\nPowers of 2 (using iterate):")
    powers_of_2 = iterate(lambda x: x * 2, 1)
    print(powers_of_2.take(10))
    
    # Prime numbers using sieve
    print("\nFirst 20 prime numbers (sieve of Eratosthenes):")
    primes = sieve_of_eratosthenes(stream_from(2))
    print(primes.take(20))
    
    # Combining streams
    print("\nZipping two streams (adding naturals and evens):")
    combined = naturals.zip_with(evens, lambda x, y: x + y)
    print(combined.take(8))
    
    print("\nAll computed lazily - no infinite loops, no memory explosions!")