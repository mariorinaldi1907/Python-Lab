"""
Date: 2026-07-18
Created a composable function pipeline with lazy evaluation and automatic memoization because I kept writing the same nested map/filter patterns everywhere.
"""

"""
Functional programming utilities: pipelines with lazy evaluation and memoization.

I got tired of writing deeply nested function calls and wanted something cleaner.
This lets me chain operations that only evaluate when needed, with automatic caching.
"""

from functools import wraps, reduce
from typing import Callable, Iterable, Any, TypeVar
from collections.abc import Iterator


T = TypeVar('T')
U = TypeVar('U')


def memoize(func: Callable) -> Callable:
    """
    Decorator that caches function results based on arguments.
    
    Uses a dict to store results — not thread-safe but good enough for my scripts.
    I'm avoiding functools.lru_cache because I want to see the implementation.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create a hashable key from args and kwargs
        key = (args, tuple(sorted(kwargs.items())))
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        
        return cache[key]
    
    # Expose cache for debugging if needed
    wrapper.cache = cache
    return wrapper


class LazySequence:
    """
    Wraps an iterable to enable lazy evaluation of transformations.
    
    Operations like map and filter don't execute immediately — they just
    stack up transformations that run when you actually iterate or collect.
    """
    
    def __init__(self, iterable: Iterable[T]):
        """Initialize with any iterable."""
        self._iterable = iterable
    
    def map(self, func: Callable[[T], U]) -> 'LazySequence':
        """Apply a function to each element lazily."""
        def generator():
            for item in self._iterable:
                yield func(item)
        
        return LazySequence(generator())
    
    def filter(self, predicate: Callable[[T], bool]) -> 'LazySequence':
        """Filter elements lazily based on a predicate."""
        def generator():
            for item in self._iterable:
                if predicate(item):
                    yield item
        
        return LazySequence(generator())
    
    def take(self, n: int) -> 'LazySequence':
        """Take only the first n elements."""
        def generator():
            count = 0
            for item in self._iterable:
                if count >= n:
                    break
                yield item
                count += 1
        
        return LazySequence(generator())
    
    def collect(self) -> list:
        """Force evaluation and return a list of results."""
        return list(self._iterable)
    
    def __iter__(self) -> Iterator:
        """Make LazySequence iterable."""
        return iter(self._iterable)


class Pipeline:
    """
    Compose functions into a pipeline that flows left to right.
    
    Instead of f(g(h(x))), you can write Pipeline(h, g, f)(x).
    This reads much more naturally when you have lots of transformations.
    """
    
    def __init__(self, *functions: Callable):
        """Initialize pipeline with a sequence of functions."""
        if not functions:
            raise ValueError("Pipeline needs at least one function")
        
        self.functions = functions
    
    def __call__(self, initial_value: Any) -> Any:
        """Execute the pipeline by threading the value through each function."""
        return reduce(lambda value, func: func(value), self.functions, initial_value)
    
    def __rshift__(self, other: 'Pipeline') -> 'Pipeline':
        """
        Allow composing pipelines with >> operator.
        
        This is purely for fun — lets you write pipeline1 >> pipeline2.
        """
        if isinstance(other, Pipeline):
            return Pipeline(*self.functions, *other.functions)
        raise TypeError("Can only compose with another Pipeline")


def curry(func: Callable) -> Callable:
    """
    Transform a function to allow partial application.
    
    This is a simple currying implementation — it lets you call a function
    with fewer args than it needs and get back a function expecting the rest.
    """
    @wraps(func)
    def curried(*args, **kwargs):
        try:
            # Try to call with current args
            return func(*args, **kwargs)
        except TypeError:
            # If it fails, return a new function that captures these args
            def partial(*more_args, **more_kwargs):
                combined_kwargs = {**kwargs, **more_kwargs}
                return curried(*(args + more_args), **combined_kwargs)
            return partial
    
    return curried


if __name__ == "__main__":
    print("=== Functional Programming Utilities Demo ===\n")
    
    # Demo 1: Memoization with expensive fibonacci
    print("1. Memoization Example:")
    
    @memoize
    def fibonacci(n: int) -> int:
        """Classic fibonacci with memoization to avoid recalculation."""
        if n <= 1:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)
    
    print(f"   fib(30) = {fibonacci(30)}")
    print(f"   Cache size: {len(fibonacci.cache)} entries")
    print()
    
    # Demo 2: Lazy evaluation
    print("2. Lazy Sequence Example:")
    numbers = LazySequence(range(1000000))  # Million numbers, but not evaluated yet
    
    result = (numbers
              .filter(lambda x: x % 2 == 0)      # Only evens
              .map(lambda x: x * x)              # Square them
              .filter(lambda x: x % 3 == 0)      # Divisible by 3
              .take(5)                            # Just the first 5
              .collect())                         # Now it actually runs
    
    print(f"   First 5 squares of evens divisible by 3: {result}")
    print()
    
    # Demo 3: Function pipeline
    print("3. Pipeline Example:")
    
    # Build a text processing pipeline
    process_text = Pipeline(
        str.lower,
        lambda s: s.replace(" ", "_"),
        lambda s: s[:20]  # Truncate to 20 chars
    )
    
    text = "Hello World This Is A Test String"
    print(f"   Original: '{text}'")
    print(f"   Processed: '{process_text(text)}'")
    print()
    
    # Demo 4: Currying
    print("4. Currying Example:")
    
    @curry
    def multiply_and_add(a, b, c):
        """Multiply a and b, then add c."""
        return a * b + c
    
    # Partial application
    times_5 = multiply_and_add(5)
    times_5_plus = times_5(3)  # Now we have 5 * 3 + ?
    
    print(f"   multiply_and_add(5, 3, 2) = {times_5_plus(2)}")
    print(f"   multiply_and_add(5)(3)(10) = {multiply_and_add(5)(3)(10)}")
    print()
    
    print("All demos completed!")