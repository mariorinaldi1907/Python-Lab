"""
Date: 2026-07-11
Created a functional programming toolkit that combines lazy evaluation, automatic memoization, and chainable pipelines so I can compose transformations efficiently without wasting cycles on unused computations.
"""

import functools
from typing import Callable, Iterable, Any, TypeVar, Generic
from collections.abc import Iterator


T = TypeVar('T')
U = TypeVar('U')


def memoize(func: Callable) -> Callable:
    """
    Decorator that caches function results based on arguments.
    
    I use this to avoid recomputing expensive operations. Works with
    hashable arguments only, which is fine for most of my use cases.
    """
    cache = {}
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create a hashable key from args and kwargs
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    # Expose the cache so I can inspect or clear it if needed
    wrapper.cache = cache
    return wrapper


def curry(func: Callable) -> Callable:
    """
    Transforms a multi-argument function into a chain of single-argument functions.
    
    This makes partial application super clean. Instead of functools.partial,
    I can just call with one arg at a time.
    """
    @functools.wraps(func)
    def curried(*args, **kwargs):
        # If we have enough args, call the function
        if len(args) + len(kwargs) >= func.__code__.co_argcount:
            return func(*args, **kwargs)
        # Otherwise, return a partial application
        return lambda *more_args, **more_kwargs: curried(
            *(args + more_args), **{**kwargs, **more_kwargs}
        )
    return curried


class LazyPipeline(Generic[T]):
    """
    A lazy evaluation pipeline that chains operations without executing them.
    
    I built this because I often write data transformations that I don't always
    fully consume, and eager evaluation wastes CPU. The pipeline only computes
    values when you actually iterate or materialize the result.
    """
    
    def __init__(self, source: Iterable[T]):
        """Initialize pipeline with a data source."""
        self._source = source
        self._operations = []
    
    def map(self, func: Callable[[T], U]) -> 'LazyPipeline[U]':
        """
        Apply a transformation to each element.
        
        Returns a new pipeline (immutable style) so I can branch if needed.
        """
        new_pipeline = LazyPipeline(self._source)
        new_pipeline._operations = self._operations + [('map', func)]
        return new_pipeline
    
    def filter(self, predicate: Callable[[T], bool]) -> 'LazyPipeline[T]':
        """Keep only elements that satisfy the predicate."""
        new_pipeline = LazyPipeline(self._source)
        new_pipeline._operations = self._operations + [('filter', predicate)]
        return new_pipeline
    
    def take(self, n: int) -> 'LazyPipeline[T]':
        """Take only the first n elements."""
        new_pipeline = LazyPipeline(self._source)
        new_pipeline._operations = self._operations + [('take', n)]
        return new_pipeline
    
    def _execute(self) -> Iterator[T]:
        """
        Execute the pipeline lazily.
        
        This is where the magic happens - operations are applied one by one
        as we iterate, not all at once upfront.
        """
        result = iter(self._source)
        
        for op_type, op_arg in self._operations:
            if op_type == 'map':
                result = map(op_arg, result)
            elif op_type == 'filter':
                result = filter(op_arg, result)
            elif op_type == 'take':
                result = (x for i, x in enumerate(result) if i < op_arg)
        
        return result
    
    def to_list(self) -> list[T]:
        """Materialize the pipeline into a list."""
        return list(self._execute())
    
    def __iter__(self) -> Iterator[T]:
        """Allow direct iteration over the pipeline."""
        return self._execute()


def compose(*functions: Callable) -> Callable:
    """
    Compose functions right-to-left (mathematical style).
    
    compose(f, g, h)(x) = f(g(h(x)))
    
    I prefer this to nested calls when I have lots of transformations.
    """
    def composed(arg):
        result = arg
        for func in reversed(functions):
            result = func(result)
        return result
    return composed


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Create a pipeline that processes numbers
    numbers = range(1, 100)
    
    pipeline = (
        LazyPipeline(numbers)
        .filter(lambda x: x % 2 == 0)  # Only even numbers
        .map(lambda x: x ** 2)          # Square them
        .take(5)                        # Take first 5
    )
    
    print("Pipeline created (not executed yet)")
    print("Materializing first 5 even squares:")
    print(pipeline.to_list())
    
    print("\n=== Memoization Demo ===\n")
    
    @memoize
    def expensive_fibonacci(n: int) -> int:
        """Recursive fibonacci that would normally be O(2^n) without memoization."""
        if n <= 1:
            return n
        return expensive_fibonacci(n - 1) + expensive_fibonacci(n - 2)
    
    print("Computing fibonacci(35) with memoization...")
    result = expensive_fibonacci(35)
    print(f"Result: {result}")
    print(f"Cache size: {len(expensive_fibonacci.cache)} entries")
    
    print("\n=== Currying Demo ===\n")
    
    @curry
    def multiply_three(a: int, b: int, c: int) -> int:
        """Multiply three numbers together."""
        return a * b * c
    
    # Partial application through currying
    double = multiply_three(2)
    double_and_triple = double(3)
    
    print("Curried multiply_three(2)(3)(4):", double_and_triple(4))
    print("Or all at once: multiply_three(2, 3, 4):", multiply_three(2, 3, 4))
    
    print("\n=== Function Composition Demo ===\n")
    
    add_ten = lambda x: x + 10
    multiply_by_two = lambda x: x * 2
    square = lambda x: x ** 2
    
    # compose applies right to left: square, then *2, then +10
    transform = compose(add_ten, multiply_by_two, square)
    
    print("compose(add_10, multiply_by_2, square)(5)")
    print(f"Steps: 5 -> square(5)=25 -> *2=50 -> +10=60")
    print(f"Result: {transform(5)}")