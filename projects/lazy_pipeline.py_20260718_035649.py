"""
Date: 2026-07-18
Created a composable lazy pipeline system that defers execution until values are pulled, with built-in memoization for expensive computations.
"""

"""
Lazy evaluation pipeline with memoization.

I wanted a clean way to chain operations on data without immediately executing them.
This lets me build up a series of transformations and only compute what I actually need.
"""

from functools import wraps
from typing import Any, Callable, Iterable, Iterator


def memoize(func: Callable) -> Callable:
    """
    Decorator that caches function results based on arguments.
    
    I use this for expensive operations in the pipeline so we don't
    recompute the same values over and over.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create a hashable key from args and kwargs
        key = (args, tuple(sorted(kwargs.items())))
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    wrapper.cache = cache  # Expose cache for inspection/clearing
    return wrapper


class LazyPipeline:
    """
    A lazy evaluation pipeline that chains transformations.
    
    Nothing actually executes until you call .collect() or iterate.
    This is great for working with large datasets or expensive operations
    where you might not need all the results.
    """
    
    def __init__(self, source: Iterable):
        """Initialize with a data source."""
        self._source = source
        self._operations = []
    
    def map(self, func: Callable) -> 'LazyPipeline':
        """Apply a function to each element."""
        self._operations.append(('map', func))
        return self
    
    def filter(self, predicate: Callable) -> 'LazyPipeline':
        """Keep only elements matching the predicate."""
        self._operations.append(('filter', predicate))
        return self
    
    def take(self, n: int) -> 'LazyPipeline':
        """Take only the first n elements."""
        self._operations.append(('take', n))
        return self
    
    def skip(self, n: int) -> 'LazyPipeline':
        """Skip the first n elements."""
        self._operations.append(('skip', n))
        return self
    
    def _execute(self) -> Iterator:
        """
        Execute the pipeline lazily.
        
        This is where the magic happens - we build up an iterator chain
        that processes elements one at a time, only when needed.
        """
        result = iter(self._source)
        
        for operation, arg in self._operations:
            if operation == 'map':
                result = map(arg, result)
            elif operation == 'filter':
                result = filter(arg, result)
            elif operation == 'take':
                result = (item for i, item in enumerate(result) if i < arg)
            elif operation == 'skip':
                # Skip the first n items
                for _ in range(arg):
                    try:
                        next(result)
                    except StopIteration:
                        break
        
        return result
    
    def collect(self) -> list:
        """Force evaluation and collect all results into a list."""
        return list(self._execute())
    
    def __iter__(self) -> Iterator:
        """Allow direct iteration over the pipeline."""
        return self._execute()


def curry(func: Callable, *fixed_args, **fixed_kwargs) -> Callable:
    """
    Partial application / currying helper.
    
    I built this to make it easier to create specialized versions of functions
    for use in pipelines. Way cleaner than writing lambdas everywhere.
    """
    @wraps(func)
    def curried(*args, **kwargs):
        combined_args = fixed_args + args
        combined_kwargs = {**fixed_kwargs, **kwargs}
        return func(*combined_args, **combined_kwargs)
    
    return curried


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Example 1: Basic pipeline with lazy evaluation
    print("1. Processing numbers 1-10:")
    
    @memoize
    def expensive_square(x: int) -> int:
        """Simulate an expensive operation."""
        print(f"   Computing square of {x}...")
        return x * x
    
    pipeline = (
        LazyPipeline(range(1, 11))
        .map(expensive_square)
        .filter(lambda x: x > 20)
        .take(3)
    )
    
    print("Pipeline created (nothing computed yet!)")
    print("Results:", pipeline.collect())
    print()
    
    # Example 2: Infinite sequence with take
    print("2. Working with infinite sequences:")
    
    def fibonacci():
        """Generate fibonacci numbers forever."""
        a, b = 0, 1
        while True:
            yield a
            a, b = b, a + b
    
    fib_pipeline = (
        LazyPipeline(fibonacci())
        .filter(lambda x: x % 2 == 0)  # Even fibonacci numbers
        .take(8)
    )
    
    print("First 8 even Fibonacci numbers:", fib_pipeline.collect())
    print()
    
    # Example 3: Currying example
    print("3. Using curry for cleaner transformations:")
    
    def multiply(x: int, factor: int) -> int:
        """Multiply x by factor."""
        return x * factor
    
    triple = curry(multiply, factor=3)
    double = curry(multiply, factor=2)
    
    numbers = LazyPipeline(range(1, 6))
    print("Triple then filter > 5:", numbers.map(triple).filter(lambda x: x > 5).collect())
    
    print()
    print("4. Memoization in action:")
    expensive_square.cache.clear()  # Clear cache first
    
    # Call the same function multiple times - only computes once per unique input
    results = LazyPipeline([2, 3, 2, 4, 3, 2]).map(expensive_square).collect()
    print("Results with duplicates:", results)
    print(f"Cache size: {len(expensive_square.cache)} (only computed unique values)")