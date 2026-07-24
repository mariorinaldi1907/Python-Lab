"""
Date: 2026-07-24
Created a functional programming toolkit with lazy evaluation pipelines that only compute values when needed, plus memoization and currying helpers because I got tired of rewriting these patterns.
"""

"""
Lazy evaluation pipeline system with functional programming utilities.

I wanted a way to chain transformations without immediately executing them,
especially useful when dealing with large datasets or infinite sequences.
"""

from functools import wraps
from typing import Callable, Any, Iterable, Iterator
from itertools import islice


class LazyPipeline:
    """
    A pipeline that defers execution until values are actually needed.
    
    This is really useful when you're chaining multiple transformations
    and don't want to create intermediate lists for everything.
    """
    
    def __init__(self, source: Iterable):
        """Initialize with an iterable source (can be infinite)."""
        self._source = source
        self._operations = []
    
    def map(self, func: Callable) -> 'LazyPipeline':
        """Apply a function to each element (lazily)."""
        self._operations.append(('map', func))
        return self
    
    def filter(self, predicate: Callable) -> 'LazyPipeline':
        """Keep only elements that match the predicate (lazily)."""
        self._operations.append(('filter', predicate))
        return self
    
    def take(self, n: int) -> list:
        """
        Actually evaluate the pipeline and return first n results.
        This is where the magic happens - nothing executes until now.
        """
        iterator = iter(self._source)
        
        # Apply each operation in sequence
        for op_type, func in self._operations:
            if op_type == 'map':
                iterator = map(func, iterator)
            elif op_type == 'filter':
                iterator = filter(func, iterator)
        
        return list(islice(iterator, n))
    
    def take_while(self, predicate: Callable) -> list:
        """Take elements while predicate is true, then stop."""
        iterator = iter(self._source)
        
        for op_type, func in self._operations:
            if op_type == 'map':
                iterator = map(func, iterator)
            elif op_type == 'filter':
                iterator = filter(func, iterator)
        
        result = []
        for item in iterator:
            if not predicate(item):
                break
            result.append(item)
        return result
    
    def realize(self) -> list:
        """Evaluate the entire pipeline (careful with infinite sequences!)."""
        iterator = iter(self._source)
        
        for op_type, func in self._operations:
            if op_type == 'map':
                iterator = map(func, iterator)
            elif op_type == 'filter':
                iterator = filter(func, iterator)
        
        return list(iterator)


def memoize(func: Callable) -> Callable:
    """
    Cache function results to avoid redundant computation.
    
    I use this for expensive recursive functions - the classic example
    being Fibonacci, but it's useful for any pure function with repeated calls.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args):
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result
    
    # Expose the cache for inspection/debugging
    wrapper.cache = cache
    return wrapper


def curry(func: Callable) -> Callable:
    """
    Transform a multi-argument function into a chain of single-argument functions.
    
    This is straight from Haskell-land. Instead of f(x, y, z), you get
    f(x)(y)(z), which is super useful for partial application.
    """
    def curried(*args):
        # If we have all arguments, just call the function
        if len(args) >= func.__code__.co_argcount:
            return func(*args)
        
        # Otherwise, return a function waiting for more arguments
        def partial(*more_args):
            return curried(*(args + more_args))
        return partial
    
    return curried


def infinite_sequence(start: int = 0, step: int = 1) -> Iterator[int]:
    """
    Generate an infinite sequence of numbers.
    
    This demonstrates why lazy evaluation matters - you can't materialize
    an infinite list, but you can take as many items as you need.
    """
    current = start
    while True:
        yield current
        current += step


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Example 1: Infinite sequence with lazy operations
    print("1. Taking first 10 even squares from infinite integers:")
    result = (LazyPipeline(infinite_sequence())
              .filter(lambda x: x % 2 == 0)  # Only evens
              .map(lambda x: x ** 2)           # Square them
              .take(10))                       # Take first 10
    print(f"   {result}\n")
    
    # Example 2: Working with a finite list
    print("2. Processing a regular list with multiple transformations:")
    numbers = range(1, 20)
    result = (LazyPipeline(numbers)
              .map(lambda x: x * 3)
              .filter(lambda x: x > 20)
              .map(lambda x: x - 5)
              .take(5))
    print(f"   {result}\n")
    
    # Example 3: Memoization demonstration
    print("3. Memoized Fibonacci (notice the cache growing):")
    
    @memoize
    def fib(n):
        if n <= 1:
            return n
        return fib(n - 1) + fib(n - 2)
    
    print(f"   fib(10) = {fib(10)}")
    print(f"   fib(20) = {fib(20)}")
    print(f"   Cache size: {len(fib.cache)} entries")
    print(f"   Sample cache entries: {dict(list(fib.cache.items())[:5])}\n")
    
    # Example 4: Currying demonstration
    print("4. Curried function for partial application:")
    
    @curry
    def multiply_three(x, y, z):
        return x * y * z
    
    # Full application
    print(f"   multiply_three(2, 3, 4) = {multiply_three(2, 3, 4)}")
    
    # Partial application - super useful for building specialized functions
    double = multiply_three(2)
    print(f"   double = multiply_three(2)")
    print(f"   double(5, 3) = {double(5, 3)}")
    
    times_six = multiply_three(2, 3)
    print(f"   times_six = multiply_three(2, 3)")
    print(f"   times_six(10) = {times_six(10)}\n")
    
    # Example 5: take_while demonstration
    print("5. Take while predicate is true (stops at first odd number):")
    evens_only = (LazyPipeline(infinite_sequence(0, 2))
                  .map(lambda x: x + 1)
                  .take_while(lambda x: x % 2 == 0))
    print(f"   Result: {evens_only}")
    print("   (Empty because map makes them odd immediately!)\n")
    
    # Better example
    print("6. Squares less than 100:")
    small_squares = (LazyPipeline(infinite_sequence(1))
                     .map(lambda x: x ** 2)
                     .take_while(lambda x: x < 100))
    print(f"   {small_squares}")