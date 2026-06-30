"""
Date: 2026-06-30
Created a functional pipeline system that lazily evaluates transformations and supports memoization, because I got tired of writing nested map/filter calls that process everything immediately.
"""

#!/usr/bin/env python3
"""
Lazy evaluation pipeline with memoization support.
Allows chaining transformations that only execute when results are consumed.
"""

from functools import wraps
from typing import Callable, Iterable, Any, Iterator
import itertools


def memoize(func: Callable) -> Callable:
    """
    Decorator that caches function results based on arguments.
    Uses a dict to store previously computed values.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Convert kwargs to a frozenset for hashing
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    wrapper.cache = cache
    wrapper.cache_clear = lambda: cache.clear()
    return wrapper


class LazyPipeline:
    """
    A lazy evaluation pipeline that chains transformations without executing them
    until the results are actually needed (e.g., when converting to list or iterating).
    """
    
    def __init__(self, iterable: Iterable):
        """Initialize with an iterable source."""
        self._iterable = iterable
    
    def map(self, func: Callable) -> 'LazyPipeline':
        """
        Apply a function to each element lazily.
        Returns a new pipeline instead of executing immediately.
        """
        self._iterable = map(func, self._iterable)
        return self
    
    def filter(self, predicate: Callable) -> 'LazyPipeline':
        """
        Filter elements based on a predicate function.
        Only keeps elements where predicate returns True.
        """
        self._iterable = filter(predicate, self._iterable)
        return self
    
    def take(self, n: int) -> 'LazyPipeline':
        """
        Take only the first n elements from the pipeline.
        Useful for limiting infinite sequences.
        """
        self._iterable = itertools.islice(self._iterable, n)
        return self
    
    def chunk(self, size: int) -> 'LazyPipeline':
        """
        Break the sequence into chunks of a given size.
        The last chunk might be smaller if there aren't enough elements.
        """
        def chunker(iterable, n):
            iterator = iter(iterable)
            while True:
                chunk = list(itertools.islice(iterator, n))
                if not chunk:
                    break
                yield chunk
        
        self._iterable = chunker(self._iterable, size)
        return self
    
    def flatten(self) -> 'LazyPipeline':
        """
        Flatten one level of nested iterables.
        [[1, 2], [3, 4]] becomes [1, 2, 3, 4]
        """
        self._iterable = itertools.chain.from_iterable(self._iterable)
        return self
    
    def enumerate_from(self, start: int = 0) -> 'LazyPipeline':
        """
        Add indices to elements, starting from the given number.
        Returns tuples of (index, element).
        """
        self._iterable = enumerate(self._iterable, start=start)
        return self
    
    def __iter__(self) -> Iterator:
        """Allow the pipeline to be iterated directly."""
        return iter(self._iterable)
    
    def to_list(self) -> list:
        """
        Materialize the pipeline into a list.
        This is when all the transformations actually execute.
        """
        return list(self._iterable)
    
    def to_set(self) -> set:
        """Materialize the pipeline into a set."""
        return set(self._iterable)
    
    def reduce(self, func: Callable, initial: Any = None) -> Any:
        """
        Reduce the pipeline to a single value using a binary function.
        If initial is provided, it's used as the starting value.
        """
        from functools import reduce as functools_reduce
        if initial is None:
            return functools_reduce(func, self._iterable)
        return functools_reduce(func, self._iterable, initial)


def curry(func: Callable) -> Callable:
    """
    Transform a function to support partial application.
    Each call with fewer arguments than needed returns a new function.
    """
    def curried(*args, **kwargs):
        try:
            # Try to call the function with current arguments
            return func(*args, **kwargs)
        except TypeError:
            # If it fails (not enough args), return a partial function
            def partial(*more_args, **more_kwargs):
                combined_kwargs = {**kwargs, **more_kwargs}
                return curried(*(args + more_args), **combined_kwargs)
            return partial
    
    return curried


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Demo 1: Basic pipeline with map and filter
    print("1. Squaring even numbers from 1-10:")
    result = (LazyPipeline(range(1, 11))
              .filter(lambda x: x % 2 == 0)
              .map(lambda x: x ** 2)
              .to_list())
    print(f"   Result: {result}\n")
    
    # Demo 2: Chunking and flattening
    print("2. Chunking numbers into groups of 3, then flattening:")
    result = (LazyPipeline(range(1, 11))
              .chunk(3)
              .to_list())
    print(f"   Chunked: {result}")
    flattened = LazyPipeline(result).flatten().to_list()
    print(f"   Flattened: {flattened}\n")
    
    # Demo 3: Memoization
    print("3. Memoization demo (expensive Fibonacci):")
    
    @memoize
    def fib(n: int) -> int:
        """Calculate Fibonacci number recursively with memoization."""
        if n < 2:
            return n
        return fib(n - 1) + fib(n - 2)
    
    result = LazyPipeline(range(15)).map(fib).to_list()
    print(f"   First 15 Fibonacci numbers: {result}")
    print(f"   Cache size: {len(fib.cache)} entries\n")
    
    # Demo 4: Currying
    print("4. Currying demo:")
    
    @curry
    def multiply_three(a, b, c):
        """Multiply three numbers together."""
        return a * b * c
    
    # Partial application
    double = multiply_three(2)
    double_and_triple = double(3)
    result = double_and_triple(4)
    print(f"   2 * 3 * 4 = {result}")
    
    # Can also call normally
    print(f"   5 * 6 * 7 = {multiply_three(5, 6, 7)}\n")
    
    # Demo 5: Pipeline with reduction
    print("5. Sum of squares of odd numbers from 1-20:")
    result = (LazyPipeline(range(1, 21))
              .filter(lambda x: x % 2 == 1)
              .map(lambda x: x ** 2)
              .reduce(lambda acc, x: acc + x, 0))
    print(f"   Result: {result}\n")
    
    print("=== All demos complete ===")