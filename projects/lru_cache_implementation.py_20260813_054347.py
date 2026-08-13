"""
Date: 2026-08-13
Implemented an LRU cache with O(1) get/put operations to really understand how functools.lru_cache works under the hood.
"""

"""
LRU (Least Recently Used) Cache implementation.
Uses a doubly-linked list for ordering and a hashmap for O(1) access.
"""


class DLLNode:
    """Node in a doubly-linked list for maintaining access order."""
    
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    LRU Cache with O(1) get and put operations.
    
    The most recently used items are at the head, least recently used at the tail.
    When capacity is exceeded, we evict from the tail.
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
        self.cache = {}  # key -> DLLNode mapping for O(1) access
        
        # Dummy head and tail nodes make insertion/deletion simpler
        # because we don't have to handle edge cases at list boundaries
        self.head = DLLNode(0, 0)
        self.tail = DLLNode(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove(self, node):
        """Remove a node from the doubly-linked list."""
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
        Get value from cache. Returns -1 if key doesn't exist.
        Marks the key as recently used by moving it to the head.
        """
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        self._move_to_head(node)  # Mark as recently used
        return node.value
    
    def put(self, key, value):
        """
        Put a key-value pair into the cache.
        If key exists, update value and mark as recently used.
        If cache is at capacity, evict the least recently used item.
        """
        if key in self.cache:
            # Key exists, update value and move to head
            node = self.cache[key]
            node.value = value
            self._move_to_head(node)
        else:
            # New key, create new node
            new_node = DLLNode(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)
            
            # Check if we exceeded capacity
            if len(self.cache) > self.capacity:
                # Remove least recently used (node before tail)
                lru_node = self.tail.prev
                self._remove(lru_node)
                del self.cache[lru_node.key]
    
    def __len__(self):
        """Return current number of items in cache."""
        return len(self.cache)
    
    def __repr__(self):
        """Show current cache state from most to least recently used."""
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"{current.key}: {current.value}")
            current = current.next
        return f"LRUCache({', '.join(items)})"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a cache with capacity 3
    cache = LRUCache(capacity=3)
    
    print("Creating cache with capacity 3")
    print(f"Initial state: {cache}\n")
    
    # Add some items
    print("Adding: (1, 'one'), (2, 'two'), (3, 'three')")
    cache.put(1, "one")
    cache.put(2, "two")
    cache.put(3, "three")
    print(f"Cache state: {cache}\n")
    
    # Access an item (moves it to front)
    print("Getting key 1 (moves to front)")
    value = cache.get(1)
    print(f"Value: {value}")
    print(f"Cache state: {cache}\n")
    
    # Add a new item, causing eviction of least recently used
    print("Adding (4, 'four') — should evict key 2 (least recently used)")
    cache.put(4, "four")
    print(f"Cache state: {cache}\n")
    
    # Try to get evicted item
    print("Trying to get key 2 (was evicted)")
    value = cache.get(2)
    print(f"Value: {value} (returns -1 when not found)\n")
    
    # Update existing key
    print("Updating key 3 to 'THREE'")
    cache.put(3, "THREE")
    print(f"Cache state: {cache}\n")
    
    # Demonstrate access pattern
    print("Access pattern: get(4), get(1), get(3)")
    cache.get(4)
    cache.get(1)
    cache.get(3)
    print(f"Cache state: {cache}")
    
    print("\n=== Performance Note ===")
    print("Both get() and put() operations are O(1) time complexity")
    print("Space complexity is O(capacity)")