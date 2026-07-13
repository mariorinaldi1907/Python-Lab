"""
Date: 2026-07-13
Created a functional programming toolkit that lets me chain operations lazily, cache expensive computations, and partially apply functions for cleaner data processing code.
"""

"""
Functional programming utilities for lazy evaluation and data transformation.
I wanted a clean way to process large datasets without loading everything at once.
"""

from functools import wraps
from typing import Callable, Iterable, Any, TypeVar
from collections.abc import Iterator


T = TypeVar('T')
U = TypeVar('U')


def memoize(func: Callable) -> Callable:
    """
    Cache function results to avoid recomputing expensive operations.
    Works with both regular functions and methods — I use this all the time
    for recursive algorithms and API calls that return the same data.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create a hashable key from args and kwargs
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    wrapper.cache = cache  # Expose cache for debugging/testing
    wrapper.clear_cache = lambda: cache.clear()
    return wrapper


def curry(func: Callable) -> Callable:
    """
    Transform a multi-argument function into a sequence of single-argument functions.
    This makes partial application super clean — you can build specialized functions
    from general ones without lambda spam.
    """
    @wraps(func)
    def curried(*args, **kwargs):
        # Try to call the function with what we have
        try:
            return func(*args, **kwargs)
        except TypeError:
            # Not enough args, return a new function that accepts more
            def partial(*more_args, **more_kwargs):
                combined_kwargs = {**kwargs, **more_kwargs}
                return curried(*(args + more_args), **combined_kwargs)
            return partial
    
    return curried


class LazyPipeline:
    """
    Chain operations on iterables without evaluating until needed.
    The key insight here is that we store transformations and only apply them
    when someone actually iterates — saves memory and allows infinite sequences.
    """
    
    def __init__(self, source: Iterable[T]):
        """Start a pipeline with an iterable source."""
        self._source = source
        self._operations = []
    
    def map(self, func: Callable[[T], U]) -> 'LazyPipeline':
        """Apply a transformation to each element (lazily)."""
        self._operations.append(('map', func))
        return self
    
    def filter(self, predicate: Callable[[T], bool]) -> 'LazyPipeline':
        """Keep only elements matching the predicate (lazily)."""
        self._operations.append(('filter', predicate))
        return self
    
    def take(self, n: int) -> 'LazyPipeline':
        """Limit the pipeline to first n elements."""
        self._operations.append(('take', n))
        return self
    
    def __iter__(self) -> Iterator:
        """
        Execute the pipeline when someone iterates.
        This is where the magic happens — we walk through the source and
        apply each operation one element at a time.
        """
        result = iter(self._source)
        
        for op_type, op_arg in self._operations:
            if op_type == 'map':
                result = map(op_arg, result)
            elif op_type == 'filter':
                result = filter(op_arg, result)
            elif op_type == 'take':
                result = self._take_helper(result, op_arg)
        
        return result
    
    @staticmethod
    def _take_helper(iterable: Iterable[T], n: int) -> Iterator[T]:
        """Helper to take first n items from an iterable."""
        for i, item in enumerate(iterable):
            if i >= n:
                break
            yield item
    
    def to_list(self) -> list:
        """Force evaluation and collect results into a list."""
        return list(self)
    
    def reduce(self, func: Callable[[T, T], T], initial: Any = None) -> Any:
        """
        Reduce the pipeline to a single value.
        Forces evaluation since we need all elements.
        """
        from functools import reduce as functools_reduce
        items = list(self)
        if initial is None:
            return functools_reduce(func, items)
        return functools_reduce(func, items, initial)


def compose(*functions: Callable) -> Callable:
    """
    Compose functions right-to-left (mathematical style).
    compose(f, g, h)(x) == f(g(h(x)))
    I prefer this to nested calls when building data transformations.
    """
    def composed(arg):
        result = arg
        for func in reversed(functions):
            result = func(result)
        return result
    return composed


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Example 1: Process infinite sequence lazily
    print("1. Infinite sequence (Fibonacci), filtered and limited:")
    
    def fibonacci():
        """Generate infinite Fibonacci sequence."""
        a, b = 0, 1
        while True:
            yield a
            a, b = b, a + b
    
    result = (LazyPipeline(fibonacci())
              .filter(lambda x: x % 2 == 0)  # Only even numbers
              .take(10)                       # First 10 matches
              .to_list())
    print(f"First 10 even Fibonacci numbers: {result}\n")
    
    # Example 2: Memoization for expensive computation
    print("2. Memoized factorial (notice speed difference):")
    
    @memoize
    def factorial(n: int) -> int:
        """Recursive factorial with memoization."""
        if n <= 1:
            return 1
        return n * factorial(n - 1)
    
    print(f"factorial(100): {factorial(100)}")
    print(f"Cache size: {len(factorial.cache)} entries\n")
    
    # Example 3: Currying for partial application
    print("3. Currying for building specialized functions:")
    
    @curry
    def multiply_and_add(x, y, z):
        """(x * y) + z"""
        return x * y + z
    
    double_and_add = multiply_and_add(2)  # Partially applied
    double_and_add_10 = double_and_add(y=5)  # More partial application
    
    print(f"double_and_add(5)(10) = {double_and_add(5)(10)}")
    print(f"double_and_add_10(7) = {double_and_add_10(7)}\n")
    
    # Example 4: Function composition
    print("4. Function composition for data transformation:")
    
    def add_one(x): return x + 1
    def square(x): return x * x
    def negate(x): return -x
    
    transform = compose(negate, square, add_one)
    
    numbers = [1, 2, 3, 4, 5]
    print(f"Original: {numbers}")
    print(f"After compose(negate, square, add_one): {[transform(x) for x in numbers]}\n")
    
    # Example 5: Complex pipeline
    print("5. Complex pipeline with multiple operations:")
    
    words = ["hello", "world", "python", "functional", "programming", "lazy"]
    result = (LazyPipeline(words)
              .filter(lambda w: len(w) > 5)      # Long words only
              .map(lambda w: w.upper())          # Uppercase
              .map(lambda w: f"[{w}]")           # Wrap in brackets
              .to_list())
    
    print(f"Processed words: {result}")