"""
Date: 2026-07-11
Built a proper LRU cache with get/put operations in O(1) time to finally understand the eviction policy mechanics myself.
"""

"""
LRU (Least Recently Used) Cache Implementation

I've always used functools.lru_cache but never really understood how it works.
This is my attempt at building one from scratch using OrderedDict to maintain
insertion order. The key insight is that we need O(1) access AND O(1) eviction,
which is exactly what OrderedDict gives us.
"""

from collections import OrderedDict


class LRUCache:
    """
    A fixed-size cache that evicts the least recently used item when full.
    
    Uses OrderedDict internally because it maintains insertion order and
    allows us to move items to the end in O(1) time when they're accessed.
    """
    
    def __init__(self, capacity: int):
        """
        Initialize the LRU cache with a fixed capacity.
        
        Args:
            capacity: Maximum number of items the cache can hold
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.cache = OrderedDict()
    
    def get(self, key: int) -> int:
        """
        Get value from cache. Returns -1 if key doesn't exist.
        
        When we access a key, we need to mark it as recently used by moving
        it to the end of our OrderedDict. The move_to_end() method does this
        efficiently without having to delete and re-insert.
        
        Args:
            key: The key to look up
            
        Returns:
            The value if found, -1 otherwise
        """
        if key not in self.cache:
            return -1
        
        # Move to end to mark as recently used
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key: int, value: int) -> None:
        """
        Add or update a key-value pair in the cache.
        
        If the key already exists, we update it and move to end.
        If it's new and we're at capacity, we evict the first item
        (least recently used) before adding the new one.
        
        Args:
            key: The key to insert/update
            value: The value to store
        """
        if key in self.cache:
            # Update existing key and move to end
            self.cache.move_to_end(key)
            self.cache[key] = value
        else:
            # Check if we need to evict before inserting
            if len(self.cache) >= self.capacity:
                # Remove the first item (least recently used)
                # last=False means FIFO order (oldest first)
                self.cache.popitem(last=False)
            
            # Add new item (will be at the end)
            self.cache[key] = value
    
    def __repr__(self) -> str:
        """String representation showing current cache state."""
        items = list(self.cache.items())
        return f"LRUCache(capacity={self.capacity}, items={items})"


def demo_basic_operations():
    """Demonstrate basic LRU cache operations."""
    print("=== Basic LRU Cache Demo ===\n")
    
    cache = LRUCache(capacity=3)
    print(f"Created cache with capacity 3: {cache}\n")
    
    # Add some items
    print("Adding items...")
    cache.put(1, 100)
    print(f"put(1, 100): {cache}")
    cache.put(2, 200)
    print(f"put(2, 200): {cache}")
    cache.put(3, 300)
    print(f"put(3, 300): {cache}\n")
    
    # Access an item (moves it to end)
    print("Accessing items...")
    val = cache.get(1)
    print(f"get(1) = {val}: {cache}")
    print("  ^ Notice how key 1 moved to the end\n")
    
    # Add another item, should evict key 2 (least recently used)
    print("Adding new item (will trigger eviction)...")
    cache.put(4, 400)
    print(f"put(4, 400): {cache}")
    print("  ^ Key 2 was evicted (least recently used)\n")
    
    # Try to get evicted item
    print("Trying to access evicted item...")
    val = cache.get(2)
    print(f"get(2) = {val} (not found)\n")


def demo_update_behavior():
    """Show how updating existing keys affects order."""
    print("=== Update Behavior Demo ===\n")
    
    cache = LRUCache(capacity=3)
    cache.put(1, 100)
    cache.put(2, 200)
    cache.put(3, 300)
    print(f"Initial state: {cache}\n")
    
    # Update key 1 with new value
    print("Updating existing key with new value...")
    cache.put(1, 999)
    print(f"put(1, 999): {cache}")
    print("  ^ Key 1 moved to end and value updated\n")
    
    # Now add a new item
    cache.put(4, 400)
    print(f"put(4, 400): {cache}")
    print("  ^ Key 2 was evicted (it was least recently used)")


if __name__ == "__main__":
    demo_basic_operations()
    print("\n" + "="*50 + "\n")
    demo_update_behavior()