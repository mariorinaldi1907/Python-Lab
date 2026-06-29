"""
Date: 2026-06-29
Created a functional programming toolkit for building composable, lazy-evaluated data pipelines with automatic memoization support.
"""

"""
Lazy evaluation pipeline utility with functional composition.

I wanted something that let me chain operations without evaluating until
the last second, kind of like how Spark or LINQ work. Plus memoization
because why compute the same thing twice?
"""

from functools import wraps, reduce
from typing import Callable, Iterable, Any, TypeVar
from collections.abc import Iterator


T = TypeVar('T')
U = TypeVar('U')


def memoize(func: Callable) -> Callable:
    """
    Cache function results based on arguments.
    
    I'm using a dict here because it's simple and handles most use cases.
    For functions with unhashable args this will blow up, but that's fine
    for my purposes.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create a cache key from args and kwargs
        key = (args, tuple(sorted(kwargs.items())))
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    # Expose cache for introspection/testing
    wrapper.cache = cache
    wrapper.cache_clear = lambda: cache.clear()
    return wrapper


def curry(func: Callable) -> Callable:
    """
    Transform a function to support partial application.
    
    Returns a curried version that accumulates arguments until all required
    params are satisfied, then executes. Super useful for composing operations.
    """
    @wraps(func)
    def curried(*args, **kwargs):
        # Try calling with current args
        try:
            return func(*args, **kwargs)
        except TypeError:
            # Not enough args yet, return another curried function
            def partial(*more_args, **more_kwargs):
                combined_args = args + more_args
                combined_kwargs = {**kwargs, **more_kwargs}
                return curried(*combined_args, **combined_kwargs)
            return partial
    
    return curried


class LazyPipeline:
    """
    Composable pipeline that delays execution until materialization.
    
    The key insight here is that we store transformations as a list of
    functions and only apply them when someone actually needs the data.
    This means we can optimize, skip work, or even parallelize later.
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
        """Keep only elements matching the predicate."""
        self._operations.append(('filter', predicate))
        return self
    
    def take(self, n: int) -> 'LazyPipeline':
        """Limit to first n elements."""
        self._operations.append(('take', n))
        return self
    
    def _execute(self) -> Iterator:
        """
        Actually run the pipeline.
        
        This is where the magic happens - we apply each operation in sequence
        but yield results one at a time. Memory efficient!
        """
        data = iter(self._source)
        
        for op_type, op_arg in self._operations:
            if op_type == 'map':
                data = map(op_arg, data)
            elif op_type == 'filter':
                data = filter(op_arg, data)
            elif op_type == 'take':
                data = (item for i, item in enumerate(data) if i < op_arg)
        
        return data
    
    def collect(self) -> list:
        """Materialize the pipeline into a list."""
        return list(self._execute())
    
    def reduce(self, func: Callable[[T, T], T], initial: Any = None) -> Any:
        """
        Reduce the pipeline to a single value.
        
        Using functools.reduce under the hood because it handles the
        initial value logic better than I could write myself.
        """
        result = self._execute()
        if initial is None:
            return reduce(func, result)
        return reduce(func, result, initial)
    
    def for_each(self, func: Callable[[T], None]) -> None:
        """Execute a side effect for each element (forces evaluation)."""
        for item in self._execute():
            func(item)


def compose(*functions: Callable) -> Callable:
    """
    Compose functions right to left.
    
    compose(f, g, h)(x) = f(g(h(x)))
    I flip the order in reduce so it reads naturally when you write it.
    """
    def composed(arg):
        return reduce(lambda acc, func: func(acc), reversed(functions), arg)
    return composed


if __name__ == "__main__":
    print("=== Memoization Demo ===")
    
    @memoize
    def expensive_fibonacci(n):
        """Recursive fib - normally terrible, but memoization saves it."""
        if n < 2:
            return n
        return expensive_fibonacci(n - 1) + expensive_fibonacci(n - 2)
    
    print(f"fib(30) = {expensive_fibonacci(30)}")
    print(f"Cache has {len(expensive_fibonacci.cache)} entries")
    
    print("\n=== Currying Demo ===")
    
    @curry
    def multiply_three(x, y, z):
        """Multiply three numbers together."""
        return x * y * z
    
    double = multiply_three(2)
    double_and_triple = double(3)
    result = double_and_triple(4)
    print(f"Curried multiplication: 2 * 3 * 4 = {result}")
    
    print("\n=== Lazy Pipeline Demo ===")
    
    # Process numbers lazily - nothing executes until collect()
    numbers = range(1, 100)
    result = (LazyPipeline(numbers)
              .filter(lambda x: x % 2 == 0)  # even numbers only
              .map(lambda x: x ** 2)          # square them
              .take(5)                        # first 5
              .collect())
    
    print(f"First 5 squared evens: {result}")
    
    # Reduce example
    sum_of_squares = (LazyPipeline(range(1, 11))
                      .map(lambda x: x ** 2)
                      .reduce(lambda a, b: a + b, 0))
    
    print(f"Sum of squares 1-10: {sum_of_squares}")
    
    print("\n=== Function Composition Demo ===")
    
    add_five = lambda x: x + 5
    multiply_by_two = lambda x: x * 2
    subtract_three = lambda x: x - 3
    
    # Read as: subtract 3, then multiply by 2, then add 5
    pipeline_func = compose(add_five, multiply_by_two, subtract_three)
    
    print(f"compose(+5, *2, -3)(10) = {pipeline_func(10)}")
    print("  -> (10 - 3) * 2 + 5 = 19")