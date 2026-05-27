"""
Date: 2026-05-27
Built an LRU cache to explore how caching strategies work under the hood — uses OrderedDict to maintain access order and evict least recently used items.
"""

#!/usr/bin/env python3
"""
LRU Cache Implementation
A simple but functional Least Recently Used cache that I built to understand
how caching eviction policies actually work. Uses OrderedDict to track access
order efficiently.
"""

from collections import OrderedDict
from typing import Any, Optional


class LRUCache:
    """
    Least Recently Used (LRU) Cache implementation.
    
    When the cache reaches capacity, it evicts the least recently accessed item.
    Both get() and put() count as "using" an item, so they update its position.
    """
    
    def __init__(self, capacity: int):
        """
        Initialize the LRU cache with a given capacity.
        
        Args:
            capacity: Maximum number of items the cache can hold
        
        Raises:
            ValueError: If capacity is less than 1
        """
        if capacity < 1:
            raise ValueError("Cache capacity must be at least 1")
        
        self.capacity = capacity
        self.cache = OrderedDict()  # Maintains insertion order, perfect for LRU
        self.hits = 0
        self.misses = 0
    
    def get(self, key: Any) -> Optional[Any]:
        """
        Retrieve a value from the cache.
        
        If the key exists, move it to the end (mark as recently used).
        This is the core of LRU behavior — accessing something makes it "fresh".
        
        Args:
            key: The key to look up
            
        Returns:
            The value associated with the key, or None if not found
        """
        if key not in self.cache:
            self.misses += 1
            return None
        
        # Move to end to mark as recently used
        self.cache.move_to_end(key)
        self.hits += 1
        return self.cache[key]
    
    def put(self, key: Any, value: Any) -> None:
        """
        Insert or update a key-value pair in the cache.
        
        If the key already exists, update it and move to end.
        If we're at capacity, evict the oldest (first) item before inserting.
        
        Args:
            key: The key to insert/update
            value: The value to store
        """
        if key in self.cache:
            # Update existing key and mark as recently used
            self.cache.move_to_end(key)
            self.cache[key] = value
            return
        
        # Check if we need to evict
        if len(self.cache) >= self.capacity:
            # Remove the first item (least recently used)
            # last=False means pop from the beginning
            evicted_key, evicted_value = self.cache.popitem(last=False)
            # In production I'd probably log this or track it
        
        # Add new item (automatically goes to the end)
        self.cache[key] = value
    
    def size(self) -> int:
        """Return the current number of items in the cache."""
        return len(self.cache)
    
    def clear(self) -> None:
        """Clear all items from the cache."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self) -> dict:
        """
        Get cache statistics.
        
        Useful for understanding cache performance in real scenarios.
        
        Returns:
            Dictionary with hits, misses, and hit rate
        """
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{hit_rate:.2f}%",
            'size': self.size(),
            'capacity': self.capacity
        }
    
    def __repr__(self) -> str:
        """String representation showing current cache contents."""
        items = list(self.cache.items())
        return f"LRUCache(capacity={self.capacity}, items={items})"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a small cache to easily see eviction behavior
    cache = LRUCache(capacity=3)
    
    print("1. Adding items to the cache:")
    cache.put("user:123", {"name": "Alice", "age": 30})
    cache.put("user:456", {"name": "Bob", "age": 25})
    cache.put("user:789", {"name": "Charlie", "age": 35})
    print(f"   Cache after 3 puts: {cache}")
    print()
    
    print("2. Accessing user:123 (should be a hit):")
    result = cache.get("user:123")
    print(f"   Result: {result}")
    print(f"   Cache after access: {cache}")
    print()
    
    print("3. Adding a 4th item (should evict user:456, the least recently used):")
    cache.put("user:999", {"name": "Dave", "age": 40})
    print(f"   Cache after new put: {cache}")
    print()
    
    print("4. Trying to access evicted user:456 (should miss):")
    result = cache.get("user:456")
    print(f"   Result: {result}")
    print()
    
    print("5. Updating existing user:789:")
    cache.put("user:789", {"name": "Charlie", "age": 36})  # Birthday!
    print(f"   Cache after update: {cache}")
    print()
    
    print("6. Cache statistics:")
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    print()
    
    # Demonstrate the LRU behavior more clearly
    print("=== LRU Eviction Order Demo ===\n")
    cache2 = LRUCache(capacity=4)
    
    print("Adding: A, B, C, D")
    for letter in ['A', 'B', 'C', 'D']:
        cache2.put(letter, f"Value_{letter}")
    print(f"Cache: {list(cache2.cache.keys())}")
    
    print("\nAccessing: B (moves B to end)")
    cache2.get('B')
    print(f"Cache: {list(cache2.cache.keys())}")
    
    print("\nAdding: E (evicts A, the oldest unused)")
    cache2.put('E', "Value_E")
    print(f"Cache: {list(cache2.cache.keys())}")
    
    print("\nAccessing: C (moves C to end)")
    cache2.get('C')
    print(f"Cache: {list(cache2.cache.keys())}")
    
    print("\nAdding: F (evicts D)")
    cache2.put('F', "Value_F")
    print(f"Cache: {list(cache2.cache.keys())}")