"""
Date: 2026-07-10
Built an LRU cache to solidify my understanding of combined data structures — uses O(1) lookups and evictions by combining a hashmap with a doubly linked list.
"""

"""
LRU Cache Implementation
========================
A least-recently-used cache that evicts the oldest item when capacity is reached.
Uses a doubly linked list for O(1) move-to-front and eviction, plus a hashmap for O(1) lookups.
"""


class Node:
    """
    Doubly linked list node to store key-value pairs.
    Need to store the key here too so we can delete from the hashmap during eviction.
    """
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    LRU Cache with O(1) get and put operations.
    
    The doubly linked list maintains access order: most recent at head, least recent at tail.
    The hashmap provides direct access to nodes without traversing the list.
    """
    
    def __init__(self, capacity):
        """
        Initialize cache with given capacity.
        
        Args:
            capacity: Maximum number of items the cache can hold
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.cache = {}  # Maps keys to nodes
        
        # Using sentinel nodes to avoid null checks when adding/removing
        # head.next is the most recently used, tail.prev is the least recently used
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove(self, node):
        """
        Remove a node from the doubly linked list.
        This doesn't delete it from the hashmap, just unlinks it.
        """
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _add_to_head(self, node):
        """
        Add a node right after the head (most recently used position).
        """
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
    
    def get(self, key):
        """
        Get value for key, moving it to most recently used position.
        
        Args:
            key: Key to look up
            
        Returns:
            Value associated with key, or -1 if not found
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
        Insert or update a key-value pair.
        If at capacity, evict the least recently used item first.
        
        Args:
            key: Key to insert/update
            value: Value to store
        """
        if key in self.cache:
            # Update existing key: remove old node, will add new one at head
            self._remove(self.cache[key])
        
        new_node = Node(key, value)
        self.cache[key] = new_node
        self._add_to_head(new_node)
        
        # Check if we exceeded capacity
        if len(self.cache) > self.capacity:
            # Evict the LRU item (right before tail)
            lru_node = self.tail.prev
            self._remove(lru_node)
            del self.cache[lru_node.key]
    
    def display(self):
        """
        Display current cache contents from most to least recently used.
        Mainly for debugging and demonstration.
        """
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"{current.key}:{current.value}")
            current = current.next
        return " -> ".join(items) if items else "(empty)"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a cache with capacity of 3
    cache = LRUCache(3)
    
    print("Creating LRU cache with capacity 3")
    print(f"Cache: {cache.display()}\n")
    
    print("put(1, 'apple')")
    cache.put(1, "apple")
    print(f"Cache: {cache.display()}\n")
    
    print("put(2, 'banana')")
    cache.put(2, "banana")
    print(f"Cache: {cache.display()}\n")
    
    print("put(3, 'cherry')")
    cache.put(3, "cherry")
    print(f"Cache: {cache.display()}\n")
    
    print("get(1) ->", cache.get(1))
    print(f"Cache (1 moved to front): {cache.display()}\n")
    
    print("put(4, 'date') — this should evict key 2 (LRU)")
    cache.put(4, "date")
    print(f"Cache: {cache.display()}\n")
    
    print("get(2) ->", cache.get(2), "(should be -1, was evicted)")
    print(f"Cache: {cache.display()}\n")
    
    print("get(3) ->", cache.get(3))
    print(f"Cache (3 moved to front): {cache.display()}\n")
    
    print("put(5, 'elderberry') — this should evict key 4 (LRU)")
    cache.put(5, "elderberry")
    print(f"Cache: {cache.display()}\n")
    
    print("Update existing key: put(1, 'avocado')")
    cache.put(1, "avocado")
    print(f"Cache: {cache.display()}\n")
    
    print("Final gets:")
    print(f"get(1) -> {cache.get(1)}")
    print(f"get(3) -> {cache.get(3)}")
    print(f"get(5) -> {cache.get(5)}")
    print(f"get(4) -> {cache.get(4)} (evicted)")