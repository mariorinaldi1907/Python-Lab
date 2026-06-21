"""
Date: 2026-06-21
Built an LRU (Least Recently Used) cache to understand the underlying mechanics of eviction policies and O(1) access patterns.
"""

"""
LRU Cache implementation using a doubly linked list + hashmap.

I wanted to really understand how @functools.lru_cache works under the hood,
so I built this from scratch. The key insight is combining a hashmap (for O(1) lookups)
with a doubly linked list (for O(1) reordering when items are accessed/added).
"""


class Node:
    """
    Doubly linked list node to maintain access order.
    Most recently used items move to the head, least recently used fall to the tail.
    """
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    Least Recently Used (LRU) cache with O(1) get and put operations.
    
    The cache evicts the least recently used item when capacity is exceeded.
    Uses a hashmap for fast lookups and a doubly linked list for maintaining order.
    """
    
    def __init__(self, capacity):
        """
        Initialize the LRU cache with a given capacity.
        
        Args:
            capacity: Maximum number of items the cache can hold
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.cache = {}  # Maps keys to nodes
        
        # Dummy head and tail make insertion/deletion easier (no edge case checks)
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove(self, node):
        """
        Remove a node from the doubly linked list.
        This doesn't delete from the hashmap, just unlinks it from the list.
        """
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _add_to_head(self, node):
        """
        Add a node right after the dummy head (most recently used position).
        """
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
    
    def get(self, key):
        """
        Retrieve a value from the cache.
        
        If the key exists, move it to the head (mark as recently used).
        
        Args:
            key: The key to look up
            
        Returns:
            The value associated with the key, or -1 if not found
        """
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        # Move to head since we just accessed it
        self._remove(node)
        self._add_to_head(node)
        return node.value
    
    def put(self, key, value):
        """
        Insert or update a key-value pair in the cache.
        
        If key exists, update its value and move to head.
        If key is new and cache is full, evict the LRU item (at tail).
        
        Args:
            key: The key to insert/update
            value: The value to store
        """
        if key in self.cache:
            # Update existing key
            node = self.cache[key]
            node.value = value
            self._remove(node)
            self._add_to_head(node)
        else:
            # New key - check if we need to evict
            if len(self.cache) >= self.capacity:
                # Remove least recently used (node before tail)
                lru_node = self.tail.prev
                self._remove(lru_node)
                del self.cache[lru_node.key]
            
            # Add new node
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)
    
    def display(self):
        """
        Display the current cache state (from most to least recently used).
        Useful for debugging and understanding the internal ordering.
        """
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"{current.key}:{current.value}")
            current = current.next
        return " -> ".join(items) if items else "(empty)"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a cache with capacity 3
    cache = LRUCache(3)
    
    print("Creating cache with capacity 3")
    print(f"Cache state: {cache.display()}\n")
    
    # Add some items
    print("Adding items: (1, 'one'), (2, 'two'), (3, 'three')")
    cache.put(1, "one")
    cache.put(2, "two")
    cache.put(3, "three")
    print(f"Cache state: {cache.display()}\n")
    
    # Access an item (should move to front)
    print("Accessing key 1")
    result = cache.get(1)
    print(f"Got: {result}")
    print(f"Cache state: {cache.display()}\n")
    
    # Add another item (should evict key 2, the LRU)
    print("Adding (4, 'four') - this should evict key 2")
    cache.put(4, "four")
    print(f"Cache state: {cache.display()}\n")
    
    # Try to get evicted item
    print("Trying to access key 2 (should be evicted)")
    result = cache.get(2)
    print(f"Got: {result}")
    print(f"Cache state: {cache.display()}\n")
    
    # Update existing item
    print("Updating key 3 to 'THREE'")
    cache.put(3, "THREE")
    print(f"Cache state: {cache.display()}\n")
    
    # Show final access pattern
    print("Final accesses: get(4), get(1), get(3)")
    print(f"get(4) = {cache.get(4)}")
    print(f"get(1) = {cache.get(1)}")
    print(f"get(3) = {cache.get(3)}")
    print(f"Final cache state: {cache.display()}")
```