"""
Date: 2026-06-04
Created a functional programming toolkit that lets me chain operations lazily and auto-curry functions — makes data transformations way cleaner.
"""

"""
Function pipeline utility with lazy evaluation and auto-currying.

I wanted a clean way to compose functions without executing immediately,
and built in currying so partial application just works naturally.
"""

from functools import wraps, reduce
from typing import Callable, Any, Iterable
import operator


def curry(func):
    """
    Auto-curry a function so it can be partially applied.
    
    Returns a new function when called with fewer args than required.
    I'm using this to make pipeline operations more flexible.
    """
    @wraps(func)
    def curried(*args, **kwargs):
        # Try to call the function; if we're missing args, return a partial
        try:
            return func(*args, **kwargs)
        except TypeError:
            # Not enough args — return a function waiting for more
            def partial(*more_args, **more_kwargs):
                combined_kwargs = {**kwargs, **more_kwargs}
                return curried(*(args + more_args), **combined_kwargs)
            return partial
    return curried


class LazyPipeline:
    """
    A pipeline that chains transformations without executing until needed.
    
    I built this because I wanted to define a series of operations upfront
    but only run them when I actually need the result. Saves computation
    when you're experimenting with different data flows.
    """
    
    def __init__(self, source=None):
        """Initialize with an optional data source."""
        self._operations = []
        self._source = source
    
    def map(self, func):
        """Apply a function to each element."""
        self._operations.append(('map', func))
        return self
    
    def filter(self, predicate):
        """Keep only elements matching the predicate."""
        self._operations.append(('filter', predicate))
        return self
    
    def take(self, n):
        """Limit output to first n elements."""
        self._operations.append(('take', n))
        return self
    
    def flatten(self):
        """Flatten one level of nesting."""
        self._operations.append(('flatten', None))
        return self
    
    def execute(self, source=None):
        """
        Run all queued operations on the source data.
        
        This is where lazy evaluation pays off — nothing happens until
        this method is called. Each operation yields values one at a time.
        """
        data = source if source is not None else self._source
        
        if data is None:
            raise ValueError("No data source provided")
        
        # Start with the source as an iterable
        result = iter(data)
        
        for op_type, op_arg in self._operations:
            if op_type == 'map':
                result = map(op_arg, result)
            elif op_type == 'filter':
                result = filter(op_arg, result)
            elif op_type == 'take':
                result = self._take_n(result, op_arg)
            elif op_type == 'flatten':
                result = self._flatten_one(result)
        
        return list(result)
    
    @staticmethod
    def _take_n(iterable, n):
        """Generator that yields first n items."""
        for i, item in enumerate(iterable):
            if i >= n:
                break
            yield item
    
    @staticmethod
    def _flatten_one(iterable):
        """Generator that flattens one level of nested iterables."""
        for item in iterable:
            if hasattr(item, '__iter__') and not isinstance(item, str):
                yield from item
            else:
                yield item
    
    def __or__(self, func):
        """
        Enable pipe syntax: pipeline | function
        
        This lets me write pipelines in a Unix-like way which feels natural.
        """
        return func(self.execute())


@curry
def compose(*functions):
    """
    Compose multiple functions right-to-left.
    
    compose(f, g, h)(x) == f(g(h(x)))
    Auto-curried so you can build compositions incrementally.
    """
    def composed(arg):
        return reduce(lambda acc, func: func(acc), reversed(functions), arg)
    return composed


@curry
def add(x, y):
    """Curried addition — useful for partial application."""
    return x + y


@curry
def multiply(x, y):
    """Curried multiplication."""
    return x * y


@curry
def power(base, exponent):
    """Curried exponentiation."""
    return base ** exponent


if __name__ == "__main__":
    print("=== Function Pipeline Demo ===\n")
    
    # Demo 1: Basic lazy pipeline
    print("1. Lazy pipeline with map, filter, take:")
    numbers = range(1, 100)
    pipeline = LazyPipeline(numbers)
    result = pipeline.map(lambda x: x * 2).filter(lambda x: x % 3 == 0).take(5).execute()
    print(f"   First 5 doubles divisible by 3: {result}")
    
    # Demo 2: Pipeline with flattening
    print("\n2. Flattening nested lists:")
    nested = [[1, 2], [3, 4], [5, 6, 7]]
    flat_result = LazyPipeline(nested).flatten().map(lambda x: x ** 2).execute()
    print(f"   Flattened and squared: {flat_result}")
    
    # Demo 3: Currying in action
    print("\n3. Auto-currying with partial application:")
    add_5 = add(5)  # Partially applied
    print(f"   add(5)(10) = {add_5(10)}")
    
    multiply_by_3 = multiply(3)
    print(f"   multiply(3)(7) = {multiply_by_3(7)}")
    
    # Demo 4: Function composition
    print("\n4. Right-to-left function composition:")
    square = lambda x: x ** 2
    add_10 = add(10)
    composed_func = compose(multiply_by_3, square, add_10)
    result = composed_func(5)  # (5 + 10)^2 * 3 = 225 * 3 = 675
    print(f"   compose(×3, square, +10)(5) = {result}")
    
    # Demo 5: Pipe syntax
    print("\n5. Unix-style pipe operator:")
    data = [1, 2, 3, 4, 5]
    result = LazyPipeline(data).map(power(2)).filter(lambda x: x > 10) | sum
    print(f"   Square each, filter >10, then sum: {result}")
    
    print("\n=== All demos completed successfully ===")