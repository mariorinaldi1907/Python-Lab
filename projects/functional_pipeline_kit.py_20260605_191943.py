"""
Date: 2026-06-05
Created a functional programming toolkit that lets me chain operations lazily and cache expensive computations, perfect for ETL-style data pipelines.
"""

#!/usr/bin/env python3
"""
Functional programming utilities for composable data pipelines.
Implements lazy evaluation, memoization, and function composition.
"""

from functools import wraps
from typing import Callable, Iterable, Any, TypeVar
from collections.abc import Iterator


T = TypeVar('T')
U = TypeVar('U')


def memoize(func: Callable) -> Callable:
    """
    Decorator that caches function results based on arguments.
    Uses a dict to store computed values — good for expensive pure functions.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create a hashable key from args and kwargs
        # Note: Only works with hashable arguments
        key = (args, tuple(sorted(kwargs.items())))
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    # Expose cache for inspection/clearing if needed
    wrapper.cache = cache
    return wrapper


class LazySequence:
    """
    Wraps an iterable and applies transformations lazily.
    Nothing gets computed until you actually iterate or collect the results.
    """
    
    def __init__(self, source: Iterable):
        """Initialize with any iterable source."""
        self._source = source
    
    def map(self, func: Callable[[T], U]) -> 'LazySequence':
        """Apply a function to each element (lazily)."""
        def generator():
            for item in self._source:
                yield func(item)
        return LazySequence(generator())
    
    def filter(self, predicate: Callable[[T], bool]) -> 'LazySequence':
        """Keep only elements matching the predicate (lazily)."""
        def generator():
            for item in self._source:
                if predicate(item):
                    yield item
        return LazySequence(generator())
    
    def take(self, n: int) -> 'LazySequence':
        """Take only the first n elements (lazily)."""
        def generator():
            for i, item in enumerate(self._source):
                if i >= n:
                    break
                yield item
        return LazySequence(generator())
    
    def collect(self) -> list:
        """Force evaluation and return a list of results."""
        return list(self._source)
    
    def __iter__(self) -> Iterator:
        """Allow direct iteration over the lazy sequence."""
        return iter(self._source)


class Pipeline:
    """
    Composable function pipeline that chains operations left-to-right.
    Each step is a function that transforms the data.
    """
    
    def __init__(self, *functions: Callable):
        """Initialize with a sequence of functions to apply in order."""
        self.functions = list(functions)
    
    def add(self, func: Callable) -> 'Pipeline':
        """Add another function to the pipeline (returns new Pipeline)."""
        return Pipeline(*self.functions, func)
    
    def __call__(self, data: Any) -> Any:
        """
        Execute the pipeline on input data.
        Each function receives the output of the previous one.
        """
        result = data
        for func in self.functions:
            result = func(result)
        return result
    
    def __or__(self, other: 'Pipeline') -> 'Pipeline':
        """Allow combining pipelines with the | operator."""
        return Pipeline(*self.functions, *other.functions)


def curry(func: Callable, arity: int = None) -> Callable:
    """
    Convert a function to its curried form.
    Allows partial application by supplying arguments one at a time.
    
    Example: add(x, y) becomes add(x)(y)
    """
    if arity is None:
        # Try to infer arity from function signature
        arity = func.__code__.co_argcount
    
    def curried(*args):
        if len(args) >= arity:
            return func(*args[:arity])
        else:
            # Not enough args yet, return a new curried function
            def partial(*more_args):
                return curried(*(args + more_args))
            return partial
    
    return curried


if __name__ == "__main__":
    print("=== Functional Programming Utilities Demo ===\n")
    
    # Demo 1: Memoization with expensive Fibonacci
    print("1. Memoization Example:")
    
    @memoize
    def fibonacci(n: int) -> int:
        """Classic recursive Fibonacci with memoization."""
        if n <= 1:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)
    
    print(f"   fib(30) = {fibonacci(30)}")
    print(f"   fib(35) = {fibonacci(35)}")
    print(f"   Cache has {len(fibonacci.cache)} entries\n")
    
    # Demo 2: Lazy evaluation with LazySequence
    print("2. Lazy Sequence Example:")
    
    # Infinite generator — would hang without lazy eval
    def naturals():
        n = 0
        while True:
            yield n
            n += 1
    
    result = (LazySequence(naturals())
              .filter(lambda x: x % 2 == 0)  # only evens
              .map(lambda x: x ** 2)         # square them
              .take(10)                      # first 10 only
              .collect())
    
    print(f"   First 10 even squares: {result}\n")
    
    # Demo 3: Function pipeline composition
    print("3. Pipeline Example:")
    
    # Data cleaning pipeline
    clean_text = Pipeline(
        str.strip,
        str.lower,
        lambda s: s.replace(',', ''),
        lambda s: s.split()
    )
    
    raw_data = "  Hello, World,  This Is A Test  "
    cleaned = clean_text(raw_data)
    print(f"   Input:  '{raw_data}'")
    print(f"   Output: {cleaned}\n")
    
    # Demo 4: Currying for reusable partial functions
    print("4. Currying Example:")
    
    @curry
    def multiply(x, y, z):
        """Multiply three numbers together."""
        return x * y * z
    
    double = multiply(2)      # partially applied
    triple = multiply(3)      # different partial application
    
    print(f"   multiply(2)(3)(4) = {multiply(2)(3)(4)}")
    print(f"   double(5)(6) = {double(5)(6)}")
    print(f"   triple(4)(5) = {triple(4)(5)}")