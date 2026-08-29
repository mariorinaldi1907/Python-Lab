"""
Date: 2026-08-29
Created a functional programming toolkit that combines lazy evaluation, function composition, currying, and automatic memoization into a fluent pipeline API.
"""

"""
Lazy evaluation pipeline with functional programming utilities.

This module provides tools for building composable, lazy-evaluated data pipelines
with automatic memoization and currying support. Perfect for chaining transformations
without processing data until you actually need the results.
"""

from functools import wraps
from typing import Callable, Any, Iterable, TypeVar
from itertools import islice


T = TypeVar('T')
U = TypeVar('U')


def memoize(func: Callable) -> Callable:
    """
    Decorator that caches function results based on arguments.
    
    I'm using a simple dict here because it's straightforward and works well
    for most use cases. Could swap this for an LRU cache if memory becomes an issue.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Convert kwargs to a hashable form
        key = (args, tuple(sorted(kwargs.items())))
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    return wrapper


def curry(func: Callable) -> Callable:
    """
    Transform a function to support partial application.
    
    This lets you call functions with fewer arguments than expected,
    returning a new function that remembers the arguments you've provided.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Try calling with current args
        try:
            return func(*args, **kwargs)
        except TypeError:
            # Not enough args, return a partial application
            def partial(*more_args, **more_kwargs):
                combined_kwargs = {**kwargs, **more_kwargs}
                return wrapper(*(args + more_args), **combined_kwargs)
            return partial
    
    return wrapper


class LazyPipeline:
    """
    A lazy evaluation pipeline for composing transformations on iterables.
    
    The key insight here is that we don't actually process anything until
    someone calls .execute() or .take(). This means you can build up complex
    transformation chains without paying the computational cost upfront.
    """
    
    def __init__(self, source: Iterable[T]):
        """Initialize pipeline with a data source."""
        self._source = source
        self._operations = []
    
    def map(self, func: Callable[[T], U]) -> 'LazyPipeline':
        """Apply a transformation to each element."""
        self._operations.append(('map', func))
        return self
    
    def filter(self, predicate: Callable[[T], bool]) -> 'LazyPipeline':
        """Keep only elements that satisfy the predicate."""
        self._operations.append(('filter', predicate))
        return self
    
    def reduce(self, func: Callable[[T, T], T], initial: Any = None) -> Any:
        """
        Reduce the pipeline to a single value.
        
        This is a terminal operation - it actually executes the pipeline.
        """
        result = self._execute_generator()
        
        iterator = iter(result)
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
    
    def take(self, n: int) -> list:
        """
        Take the first n elements from the pipeline.
        
        This is where lazy evaluation shines - we only process enough
        elements to satisfy the request.
        """
        return list(islice(self._execute_generator(), n))
    
    def execute(self) -> list:
        """Execute the entire pipeline and return results as a list."""
        return list(self._execute_generator())
    
    def _execute_generator(self):
        """
        Internal method that actually executes the pipeline as a generator.
        
        I'm using a generator here so we can maintain laziness even during execution.
        Each operation is applied in sequence, but only when values are requested.
        """
        result = iter(self._source)
        
        for operation, func in self._operations:
            if operation == 'map':
                result = map(func, result)
            elif operation == 'filter':
                result = filter(func, result)
        
        return result


def compose(*functions: Callable) -> Callable:
    """
    Compose multiple functions into a single function.
    
    The functions are applied right-to-left, like mathematical composition.
    So compose(f, g, h)(x) is equivalent to f(g(h(x))).
    """
    def composed(arg):
        result = arg
        for func in reversed(functions):
            result = func(result)
        return result
    
    return composed


if __name__ == "__main__":
    print("=== Lazy Pipeline Demo ===\n")
    
    # Demo 1: Basic lazy pipeline
    print("1. Lazy pipeline with map and filter:")
    numbers = range(1, 20)
    result = (LazyPipeline(numbers)
              .filter(lambda x: x % 2 == 0)
              .map(lambda x: x ** 2)
              .take(5))
    print(f"First 5 squares of even numbers: {result}\n")
    
    # Demo 2: Memoization
    print("2. Memoization example:")
    
    @memoize
    def expensive_fibonacci(n: int) -> int:
        """Fibonacci with memoization - much faster for large n."""
        if n <= 1:
            return n
        return expensive_fibonacci(n - 1) + expensive_fibonacci(n - 2)
    
    print(f"Fibonacci(30) = {expensive_fibonacci(30)}")
    print(f"Fibonacci(35) = {expensive_fibonacci(35)} (cached intermediate values!)\n")
    
    # Demo 3: Currying
    print("3. Currying example:")
    
    @curry
    def multiply_three(a: int, b: int, c: int) -> int:
        """Multiply three numbers together."""
        return a * b * c
    
    double = multiply_three(2)
    double_and_triple = double(3)
    result = double_and_triple(5)
    print(f"Curried multiplication: 2 * 3 * 5 = {result}\n")
    
    # Demo 4: Function composition
    print("4. Function composition:")
    
    add_ten = lambda x: x + 10
    multiply_by_two = lambda x: x * 2
    square = lambda x: x ** 2
    
    combined = compose(square, multiply_by_two, add_ten)
    print(f"compose(square, *2, +10)(5) = {combined(5)}")
    print(f"Breakdown: 5 + 10 = 15, 15 * 2 = 30, 30^2 = 900\n")
    
    # Demo 5: Complex pipeline with reduce
    print("5. Pipeline with reduce:")
    words = ["hello", "functional", "programming", "world"]
    total_length = (LazyPipeline(words)
                    .filter(lambda w: len(w) > 5)
                    .map(lambda w: len(w))
                    .reduce(lambda a, b: a + b, 0))
    print(f"Total length of words longer than 5 chars: {total_length}")