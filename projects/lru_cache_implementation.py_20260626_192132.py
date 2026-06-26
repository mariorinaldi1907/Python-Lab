"""
Date: 2026-06-26
Implemented an LRU cache with get/put in constant time because I wanted to understand how Python's functools.lru_cache actually works under the hood.
"""

"""
LRU Cache implementation using a doubly linked list + hashmap.
I always wondered how caching worked in real systems, so I built this
to understand the mechanics. Get and Put are both O(1) which is pretty neat.
"""


class Node:
    """
    Doubly linked list node to store cache entries.
    Each node holds a key-value pair plus pointers to prev/next.
    """
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    Least Recently Used cache with O(1) get and put operations.
    
    Uses a hashmap for fast lookups and a doubly linked list to track
    access order. Most recently used items are at the head, least recently
    used at the tail. When capacity is exceeded, we evict from the tail.
    """
    
    def __init__(self, capacity):
        """
        Initialize cache with given capacity.
        
        Args:
            capacity: Maximum number of items to store
        """
        self.capacity = capacity
        self.cache = {}  # Maps key -> Node
        
        # Dummy head and tail nodes make list operations cleaner
        # No need to check for None pointers everywhere
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove(self, node):
        """
        Remove a node from the doubly linked list.
        Used when we need to move a node to the front or evict it.
        """
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _add_to_head(self, node):
        """
        Add a node right after the head (most recently used position).
        Called whenever we access or add an item.
        """
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
    
    def get(self, key):
        """
        Get value for a key if it exists, otherwise return -1.
        Marks the key as recently used by moving it to the front.
        
        Args:
            key: The key to look up
            
        Returns:
            Value if found, -1 otherwise
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
        If at capacity, evicts the least recently used item.
        
        Args:
            key: The key to store
            value: The value to associate with the key
        """
        if key in self.cache:
            # Update existing key
            node = self.cache[key]
            node.value = value
            self._remove(node)
            self._add_to_head(node)
        else:
            # Add new key
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)
            
            # Check if we exceeded capacity
            if len(self.cache) > self.capacity:
                # Evict least recently used (node before tail)
                lru_node = self.tail.prev
                self._remove(lru_node)
                del self.cache[lru_node.key]
    
    def __str__(self):
        """String representation showing current cache state from MRU to LRU."""
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"{current.key}:{current.value}")
            current = current.next
        return f"[{' -> '.join(items)}]" if items else "[empty]"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a cache that holds 3 items max
    cache = LRUCache(capacity=3)
    
    print("Adding items to cache (capacity=3):")
    cache.put(1, "apple")
    print(f"  put(1, 'apple'): {cache}")
    
    cache.put(2, "banana")
    print(f"  put(2, 'banana'): {cache}")
    
    cache.put(3, "cherry")
    print(f"  put(3, 'cherry'): {cache}")
    
    print("\nAccessing key 1 (moves it to front):")
    result = cache.get(1)
    print(f"  get(1) = '{result}': {cache}")
    
    print("\nAdding key 4 (should evict key 2, the LRU):")
    cache.put(4, "date")
    print(f"  put(4, 'date'): {cache}")
    
    print("\nTrying to access evicted key 2:")
    result = cache.get(2)
    print(f"  get(2) = {result} (not found)")
    
    print("\nUpdating existing key 3:")
    cache.put(3, "cranberry")
    print(f"  put(3, 'cranberry'): {cache}")
    
    print("\nAdding key 5 (should evict key 1):")
    cache.put(5, "elderberry")
    print(f"  put(5, 'elderberry'): {cache}")
    
    print("\nFinal cache state (MRU -> LRU):")
    print(f"  {cache}")
    print("\nCache contents (as dict):", {k: cache.cache[k].value for k in cache.cache})