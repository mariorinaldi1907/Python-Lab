"""
Date: 2026-06-09
Created a functional programming toolkit that lazily evaluates transformation pipelines and caches intermediate results, useful for processing large datasets efficiently.
"""

#!/usr/bin/env python3
"""
Lazy pipeline composer with memoization and currying support.

I wanted a cleaner way to chain transformations without evaluating everything
immediately — this lets me build up complex pipelines that only run when I 
actually need the results, plus it caches intermediate steps automatically.
"""

from functools import wraps
from typing import Callable, Any, Iterable, Optional
import time


def memoize(func: Callable) -> Callable:
    """
    Decorator that caches function results based on arguments.
    
    Uses a simple dict cache — good for pure functions with hashable args.
    I'm keeping it basic here since we can't use lru_cache decorators on
    methods easily, and I want full control over cache invalidation.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create a cache key from args and kwargs
        key = (args, tuple(sorted(kwargs.items())))
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    wrapper.cache = cache  # Expose cache for inspection/clearing
    return wrapper


def curry(func: Callable) -> Callable:
    """
    Transform a function to accept arguments one at a time.
    
    This is a simplified currying implementation — it collects args until
    it has enough to call the original function. Useful for partial application.
    """
    @wraps(func)
    def curried(*args, **kwargs):
        # Try to call the function; if it needs more args, return another curried version
        try:
            return func(*args, **kwargs)
        except TypeError:
            # Not enough args, so return a partial application
            def partial(*more_args, **more_kwargs):
                combined_kwargs = {**kwargs, **more_kwargs}
                return curried(*(args + more_args), **combined_kwargs)
            return partial
    
    return curried


class LazyPipeline:
    """
    A lazy evaluation pipeline that chains transformations.
    
    The key idea: nothing executes until you call .evaluate() or iterate.
    This means you can build complex transformation chains without processing
    the data until you actually need it. Plus, with memoization, repeated
    evaluations are fast.
    """
    
    def __init__(self, source: Iterable):
        """Initialize pipeline with a data source."""
        self._source = source
        self._operations = []
        self._cache = None
    
    def map(self, func: Callable) -> 'LazyPipeline':
        """Add a map operation to the pipeline."""
        self._operations.append(('map', func))
        self._cache = None  # Invalidate cache
        return self
    
    def filter(self, predicate: Callable) -> 'LazyPipeline':
        """Add a filter operation to the pipeline."""
        self._operations.append(('filter', predicate))
        self._cache = None
        return self
    
    def take(self, n: int) -> 'LazyPipeline':
        """Take only the first n elements."""
        self._operations.append(('take', n))
        self._cache = None
        return self
    
    def evaluate(self, use_cache: bool = True) -> list:
        """
        Execute the pipeline and return results.
        
        This is where the magic happens — we iterate through all queued
        operations and apply them. With use_cache=True, we remember the
        result for subsequent calls.
        """
        if use_cache and self._cache is not None:
            return self._cache
        
        result = self._source
        
        for op_type, op_arg in self._operations:
            if op_type == 'map':
                result = map(op_arg, result)
            elif op_type == 'filter':
                result = filter(op_arg, result)
            elif op_type == 'take':
                result = list(result)[:op_arg]
        
        result = list(result)
        
        if use_cache:
            self._cache = result
        
        return result
    
    def __iter__(self):
        """Make the pipeline iterable — evaluates when you iterate over it."""
        return iter(self.evaluate())
    
    def __repr__(self):
        """Show what operations are in the pipeline."""
        ops = [f"{op[0]}({op[1].__name__ if callable(op[1]) else op[1]})" 
               for op in self._operations]
        return f"LazyPipeline({' -> '.join(ops) if ops else 'empty'})"


@memoize
def expensive_computation(x: int) -> int:
    """
    Simulate an expensive operation that we want to cache.
    
    In real code this might be a database query or complex calculation.
    The memoization means we only compute each value once.
    """
    time.sleep(0.01)  # Simulate work
    return x * x + x


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Create a pipeline that processes numbers
    numbers = range(1, 20)
    
    pipeline = (LazyPipeline(numbers)
                .map(lambda x: x * 2)
                .filter(lambda x: x % 3 == 0)
                .take(5))
    
    print(f"Pipeline structure: {pipeline}")
    print("Pipeline created but not executed yet!\n")
    
    # Now evaluate it
    print("Evaluating pipeline...")
    result = pipeline.evaluate()
    print(f"Result: {result}\n")
    
    # Second evaluation should use cache (instant)
    print("Evaluating again (should be instant due to cache)...")
    start = time.time()
    result2 = pipeline.evaluate()
    elapsed = time.time() - start
    print(f"Result: {result2}")
    print(f"Time: {elapsed:.6f}s (cached!)\n")
    
    # Demo currying
    print("=== Currying Demo ===\n")
    
    @curry
    def add_three(a, b, c):
        """Add three numbers together."""
        return a + b + c
    
    add_5 = add_three(5)
    add_5_and_10 = add_5(10)
    final_result = add_5_and_10(15)
    
    print(f"Curried addition: add_three(5)(10)(15) = {final_result}\n")
    
    # Demo memoization
    print("=== Memoization Demo ===\n")
    
    print("First calls (slow):")
    start = time.time()
    results = [expensive_computation(i) for i in range(5)]
    elapsed = time.time() - start
    print(f"Results: {results}")
    print(f"Time: {elapsed:.3f}s\n")
    
    print("Repeated calls (cached, instant):")
    start = time.time()
    results = [expensive_computation(i) for i in range(5)]
    elapsed = time.time() - start
    print(f"Results: {results}")
    print(f"Time: {elapsed:.6f}s")
    print(f"Cache size: {len(expensive_computation.cache)} entries")