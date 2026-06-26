"""
Date: 2026-06-26
Created a lazy evaluation pipeline system that chains transformations without materializing intermediate results — perfect for processing large data streams efficiently.
"""

#!/usr/bin/env python3
"""
Lazy evaluation pipeline for composable data transformations.

I got tired of running out of memory when processing large files, so I built
this to handle data transformations lazily — nothing gets computed until you
actually iterate over the results.
"""

from functools import wraps
from typing import Callable, Iterator, Any, TypeVar
from collections.abc import Iterable


T = TypeVar('T')
U = TypeVar('U')


class LazyPipeline:
    """
    A composable pipeline that applies transformations lazily.
    
    Transformations are stacked up but not executed until iteration.
    This lets you build complex data pipelines without loading everything
    into memory at once.
    """
    
    def __init__(self, source: Iterable):
        """Initialize pipeline with a data source."""
        self._source = source
        self._operations = []
    
    def map(self, func: Callable[[T], U]) -> 'LazyPipeline':
        """Apply a transformation to each element."""
        self._operations.append(('map', func))
        return self
    
    def filter(self, predicate: Callable[[T], bool]) -> 'LazyPipeline':
        """Keep only elements that satisfy the predicate."""
        self._operations.append(('filter', predicate))
        return self
    
    def take(self, n: int) -> 'LazyPipeline':
        """Limit output to first n elements."""
        self._operations.append(('take', n))
        return self
    
    def skip(self, n: int) -> 'LazyPipeline':
        """Skip the first n elements."""
        self._operations.append(('skip', n))
        return self
    
    def chunk(self, size: int) -> 'LazyPipeline':
        """Group elements into chunks of specified size."""
        self._operations.append(('chunk', size))
        return self
    
    def __iter__(self) -> Iterator:
        """
        Execute the pipeline lazily.
        
        This is where the magic happens — we build up an iterator chain
        that only computes values as they're requested.
        """
        result = iter(self._source)
        
        for operation, arg in self._operations:
            if operation == 'map':
                result = map(arg, result)
            elif operation == 'filter':
                result = filter(arg, result)
            elif operation == 'take':
                result = self._take(result, arg)
            elif operation == 'skip':
                result = self._skip(result, arg)
            elif operation == 'chunk':
                result = self._chunk(result, arg)
        
        return result
    
    @staticmethod
    def _take(iterable: Iterator, n: int) -> Iterator:
        """Helper to take first n items from iterator."""
        for i, item in enumerate(iterable):
            if i >= n:
                break
            yield item
    
    @staticmethod
    def _skip(iterable: Iterator, n: int) -> Iterator:
        """Helper to skip first n items from iterator."""
        for i, item in enumerate(iterable):
            if i >= n:
                yield item
    
    @staticmethod
    def _chunk(iterable: Iterator, size: int) -> Iterator:
        """Helper to group items into chunks."""
        chunk = []
        for item in iterable:
            chunk.append(item)
            if len(chunk) == size:
                yield tuple(chunk)
                chunk = []
        if chunk:  # yield remaining items as final chunk
            yield tuple(chunk)
    
    def to_list(self) -> list:
        """Materialize the pipeline into a list."""
        return list(self)
    
    def count(self) -> int:
        """Count elements without storing them."""
        return sum(1 for _ in self)
    
    def first(self, default=None):
        """Get first element or default if empty."""
        for item in self:
            return item
        return default


def memoize(func: Callable) -> Callable:
    """
    Memoization decorator for pure functions.
    
    Caches results based on arguments. I use this for expensive computations
    that get called repeatedly with the same inputs.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create a hashable key from args and kwargs
        key = (args, tuple(sorted(kwargs.items())))
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        
        return cache[key]
    
    # Expose cache for inspection/clearing
    wrapper.cache = cache
    return wrapper


def compose(*functions: Callable) -> Callable:
    """
    Compose functions right-to-left.
    
    compose(f, g, h)(x) is equivalent to f(g(h(x)))
    This is how I naturally think about function composition.
    """
    def composed(arg):
        result = arg
        for func in reversed(functions):
            result = func(result)
        return result
    return composed


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Example 1: Processing a large range without materializing it
    print("1. Processing numbers 1-1000, filtering evens, squaring, taking first 5:")
    pipeline = (
        LazyPipeline(range(1, 1001))
        .filter(lambda x: x % 2 == 0)
        .map(lambda x: x ** 2)
        .take(5)
    )
    print(f"   Result: {pipeline.to_list()}")
    print(f"   (only computed 5 values despite 1000-element source)\n")
    
    # Example 2: Chunking data
    print("2. Chunking first 10 odd numbers into pairs:")
    chunks = (
        LazyPipeline(range(1, 100))
        .filter(lambda x: x % 2 == 1)
        .take(10)
        .chunk(2)
        .to_list()
    )
    print(f"   Result: {chunks}\n")
    
    # Example 3: Memoization in action
    print("3. Memoization demo with expensive computation:")
    
    @memoize
    def expensive_fibonacci(n):
        """Recursive fibonacci with memoization."""
        if n < 2:
            return n
        return expensive_fibonacci(n - 1) + expensive_fibonacci(n - 2)
    
    print(f"   fib(30) = {expensive_fibonacci(30)}")
    print(f"   Cache size: {len(expensive_fibonacci.cache)} entries")
    print(f"   (without memoization, this would take forever)\n")
    
    # Example 4: Function composition
    print("4. Function composition:")
    
    add_ten = lambda x: x + 10
    multiply_by_two = lambda x: x * 2
    square = lambda x: x ** 2
    
    # Compose: square(multiply_by_two(add_ten(x)))
    transform = compose(square, multiply_by_two, add_ten)
    
    result = transform(5)  # (5 + 10) * 2 = 30, then 30^2 = 900
    print(f"   compose(square, mult_by_2, add_10)(5) = {result}")
    print(f"   Step by step: (5 + 10) * 2 = 30, then 30² = 900\n")
    
    # Example 5: Real-world use case — processing log lines
    print("5. Simulated log processing (skip header, filter errors, take first 3):")
    
    fake_logs = [
        "# Log started",
        "INFO: Server starting",
        "ERROR: Database connection failed",
        "INFO: Retrying connection",
        "ERROR: Timeout exceeded",
        "WARNING: High memory usage",
        "ERROR: Disk space low",
        "INFO: All systems normal"
    ]
    
    errors = (
        LazyPipeline(fake_logs)
        .skip(1)  # skip header
        .filter(lambda line: "ERROR" in line)
        .map(lambda line: line.replace("ERROR: ", ""))
        .take(3)
        .to_list()
    )
    
    print(f"   First 3 errors: {errors}")