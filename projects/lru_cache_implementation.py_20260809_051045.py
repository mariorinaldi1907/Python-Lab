"""
Date: 2026-08-09
Built a proper LRU cache with O(1) get/put operations to finally understand the data structure behind Python's functools decorator.
"""

#!/usr/bin/env python3
"""
LRU Cache Implementation

A least-recently-used cache that evicts the oldest item when capacity is reached.
Uses a doubly linked list for O(1) access order maintenance and a hashmap for O(1) lookups.
"""


class Node:
    """
    Doubly linked list node for maintaining access order.
    
    Stores the key so we can remove it from the hashmap during eviction,
    and the value for quick retrieval.
    """
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    LRU Cache with O(1) get and put operations.
    
    The doubly linked list maintains items in access order (most recent at head).
    The hashmap provides O(1) lookups to nodes in the list.
    """
    
    def __init__(self, capacity):
        """
        Initialize the cache with a fixed capacity.
        
        Args:
            capacity: Maximum number of items the cache can hold
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.cache = {}  # key -> Node mapping
        
        # Dummy head and tail make list operations simpler
        # because we never have to handle None cases at the ends
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove_node(self, node):
        """Remove a node from the doubly linked list."""
        node.prev.next = node.next
        node.next.prev = node.prev
    
    def _add_to_head(self, node):
        """Add a node right after the dummy head (most recently used position)."""
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
    
    def _move_to_head(self, node):
        """Move an existing node to the head (mark as recently used)."""
        self._remove_node(node)
        self._add_to_head(node)
    
    def _evict_tail(self):
        """Remove the least recently used item (the one before dummy tail)."""
        lru_node = self.tail.prev
        self._remove_node(lru_node)
        del self.cache[lru_node.key]
    
    def get(self, key):
        """
        Retrieve a value from the cache.
        
        Args:
            key: The key to look up
            
        Returns:
            The value if found, None otherwise
        """
        if key not in self.cache:
            return None
        
        # Move to head since we just accessed it
        node = self.cache[key]
        self._move_to_head(node)
        return node.value
    
    def put(self, key, value):
        """
        Insert or update a key-value pair in the cache.
        
        If the cache is at capacity and we're adding a new key,
        evict the least recently used item first.
        
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
            # Add new key
            if len(self.cache) >= self.capacity:
                self._evict_tail()
            
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)
    
    def __str__(self):
        """String representation showing items from most to least recent."""
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"{current.key}={current.value}")
            current = current.next
        return f"LRUCache([{', '.join(items)}])"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a cache that holds 3 items
    cache = LRUCache(capacity=3)
    
    print("Creating cache with capacity=3")
    print(f"Cache: {cache}\n")
    
    # Add some items
    print("Adding: cache.put('user:1', 'Alice')")
    cache.put('user:1', 'Alice')
    print(f"Cache: {cache}\n")
    
    print("Adding: cache.put('user:2', 'Bob')")
    cache.put('user:2', 'Bob')
    print(f"Cache: {cache}\n")
    
    print("Adding: cache.put('user:3', 'Charlie')")
    cache.put('user:3', 'Charlie')
    print(f"Cache: {cache}\n")
    
    # Access an item (moves it to the front)
    print("Accessing: cache.get('user:1')")
    result = cache.get('user:1')
    print(f"Result: {result}")
    print(f"Cache: {cache}")
    print("(Notice user:1 moved to the front)\n")
    
    # Add a 4th item, should evict user:2 (the LRU)
    print("Adding 4th item: cache.put('user:4', 'David')")
    cache.put('user:4', 'David')
    print(f"Cache: {cache}")
    print("(user:2 was evicted as LRU)\n")
    
    # Try to get the evicted item
    print("Trying to get evicted item: cache.get('user:2')")
    result = cache.get('user:2')
    print(f"Result: {result}")
    print(f"Cache: {cache}\n")
    
    # Update an existing key
    print("Updating: cache.put('user:3', 'Charlie Updated')")
    cache.put('user:3', 'Charlie Updated')
    print(f"Cache: {cache}")
    print("(user:3 moved to front and value updated)\n")
    
    print("=== Demo Complete ===")