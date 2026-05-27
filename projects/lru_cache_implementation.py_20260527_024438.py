"""
Date: 2026-05-27
Built an LRU cache with O(1) get/put operations to finally grok how @lru_cache actually works under the hood.
"""

"""
LRU Cache Implementation
------------------------
I wanted to understand how caching works at a fundamental level, so I built
this Least Recently Used cache from scratch. Uses OrderedDict to maintain
insertion order which makes the LRU logic way cleaner than a custom doubly-linked list.

The idea: when capacity is hit, evict the oldest item that hasn't been accessed.
Every get() or put() moves that key to the end (most recent).
"""

from collections import OrderedDict


class LRUCache:
    """
    A Least Recently Used cache with O(1) get and put operations.
    
    Uses OrderedDict to maintain access order — items are moved to the end
    when accessed, so the front always contains the least recently used item.
    """
    
    def __init__(self, capacity):
        """
        Initialize the cache with a fixed capacity.
        
        Args:
            capacity (int): Maximum number of items the cache can hold
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.cache = OrderedDict()
    
    def get(self, key):
        """
        Retrieve a value from the cache.
        
        Args:
            key: The key to look up
            
        Returns:
            The value if key exists, None otherwise
            
        Side effect: Moves the accessed key to the end (most recent)
        """
        if key not in self.cache:
            return None
        
        # Move to end to mark as recently used
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key, value):
        """
        Insert or update a key-value pair in the cache.
        
        Args:
            key: The key to insert/update
            value: The value to store
            
        Side effect: If at capacity and key is new, evicts the LRU item
        """
        if key in self.cache:
            # Update existing key and mark as recently used
            self.cache.move_to_end(key)
            self.cache[key] = value
        else:
            # New key — check capacity
            if len(self.cache) >= self.capacity:
                # Evict the least recently used (first item)
                evicted_key = next(iter(self.cache))
                del self.cache[evicted_key]
                print(f"  [Evicted '{evicted_key}' to make room]")
            
            self.cache[key] = value
    
    def peek_lru(self):
        """
        Return the least recently used key without modifying the cache.
        
        Returns:
            The LRU key if cache is non-empty, None otherwise
        """
        if not self.cache:
            return None
        return next(iter(self.cache))
    
    def peek_mru(self):
        """
        Return the most recently used key without modifying the cache.
        
        Returns:
            The MRU key if cache is non-empty, None otherwise
        """
        if not self.cache:
            return None
        return next(reversed(self.cache))
    
    def __len__(self):
        """Return the current number of items in the cache."""
        return len(self.cache)
    
    def __repr__(self):
        """String representation showing cache state in LRU order."""
        items = list(self.cache.items())
        return f"LRUCache({items})"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a small cache to see eviction behavior
    cache = LRUCache(capacity=3)
    
    print("Capacity: 3\n")
    
    print("1. Adding three items:")
    cache.put("user:123", {"name": "Alice", "age": 30})
    cache.put("user:456", {"name": "Bob", "age": 25})
    cache.put("user:789", {"name": "Charlie", "age": 35})
    print(f"   Cache state: {cache}\n")
    
    print("2. Accessing 'user:123' (moves it to most recent):")
    data = cache.get("user:123")
    print(f"   Retrieved: {data}")
    print(f"   Cache state: {cache}\n")
    
    print("3. Adding a 4th item (should evict LRU, which is now 'user:456'):")
    cache.put("user:999", {"name": "Diana", "age": 28})
    print(f"   Cache state: {cache}\n")
    
    print("4. Trying to get evicted item 'user:456':")
    result = cache.get("user:456")
    print(f"   Result: {result} (None = cache miss)\n")
    
    print("5. Updating existing key 'user:789' (moves to end):")
    cache.put("user:789", {"name": "Charlie", "age": 36})
    print(f"   Cache state: {cache}\n")
    
    print("6. Cache inspection:")
    print(f"   Current size: {len(cache)}")
    print(f"   Least recently used: {cache.peek_lru()}")
    print(f"   Most recently used: {cache.peek_mru()}")
    
    print("\n✓ Demo complete!")