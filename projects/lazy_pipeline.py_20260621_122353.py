"""
Date: 2026-06-21
Created a functional programming utility that implements lazy evaluation pipelines with method chaining — transformations only execute when you actually consume the results.
"""

"""
Lazy evaluation pipeline for functional-style data transformations.

This lets you chain map/filter/reduce operations without executing them
until you actually need the results. Saves memory and compute when you're
dealing with large datasets or expensive operations.
"""

from typing import Callable, Iterable, Any, TypeVar, Optional
from functools import reduce, wraps
from itertools import islice


T = TypeVar('T')
U = TypeVar('U')


def memoize(func: Callable) -> Callable:
    """
    Decorator that caches function results based on arguments.
    
    Only works with hashable arguments. I use this internally for
    expensive transformations that might get called multiple times.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create a cache key from args and sorted kwargs
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    return wrapper


def curry(func: Callable, arity: Optional[int] = None) -> Callable:
    """
    Curries a function so you can partially apply arguments.
    
    If arity isn't specified, uses the function's argument count.
    This is useful for creating specialized versions of general functions.
    """
    if arity is None:
        arity = func.__code__.co_argcount
    
    def curried(*args):
        if len(args) >= arity:
            return func(*args)
        return lambda *more_args: curried(*(args + more_args))
    
    return curried


class LazyPipeline:
    """
    A lazy evaluation pipeline that chains transformations.
    
    Nothing actually executes until you call a terminal operation like
    collect(), first(), or reduce(). This is inspired by Java streams
    and Rust iterators — I wanted something similar for Python.
    """
    
    def __init__(self, source: Iterable[T]):
        """Initialize with an iterable source."""
        self._source = source
        self._operations = []
    
    def map(self, func: Callable[[T], U]) -> 'LazyPipeline':
        """
        Apply a transformation to each element.
        Returns a new pipeline (immutable style).
        """
        new_pipeline = LazyPipeline(self._source)
        new_pipeline._operations = self._operations + [('map', func)]
        return new_pipeline
    
    def filter(self, predicate: Callable[[T], bool]) -> 'LazyPipeline':
        """
        Keep only elements that satisfy the predicate.
        """
        new_pipeline = LazyPipeline(self._source)
        new_pipeline._operations = self._operations + [('filter', predicate)]
        return new_pipeline
    
    def take(self, n: int) -> 'LazyPipeline':
        """
        Take only the first n elements.
        Useful for limiting output or testing on a subset.
        """
        new_pipeline = LazyPipeline(self._source)
        new_pipeline._operations = self._operations + [('take', n)]
        return new_pipeline
    
    def _execute(self) -> Iterable:
        """
        Internal method that actually executes the pipeline.
        This is where the lazy magic happens — we build up the iterator
        chain and return it without consuming it.
        """
        result = iter(self._source)
        
        for op_type, op_arg in self._operations:
            if op_type == 'map':
                result = map(op_arg, result)
            elif op_type == 'filter':
                result = filter(op_arg, result)
            elif op_type == 'take':
                result = islice(result, op_arg)
        
        return result
    
    def collect(self) -> list:
        """
        Terminal operation: consume the pipeline into a list.
        """
        return list(self._execute())
    
    def first(self, default=None) -> Any:
        """
        Terminal operation: get the first element or default.
        """
        try:
            return next(iter(self._execute()))
        except StopIteration:
            return default
    
    def reduce(self, func: Callable[[T, T], T], initial=None) -> Any:
        """
        Terminal operation: reduce all elements to a single value.
        """
        items = self._execute()
        if initial is None:
            return reduce(func, items)
        return reduce(func, items, initial)
    
    def for_each(self, func: Callable[[T], None]) -> None:
        """
        Terminal operation: apply a function to each element for side effects.
        """
        for item in self._execute():
            func(item)


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Example 1: Simple transformation chain
    print("1. Processing numbers 1-10:")
    result = (LazyPipeline(range(1, 11))
              .filter(lambda x: x % 2 == 0)  # keep evens
              .map(lambda x: x ** 2)          # square them
              .collect())
    print(f"   Even squares: {result}\n")
    
    # Example 2: Early termination with take()
    print("2. First 3 squares of multiples of 3:")
    result = (LazyPipeline(range(1, 100))
              .filter(lambda x: x % 3 == 0)
              .map(lambda x: x ** 2)
              .take(3)
              .collect())
    print(f"   Result: {result}\n")
    
    # Example 3: Using reduce
    print("3. Sum of squares up to 5:")
    total = (LazyPipeline(range(1, 6))
             .map(lambda x: x ** 2)
             .reduce(lambda a, b: a + b, 0))
    print(f"   Total: {total}\n")
    
    # Example 4: Demonstrating laziness
    print("4. Demonstrating lazy evaluation:")
    print("   Creating pipeline... (nothing happens yet)")
    pipeline = (LazyPipeline(range(1, 100))
                .map(lambda x: (print(f"   Processing {x}"), x)[1])
                .filter(lambda x: x > 5)
                .take(3))
    print("   Pipeline created. Now calling first()...")
    first_item = pipeline.first()
    print(f"   Got first item: {first_item}\n")
    
    # Example 5: Currying demonstration
    print("5. Currying example:")
    
    @curry
    def add_three_numbers(a, b, c):
        return a + b + c
    
    add_five = add_three_numbers(2)(3)  # partially applied
    print(f"   add_three_numbers(2)(3)(10) = {add_five(10)}")
    print(f"   add_three_numbers(2)(3)(20) = {add_five(20)}\n")
    
    # Example 6: Using memoization
    print("6. Memoization example:")
    
    @memoize
    def expensive_computation(n):
        print(f"   Computing fib({n})...")
        if n <= 1:
            return n
        return expensive_computation(n - 1) + expensive_computation(n - 2)
    
    print(f"   First call - fib(10): {expensive_computation(10)}")
    print(f"   Second call - fib(10): {expensive_computation(10)} (cached!)")