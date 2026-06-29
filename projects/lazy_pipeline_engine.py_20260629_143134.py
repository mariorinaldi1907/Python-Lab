"""
Date: 2026-06-29
Created a functional pipeline utility that delays computation until needed, supporting map/filter/reduce operations with automatic memoization for expensive transformations.
"""

"""
Lazy evaluation pipeline engine with built-in memoization.

I got tired of writing nested map() and filter() calls that execute immediately,
so I built this to chain operations that only run when you actually need the result.
"""

from functools import wraps, reduce
from typing import Callable, Any, Iterable, Optional


def memoize(func: Callable) -> Callable:
    """
    Simple memoization decorator to cache function results.
    
    I'm using this to avoid recomputing expensive pipeline operations
    when the same inputs come through multiple times.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Only cache if args are hashable
        try:
            key = (args, tuple(sorted(kwargs.items())))
            if key not in cache:
                cache[key] = func(*args, **kwargs)
            return cache[key]
        except TypeError:
            # If unhashable, just compute without caching
            return func(*args, **kwargs)
    
    return wrapper


class LazyPipeline:
    """
    A lazy evaluation pipeline that chains functional operations.
    
    Operations are stored but not executed until you call .execute() or .collect().
    This lets you build complex transformations without intermediate lists.
    """
    
    def __init__(self, source: Iterable):
        """Initialize with a data source (list, generator, etc)."""
        self._source = source
        self._operations = []
    
    def map(self, func: Callable) -> 'LazyPipeline':
        """
        Add a mapping operation to the pipeline.
        
        Args:
            func: Function to apply to each element
        
        Returns:
            Self for method chaining
        """
        self._operations.append(('map', func))
        return self
    
    def filter(self, predicate: Callable) -> 'LazyPipeline':
        """
        Add a filtering operation to the pipeline.
        
        Args:
            predicate: Function that returns True to keep element
        
        Returns:
            Self for method chaining
        """
        self._operations.append(('filter', predicate))
        return self
    
    def reduce(self, func: Callable, initial: Optional[Any] = None) -> Any:
        """
        Reduce the pipeline to a single value.
        
        This is a terminal operation - it triggers execution.
        
        Args:
            func: Binary function for reduction
            initial: Starting value (optional)
        
        Returns:
            The reduced value
        """
        result = self._execute_pipeline()
        if initial is None:
            return reduce(func, result)
        return reduce(func, result, initial)
    
    def take(self, n: int) -> 'LazyPipeline':
        """
        Limit pipeline to first n elements.
        
        Useful for infinite generators or early termination.
        """
        self._operations.append(('take', n))
        return self
    
    def _execute_pipeline(self) -> Iterable:
        """
        Actually run all the queued operations.
        
        This is where the magic happens - we iterate through operations
        and apply them in sequence without creating intermediate lists.
        """
        result = iter(self._source)
        
        for op_type, op_arg in self._operations:
            if op_type == 'map':
                result = map(op_arg, result)
            elif op_type == 'filter':
                result = filter(op_arg, result)
            elif op_type == 'take':
                result = self._take_n(result, op_arg)
        
        return result
    
    @staticmethod
    def _take_n(iterable: Iterable, n: int) -> Iterable:
        """Helper to take first n items from an iterable."""
        for i, item in enumerate(iterable):
            if i >= n:
                break
            yield item
    
    def collect(self) -> list:
        """
        Execute pipeline and collect results into a list.
        
        This is a terminal operation.
        """
        return list(self._execute_pipeline())
    
    def execute(self) -> Iterable:
        """
        Execute pipeline and return an iterator.
        
        Use this if you want to iterate results without building a full list.
        """
        return self._execute_pipeline()


def curry(func: Callable) -> Callable:
    """
    Transform a multi-argument function into a chain of single-argument functions.
    
    I added this because currying is a classic FP pattern and it plays
    nicely with the pipeline when you need partial application.
    """
    def curried(*args):
        if len(args) >= func.__code__.co_argcount:
            return func(*args)
        return lambda *more_args: curried(*(args + more_args))
    return curried


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Example 1: Basic pipeline with map and filter
    print("1. Square even numbers from 1-10:")
    result = (LazyPipeline(range(1, 11))
              .filter(lambda x: x % 2 == 0)
              .map(lambda x: x ** 2)
              .collect())
    print(f"   {result}\n")
    
    # Example 2: Demonstrate laziness with infinite generator
    print("2. First 5 Fibonacci numbers (from infinite generator):")
    def fibonacci():
        """Infinite fibonacci generator to show lazy evaluation works."""
        a, b = 0, 1
        while True:
            yield a
            a, b = b, a + b
    
    fibs = (LazyPipeline(fibonacci())
            .take(5)
            .collect())
    print(f"   {fibs}\n")
    
    # Example 3: Reduce operation
    print("3. Sum of squares of odd numbers 1-20:")
    total = (LazyPipeline(range(1, 21))
             .filter(lambda x: x % 2 == 1)
             .map(lambda x: x ** 2)
             .reduce(lambda a, b: a + b, 0))
    print(f"   {total}\n")
    
    # Example 4: Memoization demo
    print("4. Memoization test (expensive computation):")
    
    @memoize
    def expensive_operation(n: int) -> int:
        """Simulated expensive calculation."""
        print(f"   Computing for {n}...")
        return n ** 3
    
    print("   First call:")
    print(f"   Result: {expensive_operation(5)}")
    print("   Second call (should use cache):")
    print(f"   Result: {expensive_operation(5)}\n")
    
    # Example 5: Currying demo
    print("5. Currying example:")
    
    @curry
    def multiply_three(a, b, c):
        """Multiply three numbers together."""
        return a * b * c
    
    double = multiply_three(2)
    quadruple = double(2)
    result = quadruple(5)
    print(f"   multiply_three(2)(2)(5) = {result}")