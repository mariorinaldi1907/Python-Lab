"""
Date: 2026-08-03
Built an LRU cache with O(1) get/put operations to understand how caching eviction policies work under the hood.
"""

#!/usr/bin/env python3
"""
LRU (Least Recently Used) Cache Implementation

I wanted to really understand how LRU caching works internally, so I built
this from scratch. Uses a doubly linked list for O(1) removal/insertion and
a dict for O(1) lookups. When capacity is hit, we evict the least recently
used item (the tail of our list).
"""


class Node:
    """
    Doubly linked list node for the LRU cache.
    
    Each node holds a key-value pair plus pointers to prev/next nodes.
    The key is stored here so we can delete from the hash map during eviction.
    """
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    Least Recently Used (LRU) Cache with O(1) get and put operations.
    
    Uses a hash map for fast lookups and a doubly linked list to track
    access order. Most recently used items are at the head, least recently
    used at the tail.
    """
    
    def __init__(self, capacity):
        """
        Initialize LRU cache with given capacity.
        
        Args:
            capacity: Maximum number of items the cache can hold
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.cache = {}  # Maps keys to Node objects
        
        # Dummy head and tail nodes make list operations cleaner
        # (no need to check for None on every insert/remove)
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove(self, node):
        """
        Remove a node from the doubly linked list.
        
        Args:
            node: The node to remove
        """
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _add_to_head(self, node):
        """
        Add a node right after the head (most recently used position).
        
        Args:
            node: The node to add
        """
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
    
    def get(self, key):
        """
        Get value for a key and mark it as recently used.
        
        Args:
            key: The key to look up
            
        Returns:
            The value if key exists, -1 otherwise
        """
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        # Move to front since it was just accessed
        self._remove(node)
        self._add_to_head(node)
        return node.value
    
    def put(self, key, value):
        """
        Add or update a key-value pair in the cache.
        
        If key exists, update value and move to front.
        If cache is full, evict least recently used item first.
        
        Args:
            key: The key to add/update
            value: The value to store
        """
        if key in self.cache:
            # Update existing key - remove old node
            self._remove(self.cache[key])
        
        # Create new node and add to front
        new_node = Node(key, value)
        self._add_to_head(new_node)
        self.cache[key] = new_node
        
        # Check capacity and evict if needed
        if len(self.cache) > self.capacity:
            # Remove least recently used (node before tail)
            lru = self.tail.prev
            self._remove(lru)
            del self.cache[lru.key]
    
    def __repr__(self):
        """Return string representation showing cache contents in order."""
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"{current.key}:{current.value}")
            current = current.next
        return f"LRUCache({len(self.cache)}/{self.capacity}): [{' -> '.join(items)}]"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a cache with capacity 3
    cache = LRUCache(3)
    print(f"Created cache with capacity 3\n")
    
    # Add some items
    print("Adding items:")
    cache.put(1, "one")
    print(f"  put(1, 'one') -> {cache}")
    
    cache.put(2, "two")
    print(f"  put(2, 'two') -> {cache}")
    
    cache.put(3, "three")
    print(f"  put(3, 'three') -> {cache}")
    
    # Access an item (moves it to front)
    print(f"\nAccessing key 1:")
    result = cache.get(1)
    print(f"  get(1) = '{result}' -> {cache}")
    
    # Add another item, should evict key 2 (least recently used)
    print(f"\nAdding key 4 (should evict key 2):")
    cache.put(4, "four")
    print(f"  put(4, 'four') -> {cache}")
    
    # Try to access evicted item
    print(f"\nTrying to access evicted key 2:")
    result = cache.get(2)
    print(f"  get(2) = {result} (not found)")
    
    # Update existing key
    print(f"\nUpdating key 3:")
    cache.put(3, "THREE")
    print(f"  put(3, 'THREE') -> {cache}")
    
    # Show final state
    print(f"\nFinal cache state: {cache}")
    print(f"  get(1) = '{cache.get(1)}'")
    print(f"  get(3) = '{cache.get(3)}'")
    print(f"  get(4) = '{cache.get(4)}'")