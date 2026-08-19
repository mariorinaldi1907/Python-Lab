"""
Date: 2026-08-19
Implemented a proper LRU cache with O(1) get/put operations using a doubly linked list and dictionary, because I was curious how eviction policies actually work in practice.
"""

"""
LRU (Least Recently Used) Cache Implementation

I wanted to understand how caching with eviction policies works, so I built this
from scratch. The trick is maintaining O(1) operations by combining a hashmap
with a doubly linked list — the hashmap gives fast lookups, and the linked list
tracks access order so we can evict the least recently used item quickly.
"""


class Node:
    """
    Doubly linked list node to track key-value pairs and their access order.
    """
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    LRU Cache that supports get and put operations in O(1) time.
    
    When capacity is reached, the least recently used item gets evicted.
    Recent usage means either getting or putting an item — both count as "using" it.
    """
    
    def __init__(self, capacity):
        """
        Initialize the cache with a given capacity.
        
        Args:
            capacity: Maximum number of items the cache can hold
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.cache = {}  # Maps keys to nodes for O(1) lookup
        
        # Dummy head and tail nodes make list operations cleaner
        # Real nodes live between head and tail
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove(self, node):
        """
        Remove a node from the doubly linked list.
        
        This doesn't delete from the cache dict, just unlinks from the list.
        """
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _add_to_front(self, node):
        """
        Add a node right after the head (most recently used position).
        
        The front of the list represents "recently used" and back represents "old".
        """
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
    
    def get(self, key):
        """
        Get value for a key, marking it as recently used.
        
        Args:
            key: The key to look up
            
        Returns:
            The value if found, -1 if not in cache
        """
        if key not in self.cache:
            return -1
        
        # Move this node to the front since we just accessed it
        node = self.cache[key]
        self._remove(node)
        self._add_to_front(node)
        return node.value
    
    def put(self, key, value):
        """
        Put a key-value pair in the cache.
        
        If key exists, update its value and move to front.
        If cache is full, evict the least recently used item first.
        
        Args:
            key: The key to store
            value: The value to associate with the key
        """
        if key in self.cache:
            # Update existing key: remove old node, will add new one at front
            self._remove(self.cache[key])
        
        # Create new node and add to front
        new_node = Node(key, value)
        self._add_to_front(new_node)
        self.cache[key] = new_node
        
        # Evict LRU item if we exceeded capacity
        if len(self.cache) > self.capacity:
            # LRU item is right before tail
            lru_node = self.tail.prev
            self._remove(lru_node)
            del self.cache[lru_node.key]
    
    def __str__(self):
        """String representation showing cache contents from MRU to LRU."""
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"{current.key}:{current.value}")
            current = current.next
        return f"LRUCache[{' -> '.join(items)}]"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a cache with capacity of 3
    cache = LRUCache(3)
    
    print("Created cache with capacity 3\n")
    
    # Add some items
    print("Adding items...")
    cache.put(1, "one")
    print(f"put(1, 'one') -> {cache}")
    
    cache.put(2, "two")
    print(f"put(2, 'two') -> {cache}")
    
    cache.put(3, "three")
    print(f"put(3, 'three') -> {cache}")
    
    print("\n--- Cache is now full ---\n")
    
    # Access an item to make it recently used
    value = cache.get(1)
    print(f"get(1) -> '{value}'")
    print(f"Cache after access: {cache}")
    print("(Notice key 1 moved to front)\n")
    
    # Add a new item, which should evict key 2 (least recently used)
    cache.put(4, "four")
    print(f"put(4, 'four') -> {cache}")
    print("(Key 2 was evicted since it was LRU)\n")
    
    # Try to get the evicted item
    value = cache.get(2)
    print(f"get(2) -> {value} (not found, returns -1)\n")
    
    # Update an existing key
    cache.put(3, "THREE_UPDATED")
    print(f"put(3, 'THREE_UPDATED') -> {cache}")
    print("(Key 3 moved to front with new value)\n")
    
    # Add one more item to trigger another eviction
    cache.put(5, "five")
    print(f"put(5, 'five') -> {cache}")
    print("(Key 1 was evicted — it was LRU after key 3 was updated)")