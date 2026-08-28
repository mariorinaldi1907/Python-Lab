"""
Date: 2026-08-28
Built an LRU cache with O(1) get/put operations to really understand how caching works under the hood — uses a doubly-linked list to track recency.
"""

"""
LRU Cache implementation using a doubly-linked list + hashmap.

I wanted to understand how LRU caching actually works instead of just
using functools.lru_cache everywhere. The trick is maintaining insertion
order and quick access at the same time.
"""


class Node:
    """
    Doubly-linked list node to track cache entries.
    
    Each node stores a key-value pair plus pointers to previous/next nodes.
    This lets us move items to the front in O(1) time when they're accessed.
    """
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    Least Recently Used cache with fixed capacity.
    
    When capacity is reached, the least recently used item gets evicted.
    Both get() and put() count as "using" an item, moving it to the front.
    """
    
    def __init__(self, capacity):
        """
        Initialize the cache with a maximum capacity.
        
        Args:
            capacity: Maximum number of items to store
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.cache = {}  # Maps keys to nodes for O(1) lookup
        
        # Dummy head and tail make insertion/deletion simpler
        # No need to check for None pointers at the boundaries
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove(self, node):
        """
        Remove a node from the doubly-linked list.
        
        This doesn't delete from the hashmap, just unlinks from the list.
        """
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _add_to_front(self, node):
        """
        Add a node right after the head (most recently used position).
        
        This is where newly accessed or inserted items go.
        """
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
    
    def get(self, key):
        """
        Retrieve a value from the cache.
        
        If the key exists, move it to the front (mark as recently used).
        Returns -1 if key doesn't exist (could also return None, but going
        with LeetCode convention here).
        """
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        # Move to front since we just accessed it
        self._remove(node)
        self._add_to_front(node)
        return node.value
    
    def put(self, key, value):
        """
        Insert or update a key-value pair in the cache.
        
        If key already exists, update its value and move to front.
        If cache is at capacity, evict the least recently used item first.
        """
        if key in self.cache:
            # Update existing key
            node = self.cache[key]
            node.value = value
            self._remove(node)
            self._add_to_front(node)
        else:
            # Insert new key
            if len(self.cache) >= self.capacity:
                # Evict least recently used (right before tail)
                lru_node = self.tail.prev
                self._remove(lru_node)
                del self.cache[lru_node.key]
            
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_front(new_node)
    
    def __repr__(self):
        """String representation showing current cache state from MRU to LRU."""
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"{current.key}:{current.value}")
            current = current.next
        return f"LRUCache({' -> '.join(items)})"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a cache that holds max 3 items
    cache = LRUCache(3)
    
    print("Creating cache with capacity=3")
    print(f"Cache state: {cache}\n")
    
    # Add some items
    print("Adding items:")
    cache.put(1, "apple")
    print(f"  put(1, 'apple') -> {cache}")
    
    cache.put(2, "banana")
    print(f"  put(2, 'banana') -> {cache}")
    
    cache.put(3, "cherry")
    print(f"  put(3, 'cherry') -> {cache}\n")
    
    # Access item 1 (moves it to front)
    print("Accessing items:")
    result = cache.get(1)
    print(f"  get(1) = '{result}' -> {cache}")
    
    # Add a 4th item, should evict key 2 (LRU)
    print("\nAdding 4th item (capacity=3, so eviction happens):")
    cache.put(4, "date")
    print(f"  put(4, 'date') -> {cache}")
    print("  (key 2 was evicted as LRU)")
    
    # Try to get evicted item
    result = cache.get(2)
    print(f"\n  get(2) = {result} (not found)")
    
    # Update existing key
    print("\nUpdating existing key:")
    cache.put(3, "CHERRY!")
    print(f"  put(3, 'CHERRY!') -> {cache}")
    
    # Access pattern that moves items around
    print("\nAccess pattern to show LRU ordering:")
    cache.get(4)
    print(f"  get(4) -> {cache}")
    cache.get(1)
    print(f"  get(1) -> {cache}")
    
    cache.put(5, "elderberry")
    print(f"  put(5, 'elderberry') -> {cache}")
    print("  (key 3 was evicted)")