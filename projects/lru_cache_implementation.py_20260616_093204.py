"""
Date: 2026-06-16
Built an LRU cache from scratch to understand how caching strategies work — uses OrderedDict to track access order and supports capacity limits.
"""

#!/usr/bin/env python3
"""
LRU Cache Implementation
A Least Recently Used cache that evicts the oldest item when capacity is reached.
Using OrderedDict because it maintains insertion order and makes LRU logic cleaner.
"""

from collections import OrderedDict


class LRUCache:
    """
    LRU (Least Recently Used) Cache implementation.
    
    When the cache reaches capacity, the least recently accessed item gets evicted.
    Uses OrderedDict to efficiently track access order - move_to_end() is O(1).
    """
    
    def __init__(self, capacity):
        """
        Initialize the LRU cache.
        
        Args:
            capacity: Maximum number of items the cache can hold
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.cache = OrderedDict()
        self.hits = 0
        self.misses = 0
    
    def get(self, key):
        """
        Retrieve a value from the cache.
        
        Args:
            key: The key to look up
            
        Returns:
            The value if found, None otherwise
            
        Side effect: Marks the key as recently used by moving it to the end.
        """
        if key not in self.cache:
            self.misses += 1
            return None
        
        # Move to end to mark as recently used
        self.cache.move_to_end(key)
        self.hits += 1
        return self.cache[key]
    
    def put(self, key, value):
        """
        Insert or update a key-value pair in the cache.
        
        Args:
            key: The key to insert/update
            value: The value to store
            
        If cache is at capacity and key is new, evicts the LRU item first.
        If key exists, updates value and marks as recently used.
        """
        if key in self.cache:
            # Update existing key and mark as recently used
            self.cache.move_to_end(key)
            self.cache[key] = value
        else:
            # Check if we need to evict
            if len(self.cache) >= self.capacity:
                # popitem(last=False) removes the first (oldest) item
                evicted_key, evicted_value = self.cache.popitem(last=False)
                print(f"  [Evicted: {evicted_key} -> {evicted_value}]")
            
            # Insert new key-value pair
            self.cache[key] = value
    
    def delete(self, key):
        """
        Remove a key from the cache.
        
        Args:
            key: The key to remove
            
        Returns:
            True if key was present and removed, False otherwise
        """
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def size(self):
        """Return the current number of items in the cache."""
        return len(self.cache)
    
    def clear(self):
        """Remove all items from the cache."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self):
        """
        Return cache statistics.
        
        Returns:
            Dict with hits, misses, and hit rate
        """
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0.0
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{hit_rate:.1f}%"
        }
    
    def __str__(self):
        """String representation showing current cache contents in access order."""
        items = [f"{k}: {v}" for k, v in self.cache.items()]
        return f"LRUCache({len(self.cache)}/{self.capacity}): [{', '.join(items)}]"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a cache with capacity of 3
    cache = LRUCache(capacity=3)
    print(f"Created cache with capacity 3\n")
    
    # Add some items
    print("Adding items:")
    cache.put("user:123", {"name": "Alice", "age": 30})
    print(f"  put('user:123', Alice) -> {cache}")
    
    cache.put("user:456", {"name": "Bob", "age": 25})
    print(f"  put('user:456', Bob) -> {cache}")
    
    cache.put("session:abc", {"token": "xyz789"})
    print(f"  put('session:abc', token) -> {cache}")
    
    # Cache is now full
    print(f"\nCache is full: {cache}\n")
    
    # Access an old item (moves it to end)
    print("Accessing 'user:123' (makes it recently used):")
    result = cache.get("user:123")
    print(f"  get('user:123') -> {result['name']}")
    print(f"  {cache}\n")
    
    # Add new item - should evict user:456 (least recently used)
    print("Adding new item (should evict 'user:456'):")
    cache.put("page:home", {"views": 1523})
    print(f"  {cache}\n")
    
    # Try to get evicted item
    print("Trying to access evicted item:")
    result = cache.get("user:456")
    print(f"  get('user:456') -> {result}\n")
    
    # More operations
    print("More operations:")
    cache.put("user:789", {"name": "Charlie", "age": 35})
    print(f"  Added user:789 -> {cache}")
    
    cache.get("session:abc")
    print(f"  Accessed session:abc -> {cache}\n")
    
    # Show stats
    stats = cache.get_stats()
    print(f"Cache Statistics:")
    print(f"  Hits: {stats['hits']}")
    print(f"  Misses: {stats['misses']}")
    print(f"  Hit Rate: {stats['hit_rate']}")