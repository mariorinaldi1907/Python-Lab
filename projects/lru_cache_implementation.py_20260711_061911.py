"""
Date: 2026-07-11
Implemented an LRU cache with get/put operations in constant time using a custom doubly linked list — wanted to really understand how these work under the hood.
"""

"""
LRU Cache Implementation
========================
A Least Recently Used cache with O(1) get and put operations.
Uses a doubly linked list for maintaining order and a hash map for fast lookups.
"""


class Node:
    """Doubly linked list node for storing key-value pairs."""
    
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    LRU Cache with fixed capacity.
    
    When capacity is exceeded, the least recently used item is evicted.
    Both get() and put() operations run in O(1) time.
    """
    
    def __init__(self, capacity):
        """
        Initialize cache with given capacity.
        
        Args:
            capacity: Maximum number of items the cache can hold
        """
        self.capacity = capacity
        self.cache = {}  # maps keys to nodes
        
        # Using sentinel nodes to avoid edge case checks
        # head.next is the most recently used, tail.prev is least recently used
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove_node(self, node):
        """Remove a node from the doubly linked list."""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _add_to_front(self, node):
        """Add a node right after the head (most recently used position)."""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
    
    def _move_to_front(self, node):
        """Move an existing node to the front (mark as most recently used)."""
        self._remove_node(node)
        self._add_to_front(node)
    
    def get(self, key):
        """
        Get value for a key if it exists in cache.
        
        Marks the key as recently used by moving it to the front.
        
        Args:
            key: The key to look up
            
        Returns:
            The value associated with the key, or -1 if not found
        """
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        self._move_to_front(node)
        return node.value
    
    def put(self, key, value):
        """
        Insert or update a key-value pair in the cache.
        
        If the key exists, updates the value and marks as recently used.
        If cache is at capacity, evicts the least recently used item first.
        
        Args:
            key: The key to insert/update
            value: The value to associate with the key
        """
        if key in self.cache:
            # Update existing key
            node = self.cache[key]
            node.value = value
            self._move_to_front(node)
        else:
            # Insert new key
            if len(self.cache) >= self.capacity:
                # Evict least recently used (node before tail)
                lru_node = self.tail.prev
                self._remove_node(lru_node)
                del self.cache[lru_node.key]
            
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_front(new_node)
    
    def display_cache_state(self):
        """Display the current state of the cache from most to least recent."""
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"({current.key}: {current.value})")
            current = current.next
        print(f"Cache state (MRU -> LRU): {' -> '.join(items) if items else 'empty'}")


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a cache with capacity 3
    cache = LRUCache(capacity=3)
    print("Created LRU cache with capacity 3\n")
    
    # Add some items
    print("Adding items (1, 'apple'), (2, 'banana'), (3, 'cherry'):")
    cache.put(1, "apple")
    cache.put(2, "banana")
    cache.put(3, "cherry")
    cache.display_cache_state()
    print()
    
    # Access an item (should move it to front)
    print("Accessing key 1:")
    value = cache.get(1)
    print(f"Got value: {value}")
    cache.display_cache_state()
    print()
    
    # Add another item (should evict LRU, which is key 2)
    print("Adding (4, 'date') - this should evict key 2 (banana):")
    cache.put(4, "date")
    cache.display_cache_state()
    print()
    
    # Try to get evicted item
    print("Trying to access evicted key 2:")
    value = cache.get(2)
    print(f"Got value: {value} (returns -1 when not found)")
    print()
    
    # Update existing item
    print("Updating key 3 with new value 'coconut':")
    cache.put(3, "coconut")
    cache.display_cache_state()
    print()
    
    # Access in different order
    print("Accessing keys in order: 4, 1, 3")
    cache.get(4)
    cache.get(1)
    cache.get(3)
    cache.display_cache_state()
    print()
    
    print("Adding (5, 'elderberry') - should evict key 4 now:")
    cache.put(5, "elderberry")
    cache.display_cache_state()