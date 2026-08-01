"""
Date: 2026-08-01
Created a functional programming utility that lets me compose data transformations lazily with automatic memoization, because I got tired of rewriting the same map/filter/reduce chains.
"""

"""
Lazy evaluation pipeline with built-in memoization.

I wanted a clean way to chain operations on iterables without computing
everything upfront. This lets me build complex transformations that only
execute when I actually need the results.
"""

from functools import wraps
from typing import Callable, Iterable, Any, TypeVar
from collections.abc import Iterator


T = TypeVar('T')
U = TypeVar('U')


def memoize(func: Callable) -> Callable:
    """
    Decorator that caches function results based on arguments.
    
    Uses a dict to store computed values. Only works with hashable args,
    but that's fine for most pure functions I write.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # kwargs make the key more complex, but I need them sometimes
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    wrapper.cache = cache  # expose cache for debugging
    return wrapper


class LazyPipeline:
    """
    Composable lazy evaluation pipeline.
    
    Each operation returns a new pipeline without executing anything.
    Only when you call collect(), take(), or iterate does it actually run.
    This is useful when working with large datasets or expensive operations.
    """
    
    def __init__(self, source: Iterable[T]):
        """Initialize pipeline with a data source."""
        self._source = source
        self._operations = []
    
    def map(self, func: Callable[[T], U]) -> 'LazyPipeline':
        """Apply a function to each element."""
        new_pipeline = LazyPipeline(self._source)
        new_pipeline._operations = self._operations + [('map', func)]
        return new_pipeline
    
    def filter(self, predicate: Callable[[T], bool]) -> 'LazyPipeline':
        """Keep only elements that satisfy the predicate."""
        new_pipeline = LazyPipeline(self._source)
        new_pipeline._operations = self._operations + [('filter', predicate)]
        return new_pipeline
    
    def flat_map(self, func: Callable[[T], Iterable[U]]) -> 'LazyPipeline':
        """Map and flatten the results (useful for nested structures)."""
        new_pipeline = LazyPipeline(self._source)
        new_pipeline._operations = self._operations + [('flat_map', func)]
        return new_pipeline
    
    def memoized(self, func: Callable[[T], U]) -> 'LazyPipeline':
        """Apply a memoized function — caches results for repeated inputs."""
        memoized_func = memoize(func)
        return self.map(memoized_func)
    
    def _execute(self) -> Iterator:
        """
        Internal method that actually runs the pipeline.
        
        Iterates through each operation in sequence. I'm using generators
        here so everything stays lazy until the very end.
        """
        result = iter(self._source)
        
        for op_type, func in self._operations:
            if op_type == 'map':
                result = map(func, result)
            elif op_type == 'filter':
                result = filter(func, result)
            elif op_type == 'flat_map':
                # flatten by chaining all sub-iterables
                def flatten(it):
                    for item in it:
                        yield from func(item)
                result = flatten(result)
        
        return result
    
    def collect(self) -> list:
        """Execute the pipeline and collect all results into a list."""
        return list(self._execute())
    
    def take(self, n: int) -> list:
        """Execute and take only the first n results."""
        result = []
        for i, item in enumerate(self._execute()):
            if i >= n:
                break
            result.append(item)
        return result
    
    def reduce(self, func: Callable[[T, T], T], initial: Any = None) -> Any:
        """
        Reduce the pipeline to a single value.
        
        I could've used functools.reduce here, but wrote it out explicitly
        to handle the optional initial value more clearly.
        """
        iterator = self._execute()
        
        if initial is None:
            try:
                accumulator = next(iterator)
            except StopIteration:
                raise ValueError("reduce() of empty sequence with no initial value")
        else:
            accumulator = initial
        
        for item in iterator:
            accumulator = func(accumulator, item)
        
        return accumulator
    
    def __iter__(self):
        """Make the pipeline itself iterable."""
        return self._execute()


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Example 1: Basic transformations
    print("1. Basic map/filter chain:")
    numbers = range(1, 11)
    result = (LazyPipeline(numbers)
              .filter(lambda x: x % 2 == 0)
              .map(lambda x: x ** 2)
              .collect())
    print(f"   Even squares from 1-10: {result}")
    
    # Example 2: Expensive computation with memoization
    print("\n2. Memoized expensive operation:")
    call_count = {'count': 0}
    
    def expensive_operation(n: int) -> int:
        """Simulates an expensive calculation."""
        call_count['count'] += 1
        return n * n + 2 * n + 1
    
    data = [1, 2, 3, 2, 1, 4, 3, 2]  # intentional duplicates
    result = (LazyPipeline(data)
              .memoized(expensive_operation)
              .collect())
    print(f"   Input: {data}")
    print(f"   Result: {result}")
    print(f"   Function called {call_count['count']} times (not 8, due to memoization)")
    
    # Example 3: Flat map for nested structures
    print("\n3. Flat map example:")
    words = ["hello world", "lazy evaluation", "python rocks"]
    result = (LazyPipeline(words)
              .flat_map(lambda s: s.split())
              .map(str.upper)
              .collect())
    print(f"   Flattened and uppercased: {result}")
    
    # Example 4: Lazy evaluation with take (only computes what's needed)
    print("\n4. Lazy evaluation with take():")
    result = (LazyPipeline(range(1000000))
              .map(lambda x: x ** 2)
              .filter(lambda x: x % 7 == 0)
              .take(5))
    print(f"   First 5 squares divisible by 7: {result}")
    
    # Example 5: Reduce to sum
    print("\n5. Reduce example:")
    total = (LazyPipeline(range(1, 6))
             .map(lambda x: x * 2)
             .reduce(lambda a, b: a + b))
    print(f"   Sum of doubled numbers 1-5: {total}")