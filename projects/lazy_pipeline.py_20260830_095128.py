"""
Date: 2026-08-30
Created a lazy pipeline system that chains transformations without evaluating until needed, inspired by how Clojure handles sequences.
"""

"""
Lazy evaluation pipeline for functional-style data processing.

I always wanted something like LINQ or Clojure's transducers in Python,
so I built this to chain operations without evaluating until absolutely necessary.
Saves memory when dealing with large datasets or infinite sequences.
"""

from typing import Iterator, Callable, Any, Iterable
from functools import wraps
import itertools


class LazyPipeline:
    """
    A pipeline that defers computation until values are actually needed.
    
    Chains transformations together, but nothing happens until you iterate
    or call a terminal operation like to_list() or reduce().
    """
    
    def __init__(self, source: Iterable):
        """Initialize with any iterable source."""
        self._source = source
    
    def map(self, func: Callable[[Any], Any]) -> 'LazyPipeline':
        """
        Transform each element lazily.
        
        Won't actually call func until someone iterates through the pipeline.
        """
        return LazyPipeline(map(func, self._source))
    
    def filter(self, predicate: Callable[[Any], bool]) -> 'LazyPipeline':
        """Keep only elements that satisfy the predicate."""
        return LazyPipeline(filter(predicate, self._source))
    
    def take(self, n: int) -> 'LazyPipeline':
        """Take only the first n elements."""
        return LazyPipeline(itertools.islice(self._source, n))
    
    def drop(self, n: int) -> 'LazyPipeline':
        """Skip the first n elements."""
        return LazyPipeline(itertools.islice(self._source, n, None))
    
    def flat_map(self, func: Callable[[Any], Iterable]) -> 'LazyPipeline':
        """
        Map each element to an iterable, then flatten the results.
        
        Useful for things like splitting strings into words.
        """
        def flatten():
            for item in self._source:
                yield from func(item)
        return LazyPipeline(flatten())
    
    def chunk(self, size: int) -> 'LazyPipeline':
        """Group elements into chunks of given size."""
        def chunked():
            iterator = iter(self._source)
            while True:
                chunk = list(itertools.islice(iterator, size))
                if not chunk:
                    break
                yield chunk
        return LazyPipeline(chunked())
    
    # Terminal operations — these actually evaluate the pipeline
    
    def to_list(self) -> list:
        """Evaluate the entire pipeline and return as a list."""
        return list(self._source)
    
    def to_set(self) -> set:
        """Evaluate and return as a set."""
        return set(self._source)
    
    def reduce(self, func: Callable[[Any, Any], Any], initial: Any = None) -> Any:
        """
        Reduce the pipeline to a single value.
        
        If initial is None, uses the first element as the starting value.
        """
        if initial is None:
            return reduce(func, self._source)
        from functools import reduce
        return reduce(func, self._source, initial)
    
    def for_each(self, func: Callable[[Any], None]) -> None:
        """Execute a side effect for each element (forces evaluation)."""
        for item in self._source:
            func(item)
    
    def __iter__(self) -> Iterator:
        """Allow direct iteration over the pipeline."""
        return iter(self._source)


def memoize(func: Callable) -> Callable:
    """
    Cache function results to avoid redundant computation.
    
    I use this all the time for expensive recursive functions.
    Only works with hashable arguments though.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    
    # Expose cache for debugging if needed
    wrapper.cache = cache
    return wrapper


def curry(func: Callable) -> Callable:
    """
    Transform a multi-argument function into a chain of single-argument functions.
    
    Makes it easier to partially apply functions in a pipeline.
    """
    def curried(*args, **kwargs):
        # Try to call the function with current args
        try:
            return func(*args, **kwargs)
        except TypeError:
            # Not enough args yet, return a function waiting for more
            def partial(*more_args, **more_kwargs):
                combined_kwargs = {**kwargs, **more_kwargs}
                return curried(*(args + more_args), **combined_kwargs)
            return partial
    
    return curried


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Example 1: Processing numbers without loading everything into memory
    print("1. Infinite sequence with lazy evaluation:")
    result = (
        LazyPipeline(itertools.count(1))  # infinite: 1, 2, 3, ...
        .filter(lambda x: x % 2 == 0)      # only evens
        .map(lambda x: x ** 2)              # square them
        .take(5)                            # grab first 5
        .to_list()
    )
    print(f"   First 5 even squares: {result}")
    
    # Example 2: Text processing
    print("\n2. Text processing pipeline:")
    text = ["Hello world", "Lazy evaluation", "is pretty cool"]
    words = (
        LazyPipeline(text)
        .flat_map(lambda s: s.lower().split())  # split into words
        .filter(lambda w: len(w) > 3)           # only longer words
        .map(lambda w: w.upper())               # uppercase
        .to_list()
    )
    print(f"   Filtered words: {words}")
    
    # Example 3: Chunking data
    print("\n3. Chunking a sequence:")
    chunks = LazyPipeline(range(10)).chunk(3).to_list()
    print(f"   Range(10) in chunks of 3: {chunks}")
    
    # Example 4: Memoization
    print("\n4. Memoization (fibonacci):")
    
    @memoize
    def fib(n):
        """Classic fibonacci — super slow without memoization."""
        if n <= 1:
            return n
        return fib(n - 1) + fib(n - 2)
    
    print(f"   fib(30) = {fib(30)}")
    print(f"   Cache has {len(fib.cache)} entries after computing fib(30)")
    
    # Example 5: Currying
    print("\n5. Currying for partial application:")
    
    @curry
    def multiply(a, b, c):
        """Multiply three numbers together."""
        return a * b * c
    
    # Partially apply to create specialized functions
    double = multiply(2)
    triple = multiply(3)
    
    print(f"   double(5, 10) = {double(5, 10)}")
    print(f"   triple(2)(3) = {triple(2)(3)}")
    
    # Example 6: Combining everything
    print("\n6. Complex pipeline with reduction:")
    total = (
        LazyPipeline(range(1, 100))
        .filter(lambda x: x % 3 == 0 or x % 5 == 0)  # divisible by 3 or 5
        .map(lambda x: x ** 2)                        # square them
        .reduce(lambda acc, x: acc + x, 0)           # sum everything
    )
    print(f"   Sum of squares (multiples of 3 or 5 under 100): {total}")
    
    print("\n=== All examples completed successfully ===")