"""
Date: 2026-06-25
Created a composable pipeline utility that lazily evaluates function chains and caches results, because I got tired of recomputing expensive operations in my data scripts.
"""

"""
Lazy evaluation pipeline with automatic memoization.

I kept running into situations where I'd chain a bunch of data transformations
but only need the result sometimes, or need it multiple times. This lets me
compose functions lazily and cache results automatically.
"""

import functools
from typing import Any, Callable, Iterator, Optional


def memoize(func: Callable) -> Callable:
    """
    Simple memoization decorator that caches function results.
    
    I'm using a dict here instead of lru_cache because I want full control
    over the cache and it's easier to inspect for debugging.
    """
    cache = {}
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create a hashable key from args and kwargs
        # This won't work for unhashable types but that's fine for my use case
        cache_key = (args, tuple(sorted(kwargs.items())))
        
        if cache_key not in cache:
            cache[cache_key] = func(*args, **kwargs)
        return cache[cache_key]
    
    # Attach cache so I can inspect it if needed
    wrapper.cache = cache
    return wrapper


class LazyPipeline:
    """
    Composable pipeline that doesn't evaluate until you explicitly ask for results.
    
    This is useful when you want to define a series of transformations but only
    compute them if/when needed. Each step is memoized automatically.
    """
    
    def __init__(self, data: Any):
        """Initialize with some starting data."""
        self._data = data
        self._operations = []
        self._computed = False
        self._result = None
    
    def map(self, func: Callable) -> 'LazyPipeline':
        """
        Apply a function to each element (if iterable) or to the whole value.
        
        Returns self for method chaining.
        """
        self._operations.append(('map', func))
        self._computed = False
        return self
    
    def filter(self, predicate: Callable) -> 'LazyPipeline':
        """Filter elements based on a predicate function."""
        self._operations.append(('filter', predicate))
        self._computed = False
        return self
    
    def reduce(self, func: Callable, initial: Optional[Any] = None) -> 'LazyPipeline':
        """
        Reduce operation — accumulate values using a binary function.
        
        If initial is None, uses the first element as the starting value.
        """
        self._operations.append(('reduce', func, initial))
        self._computed = False
        return self
    
    def execute(self) -> Any:
        """
        Actually compute the pipeline result.
        
        This is where the lazy evaluation happens — nothing runs until you call this.
        Results are cached so subsequent calls don't recompute.
        """
        if self._computed:
            return self._result
        
        result = self._data
        
        for operation in self._operations:
            op_type = operation[0]
            
            if op_type == 'map':
                func = operation[1]
                # Check if result is iterable (but not string, because strings are weird)
                if hasattr(result, '__iter__') and not isinstance(result, str):
                    result = [func(x) for x in result]
                else:
                    result = func(result)
            
            elif op_type == 'filter':
                predicate = operation[1]
                result = [x for x in result if predicate(x)]
            
            elif op_type == 'reduce':
                func = operation[1]
                initial = operation[2]
                
                if initial is not None:
                    accumulator = initial
                    items = result
                else:
                    accumulator = result[0]
                    items = result[1:]
                
                for item in items:
                    accumulator = func(accumulator, item)
                result = accumulator
        
        self._result = result
        self._computed = True
        return result
    
    def __repr__(self) -> str:
        """Show pipeline state for debugging."""
        status = "computed" if self._computed else "lazy"
        return f"LazyPipeline({len(self._operations)} operations, {status})"


def curry(func: Callable, arity: Optional[int] = None) -> Callable:
    """
    Curry a function — transforms f(a, b, c) into f(a)(b)(c).
    
    I added the arity parameter because Python doesn't make it easy to inspect
    how many args a function actually needs (especially with *args).
    """
    if arity is None:
        arity = func.__code__.co_argcount
    
    @functools.wraps(func)
    def curried(*args):
        if len(args) >= arity:
            return func(*args)
        return lambda *more_args: curried(*(args + more_args))
    
    return curried


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Example 1: Processing numbers lazily
    print("1. Lazy number processing:")
    numbers = LazyPipeline([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    result_pipeline = (
        numbers
        .map(lambda x: x * 2)
        .filter(lambda x: x > 10)
        .map(lambda x: x ** 2)
    )
    print(f"   Pipeline created: {result_pipeline}")
    print(f"   Executing now...")
    print(f"   Result: {result_pipeline.execute()}")
    print(f"   Cached call: {result_pipeline.execute()}\n")
    
    # Example 2: String processing with reduce
    print("2. String processing with reduce:")
    words = LazyPipeline(["hello", "world", "from", "python"])
    sentence = (
        words
        .map(str.capitalize)
        .reduce(lambda a, b: f"{a} {b}")
        .execute()
    )
    print(f"   Result: {sentence}\n")
    
    # Example 3: Memoization decorator
    print("3. Memoization demonstration:")
    
    @memoize
    def expensive_fibonacci(n):
        """Deliberately inefficient to show memoization benefit."""
        if n <= 1:
            return n
        return expensive_fibonacci(n - 1) + expensive_fibonacci(n - 2)
    
    print(f"   Computing fib(10): {expensive_fibonacci(10)}")
    print(f"   Cache size: {len(expensive_fibonacci.cache)}")
    print(f"   Computing fib(15): {expensive_fibonacci(15)}")
    print(f"   Cache size: {len(expensive_fibonacci.cache)}\n")
    
    # Example 4: Currying
    print("4. Currying example:")
    
    @curry
    def add_three(a, b, c):
        """Add three numbers together."""
        return a + b + c
    
    add_5 = add_three(5)
    add_5_and_10 = add_5(10)
    result = add_5_and_10(3)
    print(f"   Curried add_three(5)(10)(3) = {result}")
    print(f"   Or all at once: add_three(5, 10, 3) = {add_three(5, 10, 3)}")