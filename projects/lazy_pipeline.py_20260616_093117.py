"""
Date: 2026-06-16
Created a composable lazy pipeline that delays computation until values are needed, with support for currying and function composition because I got tired of writing nested map/filter calls.
"""

"""
Lazy evaluation pipeline with currying support.

I built this because I wanted cleaner data transformations without creating
tons of intermediate lists. The pipeline only computes values when you actually
iterate over them, which is way more memory-efficient for large datasets.
"""

from functools import wraps, reduce
from typing import Callable, Iterable, Any, TypeVar


T = TypeVar('T')
U = TypeVar('U')


def curry(func: Callable) -> Callable:
    """
    Transform a multi-argument function into a series of single-argument functions.
    
    This lets you partially apply functions, which is super handy for pipelines.
    """
    @wraps(func)
    def curried(*args, **kwargs):
        # Check if we have enough arguments to call the function
        try:
            return func(*args, **kwargs)
        except TypeError:
            # Not enough args, return a new partial function
            def partial(*more_args, **more_kwargs):
                return curried(*(args + more_args), **{**kwargs, **more_kwargs})
            return partial
    return curried


class LazyPipeline:
    """
    A lazy evaluation pipeline that chains operations without executing them.
    
    Operations are only computed when you actually iterate or convert to a list.
    This is the core of the whole thing — everything else builds on this.
    """
    
    def __init__(self, iterable: Iterable[T]):
        """Initialize with an iterable source."""
        self._iterable = iterable
    
    def map(self, func: Callable[[T], U]) -> 'LazyPipeline':
        """Apply a function to each element lazily."""
        def gen():
            for item in self._iterable:
                yield func(item)
        return LazyPipeline(gen())
    
    def filter(self, predicate: Callable[[T], bool]) -> 'LazyPipeline':
        """Keep only elements where predicate returns True."""
        def gen():
            for item in self._iterable:
                if predicate(item):
                    yield item
        return LazyPipeline(gen())
    
    def take(self, n: int) -> 'LazyPipeline':
        """Take only the first n elements."""
        def gen():
            count = 0
            for item in self._iterable:
                if count >= n:
                    break
                yield item
                count += 1
        return LazyPipeline(gen())
    
    def skip(self, n: int) -> 'LazyPipeline':
        """Skip the first n elements."""
        def gen():
            iterator = iter(self._iterable)
            for _ in range(n):
                try:
                    next(iterator)
                except StopIteration:
                    return
            yield from iterator
        return LazyPipeline(gen())
    
    def reduce(self, func: Callable[[T, T], T], initial: Any = None) -> Any:
        """
        Reduce the pipeline to a single value.
        
        This is eager because we need the final result.
        """
        if initial is None:
            return reduce(func, self._iterable)
        return reduce(func, self._iterable, initial)
    
    def to_list(self) -> list:
        """Force evaluation and return a list."""
        return list(self._iterable)
    
    def __iter__(self):
        """Make the pipeline itself iterable."""
        return iter(self._iterable)


def compose(*functions: Callable) -> Callable:
    """
    Compose multiple functions right-to-left.
    
    compose(f, g, h)(x) == f(g(h(x)))
    I use this when I want to build complex transformations from simple ones.
    """
    def composed(arg):
        result = arg
        for func in reversed(functions):
            result = func(result)
        return result
    return composed


def memoize(func: Callable) -> Callable:
    """
    Cache function results to avoid recomputation.
    
    Simple dict-based memoization. Works great for expensive pure functions.
    """
    cache = {}
    
    @wraps(func)
    def memoized(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    
    return memoized


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Example 1: Processing a large range without materializing it
    print("1. Processing numbers 1-1000 lazily:")
    result = (
        LazyPipeline(range(1, 1001))
        .filter(lambda x: x % 2 == 0)  # only evens
        .map(lambda x: x * x)           # square them
        .take(5)                        # first 5
        .to_list()
    )
    print(f"   First 5 squared evens: {result}")
    
    # Example 2: Currying for partial application
    print("\n2. Currying example:")
    @curry
    def multiply_then_add(x, y, z):
        return x * y + z
    
    times_5_plus_10 = multiply_then_add(5)(10)  # partially applied
    print(f"   times_5_plus_10(3) = {times_5_plus_10(3)}")  # (5 * 3) + 10 = 25
    
    # Example 3: Function composition
    print("\n3. Function composition:")
    double = lambda x: x * 2
    increment = lambda x: x + 1
    square = lambda x: x * x
    
    # Build a composed function: square(increment(double(x)))
    transform = compose(square, increment, double)
    print(f"   transform(3) = square(increment(double(3))) = {transform(3)}")
    
    # Example 4: Memoization for expensive computation
    print("\n4. Memoization (Fibonacci):")
    
    @memoize
    def fib(n):
        """Fibonacci with memoization — way faster than naive recursion."""
        if n <= 1:
            return n
        return fib(n - 1) + fib(n - 2)
    
    print(f"   fib(10) = {fib(10)}")
    print(f"   fib(30) = {fib(30)}")  # Would be slow without memoization
    
    # Example 5: Combining everything
    print("\n5. Combining pipeline + composition + currying:")
    
    @curry
    def power(base, exponent):
        return base ** exponent
    
    square_func = power(2)  # partially applied
    add_100 = lambda x: x + 100
    
    pipeline_transform = compose(add_100, square_func)
    
    result = (
        LazyPipeline(range(1, 11))
        .map(pipeline_transform)
        .filter(lambda x: x > 110)
        .to_list()
    )
    print(f"   Numbers 1-10 -> square -> add 100 -> filter > 110:")
    print(f"   {result}")
    
    print("\n=== Demo Complete ===")