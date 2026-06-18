"""
Date: 2026-06-18
Created a functional programming utility that combines lazy evaluation, memoization, and pipeline composition to make data transformations more elegant and performant.
"""

"""
Functional programming toolkit with lazy evaluation, memoization, and pipelines.

I wanted to build something that makes working with data transformations more
elegant, inspired by how languages like Haskell and Clojure handle sequences.
"""

from functools import wraps
from typing import Callable, Iterable, Any, TypeVar
from collections.abc import Iterator


T = TypeVar('T')
U = TypeVar('U')


def memoize(func: Callable) -> Callable:
    """
    Decorator that caches function results based on arguments.
    
    I'm using a simple dict here because for most use cases, the memory tradeoff
    is worth it. For production code with unbounded inputs, you'd want an LRU cache.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create a hashable key from args and kwargs
        # This won't work for unhashable types, but that's a known limitation
        key = (args, tuple(sorted(kwargs.items())))
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    return wrapper


class LazySequence:
    """
    Lazy evaluation wrapper for iterables.
    
    Operations don't execute until you actually consume the data. This is great
    for working with large datasets or expensive computations where you might
    only need part of the result.
    """
    
    def __init__(self, iterable: Iterable[T]):
        """Initialize with any iterable — won't be consumed until needed."""
        self._iterable = iterable
    
    def map(self, func: Callable[[T], U]) -> 'LazySequence':
        """Apply a function to each element, lazily."""
        def generator():
            for item in self._iterable:
                yield func(item)
        return LazySequence(generator())
    
    def filter(self, predicate: Callable[[T], bool]) -> 'LazySequence':
        """Keep only elements that satisfy the predicate, lazily."""
        def generator():
            for item in self._iterable:
                if predicate(item):
                    yield item
        return LazySequence(generator())
    
    def take(self, n: int) -> 'LazySequence':
        """Take the first n elements, lazily."""
        def generator():
            count = 0
            for item in self._iterable:
                if count >= n:
                    break
                yield item
                count += 1
        return LazySequence(generator())
    
    def collect(self) -> list:
        """Force evaluation and return results as a list."""
        return list(self._iterable)
    
    def __iter__(self) -> Iterator[T]:
        """Make the sequence iterable."""
        return iter(self._iterable)


class Pipeline:
    """
    Function composition pipeline with left-to-right application.
    
    I find left-to-right more intuitive than traditional math notation because
    it reads like a sequence of transformations: data goes in one end, gets
    transformed step by step, comes out the other.
    """
    
    def __init__(self, *functions: Callable):
        """Initialize with a sequence of functions to apply in order."""
        self.functions = functions
    
    def __call__(self, value: Any) -> Any:
        """Apply all functions in sequence to the input value."""
        result = value
        for func in self.functions:
            result = func(result)
        return result
    
    def then(self, func: Callable) -> 'Pipeline':
        """Add another function to the pipeline and return a new Pipeline."""
        return Pipeline(*self.functions, func)


def curry(func: Callable) -> Callable:
    """
    Convert a function to accept arguments one at a time.
    
    This is a simplified currying implementation. Real currying is more complex,
    but this handles the common case of partially applying functions.
    """
    @wraps(func)
    def curried(*args, **kwargs):
        # Try to call the function with current args
        try:
            return func(*args, **kwargs)
        except TypeError:
            # If it fails (not enough args), return a partial application
            def partial(*more_args, **more_kwargs):
                combined_args = args + more_args
                combined_kwargs = {**kwargs, **more_kwargs}
                return curried(*combined_args, **combined_kwargs)
            return partial
    
    return curried


if __name__ == "__main__":
    print("=== Functional Pipeline Toolkit Demo ===\n")
    
    # Demo 1: Memoization with expensive computation
    print("1. Memoization Demo:")
    
    @memoize
    def fibonacci(n):
        """Classic recursive fibonacci — super slow without memoization."""
        if n <= 1:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)
    
    print(f"   fibonacci(35) = {fibonacci(35)}")
    print(f"   fibonacci(40) = {fibonacci(40)} (instant thanks to memoization!)")
    
    # Demo 2: Lazy evaluation
    print("\n2. Lazy Evaluation Demo:")
    numbers = range(1, 1001)  # Large range
    
    # This chain doesn't execute until we call collect()
    result = (LazySequence(numbers)
              .filter(lambda x: x % 2 == 0)  # Even numbers only
              .map(lambda x: x ** 2)          # Square them
              .filter(lambda x: x > 100)      # Only large squares
              .take(5)                        # Just the first 5
              .collect())
    
    print(f"   First 5 even squares > 100: {result}")
    
    # Demo 3: Pipeline composition
    print("\n3. Pipeline Composition Demo:")
    
    # Build a text processing pipeline
    strip_text = lambda s: s.strip()
    to_upper = lambda s: s.upper()
    add_exclamation = lambda s: f"{s}!!!"
    
    text_pipeline = Pipeline(strip_text, to_upper, add_exclamation)
    
    messy_input = "  hello world  "
    clean_output = text_pipeline(messy_input)
    print(f"   '{messy_input}' -> '{clean_output}'")
    
    # Can extend pipelines
    extended_pipeline = text_pipeline.then(lambda s: f">>> {s}")
    print(f"   Extended: '{extended_pipeline(messy_input)}'")
    
    # Demo 4: Currying
    print("\n4. Currying Demo:")
    
    @curry
    def multiply(a, b, c):
        """Multiply three numbers together."""
        return a * b * c
    
    # Can apply arguments one at a time
    double = multiply(2)
    double_and_triple = double(3)
    result = double_and_triple(5)
    
    print(f"   multiply(2)(3)(5) = {result}")
    
    # Or all at once
    print(f"   multiply(2, 3, 5) = {multiply(2, 3, 5)}")
    
    print("\n=== All demos completed successfully! ===")