"""
Date: 2026-06-13
Created a functional pipeline utility that lazily evaluates transformations on iterables, supporting currying and method chaining for cleaner data processing workflows.
"""

"""
Lazy evaluation pipeline system for composable transformations.

This module provides a Pipeline class that wraps iterables and allows
chaining transformations (map, filter, reduce, etc.) without eager evaluation.
Everything stays lazy until you actually consume the results.
"""

from functools import wraps, reduce
from typing import Callable, Iterable, Any, TypeVar


T = TypeVar('T')
U = TypeVar('U')


def curry(func: Callable) -> Callable:
    """
    Decorator that enables currying for functions.
    
    Currying allows partial application of arguments. If you call the function
    with fewer arguments than it expects, you get back a new function waiting
    for the rest.
    """
    @wraps(func)
    def curried(*args, **kwargs):
        # Try to call the function; if it needs more args, return a partial
        try:
            return func(*args, **kwargs)
        except TypeError:
            # Not enough arguments, so return a function that remembers these
            def partial(*more_args, **more_kwargs):
                combined_kwargs = {**kwargs, **more_kwargs}
                return curried(*(args + more_args), **combined_kwargs)
            return partial
    return curried


class Pipeline:
    """
    A lazy evaluation pipeline for composable data transformations.
    
    The pipeline wraps an iterable and applies transformations only when
    the data is actually consumed (via collect(), list(), etc.). This avoids
    creating intermediate lists and can be more memory-efficient.
    """
    
    def __init__(self, iterable: Iterable[Any]):
        """Initialize the pipeline with an iterable source."""
        self._iterable = iterable
    
    def map(self, func: Callable[[T], U]) -> 'Pipeline':
        """
        Apply a transformation function to each element.
        
        Stays lazy — the function isn't called until you consume the pipeline.
        """
        self._iterable = map(func, self._iterable)
        return self
    
    def filter(self, predicate: Callable[[T], bool]) -> 'Pipeline':
        """
        Keep only elements where predicate returns True.
        
        Like map(), this is lazy and won't evaluate until consumption.
        """
        self._iterable = filter(predicate, self._iterable)
        return self
    
    def take(self, n: int) -> 'Pipeline':
        """
        Take only the first n elements.
        
        Useful for limiting expensive operations or working with infinite sequences.
        """
        def take_gen():
            for i, item in enumerate(self._iterable):
                if i >= n:
                    break
                yield item
        
        self._iterable = take_gen()
        return self
    
    def drop(self, n: int) -> 'Pipeline':
        """
        Skip the first n elements.
        
        Returns a pipeline starting from the (n+1)th element.
        """
        def drop_gen():
            iterator = iter(self._iterable)
            # Consume and discard first n items
            for _ in range(n):
                try:
                    next(iterator)
                except StopIteration:
                    return
            # Yield the rest
            yield from iterator
        
        self._iterable = drop_gen()
        return self
    
    def reduce(self, func: Callable[[T, T], T], initial: Any = None) -> Any:
        """
        Reduce the pipeline to a single value using a binary function.
        
        This is an eager operation — it consumes the entire pipeline.
        """
        if initial is None:
            return reduce(func, self._iterable)
        return reduce(func, self._iterable, initial)
    
    def collect(self) -> list:
        """
        Materialize the pipeline into a list.
        
        This is where the lazy evaluation actually happens — all pending
        transformations are executed here.
        """
        return list(self._iterable)
    
    def __iter__(self):
        """Allow direct iteration over the pipeline."""
        return iter(self._iterable)
    
    def __repr__(self):
        return f"Pipeline(<lazy>)"


@curry
def add(x: int, y: int) -> int:
    """Curried addition function for demonstration."""
    return x + y


@curry
def multiply(x: int, y: int) -> int:
    """Curried multiplication function for demonstration."""
    return x * y


if __name__ == "__main__":
    print("=== Lazy Pipeline Evaluator Demo ===\n")
    
    # Demo 1: Basic pipeline with chaining
    print("1. Basic pipeline: square evens, take first 5")
    result = (Pipeline(range(20))
              .filter(lambda x: x % 2 == 0)
              .map(lambda x: x ** 2)
              .take(5)
              .collect())
    print(f"   Result: {result}")
    print()
    
    # Demo 2: Using curried functions in pipeline
    print("2. Using curried functions")
    add_10 = add(10)  # Partial application
    multiply_3 = multiply(3)
    
    result = (Pipeline(range(1, 6))
              .map(add_10)
              .map(multiply_3)
              .collect())
    print(f"   Add 10, then multiply by 3: {result}")
    print()
    
    # Demo 3: Reduce operation (eager)
    print("3. Reduce to sum")
    total = (Pipeline(range(1, 11))
             .map(lambda x: x ** 2)
             .reduce(lambda a, b: a + b, 0))
    print(f"   Sum of squares 1-10: {total}")
    print()
    
    # Demo 4: Drop and take
    print("4. Drop first 3, take next 4")
    result = (Pipeline(range(100))
              .drop(3)
              .take(4)
              .collect())
    print(f"   Result: {result}")
    print()
    
    # Demo 5: Complex transformation showing laziness
    print("5. Demonstrating lazy evaluation")
    
    def expensive_transform(x):
        """A function that prints to show when it's actually called."""
        print(f"   > Processing {x}")
        return x * 2
    
    print("   Creating pipeline (nothing happens yet)...")
    pipeline = (Pipeline(range(10))
                .map(expensive_transform)
                .filter(lambda x: x > 10)
                .take(3))
    
    print("   Now calling collect() — this is where work happens:")
    result = pipeline.collect()
    print(f"   Final result: {result}")