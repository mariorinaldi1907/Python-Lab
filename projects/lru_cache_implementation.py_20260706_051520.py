"""
Date: 2026-07-06
Implemented an LRU cache with O(1) get/put operations because I wanted to understand how Python's functools.lru_cache works under the hood.
"""

#!/usr/bin/env python3
"""
LRU Cache Implementation
A proper least-recently-used cache that evicts old items when capacity is reached.
Uses a doubly linked list for ordering and a dict for O(1) lookups.
"""


class Node:
    """
    Doubly linked list node to maintain access order.
    Stores key-value pairs and pointers to prev/next nodes.
    """
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    LRU Cache with fixed capacity.
    
    When at capacity, evicts the least recently used item before adding new ones.
    Both get() and put() count as "using" an item, moving it to most recent.
    """
    
    def __init__(self, capacity):
        """
        Initialize cache with given capacity.
        
        Args:
            capacity: Maximum number of items to store
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.cache = {}  # Maps keys to Node objects for O(1) lookup
        
        # Dummy head and tail make list operations way simpler
        # Real nodes live between these sentinels
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove_node(self, node):
        """
        Remove a node from the doubly linked list.
        Doesn't touch the cache dict — that's the caller's job.
        """
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _add_to_front(self, node):
        """
        Add node right after head (most recently used position).
        """
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
    
    def _move_to_front(self, node):
        """
        Move existing node to front (mark as recently used).
        """
        self._remove_node(node)
        self._add_to_front(node)
    
    def get(self, key):
        """
        Retrieve value for key, or return -1 if not found.
        Marks the key as recently used.
        
        Args:
            key: The key to look up
            
        Returns:
            Value if found, -1 otherwise
        """
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        self._move_to_front(node)  # Accessing counts as using it
        return node.value
    
    def put(self, key, value):
        """
        Insert or update a key-value pair.
        Evicts LRU item if at capacity.
        
        Args:
            key: The key to store
            value: The value to associate with the key
        """
        if key in self.cache:
            # Update existing key — remove old node
            node = self.cache[key]
            node.value = value
            self._move_to_front(node)
        else:
            # New key — check if we need to evict
            if len(self.cache) >= self.capacity:
                # Remove least recently used (node before tail)
                lru_node = self.tail.prev
                self._remove_node(lru_node)
                del self.cache[lru_node.key]
            
            # Add new node
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_front(new_node)
    
    def __repr__(self):
        """
        Show current cache contents in order from most to least recent.
        """
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"{current.key}:{current.value}")
            current = current.next
        return f"LRUCache({self.capacity}) [{' -> '.join(items)}]"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a cache that holds 3 items
    cache = LRUCache(3)
    
    print("Creating cache with capacity=3\n")
    
    print("Operations:")
    print("put(1, 'apple')")
    cache.put(1, "apple")
    print(f"State: {cache}\n")
    
    print("put(2, 'banana')")
    cache.put(2, "banana")
    print(f"State: {cache}\n")
    
    print("put(3, 'cherry')")
    cache.put(3, "cherry")
    print(f"State: {cache}\n")
    
    print("get(1) ->", cache.get(1))
    print(f"State: {cache}")
    print("(1 moved to front since we just accessed it)\n")
    
    print("put(4, 'date')")
    cache.put(4, "date")
    print(f"State: {cache}")
    print("(2 was evicted — it was least recently used)\n")
    
    print("get(2) ->", cache.get(2))
    print("(returns -1, key not found)\n")
    
    print("get(3) ->", cache.get(3))
    print(f"State: {cache}")
    print("(3 moved to front)\n")
    
    print("put(1, 'APPLE')")
    cache.put(1, "APPLE")
    print(f"State: {cache}")
    print("(updated value for existing key 1)\n")
    
    print("put(5, 'elderberry')")
    cache.put(5, "elderberry")
    print(f"State: {cache}")
    print("(4 was evicted)")