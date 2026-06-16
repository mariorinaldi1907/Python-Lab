"""
Date: 2026-06-16
Implemented a lazy evaluation pipeline system with currying support that only computes values when needed, perfect for working with large data sequences efficiently.
"""

#!/usr/bin/env python3
"""
Lazy evaluation pipeline for functional-style data transformations.
Only computes values when absolutely necessary — great for memory efficiency.
"""

from functools import wraps
from typing import Callable, Iterable, Any, TypeVar


T = TypeVar('T')
U = TypeVar('U')


def memoize(func: Callable) -> Callable:
    """
    Cache function results to avoid recomputation.
    Uses a dict because I need hashable args — won't work with lists/dicts as params.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create a cache key from args and kwargs
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    return wrapper


def curry(func: Callable) -> Callable:
    """
    Transform a multi-argument function into a sequence of single-argument functions.
    Keeps collecting args until we have enough to actually call the function.
    """
    @wraps(func)
    def curried(*args, **kwargs):
        # If we have enough args, just call it
        if len(args) + len(kwargs) >= func.__code__.co_argcount:
            return func(*args, **kwargs)
        
        # Otherwise, return a function that collects more args
        def partial(*more_args, **more_kwargs):
            combined_args = args + more_args
            combined_kwargs = {**kwargs, **more_kwargs}
            return curried(*combined_args, **combined_kwargs)
        
        return partial
    
    return curried


class LazyPipeline:
    """
    A pipeline that chains operations but doesn't execute until you ask for results.
    This is the core of lazy evaluation — transformations stack up, execution happens once.
    """
    
    def __init__(self, source: Iterable):
        """Initialize with a data source (list, generator, whatever)."""
        self._source = source
        self._operations = []
    
    def map(self, func: Callable[[T], U]) -> 'LazyPipeline':
        """
        Apply a transformation to each element.
        Doesn't actually run — just queues the operation.
        """
        self._operations.append(('map', func))
        return self
    
    def filter(self, predicate: Callable[[T], bool]) -> 'LazyPipeline':
        """
        Keep only elements that satisfy the predicate.
        Again, lazy — we're just recording what to do later.
        """
        self._operations.append(('filter', predicate))
        return self
    
    def take(self, n: int) -> 'LazyPipeline':
        """Limit output to first n elements."""
        self._operations.append(('take', n))
        return self
    
    def skip(self, n: int) -> 'LazyPipeline':
        """Skip the first n elements."""
        self._operations.append(('skip', n))
        return self
    
    def _execute(self) -> Iterable:
        """
        Actually run the pipeline.
        This is where all the magic happens — we process one item at a time
        through all operations, never materializing the whole dataset.
        """
        result = iter(self._source)
        
        for operation, param in self._operations:
            if operation == 'map':
                result = map(param, result)
            elif operation == 'filter':
                result = filter(param, result)
            elif operation == 'take':
                result = (item for i, item in enumerate(result) if i < param)
            elif operation == 'skip':
                # Consume and discard the first n items
                for _ in range(param):
                    try:
                        next(result)
                    except StopIteration:
                        break
        
        return result
    
    def to_list(self) -> list:
        """Materialize the pipeline into a list."""
        return list(self._execute())
    
    def collect(self) -> list:
        """Alias for to_list — I prefer this name sometimes."""
        return self.to_list()
    
    def for_each(self, func: Callable[[T], None]) -> None:
        """
        Execute a side effect for each element.
        This is terminal — it actually runs the pipeline.
        """
        for item in self._execute():
            func(item)
    
    def reduce(self, func: Callable[[T, T], T], initial: Any = None) -> Any:
        """
        Reduce the pipeline to a single value.
        Using functools.reduce under the hood but fitting it into our pipeline.
        """
        from functools import reduce as functools_reduce
        items = list(self._execute())
        
        if initial is None:
            return functools_reduce(func, items)
        return functools_reduce(func, items, initial)


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Demo 1: Basic pipeline with large range (shows laziness)
    print("1. Processing numbers 1-1000, but only taking first 5 squares of evens:")
    result = (
        LazyPipeline(range(1, 1001))
        .filter(lambda x: x % 2 == 0)
        .map(lambda x: x ** 2)
        .take(5)
        .collect()
    )
    print(f"   Result: {result}\n")
    
    # Demo 2: Memoization example
    print("2. Memoized fibonacci (notice how fast subsequent calls are):")
    
    @memoize
    def fib(n):
        if n <= 1:
            return n
        return fib(n - 1) + fib(n - 2)
    
    print(f"   fib(30) = {fib(30)}")
    print(f"   fib(35) = {fib(35)}")  # Should be instant due to memoization
    print()
    
    # Demo 3: Currying example
    print("3. Curried function example:")
    
    @curry
    def multiply_three(a, b, c):
        return a * b * c
    
    double = multiply_three(2)
    double_and_triple = double(3)
    result = double_and_triple(4)
    print(f"   multiply_three(2)(3)(4) = {result}\n")
    
    # Demo 4: Complex pipeline with reduce
    print("4. Sum of squares of odd numbers from 1-20:")
    total = (
        LazyPipeline(range(1, 21))
        .filter(lambda x: x % 2 == 1)
        .map(lambda x: x ** 2)
        .reduce(lambda acc, x: acc + x, 0)
    )
    print(f"   Result: {total}\n")
    
    # Demo 5: String processing pipeline
    print("5. Processing words (skip first 2, take 3, uppercase):")
    words = ["apple", "banana", "cherry", "date", "elderberry", "fig", "grape"]
    result = (
        LazyPipeline(words)
        .skip(2)
        .take(3)
        .map(str.upper)
        .collect()
    )
    print(f"   Result: {result}\n")
    
    print("=== All demos completed successfully! ===")
```