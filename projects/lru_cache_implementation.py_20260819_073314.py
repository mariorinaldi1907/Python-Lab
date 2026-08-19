"""
Date: 2026-08-19
Built a proper LRU cache with O(1) get/put operations to finally understand the data structure behind Python's caching decorator.
"""

"""
LRU Cache Implementation
========================
A least-recently-used cache that evicts the oldest item when capacity is reached.
Uses a hashmap for O(1) lookups and a doubly linked list for O(1) reordering.
"""


class Node:
    """
    Doubly linked list node for tracking access order.
    Most recently used items move to the head, least recently used fall to the tail.
    """
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    LRU Cache with O(1) get and put operations.
    
    The trick here is maintaining both a hashmap (for fast lookups) and a doubly
    linked list (for tracking access order). Every access moves the node to the front.
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
        
        # Using sentinel nodes to avoid edge case handling
        # head.next is most recent, tail.prev is least recent
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove(self, node):
        """
        Remove a node from the linked list (doesn't delete from hashmap).
        This is used when we need to reposition a node.
        """
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _add_to_head(self, node):
        """
        Add a node right after the head (marking it as most recently used).
        """
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
    
    def get(self, key):
        """
        Get a value from the cache. Returns -1 if key doesn't exist.
        Marks the accessed item as most recently used.
        
        Args:
            key: The key to look up
            
        Returns:
            The value associated with the key, or -1 if not found
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
        If the cache is full, evicts the least recently used item.
        
        Args:
            key: The key to insert/update
            value: The value to store
        """
        if key in self.cache:
            # Update existing key - remove old node
            self._remove(self.cache[key])
        
        # Create new node and add to front
        new_node = Node(key, value)
        self._add_to_head(new_node)
        self.cache[key] = new_node
        
        # Check if we exceeded capacity
        if len(self.cache) > self.capacity:
            # Remove least recently used (node before tail)
            lru = self.tail.prev
            self._remove(lru)
            del self.cache[lru.key]
    
    def __repr__(self):
        """String representation showing current cache state in order of recency."""
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"{current.key}:{current.value}")
            current = current.next
        return f"LRUCache(capacity={self.capacity}, items=[{' -> '.join(items)}])"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a cache that holds 3 items max
    cache = LRUCache(3)
    
    print("Creating cache with capacity 3")
    print(f"Initial state: {cache}\n")
    
    # Add some items
    print("Operations:")
    cache.put(1, "one")
    print(f"put(1, 'one')   -> {cache}")
    
    cache.put(2, "two")
    print(f"put(2, 'two')   -> {cache}")
    
    cache.put(3, "three")
    print(f"put(3, 'three') -> {cache}")
    
    # Access an item (moves it to front)
    value = cache.get(1)
    print(f"get(1)          -> '{value}' (moved to front)")
    print(f"                   {cache}")
    
    # Adding a 4th item should evict key=2 (least recently used)
    cache.put(4, "four")
    print(f"put(4, 'four')  -> {cache}")
    print("                   ^ key=2 was evicted (LRU)")
    
    # Try to get the evicted key
    value = cache.get(2)
    print(f"get(2)          -> {value} (not found)\n")
    
    # Update an existing key
    cache.put(3, "THREE")
    print(f"put(3, 'THREE') -> {cache}")
    print("                   ^ updated value and moved to front")
    
    print("\n=== Cache Access Pattern Test ===")
    test_cache = LRUCache(2)
    print("Cache with capacity 2:")
    test_cache.put("a", 1)
    test_cache.put("b", 2)
    print(f"After put('a',1), put('b',2): {test_cache}")
    print(f"get('a'): {test_cache.get('a')}")
    test_cache.put("c", 3)
    print(f"After put('c',3): {test_cache}")
    print("'b' was evicted because 'a' was accessed more recently")