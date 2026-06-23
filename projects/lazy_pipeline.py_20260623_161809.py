"""
Date: 2026-06-23
Created a composable pipeline that lazily evaluates transformations on iterables, inspired by how much I love Elixir's pipe operator but wanted it in Python.
"""

"""
Lazy evaluation pipeline for composing transformations on iterables.

I got tired of writing nested comprehensions and wanted something cleaner
that doesn't blow up memory when processing large sequences. This evaluates
transformations only when you call .collect() or iterate over it.
"""

from functools import wraps
from typing import Callable, Iterable, Any, TypeVar


T = TypeVar('T')
U = TypeVar('U')


class LazyPipeline:
    """
    A lazy evaluation pipeline that chains transformations without immediate execution.
    
    The core idea: store operations as a list of functions, then apply them all
    at once when someone actually requests the data. This keeps memory usage low
    and lets us compose complex transformations readably.
    """
    
    def __init__(self, iterable: Iterable[Any]):
        """Initialize with a source iterable."""
        self._source = iterable
        self._operations = []
    
    def map(self, func: Callable[[T], U]) -> 'LazyPipeline':
        """
        Apply a transformation to each element.
        
        Doesn't execute immediately — just records that we want to map later.
        """
        self._operations.append(('map', func))
        return self
    
    def filter(self, predicate: Callable[[T], bool]) -> 'LazyPipeline':
        """Keep only elements where predicate returns True."""
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
    
    def flat_map(self, func: Callable[[T], Iterable[U]]) -> 'LazyPipeline':
        """Map then flatten one level — useful for expanding elements."""
        self._operations.append(('flat_map', func))
        return self
    
    def _execute(self) -> Iterable[Any]:
        """
        Actually run all the queued operations.
        
        This is where the magic happens — we chain all operations into
        a single generator expression to keep memory usage constant.
        """
        result = iter(self._source)
        
        for op_type, op_arg in self._operations:
            if op_type == 'map':
                result = (op_arg(item) for item in result)
            elif op_type == 'filter':
                result = (item for item in result if op_arg(item))
            elif op_type == 'take':
                result = self._take_helper(result, op_arg)
            elif op_type == 'skip':
                result = self._skip_helper(result, op_arg)
            elif op_type == 'flat_map':
                result = (sub_item for item in result for sub_item in op_arg(item))
        
        return result
    
    @staticmethod
    def _take_helper(iterable: Iterable[T], n: int) -> Iterable[T]:
        """Helper to take first n items from an iterable."""
        for i, item in enumerate(iterable):
            if i >= n:
                break
            yield item
    
    @staticmethod
    def _skip_helper(iterable: Iterable[T], n: int) -> Iterable[T]:
        """Helper to skip first n items from an iterable."""
        for i, item in enumerate(iterable):
            if i >= n:
                yield item
    
    def collect(self) -> list:
        """Execute the pipeline and return results as a list."""
        return list(self._execute())
    
    def reduce(self, func: Callable[[T, T], T], initial: Any = None) -> Any:
        """
        Reduce the pipeline to a single value.
        
        I went back and forth on whether to include an initial value param,
        but it's too useful for things like summing to skip it.
        """
        result = self._execute()
        
        if initial is None:
            # No initial value — use first element
            try:
                accumulator = next(iter(result))
            except StopIteration:
                raise ValueError("reduce() of empty sequence with no initial value")
        else:
            accumulator = initial
        
        for item in result:
            accumulator = func(accumulator, item)
        
        return accumulator
    
    def for_each(self, func: Callable[[T], None]) -> None:
        """Execute a side effect for each element (终端 operation)."""
        for item in self._execute():
            func(item)
    
    def __iter__(self):
        """Allow direct iteration over the pipeline."""
        return iter(self._execute())


def memoize(func: Callable) -> Callable:
    """
    Simple memoization decorator with unbounded cache.
    
    Yeah, functools.lru_cache exists, but I wanted to write my own to understand
    the mechanics. In production I'd use lru_cache for the eviction policy.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create a cache key from args and kwargs
        # Using repr() since not all types are hashable
        key = (args, tuple(sorted(kwargs.items())))
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        
        return cache[key]
    
    wrapper.cache = cache  # Expose cache for inspection/clearing
    return wrapper


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Example 1: Processing numbers with multiple transformations
    print("1. Chain transformations on range(1, 20):")
    result = (
        LazyPipeline(range(1, 20))
        .filter(lambda x: x % 2 == 0)  # Keep evens
        .map(lambda x: x * x)           # Square them
        .take(5)                         # Take first 5
        .collect()
    )
    print(f"   Evens squared, first 5: {result}")
    
    # Example 2: Flat mapping to expand elements
    print("\n2. Flat map to duplicate elements:")
    words = ["hello", "world", "lazy", "eval"]
    result = (
        LazyPipeline(words)
        .flat_map(lambda word: [word, word.upper()])
        .collect()
    )
    print(f"   {result}")
    
    # Example 3: Reduce to sum
    print("\n3. Reduce to calculate sum:")
    total = (
        LazyPipeline(range(1, 11))
        .map(lambda x: x * 2)
        .reduce(lambda a, b: a + b, 0)
    )
    print(f"   Sum of doubled numbers 1-10: {total}")
    
    # Example 4: Demonstrating laziness with side effects
    print("\n4. Demonstrating lazy evaluation (watch the execution order):")
    
    def loud_square(x):
        print(f"   -> Squaring {x}")
        return x * x
    
    pipeline = (
        LazyPipeline(range(5))
        .map(loud_square)
        .filter(lambda x: x > 5)
    )
    
    print("   Pipeline created but not executed yet...")
    print("   Now collecting:")
    result = pipeline.collect()
    print(f"   Result: {result}")
    
    # Example 5: Memoization demo
    print("\n5. Memoization with expensive Fibonacci:")
    
    @memoize
    def fib(n):
        if n < 2:
            return n
        return fib(n - 1) + fib(n - 2)
    
    print(f"   fib(10) = {fib(10)}")
    print(f"   fib(15) = {fib(15)} (reuses cached values)")
    print(f"   Cache size: {len(fib.cache)} entries")