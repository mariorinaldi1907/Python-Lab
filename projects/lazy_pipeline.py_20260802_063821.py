"""
Date: 2026-08-02
Created a functional programming toolkit that chains operations lazily, only computing when needed, with automatic memoization and currying support.
"""

"""
Lazy evaluation pipeline with currying and memoization.

I wanted to understand how libraries like toolz work under the hood,
so I built this from scratch. The pipeline evaluates lazily — nothing
runs until you actually need the result.
"""

from functools import wraps
from typing import Callable, Any, Iterable, TypeVar
from collections.abc import Iterator


T = TypeVar('T')
R = TypeVar('R')


def memoize(func: Callable) -> Callable:
    """
    Cache function results to avoid recomputation.
    
    I'm using a dict here instead of lru_cache because I want
    to see exactly what's happening. Works with hashable args only.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args):
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result
    
    # Expose cache for debugging/inspection
    wrapper.cache = cache
    return wrapper


def curry(func: Callable) -> Callable:
    """
    Transform a function to accept arguments one at a time.
    
    This was trickier than I thought — had to handle the case where
    we've collected enough args vs. still waiting for more.
    """
    @wraps(func)
    def curried(*args, **kwargs):
        # Try to call the function with what we have
        try:
            return func(*args, **kwargs)
        except TypeError:
            # Not enough args yet, return a partial application
            def partial(*more_args, **more_kwargs):
                combined_args = args + more_args
                combined_kwargs = {**kwargs, **more_kwargs}
                return curried(*combined_args, **combined_kwargs)
            return partial
    
    return curried


class LazyPipeline:
    """
    Chainable lazy evaluation pipeline.
    
    Operations aren't executed until you call collect(), list(), or iterate.
    This is the core of the whole module — lets you compose transformations
    without actually doing the work until necessary.
    """
    
    def __init__(self, iterable: Iterable[T]):
        """Start a pipeline with an iterable data source."""
        self._source = iterable
        self._operations = []
    
    def map(self, func: Callable[[T], R]) -> 'LazyPipeline':
        """Apply a function to each element."""
        self._operations.append(('map', func))
        return self
    
    def filter(self, predicate: Callable[[T], bool]) -> 'LazyPipeline':
        """Keep only elements that satisfy the predicate."""
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
        Actually run the pipeline.
        
        This is where the magic happens — we iterate through the source
        and apply each operation in sequence. Everything's lazy until now.
        """
        result = iter(self._source)
        
        for operation, arg in self._operations:
            if operation == 'map':
                result = map(arg, result)
            elif operation == 'filter':
                result = filter(arg, result)
            elif operation == 'take':
                result = (x for i, x in enumerate(result) if i < arg)
            elif operation == 'skip':
                result = (x for i, x in enumerate(result) if i >= arg)
        
        return result
    
    def collect(self) -> list:
        """Evaluate the pipeline and return a list."""
        return list(self._execute())
    
    def __iter__(self):
        """Allow iteration over the pipeline directly."""
        return self._execute()


def compose(*functions: Callable) -> Callable:
    """
    Compose functions right-to-left.
    
    compose(f, g, h)(x) == f(g(h(x)))
    
    I always mess up the order, so I added the docstring as a reminder.
    """
    def composed(arg):
        result = arg
        for func in reversed(functions):
            result = func(result)
        return result
    return composed


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Example 1: Basic lazy pipeline
    print("1. Lazy evaluation with pipeline:")
    numbers = range(1, 100)
    result = (LazyPipeline(numbers)
              .filter(lambda x: x % 2 == 0)  # even numbers only
              .map(lambda x: x ** 2)          # square them
              .take(5)                         # first 5
              .collect())
    print(f"   First 5 squares of even numbers: {result}")
    
    # Example 2: Memoization in action
    print("\n2. Memoization (expensive computation):")
    
    @memoize
    def fibonacci(n):
        """Recursive fibonacci — terrible without memoization."""
        if n <= 1:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)
    
    print(f"   fib(35) = {fibonacci(35)}")
    print(f"   Cache size: {len(fibonacci.cache)} entries")
    print(f"   Running fib(30) again (cached): {fibonacci(30)}")
    
    # Example 3: Currying
    print("\n3. Currying example:")
    
    @curry
    def add_three_numbers(a, b, c):
        """Add three numbers together."""
        return a + b + c
    
    add_five = add_three_numbers(5)
    add_five_and_ten = add_five(10)
    result = add_five_and_ten(3)
    print(f"   Curried addition: 5 + 10 + 3 = {result}")
    
    # Example 4: Function composition
    print("\n4. Function composition:")
    
    def double(x):
        return x * 2
    
    def add_ten(x):
        return x + 10
    
    def square(x):
        return x ** 2
    
    pipeline_func = compose(square, add_ten, double)
    value = 5
    result = pipeline_func(value)
    print(f"   compose(square, add_ten, double)({value}) = {result}")
    print(f"   Breakdown: {value} -> double -> {double(value)} -> add_ten -> {add_ten(double(value))} -> square -> {result}")
    
    # Example 5: Combining everything
    print("\n5. Combining lazy pipeline with memoized function:")
    
    @memoize
    def expensive_transform(x):
        """Simulated expensive operation."""
        return x ** 3 - 2 * x ** 2 + x
    
    result = (LazyPipeline(range(1, 20))
              .map(expensive_transform)
              .filter(lambda x: x > 100)
              .take(3)
              .collect())
    print(f"   First 3 values > 100 from expensive transform: {result}")
    print(f"   Expensive function cache size: {len(expensive_transform.cache)}")