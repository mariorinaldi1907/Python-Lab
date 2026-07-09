"""
Date: 2026-07-09
Created a functional programming toolkit that lets me chain operations lazily, memoize expensive computations, and compose functions like I'm writing Haskell but in Python.
"""

"""
Functional programming utilities: pipelines, lazy evaluation, and memoization.
I got tired of writing deeply nested function calls and wanted something cleaner.
"""

from functools import wraps
from typing import Callable, Iterator, Any, TypeVar


T = TypeVar('T')
U = TypeVar('U')


def memoize(func: Callable) -> Callable:
    """
    Decorator that caches function results based on arguments.
    Uses a dict to store previously computed values — great for expensive recursive functions.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create a hashable key from args and kwargs
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    # Expose cache for introspection/clearing
    wrapper.cache = cache
    return wrapper


def curry(func: Callable, arity: int = None) -> Callable:
    """
    Transform a function to accept arguments one at a time.
    If arity isn't provided, we'll try to inspect the function signature.
    """
    if arity is None:
        arity = func.__code__.co_argcount
    
    def curried(*args):
        if len(args) >= arity:
            return func(*args[:arity])
        return lambda *more_args: curried(*(args + more_args))
    
    return curried


class LazySequence:
    """
    Wrapper around an iterator that applies transformations lazily.
    Nothing gets computed until you actually iterate or call collect().
    This is inspired by Rust's iterators and Haskell's lazy lists.
    """
    
    def __init__(self, iterable):
        """Initialize with any iterable."""
        self._iterable = iterable
    
    def map(self, func: Callable[[T], U]) -> 'LazySequence':
        """Apply a function to each element lazily."""
        def generator():
            for item in self._iterable:
                yield func(item)
        return LazySequence(generator())
    
    def filter(self, predicate: Callable[[T], bool]) -> 'LazySequence':
        """Keep only elements that satisfy the predicate."""
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
        """Force evaluation and collect results into a list."""
        return list(self._iterable)
    
    def __iter__(self) -> Iterator:
        """Make LazySequence directly iterable."""
        return iter(self._iterable)


class Pipeline:
    """
    Compose multiple functions into a single pipeline.
    Data flows left-to-right through the pipeline, which feels more natural
    than the typical right-to-left function composition.
    """
    
    def __init__(self, *functions: Callable):
        """Initialize with a sequence of functions to compose."""
        self.functions = functions
    
    def __call__(self, value: Any) -> Any:
        """Execute the pipeline by threading the value through all functions."""
        result = value
        for func in self.functions:
            result = func(result)
        return result
    
    def __or__(self, other: 'Pipeline') -> 'Pipeline':
        """Allow chaining pipelines with the | operator."""
        if isinstance(other, Pipeline):
            return Pipeline(*self.functions, *other.functions)
        # If it's just a function, wrap it
        return Pipeline(*self.functions, other)


def compose(*functions: Callable) -> Callable:
    """
    Traditional function composition: compose(f, g, h)(x) == f(g(h(x)))
    Right-to-left, like math notation.
    """
    def composed(value):
        result = value
        # Apply functions in reverse order
        for func in reversed(functions):
            result = func(result)
        return result
    return composed


if __name__ == "__main__":
    print("=== Memoization Demo ===")
    
    @memoize
    def fibonacci(n):
        """Classic fib with memoization — normally this would be super slow."""
        if n <= 1:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)
    
    print(f"fibonacci(30) = {fibonacci(30)}")
    print(f"Cache has {len(fibonacci.cache)} entries\n")
    
    print("=== Currying Demo ===")
    
    def multiply(x, y, z):
        return x * y * z
    
    curried_multiply = curry(multiply)
    times_2 = curried_multiply(2)
    times_2_3 = times_2(3)
    result = times_2_3(4)
    print(f"Curried multiply(2)(3)(4) = {result}\n")
    
    print("=== Lazy Sequence Demo ===")
    
    # Generate squares of even numbers, but lazily
    numbers = range(1, 20)
    lazy_result = (LazySequence(numbers)
                   .filter(lambda x: x % 2 == 0)
                   .map(lambda x: x ** 2)
                   .take(5)
                   .collect())
    print(f"Lazy squares of first 5 even numbers: {lazy_result}\n")
    
    print("=== Pipeline Demo ===")
    
    # Create a data processing pipeline
    strip_and_lower = Pipeline(
        str.strip,
        str.lower
    )
    
    process_text = strip_and_lower | Pipeline(
        lambda s: s.replace(' ', '_'),
        lambda s: f"processed_{s}"
    )
    
    print(f"Pipeline result: {process_text('  Hello World  ')}\n")
    
    print("=== Function Composition Demo ===")
    
    add_10 = lambda x: x + 10
    multiply_by_2 = lambda x: x * 2
    square = lambda x: x ** 2
    
    # Compose: square(multiply_by_2(add_10(x)))
    process = compose(square, multiply_by_2, add_10)
    print(f"compose(square, *2, +10)(5) = {process(5)}")