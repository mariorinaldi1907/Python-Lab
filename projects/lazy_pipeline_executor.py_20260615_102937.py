"""
Date: 2026-06-15
Created a composable function pipeline that evaluates lazily and caches results, because I got tired of recomputing expensive operations in my data scripts.
"""

#!/usr/bin/env python3
"""
Lazy Pipeline Executor with Memoization

A functional programming utility that lets you compose functions into pipelines
that evaluate lazily (only when needed) and cache intermediate results.
Perfect for chaining expensive operations without wasting compute.
"""

from functools import wraps
from typing import Any, Callable, Iterator, Optional
import time


def memoize(func: Callable) -> Callable:
    """
    Decorator that caches function results based on arguments.
    
    Uses a dict to store results keyed by stringified args/kwargs.
    Not perfect for all types, but works great for hashable primitives.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create a cache key from args and kwargs
        key = str(args) + str(sorted(kwargs.items()))
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        
        return cache[key]
    
    # Expose cache for inspection/debugging
    wrapper.cache = cache
    return wrapper


class LazyPipeline:
    """
    A composable pipeline that evaluates functions lazily.
    
    Instead of running all transformations immediately, we build up
    a chain of operations and only execute when we actually need the result.
    This is especially useful when dealing with generators or expensive ops.
    """
    
    def __init__(self, iterable: Iterator):
        """Initialize with an iterable (can be a generator or list)."""
        self._iterable = iterable
        self._operations = []
    
    def map(self, func: Callable) -> 'LazyPipeline':
        """
        Apply a function to each element.
        
        Doesn't execute immediately — just records the operation.
        """
        self._operations.append(('map', func))
        return self
    
    def filter(self, predicate: Callable) -> 'LazyPipeline':
        """
        Keep only elements where predicate returns True.
        
        Again, lazy — we just queue this up.
        """
        self._operations.append(('filter', predicate))
        return self
    
    def take(self, n: int) -> 'LazyPipeline':
        """Limit results to first n elements."""
        self._operations.append(('take', n))
        return self
    
    def _execute(self) -> Iterator:
        """
        Actually run the pipeline.
        
        This is where the magic happens — we iterate through the data
        and apply each queued operation in sequence.
        """
        result = iter(self._iterable)
        
        for op_type, op_arg in self._operations:
            if op_type == 'map':
                result = map(op_arg, result)
            elif op_type == 'filter':
                result = filter(op_arg, result)
            elif op_type == 'take':
                result = (x for i, x in enumerate(result) if i < op_arg)
        
        return result
    
    def collect(self) -> list:
        """Force evaluation and return results as a list."""
        return list(self._execute())
    
    def reduce(self, func: Callable, initial: Optional[Any] = None) -> Any:
        """
        Reduce the pipeline to a single value.
        
        Uses functools.reduce under the hood but fits our API.
        """
        from functools import reduce as functools_reduce
        result = self._execute()
        
        if initial is not None:
            return functools_reduce(func, result, initial)
        return functools_reduce(func, result)


def curry(func: Callable) -> Callable:
    """
    Transform a multi-argument function into a chain of single-argument functions.
    
    Example: add(x, y) becomes add(x)(y)
    Useful for partial application patterns.
    """
    def curried(*args, **kwargs):
        # If we have enough args, just call it
        try:
            return func(*args, **kwargs)
        except TypeError:
            # Not enough args, return a function waiting for more
            def partial(*more_args, **more_kwargs):
                return curried(*(args + more_args), **{**kwargs, **more_kwargs})
            return partial
    
    return curried


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Expensive operation that we'll memoize
    @memoize
    def expensive_square(x: int) -> int:
        """Simulate an expensive computation."""
        time.sleep(0.1)  # Pretend this takes time
        return x * x
    
    print("1. Testing memoization:")
    print(f"   First call expensive_square(5): {expensive_square(5)}")
    print(f"   Second call expensive_square(5): {expensive_square(5)} (instant!)")
    print(f"   Cache contents: {expensive_square.cache}\n")
    
    # Lazy pipeline example
    print("2. Building a lazy pipeline:")
    print("   Pipeline: range(100) -> filter(even) -> map(square) -> take(5)")
    
    pipeline = (LazyPipeline(range(100))
                .filter(lambda x: x % 2 == 0)
                .map(lambda x: x * x)
                .take(5))
    
    print(f"   Results: {pipeline.collect()}\n")
    
    # Currying example
    print("3. Currying demonstration:")
    
    @curry
    def multiply(x: int, y: int, z: int) -> int:
        """Multiply three numbers."""
        return x * y * z
    
    # Partial application
    double = multiply(2)
    double_and_triple = double(3)
    
    print(f"   multiply(2)(3)(4) = {multiply(2)(3)(4)}")
    print(f"   Partially applied: double_and_triple(5) = {double_and_triple(5)}\n")
    
    # Combined example: pipeline with memoized operations
    print("4. Pipeline with memoized expensive operations:")
    
    def double_if_odd(x: int) -> int:
        """Only do expensive computation for odd numbers."""
        if x % 2 == 1:
            return expensive_square(x)
        return x
    
    result = (LazyPipeline(range(10))
              .map(double_if_odd)
              .filter(lambda x: x > 10)
              .collect())
    
    print(f"   Results: {result}")
    print(f"   Memoization saved us from recomputing squares!")