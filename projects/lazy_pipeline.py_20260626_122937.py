"""
Date: 2026-06-26
Created a functional programming toolkit that lets me compose data transformations lazily, only executing when results are actually pulled, with automatic memoization to avoid recomputation.
"""

"""
Lazy evaluation pipeline with memoization.

I wanted a way to chain data transformations functionally without computing
everything eagerly. This lets me build up complex pipelines and only run them
when I actually need the results.
"""

from functools import wraps
from typing import Callable, Any, Iterable, Iterator


def memoize(func: Callable) -> Callable:
    """
    Cache function results to avoid recomputation.
    
    I use this for expensive operations in the pipeline. The cache is stored
    on the function object itself so it persists across calls.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Only cache if all args are hashable
        try:
            key = (args, tuple(sorted(kwargs.items())))
        except TypeError:
            # If unhashable, just call the function
            return func(*args, **kwargs)
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    wrapper.cache = cache
    wrapper.cache_clear = cache.clear
    return wrapper


class LazyPipeline:
    """
    A pipeline that defers computation until values are actually needed.
    
    I designed this to work with iterables and transformations. Operations
    are stacked up but not executed until you iterate or materialize the result.
    """
    
    def __init__(self, source: Iterable):
        """Initialize with a data source."""
        self.source = source
        self.operations = []
    
    def map(self, func: Callable) -> 'LazyPipeline':
        """Apply a function to each element (lazily)."""
        self.operations.append(('map', func))
        return self
    
    def filter(self, predicate: Callable) -> 'LazyPipeline':
        """Keep only elements that match the predicate (lazily)."""
        self.operations.append(('filter', predicate))
        return self
    
    def take(self, n: int) -> 'LazyPipeline':
        """Take only the first n elements (lazily)."""
        self.operations.append(('take', n))
        return self
    
    def _execute(self) -> Iterator:
        """
        Execute the pipeline and yield results.
        
        This is where the actual computation happens. I walk through all
        the queued operations and apply them to the source data.
        """
        result = iter(self.source)
        
        for op_type, op_arg in self.operations:
            if op_type == 'map':
                result = map(op_arg, result)
            elif op_type == 'filter':
                result = filter(op_arg, result)
            elif op_type == 'take':
                result = (x for i, x in enumerate(result) if i < op_arg)
        
        return result
    
    def to_list(self) -> list:
        """Materialize the pipeline into a list."""
        return list(self._execute())
    
    def __iter__(self) -> Iterator:
        """Allow direct iteration over the pipeline."""
        return self._execute()


def curry(func: Callable, arity: int = None) -> Callable:
    """
    Convert a function into a curried version.
    
    I wanted proper currying where you can partially apply arguments.
    If arity isn't specified, I try to figure it out from the function.
    """
    if arity is None:
        arity = func.__code__.co_argcount
    
    def curried(*args):
        if len(args) >= arity:
            return func(*args[:arity])
        else:
            # Not enough args, return a new curried function
            def partial(*more_args):
                return curried(*(args + more_args))
            return partial
    
    return curried


def compose(*functions: Callable) -> Callable:
    """
    Compose functions right-to-left (like math notation).
    
    compose(f, g, h)(x) == f(g(h(x)))
    I use this when I want clear function composition without nesting.
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
    
    # Build a pipeline without executing it yet
    print("Creating a lazy pipeline...")
    numbers = range(1, 100)
    
    pipeline = (LazyPipeline(numbers)
                .filter(lambda x: x % 2 == 0)  # Only evens
                .map(lambda x: x ** 2)          # Square them
                .filter(lambda x: x > 100)      # Only big squares
                .take(5))                        # Just the first 5
    
    print("Pipeline created (nothing computed yet)")
    print("Executing pipeline now...\n")
    
    result = pipeline.to_list()
    print(f"Result: {result}")
    
    print("\n=== Memoization Demo ===\n")
    
    @memoize
    def expensive_fibonacci(n: int) -> int:
        """Recursive fibonacci that would be slow without memoization."""
        if n <= 1:
            return n
        return expensive_fibonacci(n - 1) + expensive_fibonacci(n - 2)
    
    print("Computing fibonacci(35) with memoization...")
    result = expensive_fibonacci(35)
    print(f"fib(35) = {result}")
    print(f"Cache size: {len(expensive_fibonacci.cache)} entries")
    
    print("\n=== Currying Demo ===\n")
    
    def multiply(x, y, z):
        """Simple function to demonstrate currying."""
        return x * y * z
    
    curried_multiply = curry(multiply)
    
    # Partial application
    double = curried_multiply(2)
    double_and_triple = double(3)
    
    print("curried_multiply(2)(3)(5) =", double_and_triple(5))
    print("Fully applied: curried_multiply(2, 3, 5) =", curried_multiply(2, 3, 5))
    
    print("\n=== Function Composition Demo ===\n")
    
    def add_one(x):
        return x + 1
    
    def square(x):
        return x ** 2
    
    def negate(x):
        return -x
    
    # Compose: negate(square(add_one(x)))
    transform = compose(negate, square, add_one)
    
    print("compose(negate, square, add_one)(4):")
    print(f"  4 -> add_one -> 5 -> square -> 25 -> negate -> {transform(4)}")