"""
Date: 2026-07-04
Created a functional programming toolkit that lets me compose transformations lazily, so operations only run when I actually iterate the results.
"""

"""
Lazy evaluation pipeline with functional programming utilities.

I wanted to chain operations on sequences without immediately executing them,
kind of like how itertools works but with a cleaner API and built-in memoization.
"""

from functools import wraps, reduce
from typing import Callable, Iterator, Any, TypeVar


T = TypeVar('T')
U = TypeVar('U')


def memoize(func: Callable) -> Callable:
    """
    Cache function results to avoid recomputation.
    
    I use this when operations are expensive and I might call them
    with the same arguments multiple times. Not thread-safe, but good
    enough for single-threaded scripts.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Only works with hashable arguments
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    return wrapper


def curry(func: Callable) -> Callable:
    """
    Transform a function to allow partial application.
    
    Makes it easier to build specialized functions from generic ones.
    The implementation collects arguments until we have enough to call.
    """
    @wraps(func)
    def curried(*args, **kwargs):
        # Try to call the function; if we don't have enough args, return a new partial
        try:
            return func(*args, **kwargs)
        except TypeError:
            # Not enough arguments, so return a new function that remembers these
            def partial(*more_args, **more_kwargs):
                combined_kwargs = {**kwargs, **more_kwargs}
                return curried(*(args + more_args), **combined_kwargs)
            return partial
    
    return curried


class LazyPipeline:
    """
    Composable pipeline that only executes when you iterate over it.
    
    I built this because I wanted to chain map/filter/reduce operations
    without creating intermediate lists. Each transformation is stored
    and applied lazily when the pipeline is consumed.
    """
    
    def __init__(self, source: Iterator[T]):
        """Initialize with an iterable source."""
        self._source = source
        self._operations = []
    
    def map(self, func: Callable[[T], U]) -> 'LazyPipeline':
        """Apply a transformation to each element."""
        new_pipeline = LazyPipeline(self._source)
        new_pipeline._operations = self._operations + [('map', func)]
        return new_pipeline
    
    def filter(self, predicate: Callable[[T], bool]) -> 'LazyPipeline':
        """Keep only elements matching the predicate."""
        new_pipeline = LazyPipeline(self._source)
        new_pipeline._operations = self._operations + [('filter', predicate)]
        return new_pipeline
    
    def take(self, n: int) -> 'LazyPipeline':
        """Limit to first n elements."""
        new_pipeline = LazyPipeline(self._source)
        new_pipeline._operations = self._operations + [('take', n)]
        return new_pipeline
    
    def __iter__(self) -> Iterator[T]:
        """
        Execute the pipeline and yield results.
        
        This is where the magic happens — we apply all queued operations
        in order, but only as items are requested.
        """
        items = iter(self._source)
        
        for op_type, op_arg in self._operations:
            if op_type == 'map':
                items = map(op_arg, items)
            elif op_type == 'filter':
                items = filter(op_arg, items)
            elif op_type == 'take':
                items = (item for i, item in enumerate(items) if i < op_arg)
        
        yield from items
    
    def collect(self) -> list:
        """Consume the pipeline and return a list."""
        return list(self)
    
    def reduce(self, func: Callable, initial=None) -> Any:
        """
        Reduce the pipeline to a single value.
        
        Uses functools.reduce under the hood, but fits nicely into
        the pipeline API.
        """
        items = list(self)
        if initial is None:
            return reduce(func, items)
        return reduce(func, items, initial)


def compose(*functions: Callable) -> Callable:
    """
    Compose multiple functions into a single function.
    
    The result applies functions right-to-left, like mathematical composition.
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
    
    # Example 1: Process numbers lazily
    print("1. Chain operations without executing immediately:")
    pipeline = LazyPipeline(range(1, 21))
    result = (pipeline
              .filter(lambda x: x % 2 == 0)  # only evens
              .map(lambda x: x ** 2)          # square them
              .take(5)                         # first 5
              .collect())
    print(f"   Even squares (first 5): {result}")
    
    # Example 2: Memoization in action
    print("\n2. Memoization prevents expensive recomputation:")
    
    @memoize
    def expensive_operation(n: int) -> int:
        """Simulate an expensive calculation."""
        print(f"   Computing fib({n})...")
        if n <= 1:
            return n
        return expensive_operation(n - 1) + expensive_operation(n - 2)
    
    print(f"   Result: {expensive_operation(10)}")
    print(f"   Calling again (cached): {expensive_operation(10)}")
    
    # Example 3: Currying for partial application
    print("\n3. Currying for building specialized functions:")
    
    @curry
    def multiply(a: int, b: int, c: int) -> int:
        """Multiply three numbers."""
        return a * b * c
    
    double = multiply(2)      # partially applied
    quadruple = double(2)     # partially applied again
    result = quadruple(5)     # final application
    print(f"   2 * 2 * 5 = {result}")
    
    # Example 4: Function composition
    print("\n4. Composing functions:")
    add_ten = lambda x: x + 10
    times_two = lambda x: x * 2
    square = lambda x: x ** 2
    
    combined = compose(square, times_two, add_ten)
    print(f"   ((5 + 10) * 2) ** 2 = {combined(5)}")
    
    # Example 5: Reduce on pipeline
    print("\n5. Reducing a pipeline to single value:")
    total = (LazyPipeline(range(1, 11))
             .filter(lambda x: x % 2 == 1)
             .reduce(lambda acc, x: acc + x, 0))
    print(f"   Sum of odd numbers 1-10: {total}")