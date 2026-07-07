"""
Date: 2026-07-07
Created a composable pipeline utility that lazily evaluates transformations and includes automatic memoization — been wanting to build this for my data processing scripts.
"""

#!/usr/bin/env python3
"""
Lazy evaluation pipeline with memoization support.

This module provides tools for building composable, lazy-evaluated data
transformation pipelines. I built this because I kept writing the same
boilerplate for chaining transformations in my data scripts.
"""

from functools import wraps
from typing import Callable, Any, Iterable, Iterator
from collections.abc import Hashable


def memoize(func: Callable) -> Callable:
    """
    Decorator that caches function results based on arguments.
    
    Only works with hashable arguments. I added this because some of my
    pipeline stages do expensive calculations that get repeated often.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create a cache key from args and sorted kwargs
        # kwargs need to be sorted for consistent hashing
        cache_key = (args, tuple(sorted(kwargs.items())))
        
        if cache_key not in cache:
            cache[cache_key] = func(*args, **kwargs)
        return cache[cache_key]
    
    # Expose cache for inspection/clearing if needed
    wrapper.cache = cache
    return wrapper


def curry(func: Callable) -> Callable:
    """
    Transforms a function to support partial application.
    
    Returns a curried version that accumulates arguments until it has enough
    to call the original function. Useful for building pipeline stages.
    """
    @wraps(func)
    def curried(*args, **kwargs):
        # Try calling the function with what we have
        try:
            return func(*args, **kwargs)
        except TypeError:
            # Not enough args yet, return a new curried function with these args baked in
            def partial(*more_args, **more_kwargs):
                combined_kwargs = {**kwargs, **more_kwargs}
                return curried(*(args + more_args), **combined_kwargs)
            return partial
    
    return curried


class LazyPipeline:
    """
    A composable pipeline that lazily evaluates transformations.
    
    I built this to avoid loading entire datasets into memory when I'm just
    chaining map/filter operations. Each stage is only computed when you
    actually iterate or materialize the results.
    """
    
    def __init__(self, iterable: Iterable):
        """Initialize pipeline with a data source."""
        self._iterable = iterable
        self._transformations = []
    
    def map(self, func: Callable) -> 'LazyPipeline':
        """Apply a transformation to each element."""
        self._transformations.append(('map', func))
        return self
    
    def filter(self, predicate: Callable) -> 'LazyPipeline':
        """Keep only elements that satisfy the predicate."""
        self._transformations.append(('filter', predicate))
        return self
    
    def take(self, n: int) -> 'LazyPipeline':
        """Limit the pipeline to the first n elements."""
        self._transformations.append(('take', n))
        return self
    
    def flat_map(self, func: Callable) -> 'LazyPipeline':
        """Map and flatten — useful when func returns iterables."""
        self._transformations.append(('flat_map', func))
        return self
    
    def __iter__(self) -> Iterator:
        """
        Execute the pipeline lazily.
        
        This is where the magic happens — we build up a chain of generators
        so nothing is computed until someone actually iterates.
        """
        result = iter(self._iterable)
        
        for operation, arg in self._transformations:
            if operation == 'map':
                result = map(arg, result)
            elif operation == 'filter':
                result = filter(arg, result)
            elif operation == 'take':
                result = self._take_generator(result, arg)
            elif operation == 'flat_map':
                result = self._flat_map_generator(result, arg)
        
        return result
    
    @staticmethod
    def _take_generator(iterable: Iterable, n: int) -> Iterator:
        """Helper generator for the take operation."""
        for i, item in enumerate(iterable):
            if i >= n:
                break
            yield item
    
    @staticmethod
    def _flat_map_generator(iterable: Iterable, func: Callable) -> Iterator:
        """Helper generator for flat_map operation."""
        for item in iterable:
            result = func(item)
            # Handle both iterables and single values
            if hasattr(result, '__iter__') and not isinstance(result, (str, bytes)):
                yield from result
            else:
                yield result
    
    def to_list(self) -> list:
        """Materialize the pipeline into a list."""
        return list(self)
    
    def reduce(self, func: Callable, initial: Any = None) -> Any:
        """
        Reduce the pipeline to a single value.
        
        I know functools.reduce exists, but this keeps the fluent API going.
        """
        iterator = iter(self)
        
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


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Example 1: Basic pipeline with lazy evaluation
    print("1. Basic pipeline (squares of even numbers):")
    numbers = range(1, 11)
    result = (LazyPipeline(numbers)
              .filter(lambda x: x % 2 == 0)
              .map(lambda x: x ** 2)
              .to_list())
    print(f"   Input: {list(range(1, 11))}")
    print(f"   Output: {result}\n")
    
    # Example 2: Demonstrating laziness with take
    print("2. Lazy evaluation with take (first 3 squares):")
    # This won't compute squares for all numbers, just the first 3 needed
    result = (LazyPipeline(range(1, 1000000))
              .map(lambda x: x ** 2)
              .take(3)
              .to_list())
    print(f"   Output: {result}\n")
    
    # Example 3: Memoization in action
    print("3. Memoized expensive function:")
    
    @memoize
    def expensive_calculation(n):
        """Simulates an expensive calculation."""
        print(f"   Computing for {n}...")
        return n ** 3
    
    print("   First call:")
    result1 = expensive_calculation(5)
    print(f"   Result: {result1}")
    
    print("   Second call (cached):")
    result2 = expensive_calculation(5)
    print(f"   Result: {result2}\n")
    
    # Example 4: Currying for partial application
    print("4. Curried function example:")
    
    @curry
    def multiply_three(a, b, c):
        return a * b * c
    
    double = multiply_three(2)
    double_and_triple = double(3)
    result = double_and_triple(4)
    print(f"   multiply_three(2)(3)(4) = {result}\n")
    
    # Example 5: Flat map for nested structures
    print("5. Flat map example (words to characters):")
    words = ["hello", "world"]
    result = (LazyPipeline(words)
              .flat_map(lambda word: list(word))
              .filter(lambda char: char in 'aeiou')
              .to_list())
    print(f"   Input: {words}")
    print(f"   Vowels: {result}\n")
    
    # Example 6: Reduce for aggregation
    print("6. Reduce example (sum of squares):")
    result = (LazyPipeline(range(1, 6))
              .map(lambda x: x ** 2)
              .reduce(lambda acc, x: acc + x, 0))
    print(f"   Sum of squares 1-5: {result}")