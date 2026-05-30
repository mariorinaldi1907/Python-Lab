"""
Date: 2026-05-30
Implemented an LRU (Least Recently Used) cache with O(1) get/put operations using a dictionary and doubly linked list — helps me understand caching strategies better.
"""

"""
LRU Cache Implementation
========================
A proper LRU cache that evicts the least recently used item when capacity is reached.
Uses a doubly linked list for O(1) removals and a hashmap for O(1) lookups.
"""


class Node:
    """Doubly linked list node to maintain ordering of cache entries."""
    
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    LRU Cache with O(1) get and put operations.
    
    The strategy here is:
    - Hash map gives us O(1) key lookups
    - Doubly linked list lets us move nodes to front (mark as recently used) in O(1)
    - When capacity is full, we evict the tail (least recently used)
    """
    
    def __init__(self, capacity):
        """
        Initialize the cache with a fixed capacity.
        
        Args:
            capacity: Maximum number of items the cache can hold
        """
        self.capacity = capacity
        self.cache = {}  # key -> Node mapping
        
        # Dummy head and tail make insertion/deletion logic cleaner
        # No need to handle edge cases when list is empty
        self.head = Node(0, 0)  # Most recently used
        self.tail = Node(0, 0)  # Least recently used
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove(self, node):
        """
        Remove a node from the doubly linked list.
        
        This doesn't delete from the hashmap, just unlinks from the list.
        """
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _add_to_head(self, node):
        """
        Add a node right after the head (marks it as most recently used).
        """
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
    
    def get(self, key):
        """
        Get value from cache and mark it as recently used.
        
        Args:
            key: The key to look up
            
        Returns:
            The value if found, -1 otherwise
        """
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        # Move to front since we just accessed it
        self._remove(node)
        self._add_to_head(node)
        return node.value
    
    def put(self, key, value):
        """
        Insert or update a key-value pair in the cache.
        
        If key exists, update it and mark as recently used.
        If cache is full, evict the LRU item first.
        
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
                # Evict LRU (tail's previous node)
                lru = self.tail.prev
                self._remove(lru)
                del self.cache[lru.key]
            
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)
    
    def display(self):
        """
        Display current cache state from most to least recently used.
        Useful for debugging and demonstration.
        """
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"{current.key}:{current.value}")
            current = current.next
        return " -> ".join(items) if items else "(empty)"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a cache that holds 3 items
    cache = LRUCache(3)
    
    print("Capacity: 3")
    print("Inserting key-value pairs...\n")
    
    cache.put(1, "one")
    print(f"put(1, 'one')   -> {cache.display()}")
    
    cache.put(2, "two")
    print(f"put(2, 'two')   -> {cache.display()}")
    
    cache.put(3, "three")
    print(f"put(3, 'three') -> {cache.display()}")
    
    print(f"\nget(2) = {cache.get(2)}")
    print(f"Cache after get(2): {cache.display()}")
    print("(Notice 2 moved to front)\n")
    
    cache.put(4, "four")
    print(f"put(4, 'four')  -> {cache.display()}")
    print("(1 was evicted — it was least recently used)\n")
    
    print(f"get(1) = {cache.get(1)} (not found, was evicted)")
    print(f"get(3) = {cache.get(3)}")
    print(f"Cache after get(3): {cache.display()}\n")
    
    cache.put(5, "five")
    print(f"put(5, 'five')  -> {cache.display()}")
    print("(2 was evicted this time)\n")
    
    # Update an existing key
    cache.put(3, "THREE")
    print(f"put(3, 'THREE') -> {cache.display()}")
    print("(Updated value and moved to front)")