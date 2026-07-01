"""
Date: 2026-07-01
Created a composable pipeline system with lazy evaluation, automatic memoization, and currying support because I got tired of writing nested function calls.
"""

"""
Lazy evaluation pipeline with currying and memoization support.

I built this because I kept writing deeply nested function compositions
and wanted something cleaner. The lazy evaluation means you can build
up expensive operations without executing them until you need the result.
"""

from functools import wraps
from typing import Any, Callable, Iterator


def memoize(func: Callable) -> Callable:
    """
    Decorator that caches function results based on arguments.
    
    Works for functions with hashable arguments. I use this all the time
    for expensive computations that get called repeatedly with same inputs.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create cache key from args and kwargs
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    wrapper.cache = cache  # expose cache for inspection
    return wrapper


def curry(func: Callable, *initial_args, **initial_kwargs) -> Callable:
    """
    Partial application that keeps returning functions until all args satisfied.
    
    Different from functools.partial because it chains nicely and waits
    until you've provided enough arguments before executing.
    """
    @wraps(func)
    def curried(*args, **kwargs):
        combined_args = initial_args + args
        combined_kwargs = {**initial_kwargs, **kwargs}
        
        # Try to call the function - if it needs more args, return another curry
        try:
            return func(*combined_args, **combined_kwargs)
        except TypeError:
            return curry(func, *combined_args, **combined_kwargs)
    
    return curried


class LazyPipeline:
    """
    Composable pipeline that delays execution until explicitly evaluated.
    
    This is the main class - lets you chain operations together and only
    runs them when you call .evaluate(). Super useful for building complex
    data transformations without running everything eagerly.
    """
    
    def __init__(self, data: Any = None):
        """Initialize with optional starting data."""
        self._data = data
        self._operations = []
    
    def pipe(self, func: Callable, *args, **kwargs) -> 'LazyPipeline':
        """
        Add a transformation to the pipeline.
        
        The function will receive the current data as first argument,
        followed by any additional args/kwargs you provide.
        """
        self._operations.append((func, args, kwargs))
        return self
    
    def map(self, func: Callable) -> 'LazyPipeline':
        """Apply a function to each element (assumes data is iterable)."""
        def _map_func(data):
            return (func(item) for item in data)
        return self.pipe(_map_func)
    
    def filter(self, predicate: Callable) -> 'LazyPipeline':
        """Keep only elements matching the predicate."""
        def _filter_func(data):
            return (item for item in data if predicate(item))
        return self.pipe(_filter_func)
    
    def take(self, n: int) -> 'LazyPipeline':
        """Take only the first n elements."""
        def _take_func(data):
            for i, item in enumerate(data):
                if i >= n:
                    break
                yield item
        return self.pipe(_take_func)
    
    def evaluate(self) -> Any:
        """
        Execute all queued operations and return the result.
        
        This is when the actual work happens - everything before this
        is just building up the operation queue.
        """
        result = self._data
        for func, args, kwargs in self._operations:
            result = func(result, *args, **kwargs)
        return result
    
    def evaluate_lazy(self) -> Iterator:
        """
        Like evaluate() but returns an iterator for memory efficiency.
        
        Use this when dealing with large datasets - keeps things lazy
        all the way through instead of materializing intermediate results.
        """
        result = self.evaluate()
        if hasattr(result, '__iter__') and not isinstance(result, (str, bytes)):
            return iter(result)
        return iter([result])


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Example 1: Basic pipeline with memoization
    print("1. Fibonacci with memoization:")
    
    @memoize
    def fibonacci(n: int) -> int:
        """Classic recursive fibonacci - expensive without memoization."""
        if n <= 1:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)
    
    print(f"   fib(30) = {fibonacci(30)}")
    print(f"   Cache size: {len(fibonacci.cache)}")
    
    # Example 2: Currying for reusable functions
    print("\n2. Currying example:")
    
    def multiply(x: int, y: int, z: int) -> int:
        """Multiply three numbers."""
        return x * y * z
    
    double = curry(multiply, 2)
    double_and_triple = double(3)
    result = double_and_triple(5)  # 2 * 3 * 5
    print(f"   Curried multiplication: 2 * 3 * 5 = {result}")
    
    # Example 3: Complex lazy pipeline
    print("\n3. Processing numbers lazily:")
    
    def square(x: int) -> int:
        print(f"   -> Squaring {x}")  # to show it's lazy
        return x * x
    
    numbers = range(1, 100)  # large range but won't process all
    
    pipeline = (
        LazyPipeline(numbers)
        .filter(lambda x: x % 2 == 0)  # only evens
        .map(square)                    # square them
        .take(5)                        # take first 5
    )
    
    print("   Pipeline built (nothing executed yet)")
    print("   Now evaluating...")
    result = list(pipeline.evaluate())
    print(f"   Result: {result}")
    
    # Example 4: Chaining with custom operations
    print("\n4. Custom pipeline operations:")
    
    data = [1, 2, 3, 4, 5]
    result = (
        LazyPipeline(data)
        .pipe(lambda d: [x * 2 for x in d])
        .pipe(sum)
        .pipe(lambda x: f"Sum is {x}")
        .evaluate()
    )
    print(f"   {result}")
    
    print("\n✓ All demos completed successfully")