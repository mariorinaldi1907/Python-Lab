"""
Date: 2026-07-04
Created a composable lazy pipeline system that lets me chain transformations functionally and only evaluate when I actually iterate, plus auto-memoizes expensive operations.
"""

"""
Lazy evaluation pipeline with functional programming utilities.

I wanted a way to chain transformations on data without computing everything
immediately. This lets me compose operations, curry functions, and memoize
results — all while keeping things lazy until I actually need the output.
"""

from functools import wraps
from typing import Callable, Iterable, Any, TypeVar


T = TypeVar('T')
U = TypeVar('U')


def memoize(func: Callable) -> Callable:
    """
    Cache function results to avoid recomputing expensive operations.
    
    I use this for any pure function that might get called repeatedly
    with the same arguments. Stores results in a dict keyed by args.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    
    return wrapper


def curry(func: Callable) -> Callable:
    """
    Convert a multi-argument function into a chain of single-argument functions.
    
    This is useful when I want to partially apply arguments and reuse
    the partially-applied function in different contexts.
    """
    @wraps(func)
    def curried(*args):
        # If we have enough args, call the original function
        try:
            return func(*args)
        except TypeError:
            # Not enough args, return a function waiting for more
            def partial(*more_args):
                return curried(*(args + more_args))
            return partial
    
    return curried


class LazyPipeline:
    """
    A composable pipeline that defers computation until values are needed.
    
    I built this because I was tired of intermediate lists being created
    when chaining map/filter operations. This keeps everything as generators
    and only computes when you iterate or call .collect().
    """
    
    def __init__(self, source: Iterable[T]):
        """Initialize pipeline with a data source."""
        self._source = source
        self._operations = []
    
    def map(self, func: Callable[[T], U]) -> 'LazyPipeline':
        """
        Transform each element using the provided function.
        
        Returns a new pipeline with this operation queued up.
        """
        new_pipeline = LazyPipeline(self._source)
        new_pipeline._operations = self._operations + [('map', func)]
        return new_pipeline
    
    def filter(self, predicate: Callable[[T], bool]) -> 'LazyPipeline':
        """
        Keep only elements where predicate returns True.
        
        Like map, this doesn't execute immediately — just adds to the queue.
        """
        new_pipeline = LazyPipeline(self._source)
        new_pipeline._operations = self._operations + [('filter', predicate)]
        return new_pipeline
    
    def take(self, n: int) -> 'LazyPipeline':
        """
        Limit the pipeline to the first n elements.
        
        Useful for working with infinite sequences or just grabbing a sample.
        """
        new_pipeline = LazyPipeline(self._source)
        new_pipeline._operations = self._operations + [('take', n)]
        return new_pipeline
    
    def __iter__(self):
        """
        Execute the pipeline lazily, yielding one element at a time.
        
        This is where the actual computation happens. Each operation
        is applied in order as we iterate through the source.
        """
        iterator = iter(self._source)
        
        for op_type, op_arg in self._operations:
            if op_type == 'map':
                iterator = map(op_arg, iterator)
            elif op_type == 'filter':
                iterator = filter(op_arg, iterator)
            elif op_type == 'take':
                # Manually implement take using itertools-style logic
                def take_iter(it, n):
                    for i, item in enumerate(it):
                        if i >= n:
                            break
                        yield item
                iterator = take_iter(iterator, op_arg)
        
        return iterator
    
    def collect(self) -> list:
        """
        Force evaluation and collect all results into a list.
        
        This is when lazy evaluation ends and we actually compute everything.
        """
        return list(self)
    
    def reduce(self, func: Callable[[T, T], T], initial: Any = None) -> Any:
        """
        Reduce the pipeline to a single value using the given function.
        
        I need this for aggregations like sum, product, or custom folds.
        """
        iterator = iter(self)
        
        if initial is None:
            try:
                result = next(iterator)
            except StopIteration:
                raise TypeError("reduce() of empty sequence with no initial value")
        else:
            result = initial
        
        for item in iterator:
            result = func(result, item)
        
        return result


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Example 1: Basic pipeline with map and filter
    print("1. Basic pipeline: square even numbers from 1-10")
    result = (LazyPipeline(range(1, 11))
              .filter(lambda x: x % 2 == 0)
              .map(lambda x: x ** 2)
              .collect())
    print(f"   Result: {result}\n")
    
    # Example 2: Using take to limit results
    print("2. Working with infinite sequences (first 5 Fibonacci numbers)")
    def fibonacci():
        a, b = 0, 1
        while True:
            yield a
            a, b = b, a + b
    
    fibs = LazyPipeline(fibonacci()).take(5).collect()
    print(f"   Result: {fibs}\n")
    
    # Example 3: Currying demo
    print("3. Currying example: partial application")
    @curry
    def multiply(x, y, z):
        return x * y * z
    
    double = multiply(2)  # Partially applied
    double_and_triple = double(3)  # More partial application
    result = double_and_triple(4)  # Final application
    print(f"   multiply(2)(3)(4) = {result}\n")
    
    # Example 4: Memoization demo
    print("4. Memoization: expensive fibonacci calculation")
    call_count = 0
    
    @memoize
    def fib_recursive(n):
        global call_count
        call_count += 1
        if n <= 1:
            return n
        return fib_recursive(n - 1) + fib_recursive(n - 2)
    
    result = fib_recursive(10)
    print(f"   fib(10) = {result}, function called {call_count} times (with memoization)")
    
    # Without memoization would be 177 calls!
    print(f"   Without memoization, it would take 177 calls\n")
    
    # Example 5: Complex pipeline with reduce
    print("5. Complex pipeline: sum of squares of odd numbers in range")
    result = (LazyPipeline(range(1, 20))
              .filter(lambda x: x % 2 == 1)
              .map(lambda x: x ** 2)
              .reduce(lambda a, b: a + b, 0))
    print(f"   Result: {result}\n")
    
    print("All examples completed successfully!")