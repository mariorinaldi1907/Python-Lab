"""
Date: 2026-08-25
Created a functional pipeline system that lazily evaluates transformations and caches results, makes it super clean to compose operations on iterables.
"""

"""
Lazy evaluation pipeline utilities with memoization support.

I got tired of writing nested map/filter chains and wanted something
more readable that doesn't compute everything upfront.
"""

from functools import wraps
from typing import Callable, Iterable, Any, TypeVar


T = TypeVar('T')
U = TypeVar('U')


def memoize(func: Callable) -> Callable:
    """
    Simple memoization decorator that caches function results.
    
    I'm using a dict to store results keyed by stringified args.
    Not perfect for unhashable types but works fine for primitives.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create a cache key from args and kwargs
        key = str(args) + str(sorted(kwargs.items()))
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        
        return cache[key]
    
    # Expose cache for inspection/debugging
    wrapper.cache = cache
    return wrapper


class LazyPipeline:
    """
    A composable lazy evaluation pipeline.
    
    Operations are only executed when you actually iterate or convert
    to a list. This is great when you have expensive transformations
    and only need the first few results.
    """
    
    def __init__(self, source: Iterable[T]):
        """Initialize with a source iterable."""
        self._source = source
        self._operations = []
    
    def map(self, func: Callable[[T], U]) -> 'LazyPipeline':
        """
        Apply a transformation to each element.
        
        Returns self so you can chain operations fluently.
        """
        self._operations.append(('map', func))
        return self
    
    def filter(self, predicate: Callable[[T], bool]) -> 'LazyPipeline':
        """Keep only elements that satisfy the predicate."""
        self._operations.append(('filter', predicate))
        return self
    
    def take(self, n: int) -> 'LazyPipeline':
        """Take only the first n elements."""
        self._operations.append(('take', n))
        return self
    
    def skip(self, n: int) -> 'LazyPipeline':
        """Skip the first n elements."""
        self._operations.append(('skip', n))
        return self
    
    def __iter__(self):
        """
        Execute the pipeline lazily.
        
        This is where the magic happens - we process one element at a time
        through the entire chain of operations.
        """
        iterator = iter(self._source)
        
        for op_type, op_arg in self._operations:
            if op_type == 'map':
                iterator = map(op_arg, iterator)
            elif op_type == 'filter':
                iterator = filter(op_arg, iterator)
            elif op_type == 'take':
                iterator = self._take_iterator(iterator, op_arg)
            elif op_type == 'skip':
                iterator = self._skip_iterator(iterator, op_arg)
        
        return iterator
    
    @staticmethod
    def _take_iterator(iterator: Iterable[T], n: int) -> Iterable[T]:
        """Helper to take first n items from an iterator."""
        for i, item in enumerate(iterator):
            if i >= n:
                break
            yield item
    
    @staticmethod
    def _skip_iterator(iterator: Iterable[T], n: int) -> Iterable[T]:
        """Helper to skip first n items from an iterator."""
        for i, item in enumerate(iterator):
            if i >= n:
                yield item
    
    def to_list(self) -> list:
        """Materialize the pipeline into a list."""
        return list(self)
    
    def first(self, default=None) -> Any:
        """Get the first element, or default if empty."""
        for item in self:
            return item
        return default


def curry(func: Callable) -> Callable:
    """
    Simple currying implementation for functions.
    
    Transforms f(x, y, z) into f(x)(y)(z).
    Only works with positional args - good enough for my use case.
    """
    import inspect
    
    sig = inspect.signature(func)
    num_params = len(sig.parameters)
    
    def curried(*args):
        if len(args) >= num_params:
            return func(*args[:num_params])
        else:
            # Need more args, return a partial function
            def partial(*more_args):
                return curried(*(args + more_args))
            return partial
    
    return curried


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Example 1: Basic pipeline with lazy evaluation
    print("1. Processing numbers 1-10, but only taking first 3 results:")
    result = (LazyPipeline(range(1, 11))
              .map(lambda x: x ** 2)
              .filter(lambda x: x % 2 == 0)
              .take(3)
              .to_list())
    print(f"   Result: {result}")
    
    # Example 2: Demonstrating laziness with a side effect
    print("\n2. Showing lazy evaluation (with side effects):")
    
    def expensive_transform(x):
        print(f"   Processing {x}...")
        return x * 2
    
    pipeline = LazyPipeline(range(5)).map(expensive_transform).take(2)
    print("   Pipeline created (no output yet)")
    print("   Now materializing:")
    list(pipeline)
    
    # Example 3: Memoization demo
    print("\n3. Memoization example:")
    
    @memoize
    def fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)
    
    print(f"   fib(10) = {fibonacci(10)}")
    print(f"   fib(15) = {fibonacci(15)}")
    print(f"   Cache size: {len(fibonacci.cache)} entries")
    
    # Example 4: Currying demo
    print("\n4. Currying example:")
    
    @curry
    def multiply(x, y, z):
        return x * y * z
    
    double = multiply(2)
    double_and_triple = double(3)
    result = double_and_triple(4)
    
    print(f"   multiply(2)(3)(4) = {result}")
    print(f"   Or in one go: multiply(2, 3, 4) = {multiply(2, 3, 4)}")
    
    # Example 5: Real-world-ish use case
    print("\n5. Processing log entries (simulated):")
    
    logs = [
        "ERROR: Database connection failed",
        "INFO: User logged in",
        "ERROR: Timeout on API call",
        "DEBUG: Cache hit",
        "ERROR: Invalid input",
        "INFO: Request completed"
    ]
    
    errors = (LazyPipeline(logs)
              .filter(lambda log: log.startswith("ERROR"))
              .map(lambda log: log.split(": ")[1])
              .to_list())
    
    print(f"   Found {len(errors)} errors:")
    for error in errors:
        print(f"     - {error}")