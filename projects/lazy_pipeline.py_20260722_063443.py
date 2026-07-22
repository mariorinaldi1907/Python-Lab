"""
Date: 2026-07-22
Created a functional programming toolkit with lazy pipelines, automatic memoization, and currying so I can chain operations without computing anything until I need the result.
"""

#!/usr/bin/env python3
"""
Functional programming utilities: lazy pipelines, memoization, and currying.
I wanted a clean way to chain transformations without computing everything eagerly.
"""

import functools
from typing import Callable, Iterable, Any, TypeVar


T = TypeVar('T')
R = TypeVar('R')


def memoize(func: Callable) -> Callable:
    """
    Decorator that caches function results based on arguments.
    Useful for expensive computations that get called repeatedly with same args.
    """
    cache = {}
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create a hashable key from args and kwargs
        key = (args, tuple(sorted(kwargs.items())))
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    # Expose cache for inspection/debugging
    wrapper.cache = cache
    return wrapper


def curry(func: Callable) -> Callable:
    """
    Transform a multi-argument function into a sequence of single-argument functions.
    Makes partial application cleaner and more composable.
    """
    @functools.wraps(func)
    def curried(*args, **kwargs):
        # If we have enough args, call the function
        try:
            return func(*args, **kwargs)
        except TypeError:
            # Not enough args, return a new partial function
            return lambda *more_args, **more_kwargs: curried(
                *(args + more_args), **{**kwargs, **more_kwargs}
            )
    
    return curried


class LazyPipeline:
    """
    Lazy evaluation pipeline that chains operations without executing until needed.
    This is the core — operations stack up but nothing computes until you materialize.
    """
    
    def __init__(self, source: Iterable):
        """Start a pipeline with an iterable source."""
        self._source = source
        self._operations = []
    
    def map(self, func: Callable[[T], R]) -> 'LazyPipeline':
        """Apply a transformation to each element (lazy)."""
        self._operations.append(('map', func))
        return self
    
    def filter(self, predicate: Callable[[T], bool]) -> 'LazyPipeline':
        """Keep only elements that satisfy the predicate (lazy)."""
        self._operations.append(('filter', predicate))
        return self
    
    def take(self, n: int) -> 'LazyPipeline':
        """Limit to first n elements (lazy)."""
        self._operations.append(('take', n))
        return self
    
    def _execute(self) -> Iterable:
        """
        Actually run the pipeline. This is where lazy becomes eager.
        I iterate through operations and apply them in sequence.
        """
        result = iter(self._source)
        
        for operation, arg in self._operations:
            if operation == 'map':
                result = map(arg, result)
            elif operation == 'filter':
                result = filter(arg, result)
            elif operation == 'take':
                # Custom take implementation since itertools.islice needs import
                def take_n(iterable, n):
                    for i, item in enumerate(iterable):
                        if i >= n:
                            break
                        yield item
                result = take_n(result, arg)
        
        return result
    
    def to_list(self) -> list:
        """Materialize the pipeline into a list."""
        return list(self._execute())
    
    def reduce(self, func: Callable[[T, T], T], initial: Any = None) -> Any:
        """
        Reduce the pipeline to a single value.
        The initial value is optional — if not provided, uses first element.
        """
        result = self._execute()
        if initial is None:
            return functools.reduce(func, result)
        return functools.reduce(func, result, initial)
    
    def foreach(self, action: Callable[[T], None]) -> None:
        """Execute an action for each element (side effects)."""
        for item in self._execute():
            action(item)


def compose(*functions: Callable) -> Callable:
    """
    Compose functions right-to-left: compose(f, g, h)(x) == f(g(h(x)))
    This is how mathematicians think about composition, so I kept that convention.
    """
    def composed(arg):
        result = arg
        for func in reversed(functions):
            result = func(result)
        return result
    return composed


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Example 1: Process numbers lazily
    print("1. Lazy pipeline with map/filter/take:")
    numbers = range(1, 100)
    result = (LazyPipeline(numbers)
              .map(lambda x: x * 2)
              .filter(lambda x: x % 3 == 0)
              .take(5)
              .to_list())
    print(f"   First 5 doubled numbers divisible by 3: {result}")
    
    # Example 2: Memoization
    print("\n2. Memoization (expensive fibonacci):")
    
    @memoize
    def fib(n):
        if n <= 1:
            return n
        return fib(n - 1) + fib(n - 2)
    
    print(f"   fib(30) = {fib(30)}")
    print(f"   fib(35) = {fib(35)}  # Much faster due to cache")
    print(f"   Cache size: {len(fib.cache)} entries")
    
    # Example 3: Currying
    print("\n3. Currying for partial application:")
    
    @curry
    def multiply(a, b, c):
        return a * b * c
    
    double = multiply(2)
    double_and_triple = double(3)
    
    print(f"   multiply(2, 3, 4) = {double_and_triple(4)}")
    print(f"   Reusing double(3)(5) = {double(3)(5)}")
    
    # Example 4: Function composition
    print("\n4. Function composition:")
    
    add_ten = lambda x: x + 10
    square = lambda x: x ** 2
    halve = lambda x: x / 2
    
    # Composed right-to-left: halve(square(add_ten(x)))
    pipeline_func = compose(halve, square, add_ten)
    
    print(f"   halve(square(add_ten(5))) = {pipeline_func(5)}")
    
    # Example 5: Reduce with pipeline
    print("\n5. Reduce with lazy pipeline:")
    
    total = (LazyPipeline(range(1, 11))
             .map(lambda x: x ** 2)
             .reduce(lambda a, b: a + b))
    
    print(f"   Sum of squares 1-10: {total}")
    
    print("\n✓ All demos completed successfully!")