"""
Date: 2026-08-13
Built an LRU cache with O(1) get/put operations to finally understand how they actually work under the hood.
"""

"""
LRU Cache implementation using a doubly linked list + hashmap.
I wanted to understand how this works without just using @lru_cache decorator.
The combo of hashmap for O(1) lookup + doubly linked list for O(1) reordering
is what makes this efficient.
"""


class Node:
    """
    Doubly linked list node to store cache entries.
    Prev/next pointers let us reorder quickly when items are accessed.
    """
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    Least Recently Used cache with O(1) get and put operations.
    
    The head is the most recently used, tail is least recently used.
    When capacity is hit, we evict from the tail.
    """
    
    def __init__(self, capacity):
        """
        Initialize cache with given capacity.
        Using sentinel nodes (dummy head/tail) to avoid edge case checks.
        """
        self.capacity = capacity
        self.cache = {}  # maps key -> Node
        
        # Dummy head and tail make list operations cleaner
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove(self, node):
        """
        Remove a node from the doubly linked list.
        This doesn't delete from cache dict, just unlinks it.
        """
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _add_to_head(self, node):
        """
        Add a node right after head (most recently used position).
        """
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
    
    def get(self, key):
        """
        Get value for key, moving it to front since it was just accessed.
        Returns -1 if key doesn't exist (could raise KeyError instead).
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
        Add or update key-value pair.
        If at capacity, evict least recently used item first.
        """
        if key in self.cache:
            # Update existing key - remove old node
            self._remove(self.cache[key])
        
        new_node = Node(key, value)
        self.cache[key] = new_node
        self._add_to_head(new_node)
        
        if len(self.cache) > self.capacity:
            # Evict least recently used (tail.prev)
            lru_node = self.tail.prev
            self._remove(lru_node)
            del self.cache[lru_node.key]
    
    def display(self):
        """
        Debug helper to see current cache state from MRU to LRU.
        """
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"{current.key}:{current.value}")
            current = current.next
        return " -> ".join(items) if items else "(empty)"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create cache with capacity of 3
    cache = LRUCache(3)
    
    print("Initializing cache with capacity=3\n")
    
    print("Adding items...")
    cache.put(1, "one")
    print(f"put(1, 'one') -> {cache.display()}")
    
    cache.put(2, "two")
    print(f"put(2, 'two') -> {cache.display()}")
    
    cache.put(3, "three")
    print(f"put(3, 'three') -> {cache.display()}")
    
    print("\nAccessing key 1 (should move it to front)...")
    val = cache.get(1)
    print(f"get(1) = '{val}' -> {cache.display()}")
    
    print("\nAdding key 4 (should evict key 2, the LRU)...")
    cache.put(4, "four")
    print(f"put(4, 'four') -> {cache.display()}")
    
    print("\nTrying to access evicted key 2...")
    val = cache.get(2)
    print(f"get(2) = {val} (not found)")
    
    print("\nUpdating existing key 3...")
    cache.put(3, "THREE")
    print(f"put(3, 'THREE') -> {cache.display()}")
    
    print("\nAccessing keys to change order...")
    cache.get(4)
    print(f"get(4) -> {cache.display()}")
    cache.get(3)
    print(f"get(3) -> {cache.display()}")
    
    print("\nAdding key 5 (should evict key 1 now)...")
    cache.put(5, "five")
    print(f"put(5, 'five') -> {cache.display()}")
    
    print("\n=== Final cache state ===")
    print(f"Cache contents (MRU -> LRU): {cache.display()}")
    print(f"Cache size: {len(cache.cache)}/{cache.capacity}")