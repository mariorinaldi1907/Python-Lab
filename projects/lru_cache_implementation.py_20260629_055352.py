"""
Date: 2026-06-29
Implemented an LRU cache with O(1) get/put operations because I wanted to really understand how Python's functools.lru_cache works under the hood.
"""

"""
LRU (Least Recently Used) Cache Implementation

Uses a combination of a hash map and doubly linked list to achieve O(1)
time complexity for both get and put operations. The hash map provides
fast lookups, while the doubly linked list maintains insertion order.
"""


class Node:
    """
    Node for the doubly linked list.
    Each node stores a key-value pair plus pointers to prev/next nodes.
    """
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    LRU Cache with O(1) get and put operations.
    
    The cache evicts the least recently used item when capacity is exceeded.
    Uses a dummy head and tail to simplify edge cases when adding/removing nodes.
    """
    
    def __init__(self, capacity):
        """
        Initialize the LRU cache with a given capacity.
        
        Args:
            capacity: Maximum number of items the cache can hold
        """
        self.capacity = capacity
        self.cache = {}  # Maps keys to nodes
        
        # Dummy head and tail make list operations cleaner
        # Most recent items are near head, least recent near tail
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove(self, node):
        """
        Remove a node from the doubly linked list.
        Doesn't delete from hash map — just unlinks from the list.
        """
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _add_to_head(self, node):
        """
        Add a node right after the dummy head.
        This marks it as the most recently used item.
        """
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
    
    def get(self, key):
        """
        Retrieve a value from the cache.
        
        Args:
            key: The key to look up
            
        Returns:
            The value if found, -1 otherwise
        """
        if key not in self.cache:
            return -1
        
        # Move accessed node to head (mark as recently used)
        node = self.cache[key]
        self._remove(node)
        self._add_to_head(node)
        
        return node.value
    
    def put(self, key, value):
        """
        Insert or update a key-value pair in the cache.
        
        If the key exists, update its value and mark as recently used.
        If cache is at capacity, evict the least recently used item first.
        
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
            # Insert new key
            if len(self.cache) >= self.capacity:
                # Evict least recently used (node before tail)
                lru_node = self.tail.prev
                self._remove(lru_node)
                del self.cache[lru_node.key]
            
            # Add new node
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)
    
    def __str__(self):
        """String representation showing cache contents from most to least recent."""
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
    
    # Insert some items
    print("Inserting items:")
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
    
    # This will evict key 2 (least recently used)
    print(f"\nAdding key 4 (capacity exceeded, will evict LRU):")
    cache.put(4, "four")
    print(f"  put(4, 'four') -> {cache}")
    
    # Key 2 should be gone now
    print(f"\nTrying to access evicted key 2:")
    result = cache.get(2)
    print(f"  get(2) = {result} (not found)")
    
    # Update existing key
    print(f"\nUpdating key 3:")
    cache.put(3, "THREE")
    print(f"  put(3, 'THREE') -> {cache}")
    
    # Access pattern demonstration
    print(f"\nAccess pattern test:")
    cache.get(4)
    print(f"  get(4) -> {cache}")
    cache.get(1)
    print(f"  get(1) -> {cache}")
    
    # Now 3 is LRU, so it gets evicted
    cache.put(5, "five")
    print(f"  put(5, 'five') -> {cache}")
    
    print(f"\nFinal cache state: {cache}")