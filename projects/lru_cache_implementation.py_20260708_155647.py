"""
Date: 2026-07-08
Implemented an LRU cache with get/put operations in constant time — needed this to understand how Python's functools.lru_cache actually works under the hood.
"""

"""
LRU Cache Implementation
========================
A Least Recently Used (LRU) cache that evicts the least recently accessed item
when capacity is reached. Uses a doubly linked list for O(1) removal/insertion
and a hash map for O(1) lookups.
"""


class DLLNode:
    """
    Node for a doubly linked list.
    Stores key-value pairs and pointers to prev/next nodes.
    """
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    LRU Cache with O(1) get and put operations.
    
    Uses a doubly linked list to track access order (most recent at head)
    and a dictionary to map keys to nodes for fast lookups.
    """
    
    def __init__(self, capacity):
        """
        Initialize the cache with a fixed capacity.
        
        Args:
            capacity: Maximum number of items the cache can hold
        """
        self.capacity = capacity
        self.cache = {}  # key -> DLLNode mapping
        
        # Dummy head and tail nodes make insertion/deletion logic cleaner
        # Real nodes will be between head and tail
        self.head = DLLNode()
        self.tail = DLLNode()
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove_node(self, node):
        """
        Remove a node from the doubly linked list.
        Doesn't delete from the hash map — that's done separately.
        """
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _add_to_head(self, node):
        """
        Add a node right after the head (marks it as most recently used).
        """
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
    
    def _move_to_head(self, node):
        """
        Move an existing node to the head position (refresh its access time).
        """
        self._remove_node(node)
        self._add_to_head(node)
    
    def _evict_tail(self):
        """
        Remove the least recently used item (the one right before tail).
        Returns the key that was evicted so we can remove it from the dict.
        """
        lru_node = self.tail.prev
        self._remove_node(lru_node)
        return lru_node.key
    
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
        Insert or update a key-value pair in the cache.
        
        If at capacity, evicts the least recently used item first.
        
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
            # New key — need to check capacity
            if len(self.cache) >= self.capacity:
                evicted_key = self._evict_tail()
                del self.cache[evicted_key]
            
            new_node = DLLNode(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)
    
    def __str__(self):
        """Return a string representation of the cache (most to least recent)."""
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"{current.key}:{current.value}")
            current = current.next
        return f"LRUCache[{' -> '.join(items)}]"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a cache that holds 3 items max
    cache = LRUCache(capacity=3)
    
    print("Inserting (1, 'apple'), (2, 'banana'), (3, 'cherry')...")
    cache.put(1, "apple")
    cache.put(2, "banana")
    cache.put(3, "cherry")
    print(f"Cache state: {cache}\n")
    
    print("Getting key 1 (should be 'apple')...")
    print(f"Value: {cache.get(1)}")
    print(f"Cache state: {cache}")
    print("^ Notice key 1 moved to front (most recently used)\n")
    
    print("Inserting (4, 'date')...")
    cache.put(4, "date")
    print(f"Cache state: {cache}")
    print("^ Key 2 was evicted (least recently used)\n")
    
    print("Getting key 2 (should be -1, was evicted)...")
    print(f"Value: {cache.get(2)}\n")
    
    print("Updating key 3 to 'coconut'...")
    cache.put(3, "coconut")
    print(f"Cache state: {cache}")
    print("^ Key 3 moved to front and value updated\n")
    
    print("Inserting (5, 'elderberry')...")
    cache.put(5, "elderberry")
    print(f"Cache state: {cache}")
    print("^ Key 1 was evicted (was least recently used after previous operations)")