"""
Date: 2026-07-04
Implemented an LRU cache with get/put operations in O(1) time by combining a dictionary with a doubly linked list for order tracking.
"""

"""
LRU (Least Recently Used) Cache Implementation

I wanted to understand how LRU caches work under the hood, especially how they
achieve O(1) for both get and put operations. The trick is using a hashmap for
fast lookups and a doubly linked list to track access order efficiently.
"""


class Node:
    """Doubly linked list node to store cache entries."""
    
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    LRU Cache with O(1) get and put operations.
    
    Uses a hashmap (dict) for O(1) lookups and a doubly linked list
    to maintain order. Most recently used items are at the head,
    least recently used at the tail.
    """
    
    def __init__(self, capacity):
        """
        Initialize the LRU cache with a fixed capacity.
        
        Args:
            capacity: Maximum number of items the cache can hold
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.cache = {}  # Maps keys to nodes
        
        # Dummy head and tail make insertion/deletion cleaner
        # Real nodes will be between head and tail
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
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
    
    def get(self, key):
        """
        Get value for a key, mark it as recently used.
        
        Args:
            key: The key to look up
            
        Returns:
            The value if key exists, -1 otherwise
        """
        if key not in self.cache:
            return -1
        
        # Move to head since we just accessed it
        node = self.cache[key]
        self._remove(node)
        self._add_to_head(node)
        
        return node.value
    
    def put(self, key, value):
        """
        Insert or update a key-value pair, evict LRU item if at capacity.
        
        Args:
            key: The key to insert/update
            value: The value to store
        """
        if key in self.cache:
            # Update existing key - remove old node
            self._remove(self.cache[key])
        
        # Create new node and add to head
        new_node = Node(key, value)
        self._add_to_head(new_node)
        self.cache[key] = new_node
        
        # Evict LRU item if over capacity
        if len(self.cache) > self.capacity:
            # The node right before tail is the LRU
            lru = self.tail.prev
            self._remove(lru)
            del self.cache[lru.key]
    
    def __str__(self):
        """String representation showing cache contents in order."""
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
    print("Adding items:")
    cache.put(1, "one")
    print(f"  put(1, 'one') -> {cache}")
    
    cache.put(2, "two")
    print(f"  put(2, 'two') -> {cache}")
    
    cache.put(3, "three")
    print(f"  put(3, 'three') -> {cache}")
    
    # Access an item (moves it to front)
    print(f"\nget(1) -> {cache.get(1)}")
    print(f"  Cache after access: {cache}")
    
    # Add another item - should evict key 2 (least recently used)
    print(f"\nput(4, 'four') -> this should evict key 2")
    cache.put(4, "four")
    print(f"  Cache: {cache}")
    
    # Try to get evicted item
    print(f"\nget(2) -> {cache.get(2)} (evicted, returns -1)")
    
    # Update existing key
    print(f"\nput(3, 'THREE') -> updating existing key")
    cache.put(3, "THREE")
    print(f"  Cache: {cache}")
    
    # Demonstrate access order
    print("\nAccessing items in specific order:")
    cache.get(1)
    print(f"  get(1) -> {cache}")
    cache.get(4)
    print(f"  get(4) -> {cache}")
    
    print("\nAdding new item (should evict key 3):")
    cache.put(5, "five")
    print(f"  put(5, 'five') -> {cache}")
    
    print("\n=== Demo Complete ===")