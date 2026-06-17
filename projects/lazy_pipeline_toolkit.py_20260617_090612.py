"""
Date: 2026-06-17
Created a functional programming toolkit that lets me compose operations lazily, curry functions naturally, and cache expensive computations automatically.
"""

"""
Lazy evaluation pipeline toolkit with currying and memoization.

This module provides utilities for functional programming patterns:
- LazyPipeline: compose operations that don't run until explicitly evaluated
- curry: transform multi-arg functions into chainable single-arg functions
- memoize: cache function results to avoid redundant computations
"""

from functools import wraps
from typing import Callable, Any, Iterable, TypeVar


T = TypeVar('T')


def memoize(func: Callable) -> Callable:
    """
    Decorator that caches function results based on arguments.
    
    Stores results in a dict keyed by args+kwargs. Only works with
    hashable arguments, but that's fine for most pure functions.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create a cache key from both args and kwargs
        key = (args, tuple(sorted(kwargs.items())))
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    # Expose cache for inspection/clearing
    wrapper.cache = cache
    return wrapper


def curry(func: Callable) -> Callable:
    """
    Transform a multi-argument function into a series of single-argument functions.
    
    This lets you partially apply arguments one at a time, which is super
    useful for building reusable function pipelines.
    """
    @wraps(func)
    def curried(*args, **kwargs):
        # Try calling the function with what we have
        try:
            return func(*args, **kwargs)
        except TypeError:
            # Not enough args yet, return a new function waiting for more
            def partial(*more_args, **more_kwargs):
                combined_kwargs = {**kwargs, **more_kwargs}
                return curried(*(args + more_args), **combined_kwargs)
            return partial
    
    return curried


class LazyPipeline:
    """
    A pipeline that chains operations but doesn't execute until needed.
    
    I built this because I wanted to compose transformations on data
    without actually running them until I call evaluate(). This is
    memory-efficient for large datasets and lets me reuse pipelines.
    """
    
    def __init__(self, source: Iterable[T]):
        """Initialize with a data source (iterable)."""
        self.source = source
        self.operations = []
    
    def map(self, func: Callable[[T], Any]) -> 'LazyPipeline':
        """Apply a transformation to each element."""
        self.operations.append(('map', func))
        return self
    
    def filter(self, predicate: Callable[[T], bool]) -> 'LazyPipeline':
        """Keep only elements that satisfy the predicate."""
        self.operations.append(('filter', predicate))
        return self
    
    def take(self, n: int) -> 'LazyPipeline':
        """Limit the output to first n elements."""
        self.operations.append(('take', n))
        return self
    
    def evaluate(self) -> list:
        """
        Execute all queued operations and return results.
        
        This is where the magic happens — we process the source
        through each operation in sequence, but lazily using generators
        to avoid building intermediate lists.
        """
        result = iter(self.source)
        
        for op_type, op_arg in self.operations:
            if op_type == 'map':
                result = map(op_arg, result)
            elif op_type == 'filter':
                result = filter(op_arg, result)
            elif op_type == 'take':
                result = self._take_n(result, op_arg)
        
        return list(result)
    
    @staticmethod
    def _take_n(iterable: Iterable, n: int):
        """Helper generator to take first n items from an iterable."""
        for i, item in enumerate(iterable):
            if i >= n:
                break
            yield item
    
    def __repr__(self) -> str:
        """Show what operations are queued up."""
        ops = ' -> '.join(f"{op[0]}({op[1].__name__ if callable(op[1]) else op[1]})" 
                          for op in self.operations)
        return f"LazyPipeline({ops})" if ops else "LazyPipeline(empty)"


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Create a pipeline that squares numbers, filters evens, and takes first 5
    # Notice: nothing computes until we call evaluate()!
    numbers = range(1, 100)
    pipeline = (LazyPipeline(numbers)
                .map(lambda x: x ** 2)
                .filter(lambda x: x % 2 == 0)
                .take(5))
    
    print(f"Pipeline built: {pipeline}")
    print(f"Result: {pipeline.evaluate()}\n")
    
    
    print("=== Currying Demo ===\n")
    
    @curry
    def multiply(a, b, c):
        """Multiply three numbers together."""
        return a * b * c
    
    # Can call it normally
    print(f"multiply(2, 3, 4) = {multiply(2, 3, 4)}")
    
    # Or curry it step by step
    times_two = multiply(2)
    times_two_and_three = times_two(3)
    result = times_two_and_three(4)
    print(f"Curried step-by-step: {result}\n")
    
    
    print("=== Memoization Demo ===\n")
    
    call_count = 0
    
    @memoize
    def expensive_fibonacci(n):
        """Calculate fibonacci recursively (inefficient without memoization)."""
        global call_count
        call_count += 1
        
        if n <= 1:
            return n
        return expensive_fibonacci(n - 1) + expensive_fibonacci(n - 2)
    
    # Without memoization, fib(30) would make millions of calls
    # With it, we only compute each value once
    result = expensive_fibonacci(30)
    print(f"fibonacci(30) = {result}")
    print(f"Function called only {call_count} times (would be ~2.7M without cache!)")
    print(f"Cache size: {len(expensive_fibonacci.cache)} entries\n")
    
    
    print("=== Combined Example: Curried Pipeline ===\n")
    
    @curry
    def add_then_multiply(x, y, z):
        """Add x and y, then multiply by z."""
        return (x + y) * z
    
    # Create a reusable function that adds 10 then multiplies by result
    add_10 = add_then_multiply(10)
    
    data = range(5)
    result = (LazyPipeline(data)
              .map(lambda x: add_10(x)(2))  # add 10, multiply by 2
              .filter(lambda x: x > 25)
              .evaluate())
    
    print(f"Numbers 0-4, add 10, multiply by 2, keep > 25: {result}")