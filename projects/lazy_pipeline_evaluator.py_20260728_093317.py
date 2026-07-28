"""
Date: 2026-07-28
Created a functional programming utility that combines lazy evaluation, memoization, and method chaining to process sequences efficiently without computing everything upfront.
"""

#!/usr/bin/env python3
"""
Lazy evaluation pipeline with memoization.

This module implements a lazy sequence processor that defers computation
until values are actually needed. Inspired by functional programming patterns
but made practical for everyday Python tasks.
"""

from functools import wraps
from typing import Callable, Iterator, Any, Optional
import itertools


def memoize(func: Callable) -> Callable:
    """
    Cache function results to avoid recomputation.
    
    I added this because without it, lazy evaluation can sometimes compute
    the same intermediate values multiple times when you iterate over
    the pipeline more than once.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Only cache if args are hashable
        try:
            key = (args, tuple(sorted(kwargs.items())))
            if key not in cache:
                cache[key] = func(*args, **kwargs)
            return cache[key]
        except TypeError:
            # If args aren't hashable, just call the function
            return func(*args, **kwargs)
    
    wrapper.cache = cache
    wrapper.cache_clear = lambda: cache.clear()
    return wrapper


class LazyPipeline:
    """
    A lazy evaluation pipeline that chains transformations without immediate execution.
    
    Operations like map, filter, and take don't actually process data until
    you call a terminal operation like collect() or reduce(). This means you
    can build complex transformation chains without wasting memory or CPU
    on elements you'll never use.
    """
    
    def __init__(self, source: Iterator):
        """Initialize with an iterable source."""
        self._source = source
        self._memo_enabled = False
    
    def map(self, func: Callable) -> 'LazyPipeline':
        """
        Apply a function to each element lazily.
        
        Returns a new pipeline, doesn't modify the original.
        """
        def generator():
            for item in self._source:
                yield func(item)
        
        return LazyPipeline(generator())
    
    def filter(self, predicate: Callable) -> 'LazyPipeline':
        """Keep only elements that satisfy the predicate."""
        def generator():
            for item in self._source:
                if predicate(item):
                    yield item
        
        return LazyPipeline(generator())
    
    def take(self, n: int) -> 'LazyPipeline':
        """
        Take only the first n elements.
        
        This is where lazy evaluation really shines — you can process infinite
        sequences and just grab what you need.
        """
        def generator():
            for item in itertools.islice(self._source, n):
                yield item
        
        return LazyPipeline(generator())
    
    def skip(self, n: int) -> 'LazyPipeline':
        """Skip the first n elements."""
        def generator():
            for i, item in enumerate(self._source):
                if i >= n:
                    yield item
        
        return LazyPipeline(generator())
    
    def chunk(self, size: int) -> 'LazyPipeline':
        """Group elements into chunks of the specified size."""
        def generator():
            iterator = iter(self._source)
            while True:
                chunk = list(itertools.islice(iterator, size))
                if not chunk:
                    break
                yield chunk
        
        return LazyPipeline(generator())
    
    def flatten(self) -> 'LazyPipeline':
        """Flatten one level of nesting."""
        def generator():
            for item in self._source:
                if hasattr(item, '__iter__') and not isinstance(item, (str, bytes)):
                    for subitem in item:
                        yield subitem
                else:
                    yield item
        
        return LazyPipeline(generator())
    
    def collect(self) -> list:
        """Terminal operation: consume the pipeline and return a list."""
        return list(self._source)
    
    def reduce(self, func: Callable, initial: Optional[Any] = None) -> Any:
        """
        Terminal operation: reduce the sequence to a single value.
        
        I went back and forth on whether to require an initial value,
        but decided to make it optional for flexibility.
        """
        iterator = iter(self._source)
        
        if initial is None:
            try:
                value = next(iterator)
            except StopIteration:
                raise TypeError("reduce() of empty sequence with no initial value")
        else:
            value = initial
        
        for item in iterator:
            value = func(value, item)
        
        return value
    
    def for_each(self, func: Callable) -> None:
        """Terminal operation: apply a function to each element for side effects."""
        for item in self._source:
            func(item)


def lazy(iterable: Iterator) -> LazyPipeline:
    """
    Helper function to create a lazy pipeline.
    
    Makes the API cleaner — you can just write lazy([1,2,3]) instead of
    LazyPipeline(iter([1,2,3])).
    """
    return LazyPipeline(iter(iterable))


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Example 1: Basic transformation chain
    print("1. Square even numbers, take first 5:")
    result = lazy(range(100)).filter(lambda x: x % 2 == 0).map(lambda x: x ** 2).take(5).collect()
    print(f"   Result: {result}\n")
    
    # Example 2: Infinite sequence (this is where lazy really matters)
    print("2. First 10 Fibonacci numbers (from infinite generator):")
    
    def fibonacci():
        """Generate Fibonacci numbers indefinitely."""
        a, b = 0, 1
        while True:
            yield a
            a, b = b, a + b
    
    fibs = lazy(fibonacci()).take(10).collect()
    print(f"   Result: {fibs}\n")
    
    # Example 3: Chunking and flattening
    print("3. Chunk numbers into groups of 3, then flatten:")
    result = lazy(range(10)).chunk(3).collect()
    print(f"   Chunked: {result}")
    
    flattened = lazy(range(10)).chunk(3).flatten().collect()
    print(f"   Flattened back: {flattened}\n")
    
    # Example 4: Reduction
    print("4. Sum of squares of odd numbers from 1 to 20:")
    total = lazy(range(1, 21)).filter(lambda x: x % 2 == 1).map(lambda x: x ** 2).reduce(lambda acc, x: acc + x, 0)
    print(f"   Result: {total}\n")
    
    # Example 5: Complex pipeline showing lazy evaluation benefit
    print("5. Process 1M numbers but only take 3 (lazy = efficient):")
    
    @memoize
    def expensive_operation(x):
        """Simulate expensive computation that we want to avoid when possible."""
        return x * 2 + 1
    
    # This only computes expensive_operation 3 times, not 1 million!
    result = lazy(range(1_000_000)).map(expensive_operation).take(3).collect()
    print(f"   Result: {result}")
    print(f"   Memoization cache size: {len(expensive_operation.cache)} (saved computation!)\n")
    
    print("=== Demo complete ===")