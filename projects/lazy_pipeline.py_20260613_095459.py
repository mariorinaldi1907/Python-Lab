"""
Date: 2026-06-13
Created a functional pipeline library that chains transformations lazily, only computing results when actually needed — reminds me of how Haskell does it.
"""

#!/usr/bin/env python3
"""
Lazy evaluation pipeline for functional-style data processing.
Transformations are composed but not executed until materialization.
"""

from typing import Callable, Iterator, Any, Iterable, TypeVar
from functools import wraps

T = TypeVar('T')
U = TypeVar('U')


class LazyPipeline:
    """
    A composable pipeline that defers execution until values are consumed.
    
    This lets you chain .map(), .filter(), .take(), etc. without creating
    intermediate lists. Only processes elements when you actually iterate
    or call .to_list().
    """
    
    def __init__(self, source: Iterable):
        """Initialize pipeline with a data source."""
        self._source = source
    
    def map(self, func: Callable[[T], U]) -> 'LazyPipeline':
        """Apply a transformation to each element."""
        def generator():
            for item in self._source:
                yield func(item)
        return LazyPipeline(generator())
    
    def filter(self, predicate: Callable[[T], bool]) -> 'LazyPipeline':
        """Keep only elements that satisfy the predicate."""
        def generator():
            for item in self._source:
                if predicate(item):
                    yield item
        return LazyPipeline(generator())
    
    def take(self, n: int) -> 'LazyPipeline':
        """Take only the first n elements."""
        def generator():
            count = 0
            for item in self._source:
                if count >= n:
                    break
                yield item
                count += 1
        return LazyPipeline(generator())
    
    def skip(self, n: int) -> 'LazyPipeline':
        """Skip the first n elements."""
        def generator():
            iterator = iter(self._source)
            for _ in range(n):
                try:
                    next(iterator)
                except StopIteration:
                    return
            yield from iterator
        return LazyPipeline(generator())
    
    def flat_map(self, func: Callable[[T], Iterable[U]]) -> 'LazyPipeline':
        """Map each element to an iterable and flatten the results."""
        def generator():
            for item in self._source:
                yield from func(item)
        return LazyPipeline(generator())
    
    def to_list(self) -> list:
        """Materialize the pipeline into a list."""
        return list(self._source)
    
    def __iter__(self) -> Iterator:
        """Allow iteration over the pipeline."""
        return iter(self._source)


def memoize(func: Callable) -> Callable:
    """
    Decorator that caches function results based on arguments.
    
    I'm using this for expensive computations that get called repeatedly
    with the same inputs. Simple dict-based cache.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create a hashable key from args and kwargs
        key = (args, tuple(sorted(kwargs.items())))
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    # Attach cache for inspection/clearing if needed
    wrapper.cache = cache
    return wrapper


def curry(func: Callable) -> Callable:
    """
    Transform a multi-argument function into a sequence of single-argument functions.
    
    This is useful for partial application. If you have f(x, y, z), currying
    gives you f(x)(y)(z). I mostly use this when I need to "lock in" some
    arguments early.
    """
    import inspect
    sig = inspect.signature(func)
    arity = len(sig.parameters)
    
    def curried(*args):
        if len(args) >= arity:
            return func(*args[:arity])
        else:
            return lambda *more_args: curried(*(args + more_args))
    
    return curried


def compose(*functions: Callable) -> Callable:
    """
    Compose functions right-to-left: compose(f, g, h)(x) = f(g(h(x))).
    
    I like this for building complex transformations from simple ones.
    """
    def composed(arg):
        result = arg
        for func in reversed(functions):
            result = func(result)
        return result
    return composed


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Example 1: Process numbers without creating intermediate lists
    print("1. Lazy pipeline with infinite range:")
    result = (LazyPipeline(range(1000000))  # Million items, but we won't process them all
              .filter(lambda x: x % 2 == 0)
              .map(lambda x: x * x)
              .take(5)
              .to_list())
    print(f"   First 5 even squares: {result}")
    
    # Example 2: Flat map for nested structures
    print("\n2. Flat map demo:")
    words = LazyPipeline(["hello world", "lazy evaluation", "is cool"])
    result = words.flat_map(lambda s: s.split()).to_list()
    print(f"   Split words: {result}")
    
    # Example 3: Memoization
    print("\n3. Memoization (Fibonacci):")
    
    @memoize
    def fibonacci(n: int) -> int:
        """Recursive fibonacci with memoization."""
        if n <= 1:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)
    
    print(f"   fib(30) = {fibonacci(30)}")
    print(f"   Cache size: {len(fibonacci.cache)} entries")
    
    # Example 4: Currying
    print("\n4. Currying demo:")
    
    @curry
    def add_three_numbers(a, b, c):
        return a + b + c
    
    add_5 = add_three_numbers(5)
    add_5_and_10 = add_5(10)
    print(f"   add_three_numbers(5)(10)(3) = {add_5_and_10(3)}")
    
    # Example 5: Function composition
    print("\n5. Function composition:")
    
    def double(x):
        return x * 2
    
    def increment(x):
        return x + 1
    
    def square(x):
        return x * x
    
    # Compose: square(increment(double(x)))
    transform = compose(square, increment, double)
    print(f"   square(increment(double(5))) = {transform(5)}")
    
    # Example 6: Combining everything
    print("\n6. Complex pipeline with composition:")
    pipeline = (LazyPipeline(range(1, 20))
                .filter(lambda x: x % 3 == 0)
                .map(compose(square, increment))
                .take(4)
                .to_list())
    print(f"   Multiples of 3, incremented and squared (first 4): {pipeline}")