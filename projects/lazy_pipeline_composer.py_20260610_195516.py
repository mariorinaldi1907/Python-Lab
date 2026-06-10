"""
Date: 2026-06-10
Created a functional programming toolkit that chains transformations lazily and supports partial application — because I got tired of writing nested map/filter calls.
"""

#!/usr/bin/env python3
"""
Lazy Pipeline Composer - A functional programming utility for building
composable, lazy-evaluated transformation pipelines.

I wanted something cleaner than nested comprehensions and built-in map/filter
when chaining multiple operations, especially when working with large datasets.
"""

from functools import wraps
from typing import Callable, Iterable, Any, TypeVar
from itertools import islice


T = TypeVar('T')
U = TypeVar('U')


class LazyPipeline:
    """
    A pipeline that applies transformations lazily — nothing happens until
    you actually iterate or materialize the result. Saves memory and
    allows infinite sequences.
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
        """Take only the first n elements."""
        self._operations.append(('take', n))
        return self
    
    def skip(self, n: int) -> 'LazyPipeline':
        """Skip the first n elements."""
        self._operations.append(('skip', n))
        return self
    
    def __iter__(self):
        """
        Execute the pipeline lazily. This is where the magic happens —
        operations are applied on-the-fly as we iterate.
        """
        result = iter(self._source)
        
        for op_type, op_arg in self._operations:
            if op_type == 'map':
                result = map(op_arg, result)
            elif op_type == 'filter':
                result = filter(op_arg, result)
            elif op_type == 'take':
                result = islice(result, op_arg)
            elif op_type == 'skip':
                result = islice(result, op_arg, None)
        
        return result
    
    def to_list(self) -> list:
        """Materialize the pipeline into a list."""
        return list(self)
    
    def reduce(self, func: Callable[[T, T], T], initial=None):
        """
        Reduce the pipeline to a single value. Had to import reduce
        in my head, but realized I could just do it manually.
        """
        iterator = iter(self)
        
        if initial is None:
            try:
                value = next(iterator)
            except StopIteration:
                raise TypeError("reduce() of empty sequence with no initial value")
        else:
            value = initial
        
        for element in iterator:
            value = func(value, element)
        
        return value


def curry(func: Callable) -> Callable:
    """
    Transform a function to support partial application. This was trickier
    than I thought — had to handle both args and kwargs properly.
    """
    @wraps(func)
    def curried(*args, **kwargs):
        # Try calling with what we have
        try:
            return func(*args, **kwargs)
        except TypeError:
            # Not enough arguments, return a new partial function
            def partial(*more_args, **more_kwargs):
                combined_kwargs = {**kwargs, **more_kwargs}
                return curried(*(args + more_args), **combined_kwargs)
            return partial
    
    return curried


def memoize(func: Callable) -> Callable:
    """
    Cache function results. Simple but effective for expensive computations.
    Only works with hashable arguments, but that's good enough for most cases.
    """
    cache = {}
    
    @wraps(func)
    def memoized(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    
    return memoized


def compose(*functions: Callable) -> Callable:
    """
    Compose functions right-to-left (mathematical style).
    compose(f, g, h)(x) == f(g(h(x)))
    """
    def composed(arg):
        result = arg
        # Apply functions in reverse order
        for func in reversed(functions):
            result = func(result)
        return result
    
    return composed


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Example 1: Processing numbers lazily
    print("1. Processing infinite sequence (only takes what we need):")
    def fibonacci():
        """Generate infinite Fibonacci sequence."""
        a, b = 0, 1
        while True:
            yield a
            a, b = b, a + b
    
    result = (LazyPipeline(fibonacci())
              .filter(lambda x: x % 2 == 0)  # only even numbers
              .map(lambda x: x * 2)           # double them
              .take(5)                        # take first 5
              .to_list())
    print(f"   First 5 doubled even Fibonacci numbers: {result}")
    
    # Example 2: Currying in action
    print("\n2. Currying demo:")
    @curry
    def multiply(x, y, z):
        """Multiply three numbers."""
        return x * y * z
    
    double = multiply(2)      # partially applied
    times_six = double(3)     # partially applied again
    result = times_six(7)     # final application
    print(f"   2 * 3 * 7 = {result}")
    
    # Example 3: Memoization
    print("\n3. Memoization (expensive computation):")
    
    @memoize
    def expensive_fibonacci(n):
        """Recursive Fibonacci - slow without memoization."""
        if n <= 1:
            return n
        return expensive_fibonacci(n - 1) + expensive_fibonacci(n - 2)
    
    print(f"   fib(35) = {expensive_fibonacci(35)} (try this without memoization!)")
    
    # Example 4: Function composition
    print("\n4. Function composition:")
    add_ten = lambda x: x + 10
    square = lambda x: x * x
    halve = lambda x: x / 2
    
    transform = compose(int, halve, square, add_ten)
    result = transform(5)  # ((5 + 10)^2) / 2 = 112
    print(f"   transform(5) where transform = int ∘ halve ∘ square ∘ add_ten")
    print(f"   = int(halve(square(5 + 10))) = {result}")
    
    # Example 5: Combining everything
    print("\n5. Real-world example - processing text data:")
    words = ["hello", "world", "python", "functional", "programming", "is", "fun"]
    
    result = (LazyPipeline(words)
              .filter(lambda w: len(w) > 3)
              .map(str.upper)
              .map(lambda w: f"[{w}]")
              .to_list())
    
    print(f"   Filtered and formatted: {result}")
    
    print("\n=== All demos completed successfully! ===")