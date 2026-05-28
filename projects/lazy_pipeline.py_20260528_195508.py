"""
Date: 2026-05-28
Created a lazy evaluation pipeline that chains functions together without executing until needed, with built-in memoization because I got tired of recalculating expensive operations.
"""

"""
Lazy evaluation pipeline with automatic memoization.

I wanted something that lets me chain operations like Unix pipes but doesn't
actually execute anything until I need the result. Plus, memoization so I don't
repeat expensive calculations when I'm experimenting interactively.
"""

from functools import wraps
from typing import Callable, Any, Iterator, Iterable
import itertools


def memoize(func: Callable) -> Callable:
    """
    Cache function results based on arguments.
    
    Using a dict here instead of lru_cache because I want to see what's
    happening under the hood. Only works with hashable arguments.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # kwargs need to be frozen into the key too
        key = (args, tuple(sorted(kwargs.items())))
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    # Attach cache so we can inspect it if needed
    wrapper.cache = cache
    return wrapper


class LazyPipeline:
    """
    Lazy evaluation pipeline that chains operations without executing.
    
    The idea is you can stack up a bunch of transformations and filters,
    but nothing actually runs until you iterate or call .execute().
    """
    
    def __init__(self, source: Iterable):
        """Start a pipeline with an initial data source."""
        self.source = source
        self.operations = []
    
    def map(self, func: Callable) -> 'LazyPipeline':
        """
        Apply a function to each element.
        
        Returns self so we can chain calls.
        """
        self.operations.append(('map', func))
        return self
    
    def filter(self, predicate: Callable) -> 'LazyPipeline':
        """Keep only elements where predicate returns True."""
        self.operations.append(('filter', predicate))
        return self
    
    def take(self, n: int) -> 'LazyPipeline':
        """Limit output to first n elements."""
        self.operations.append(('take', n))
        return self
    
    def _apply_operations(self, data: Iterable) -> Iterator:
        """
        Actually apply the queued operations.
        
        This is where the lazy magic happens - we yield items one at a time
        through the entire pipeline without building intermediate lists.
        """
        current = iter(data)
        
        for op_type, op_arg in self.operations:
            if op_type == 'map':
                current = map(op_arg, current)
            elif op_type == 'filter':
                current = filter(op_arg, current)
            elif op_type == 'take':
                current = itertools.islice(current, op_arg)
        
        return current
    
    def execute(self) -> list:
        """Force evaluation and return results as a list."""
        return list(self._apply_operations(self.source))
    
    def __iter__(self) -> Iterator:
        """Allow direct iteration over the pipeline."""
        return self._apply_operations(self.source)


def curry(func: Callable) -> Callable:
    """
    Transform a function to allow partial application.
    
    This lets you call a multi-argument function with fewer arguments
    and get back a new function waiting for the rest. Borrowed from
    functional languages like Haskell.
    """
    @wraps(func)
    def curried(*args, **kwargs):
        # Try calling with what we have
        try:
            return func(*args, **kwargs)
        except TypeError:
            # Not enough args - return a new function waiting for more
            def partial(*more_args, **more_kwargs):
                combined_kwargs = {**kwargs, **more_kwargs}
                return curried(*(args + more_args), **combined_kwargs)
            return partial
    
    return curried


@curry
def add(x: int, y: int, z: int = 0) -> int:
    """Example curried function - adds three numbers."""
    return x + y + z


@memoize
def expensive_calculation(n: int) -> int:
    """
    Simulate an expensive operation.
    
    Fibonacci is a classic example where memoization really shines.
    Without it, fib(35) would take forever with naive recursion.
    """
    if n <= 1:
        return n
    return expensive_calculation(n - 1) + expensive_calculation(n - 2)


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Start with numbers 1-20
    numbers = range(1, 21)
    
    # Build up a pipeline without executing
    result = (LazyPipeline(numbers)
              .filter(lambda x: x % 2 == 0)  # keep evens
              .map(lambda x: x ** 2)          # square them
              .take(5)                        # only first 5
              .execute())
    
    print(f"Even numbers squared (first 5): {result}")
    
    print("\n=== Currying Demo ===\n")
    
    # Partial application - we can build specialized functions
    add_5 = add(5)
    add_5_and_3 = add(5, 3)
    
    print(f"add(5)(10) = {add_5(10)}")
    print(f"add(5, 3)(2) = {add_5_and_3(2)}")
    print(f"add(1)(2)(3) = {add(1)(2)(3)}")
    
    print("\n=== Memoization Demo ===\n")
    
    # Calculate fibonacci with memoization
    test_values = [10, 15, 20, 15, 10]  # note the repeats
    
    print("Calculating fibonacci (watch for cache hits on repeats):")
    for n in test_values:
        result = expensive_calculation(n)
        cache_size = len(expensive_calculation.cache)
        print(f"  fib({n}) = {result:>6}  (cache size: {cache_size})")
    
    print("\n=== Combining Everything ===\n")
    
    # Use memoized function in a lazy pipeline
    fib_pipeline = (LazyPipeline(range(1, 15))
                    .map(expensive_calculation)
                    .filter(lambda x: x % 2 == 0)
                    .take(6))
    
    print("Even fibonacci numbers (lazy evaluation):")
    for fib in fib_pipeline:
        print(f"  {fib}")