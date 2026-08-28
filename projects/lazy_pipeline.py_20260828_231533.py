"""
Date: 2026-08-28
Implemented a composable lazy pipeline that defers computation until values are actually pulled, with built-in memoization to cache expensive operations.
"""

"""
Lazy evaluation pipeline with memoization support.

I wanted a clean way to chain transformations on data without immediately
computing everything — useful when you're working with large datasets or
expensive operations and only need partial results.
"""

from functools import wraps
from typing import Callable, Any, Iterable, Iterator


def memoize(func: Callable) -> Callable:
    """
    Decorator that caches function results based on arguments.
    
    I'm using a simple dict cache here. For production you'd want to handle
    unhashable args better, but this works for most cases I care about.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create a cache key from args/kwargs
        key = (args, tuple(sorted(kwargs.items())))
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    wrapper.cache = cache  # Expose cache for inspection/clearing
    return wrapper


class LazyPipeline:
    """
    A composable pipeline that defers computation until values are consumed.
    
    The idea is you build up a series of transformations, but nothing actually
    runs until you iterate or call .take() / .collect(). Saves a ton of CPU
    when you only need the first few results from a long chain.
    """
    
    def __init__(self, source: Iterable):
        """Initialize pipeline with a data source."""
        self._source = source
        self._transforms = []
    
    def map(self, func: Callable) -> 'LazyPipeline':
        """Apply a transformation to each element."""
        self._transforms.append(('map', func))
        return self
    
    def filter(self, predicate: Callable) -> 'LazyPipeline':
        """Keep only elements that satisfy the predicate."""
        self._transforms.append(('filter', predicate))
        return self
    
    def take(self, n: int) -> list:
        """
        Consume at most n elements from the pipeline.
        
        This is where the magic happens — we only compute what we need.
        """
        result = []
        for i, item in enumerate(self):
            if i >= n:
                break
            result.append(item)
        return result
    
    def collect(self) -> list:
        """Consume all elements and return as a list."""
        return list(self)
    
    def __iter__(self) -> Iterator:
        """
        Execute the pipeline lazily.
        
        Each transform is applied on-the-fly as we iterate. Nothing is
        materialized until you actually pull values out.
        """
        data = iter(self._source)
        
        for transform_type, func in self._transforms:
            if transform_type == 'map':
                data = map(func, data)
            elif transform_type == 'filter':
                data = filter(func, data)
        
        return data


def curry(func: Callable) -> Callable:
    """
    Transform a multi-argument function into a chain of single-argument functions.
    
    This is a simple currying implementation. It's not perfect (doesn't handle
    kwargs well) but it's useful for creating partially applied functions.
    """
    @wraps(func)
    def curried(*args):
        # Try to call the function with what we have
        try:
            return func(*args)
        except TypeError:
            # Not enough args, return a function that takes the rest
            def partial(*more_args):
                return curried(*(args + more_args))
            return partial
    
    return curried


@curry
def add_three(a: int, b: int, c: int) -> int:
    """Example curried function — adds three numbers."""
    return a + b + c


@memoize
def expensive_computation(n: int) -> int:
    """
    Simulates an expensive operation.
    
    In reality this would be something like an API call or complex calculation.
    The memoization ensures we only compute each value once.
    """
    print(f"  [Computing for n={n}...]")
    return n ** 2 + 2 * n + 1


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Start with a range — nothing is computed yet
    pipeline = LazyPipeline(range(1, 100))
    
    # Build up transformations — still no computation
    result = (pipeline
              .map(lambda x: x * 2)
              .filter(lambda x: x % 3 == 0)
              .map(lambda x: x ** 2)
              .take(5))  # Only now do we actually compute, and only 5 results
    
    print("First 5 results from lazy pipeline:")
    print(result)
    print()
    
    print("=== Memoization Demo ===\n")
    
    # First calls — these will compute
    print("First round of calls:")
    print(f"expensive_computation(3) = {expensive_computation(3)}")
    print(f"expensive_computation(5) = {expensive_computation(5)}")
    print()
    
    # Second calls — these hit the cache
    print("Second round (cached):")
    print(f"expensive_computation(3) = {expensive_computation(3)}")
    print(f"expensive_computation(5) = {expensive_computation(5)}")
    print()
    
    print("=== Currying Demo ===\n")
    
    # Normal usage
    print(f"add_three(1, 2, 3) = {add_three(1, 2, 3)}")
    
    # Partial application
    add_one = add_three(1)
    add_one_and_two = add_one(2)
    print(f"Curried: add_three(1)(2)(3) = {add_one_and_two(3)}")
    
    # You can also create specialized functions
    add_ten_and_five = add_three(10)(5)
    print(f"add_ten_and_five(7) = {add_ten_and_five(7)}")