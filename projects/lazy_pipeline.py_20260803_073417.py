"""
Date: 2026-08-03
Created a functional pipeline that lazily evaluates chained operations with automatic memoization and currying support — helps me avoid computing stuff I don't need.
"""

#!/usr/bin/env python3
"""
Lazy evaluation pipeline with currying and memoization.

I got tired of writing the same data transformation chains over and over,
so I built this to handle lazy evaluation (only compute what's needed),
automatic memoization (cache expensive operations), and currying (partial
application of multi-arg functions).
"""

from functools import wraps
from typing import Callable, Iterator, Any, Tuple
from itertools import islice


def memoize(func: Callable) -> Callable:
    """
    Decorator that caches function results based on arguments.
    
    Uses a dict to store previous results. Only works with hashable args,
    but that's fine for most of my use cases.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args):
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result
    
    # Expose cache for inspection/clearing if needed
    wrapper.cache = cache
    return wrapper


def curry(func: Callable) -> Callable:
    """
    Auto-curry a function so you can partially apply arguments.
    
    This lets me build specialized versions of functions by fixing some args.
    Returns a new function if not all args provided, otherwise executes.
    """
    @wraps(func)
    def curried(*args, **kwargs):
        # Try to call the function with what we have
        try:
            return func(*args, **kwargs)
        except TypeError:
            # Not enough args, return a partial application
            def partial(*more_args, **more_kwargs):
                combined_args = args + more_args
                combined_kwargs = {**kwargs, **more_kwargs}
                return curried(*combined_args, **combined_kwargs)
            return partial
    
    return curried


class LazyPipeline:
    """
    A pipeline that lazily evaluates transformations on an iterable.
    
    I wanted to chain operations without computing everything upfront.
    Only evaluates when you actually pull data out (via list(), take(), etc).
    """
    
    def __init__(self, source: Iterator):
        """Initialize with an iterable source."""
        self.source = iter(source)
        self.operations = []
    
    def map(self, func: Callable) -> 'LazyPipeline':
        """Apply a function to each element (lazily)."""
        self.operations.append(('map', func))
        return self
    
    def filter(self, predicate: Callable) -> 'LazyPipeline':
        """Keep only elements that match the predicate (lazily)."""
        self.operations.append(('filter', predicate))
        return self
    
    def take(self, n: int) -> list:
        """
        Consume and return first n elements.
        
        This is where evaluation actually happens. We only compute what's needed.
        """
        iterator = self._evaluate()
        return list(islice(iterator, n))
    
    def collect(self) -> list:
        """Consume the entire pipeline and return all results."""
        return list(self._evaluate())
    
    def _evaluate(self) -> Iterator:
        """
        Apply all queued operations to the source iterator.
        
        This is the magic — we chain all operations together as nested generators
        so nothing gets computed until someone pulls values out.
        """
        result = self.source
        
        for op_type, op_func in self.operations:
            if op_type == 'map':
                result = map(op_func, result)
            elif op_type == 'filter':
                result = filter(op_func, result)
        
        return result
    
    def __iter__(self):
        """Make the pipeline itself iterable."""
        return self._evaluate()


def pipe(*functions: Callable) -> Callable:
    """
    Compose functions left-to-right (normal reading order).
    
    I always got confused with right-to-left composition, so this reads
    naturally: pipe(f, g, h)(x) means f(x) -> g -> h.
    """
    def piped(value):
        result = value
        for func in functions:
            result = func(result)
        return result
    return piped


# Some example functions to demo the utilities
@memoize
def expensive_computation(n: int) -> int:
    """Simulate an expensive calculation (with caching)."""
    print(f"  [Computing fibonacci({n})...]")
    if n <= 1:
        return n
    return expensive_computation(n - 1) + expensive_computation(n - 2)


@curry
def multiply_add(x: int, y: int, z: int) -> int:
    """Curryable function: (x * y) + z"""
    return x * y + z


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Create a lazy pipeline that only computes what we take
    print("1. Lazy pipeline (only computing first 5):")
    numbers = range(1, 100)  # Large range, but we won't compute it all
    result = (LazyPipeline(numbers)
              .filter(lambda x: x % 2 == 0)  # even numbers
              .map(lambda x: x ** 2)          # square them
              .take(5))                       # only take 5
    print(f"   Result: {result}\n")
    
    
    print("2. Memoization (notice cached calls):")
    print(f"   fib(10) = {expensive_computation(10)}")
    print(f"   fib(10) again = {expensive_computation(10)}")  # cached, no recompute
    print(f"   Cache size: {len(expensive_computation.cache)} entries\n")
    
    
    print("3. Currying (partial application):")
    times_2 = multiply_add(2)      # Fix first arg
    times_2_plus_10 = times_2(y=10)  # Fix second arg
    print(f"   (2 * 10) + 5 = {times_2_plus_10(5)}")
    print(f"   (2 * 10) + 3 = {times_2_plus_10(3)}\n")
    
    
    print("4. Function composition (pipe):")
    add_10 = lambda x: x + 10
    square = lambda x: x ** 2
    halve = lambda x: x / 2
    
    transform = pipe(add_10, square, halve)
    print(f"   pipe(add_10, square, halve)(5) = {transform(5)}")
    print(f"   Breakdown: 5 -> 15 -> 225 -> 112.5\n")
    
    
    print("5. Combining it all (lazy + memoized operations):")
    @memoize
    def slow_transform(x):
        """Memoized transformation."""
        return x * 3 + 7
    
    pipeline_result = (LazyPipeline(range(20))
                       .filter(lambda x: x > 5)
                       .map(slow_transform)
                       .take(3))
    print(f"   First 3 transformed values > 5: {pipeline_result}")