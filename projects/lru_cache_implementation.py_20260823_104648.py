"""
Date: 2026-08-23
Built an LRU cache from scratch to understand how eviction policies work under the hood — uses a dict for lookups and a custom doubly linked list for recency tracking.
"""

"""
LRU Cache implementation using a hashmap and doubly linked list.
I wanted to understand how caching works at a low level, so I built this
from scratch instead of using functools.lru_cache.
"""


class Node:
    """Doubly linked list node to track access order."""
    
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    Least Recently Used (LRU) Cache with O(1) get and put operations.
    
    The idea is to keep a hashmap for O(1) lookups and a doubly linked list
    to maintain access order. Most recently used items are at the head,
    least recently used at the tail.
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
        
        # Dummy head and tail to simplify edge cases
        # Real nodes will be inserted between them
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove(self, node):
        """Remove a node from the doubly linked list."""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _add_to_head(self, node):
        """Add a node right after the head (most recently used position)."""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
    
    def _move_to_head(self, node):
        """Move an existing node to the head (mark as recently used)."""
        self._remove(node)
        self._add_to_head(node)
    
    def get(self, key):
        """
        Retrieve a value from the cache.
        
        Args:
            key: The key to look up
            
        Returns:
            The value if found, -1 otherwise
        """
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        # Move to head since we just accessed it
        self._move_to_head(node)
        return node.value
    
    def put(self, key, value):
        """
        Add or update a key-value pair in the cache.
        
        If the cache is at capacity, evict the least recently used item.
        
        Args:
            key: The key to store
            value: The value to store
        """
        if key in self.cache:
            # Update existing key
            node = self.cache[key]
            node.value = value
            self._move_to_head(node)
        else:
            # Create new node
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)
            
            # Check if we exceeded capacity
            if len(self.cache) > self.capacity:
                # Evict the LRU item (the one before tail)
                lru = self.tail.prev
                self._remove(lru)
                del self.cache[lru.key]
    
    def __str__(self):
        """String representation showing cache contents in access order."""
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"{current.key}:{current.value}")
            current = current.next
        return f"LRUCache({self.capacity}) [MRU -> LRU]: {' -> '.join(items)}"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a cache with capacity 3
    cache = LRUCache(3)
    
    print("Creating cache with capacity 3")
    print(f"Initial state: {cache}\n")
    
    # Add some items
    print("Adding items...")
    cache.put(1, "one")
    print(f"put(1, 'one'): {cache}")
    
    cache.put(2, "two")
    print(f"put(2, 'two'): {cache}")
    
    cache.put(3, "three")
    print(f"put(3, 'three'): {cache}\n")
    
    # Access an item (moves it to front)
    print("Accessing items...")
    result = cache.get(1)
    print(f"get(1) = '{result}': {cache}")
    
    # Add another item, should evict key 2 (LRU)
    print(f"\nAdding 4th item (capacity is 3, so LRU will be evicted)...")
    cache.put(4, "four")
    print(f"put(4, 'four'): {cache}")
    
    # Try to get the evicted item
    result = cache.get(2)
    print(f"get(2) = {result} (evicted!)\n")
    
    # Update an existing key
    print("Updating existing key...")
    cache.put(1, "ONE")
    print(f"put(1, 'ONE'): {cache}\n")
    
    # Demonstrate full eviction cycle
    print("Adding more items to show eviction order...")
    cache.put(5, "five")
    print(f"put(5, 'five'): {cache}")
    
    cache.put(6, "six")
    print(f"put(6, 'six'): {cache}")