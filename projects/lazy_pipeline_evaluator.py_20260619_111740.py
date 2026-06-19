"""
Date: 2026-06-19
Created a functional programming toolkit that lets me chain operations lazily and cache expensive computations, because I got tired of loading huge datasets just to filter them.
"""

"""
Lazy evaluation pipeline with automatic memoization.

I wanted something that could chain transformations without actually
executing them until needed. Kind of like what Spark does but simpler.
"""

from functools import wraps
from typing import Callable, Iterator, Any, Optional
import time


def memoize(func: Callable) -> Callable:
    """
    Decorator that caches function results based on arguments.
    
    I use this for expensive operations that get called with the same
    inputs repeatedly. Only works with hashable arguments though.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Make a hashable key from args and kwargs
        key = (args, tuple(sorted(kwargs.items())))
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    wrapper.cache = cache  # Expose cache for inspection/clearing
    return wrapper


class LazyPipeline:
    """
    Lazily evaluated transformation pipeline.
    
    The main idea: store operations but don't execute them until someone
    actually iterates or collects the results. This way I can chain
    a ton of filters/maps without wasting memory on intermediate lists.
    """
    
    def __init__(self, source: Iterator[Any]):
        """Initialize with an iterable source (list, range, generator, etc)."""
        self.source = source
        self.operations = []
    
    def map(self, func: Callable) -> 'LazyPipeline':
        """Apply a transformation to each element."""
        self.operations.append(('map', func))
        return self  # Return self for chaining
    
    def filter(self, predicate: Callable) -> 'LazyPipeline':
        """Keep only elements where predicate returns True."""
        self.operations.append(('filter', predicate))
        return self
    
    def take(self, n: int) -> 'LazyPipeline':
        """Limit output to first n elements."""
        self.operations.append(('take', n))
        return self
    
    def skip(self, n: int) -> 'LazyPipeline':
        """Skip the first n elements."""
        self.operations.append(('skip', n))
        return self
    
    def _execute(self) -> Iterator[Any]:
        """
        Actually run the pipeline.
        
        This is where the magic happens — we iterate through the source
        and apply operations one by one, yielding results as we go.
        """
        iterator = iter(self.source)
        
        for op_type, op_arg in self.operations:
            if op_type == 'map':
                iterator = map(op_arg, iterator)
            elif op_type == 'filter':
                iterator = filter(op_arg, iterator)
            elif op_type == 'take':
                iterator = self._take_helper(iterator, op_arg)
            elif op_type == 'skip':
                iterator = self._skip_helper(iterator, op_arg)
        
        return iterator
    
    @staticmethod
    def _take_helper(iterator: Iterator, n: int) -> Iterator:
        """Helper to take first n items from iterator."""
        for i, item in enumerate(iterator):
            if i >= n:
                break
            yield item
    
    @staticmethod
    def _skip_helper(iterator: Iterator, n: int) -> Iterator:
        """Helper to skip first n items from iterator."""
        for i, item in enumerate(iterator):
            if i >= n:
                yield item
    
    def collect(self) -> list:
        """Force evaluation and return results as a list."""
        return list(self._execute())
    
    def __iter__(self):
        """Make the pipeline itself iterable."""
        return self._execute()
    
    def reduce(self, func: Callable, initial: Optional[Any] = None) -> Any:
        """
        Reduce the pipeline to a single value.
        
        I debated whether to include this since it forces evaluation,
        but it's too useful for aggregations like sum, product, etc.
        """
        from functools import reduce as functools_reduce
        items = list(self._execute())
        
        if initial is None:
            return functools_reduce(func, items)
        return functools_reduce(func, items, initial)


def curry(func: Callable) -> Callable:
    """
    Transform a multi-argument function into nested single-argument functions.
    
    This is more of an experiment than something I use daily, but it's
    cool for creating specialized versions of generic functions.
    """
    def curried(*args, **kwargs):
        # Try calling the function with what we have
        try:
            return func(*args, **kwargs)
        except TypeError:
            # If it fails (not enough args), return a new function
            # that remembers these args and waits for more
            def partial(*more_args, **more_kwargs):
                combined_args = args + more_args
                combined_kwargs = {**kwargs, **more_kwargs}
                return curried(*combined_args, **combined_kwargs)
            return partial
    
    return curried


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Example 1: Basic pipeline with large range (doesn't load all into memory)
    print("1. Processing first 5 even squares from a huge range:")
    result = (LazyPipeline(range(1000000))
              .filter(lambda x: x % 2 == 0)
              .map(lambda x: x ** 2)
              .take(5)
              .collect())
    print(f"   Result: {result}\n")
    
    # Example 2: Memoization in action
    print("2. Memoization demo (expensive Fibonacci):")
    
    @memoize
    def fibonacci(n: int) -> int:
        """Recursive Fibonacci with memoization — way faster."""
        if n <= 1:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)
    
    start = time.time()
    fib_30 = fibonacci(30)
    first_time = time.time() - start
    
    start = time.time()
    fib_30_again = fibonacci(30)
    cached_time = time.time() - start
    
    print(f"   fib(30) = {fib_30}")
    print(f"   First call: {first_time:.6f}s")
    print(f"   Cached call: {cached_time:.6f}s (speedup: {first_time/cached_time:.1f}x)\n")
    
    # Example 3: Currying
    print("3. Currying demo:")
    
    @curry
    def power(base, exponent):
        """Raise base to exponent."""
        return base ** exponent
    
    square = power(exponent=2)
    cube = power(exponent=3)
    
    print(f"   square(5) = {square(5)}")
    print(f"   cube(3) = {cube(3)}\n")
    
    # Example 4: Complex pipeline with reduce
    print("4. Pipeline with reduce (sum of squared odd numbers):")
    total = (LazyPipeline(range(1, 20))
             .filter(lambda x: x % 2 == 1)
             .map(lambda x: x ** 2)
             .reduce(lambda a, b: a + b, 0))
    print(f"   Sum of squares of odd numbers 1-19: {total}")