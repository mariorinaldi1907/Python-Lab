"""
Date: 2026-06-10
Implemented an LRU cache with O(1) get/put operations using a hashmap and doubly linked list — wanted to understand how functools.lru_cache actually works under the hood.
"""

"""
LRU (Least Recently Used) Cache Implementation

I wanted to really understand how LRU caches work internally, so I built one
from scratch. Uses a doubly linked list to track access order and a dict for
O(1) lookups. When capacity is hit, we evict the least recently used item.
"""


class Node:
    """Doubly linked list node to track cache entries in access order."""
    
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    LRU Cache with O(1) get and put operations.
    
    The trick is using a dict for fast lookups and a doubly linked list
    to maintain the order of access. Most recently used is at the head,
    least recently used is at the tail.
    """
    
    def __init__(self, capacity):
        """
        Initialize the cache with a given capacity.
        
        Args:
            capacity: Maximum number of items the cache can hold
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.cache = {}  # key -> Node mapping
        
        # Dummy head and tail make list operations simpler
        # No need to check for None everywhere
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove(self, node):
        """Remove a node from the linked list."""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _add_to_head(self, node):
        """Add a node right after the head (most recently used position)."""
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
    
    def _move_to_head(self, node):
        """Move an existing node to the head (mark as recently used)."""
        self._remove(node)
        self._add_to_head(node)
    
    def get(self, key):
        """
        Get a value from the cache.
        
        Args:
            key: The key to look up
            
        Returns:
            The value if found, -1 otherwise
        """
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        # Move to head because we just accessed it
        self._move_to_head(node)
        return node.value
    
    def put(self, key, value):
        """
        Put a key-value pair into the cache.
        
        If the key exists, update it and mark as recently used.
        If cache is full, evict the LRU item before inserting.
        
        Args:
            key: The key to insert/update
            value: The value to store
        """
        if key in self.cache:
            # Update existing key
            node = self.cache[key]
            node.value = value
            self._move_to_head(node)
        else:
            # New key - create node and add to head
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)
            
            # Check if we exceeded capacity
            if len(self.cache) > self.capacity:
                # Remove LRU item (the one before tail)
                lru = self.tail.prev
                self._remove(lru)
                del self.cache[lru.key]
    
    def __str__(self):
        """String representation showing cache state in access order."""
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"{current.key}:{current.value}")
            current = current.next
        return f"LRUCache[{' -> '.join(items)}]"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a cache with capacity 3
    cache = LRUCache(3)
    print(f"Created cache with capacity 3\n")
    
    # Add some items
    print("Adding items...")
    cache.put(1, "one")
    print(f"put(1, 'one'): {cache}")
    
    cache.put(2, "two")
    print(f"put(2, 'two'): {cache}")
    
    cache.put(3, "three")
    print(f"put(3, 'three'): {cache}")
    
    # Access item 1 (should move to front)
    print(f"\nget(1): {cache.get(1)}")
    print(f"After access: {cache}")
    
    # Add item 4 - should evict item 2 (LRU)
    print(f"\nput(4, 'four') - this should evict key 2")
    cache.put(4, "four")
    print(f"After eviction: {cache}")
    
    # Try to get the evicted item
    print(f"\nget(2): {cache.get(2)} (should be -1, was evicted)")
    
    # Update existing key
    print(f"\nput(3, 'THREE') - updating existing key")
    cache.put(3, "THREE")
    print(f"After update: {cache}")
    
    # Access pattern that changes order
    print(f"\nAccess pattern: get(4), get(1)")
    print(f"get(4): {cache.get(4)}")
    print(f"get(1): {cache.get(1)}")
    print(f"Final state: {cache}")
    print("\nKey 3 is now LRU since we accessed 4 and 1")