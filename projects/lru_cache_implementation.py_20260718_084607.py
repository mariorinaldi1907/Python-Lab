"""
Date: 2026-07-18
Implemented a Least Recently Used cache with capacity limits using a doubly linked list for ordering and a hashmap for fast lookups, because I wanted to understand how Python's functools.lru_cache actually works under the hood.
"""

"""
LRU Cache Implementation
A Least Recently Used cache that evicts the oldest item when capacity is reached.
Uses a doubly linked list for O(1) reordering and a dict for O(1) lookups.
"""


class Node:
    """Doubly linked list node to maintain access order."""
    
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    LRU Cache with O(1) get and put operations.
    
    The cache keeps track of recently used items. When capacity is exceeded,
    it evicts the least recently used item. I'm using a doubly linked list
    to maintain order (most recent at head) and a dict for fast key lookups.
    """
    
    def __init__(self, capacity):
        """
        Initialize cache with given capacity.
        
        Args:
            capacity: Maximum number of items the cache can hold
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.cache = {}  # Maps keys to nodes for O(1) lookup
        
        # Dummy head and tail make list operations simpler
        # No need to check for None when adding/removing nodes
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove_node(self, node):
        """Remove a node from the doubly linked list."""
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
        self._remove_node(node)
        self._add_to_head(node)
    
    def get(self, key):
        """
        Get value for a key, marking it as recently used.
        
        Args:
            key: The key to look up
            
        Returns:
            The value if found, -1 otherwise
        """
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        self._move_to_head(node)  # Mark as recently used
        return node.value
    
    def put(self, key, value):
        """
        Put a key-value pair in the cache.
        
        If key exists, update its value. If cache is full, evict the LRU item.
        The new/updated item becomes the most recently used.
        
        Args:
            key: The key to store
            value: The value to associate with the key
        """
        if key in self.cache:
            # Update existing key
            node = self.cache[key]
            node.value = value
            self._move_to_head(node)
        else:
            # New key
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)
            
            # Evict LRU item if we're over capacity
            if len(self.cache) > self.capacity:
                lru = self.tail.prev  # Least recently used is right before tail
                self._remove_node(lru)
                del self.cache[lru.key]
    
    def __str__(self):
        """Return string representation showing items from most to least recent."""
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
    print("Created cache with capacity 3\n")
    
    # Add some items
    print("Operations:")
    cache.put(1, "one")
    print(f"put(1, 'one'):  {cache}")
    
    cache.put(2, "two")
    print(f"put(2, 'two'):  {cache}")
    
    cache.put(3, "three")
    print(f"put(3, 'three'): {cache}")
    
    # Access an item (should move it to front)
    print(f"\nget(1): {cache.get(1)}")
    print(f"After get(1):   {cache}")
    
    # Add a fourth item (should evict key 2, the LRU)
    cache.put(4, "four")
    print(f"\nput(4, 'four'): {cache}")
    print(f"Key 2 was evicted (LRU)")
    
    # Try to get the evicted item
    print(f"\nget(2): {cache.get(2)} (not found)")
    
    # Update an existing key
    cache.put(3, "THREE")
    print(f"\nput(3, 'THREE'): {cache}")
    
    # Access pattern that moves items around
    print(f"\nget(4): {cache.get(4)}")
    print(f"After get(4):    {cache}")
    
    print(f"\nget(3): {cache.get(3)}")
    print(f"After get(3):    {cache}")
    
    # Now key 1 is LRU, adding new item will evict it
    cache.put(5, "five")
    print(f"\nput(5, 'five'):  {cache}")
    print(f"Key 1 was evicted (became LRU)")