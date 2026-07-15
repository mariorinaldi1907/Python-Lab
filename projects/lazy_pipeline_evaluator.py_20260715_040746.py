"""
Date: 2026-07-15
Created a functional pipeline library that chains transformations lazily and only computes when needed — saves a ton of work when you only want the first few results.
"""

"""
Lazy evaluation pipeline for functional-style data processing.

I kept running into situations where I'd chain a bunch of map/filter operations
and only need a few results, but Python would eagerly process everything.
This fixes that with real lazy eval and some nice composability.
"""

from functools import wraps
from typing import Callable, Iterator, Any, TypeVar


T = TypeVar('T')
U = TypeVar('U')


class LazyPipeline:
    """
    A composable pipeline that defers execution until results are actually needed.
    
    The big win here is that if you only take(5) from a huge dataset, we'll only
    process exactly 5 items, not the whole thing. Chain as many operations as
    you want — they all stay lazy.
    """
    
    def __init__(self, source):
        """Initialize with an iterable source."""
        # Store the source as an iterator factory so we can reset if needed
        if callable(source):
            self._source_factory = source
        else:
            self._source_factory = lambda: iter(source)
        
        self._operations = []
    
    def map(self, func: Callable[[T], U]) -> 'LazyPipeline':
        """Apply a transformation to each element."""
        new_pipeline = LazyPipeline(self._source_factory)
        new_pipeline._operations = self._operations + [('map', func)]
        return new_pipeline
    
    def filter(self, predicate: Callable[[T], bool]) -> 'LazyPipeline':
        """Keep only elements that satisfy the predicate."""
        new_pipeline = LazyPipeline(self._source_factory)
        new_pipeline._operations = self._operations + [('filter', predicate)]
        return new_pipeline
    
    def take(self, n: int) -> list:
        """
        Consume up to n elements from the pipeline.
        
        This is where the magic happens — we only process exactly what we need.
        """
        result = []
        for i, item in enumerate(self._execute()):
            if i >= n:
                break
            result.append(item)
        return result
    
    def collect(self) -> list:
        """Consume all elements and return as a list."""
        return list(self._execute())
    
    def _execute(self) -> Iterator:
        """
        Actually run the pipeline by applying operations in sequence.
        
        This yields results one at a time, so if the consumer stops early,
        we stop processing. That's the whole point of lazy evaluation.
        """
        stream = self._source_factory()
        
        for operation, func in self._operations:
            if operation == 'map':
                stream = map(func, stream)
            elif operation == 'filter':
                stream = filter(func, stream)
        
        yield from stream


def memoize(func: Callable) -> Callable:
    """
    Cache function results based on arguments.
    
    I originally wrote this for some recursive Fibonacci stuff and it made
    a ridiculous difference. Works with any hashable args.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args):
        if args in cache:
            return cache[args]
        
        result = func(*args)
        cache[args] = result
        return result
    
    # Expose the cache for debugging/inspection
    wrapper.cache = cache
    return wrapper


def curry(func: Callable) -> Callable:
    """
    Transform a multi-arg function into a chain of single-arg functions.
    
    Useful for partial application. If you have add(x, y), currying gives you
    add(x)(y), which means you can do stuff like add_five = add(5).
    """
    def curried(*args):
        # Try to call with current args, if it fails, return another curried function
        try:
            return func(*args)
        except TypeError:
            # Not enough args yet, return a function that waits for more
            def partial(*more_args):
                return curried(*(args + more_args))
            return partial
    
    return curried


def compose(*functions: Callable) -> Callable:
    """
    Compose functions right-to-left (math style).
    
    compose(f, g, h)(x) is the same as f(g(h(x))).
    I always forget the direction so I put this comment here.
    """
    def composed(arg):
        result = arg
        for func in reversed(functions):
            result = func(result)
        return result
    
    return composed


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Simulating an expensive data source
    def expensive_range(n):
        """This would normally be a database query or file read."""
        for i in range(n):
            print(f"  [generating {i}]")
            yield i
    
    print("Creating pipeline: filter evens, square them, add 10")
    pipeline = (LazyPipeline(lambda: expensive_range(100))
                .filter(lambda x: x % 2 == 0)
                .map(lambda x: x ** 2)
                .map(lambda x: x + 10))
    
    print("\nTaking only first 5 results (notice we don't generate all 100):")
    result = pipeline.take(5)
    print(f"Result: {result}\n")
    
    print("\n=== Memoization Demo ===\n")
    
    @memoize
    def fibonacci(n):
        """Classic fib with memoization — makes it actually usable."""
        if n < 2:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)
    
    print("Computing fibonacci(30) with memoization:")
    result = fibonacci(30)
    print(f"Result: {result}")
    print(f"Cache size: {len(fibonacci.cache)} entries\n")
    
    print("\n=== Curry Demo ===\n")
    
    @curry
    def multiply(x, y, z):
        """Multiply three numbers."""
        return x * y * z
    
    print("Curried multiply(2, 3, 4):")
    print(f"  All at once: {multiply(2, 3, 4)}")
    print(f"  Partial application: {multiply(2)(3)(4)}")
    
    double = multiply(2)
    print(f"  double(5, 6) = {double(5, 6)}\n")
    
    print("\n=== Compose Demo ===\n")
    
    add_ten = lambda x: x + 10
    square = lambda x: x ** 2
    halve = lambda x: x / 2
    
    # Read right to left: halve, then square, then add 10
    pipeline_func = compose(add_ten, square, halve)
    
    print("compose(add_ten, square, halve)(20):")
    print(f"  Step by step: 20 -> halve -> 10 -> square -> 100 -> add_ten -> 110")
    print(f"  Result: {pipeline_func(20)}")