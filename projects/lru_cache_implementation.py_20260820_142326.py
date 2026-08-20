"""
Date: 2026-08-20
Implemented a least-recently-used cache to practice eviction policies — tracks access patterns and includes stats for hit rate analysis.
"""

#!/usr/bin/env python3
"""
LRU Cache Implementation

I wanted to understand how caching layers work under the hood, so I built
this from scratch. Uses OrderedDict to maintain insertion order, which makes
the LRU logic way cleaner than manually managing a doubly-linked list.
"""

from collections import OrderedDict
from typing import Any, Optional


class LRUCache:
    """
    Least Recently Used (LRU) cache with fixed capacity.
    
    When capacity is reached, the least recently accessed item gets evicted.
    Every get() and put() marks an item as recently used by moving it to the end.
    """
    
    def __init__(self, capacity: int):
        """
        Initialize the LRU cache.
        
        Args:
            capacity: Maximum number of items the cache can hold
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.cache = OrderedDict()  # Maintains insertion order, perfect for LRU
        
        # Stats tracking — useful for monitoring cache performance
        self.hits = 0
        self.misses = 0
    
    def get(self, key: Any) -> Optional[Any]:
        """
        Retrieve value from cache. Returns None if key doesn't exist.
        
        Marks the key as recently used by moving it to the end of the order.
        """
        if key not in self.cache:
            self.misses += 1
            return None
        
        # Move to end to mark as recently used
        # This is the key operation that maintains LRU ordering
        self.cache.move_to_end(key)
        self.hits += 1
        return self.cache[key]
    
    def put(self, key: Any, value: Any) -> None:
        """
        Add or update a key-value pair in the cache.
        
        If key exists, updates value and marks as recently used.
        If cache is full, evicts the least recently used item first.
        """
        if key in self.cache:
            # Update existing key and mark as recently used
            self.cache.move_to_end(key)
            self.cache[key] = value
        else:
            # Check if we need to evict before adding
            if len(self.cache) >= self.capacity:
                # Remove the first item (least recently used)
                # last=False means FIFO order, which gives us LRU behavior
                evicted_key, evicted_value = self.cache.popitem(last=False)
                print(f"  [EVICTED] {evicted_key}: {evicted_value}")
            
            self.cache[key] = value
    
    def size(self) -> int:
        """Return current number of items in cache."""
        return len(self.cache)
    
    def hit_rate(self) -> float:
        """Calculate cache hit rate as a percentage."""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return (self.hits / total) * 100
    
    def clear(self) -> None:
        """Clear all items from the cache and reset stats."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def __repr__(self) -> str:
        """String representation showing current cache state."""
        items = list(self.cache.items())
        return f"LRUCache(capacity={self.capacity}, items={items})"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a small cache to see eviction in action
    cache = LRUCache(capacity=3)
    
    print("Adding items to cache (capacity=3):")
    cache.put("user:123", {"name": "Alice", "age": 30})
    print(f"  Added user:123")
    
    cache.put("user:456", {"name": "Bob", "age": 25})
    print(f"  Added user:456")
    
    cache.put("session:abc", {"token": "xyz789", "expires": 3600})
    print(f"  Added session:abc")
    
    print(f"\nCache state: {cache.size()}/{cache.capacity} items")
    print(cache)
    
    print("\n--- Testing LRU eviction ---")
    print("Accessing user:123 (marks as recently used):")
    user_data = cache.get("user:123")
    print(f"  Retrieved: {user_data}")
    
    print("\nAdding new item (should evict user:456, which is now LRU):")
    cache.put("config:api", {"url": "api.example.com", "timeout": 30})
    
    print("\nTrying to access evicted user:456:")
    result = cache.get("user:456")
    print(f"  Result: {result} (cache miss)")
    
    print(f"\nFinal cache state: {cache}")
    
    print("\n--- Cache Statistics ---")
    print(f"Hits: {cache.hits}")
    print(f"Misses: {cache.misses}")
    print(f"Hit Rate: {cache.hit_rate():.1f}%")
    
    print("\n--- Stress test with repeated access ---")
    cache.clear()
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)
    
    # Access pattern that keeps 'a' hot
    for _ in range(5):
        cache.get("a")
    
    cache.put("d", 4)  # Should evict 'b' since 'a' was accessed frequently
    
    print(f"After repeated 'a' accesses: {cache}")
    print(f"Final hit rate: {cache.hit_rate():.1f}%")