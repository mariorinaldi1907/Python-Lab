"""
Date: 2026-07-27
Built an LRU cache from scratch using a doubly linked list for O(1) eviction and a hashmap for O(1) lookups — wanted to understand how caching works under the hood.
"""

"""
LRU Cache Implementation
========================
Classic interview question that I wanted to implement properly.
Using a doubly linked list + hashmap combo for O(1) get/put operations.
"""


class Node:
    """Doubly linked list node to maintain order of cache access."""
    
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    Least Recently Used (LRU) Cache implementation.
    
    When the cache is full, removes the least recently used item.
    Both get and put operations run in O(1) time.
    """
    
    def __init__(self, capacity):
        """
        Initialize the LRU cache with a fixed capacity.
        
        Args:
            capacity: Maximum number of items the cache can hold
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.cache = {}  # maps key -> node
        
        # Dummy head and tail nodes make insertion/deletion logic cleaner
        # Real nodes will be between head and tail
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove(self, node):
        """
        Remove a node from the doubly linked list.
        
        This is used when we need to move a node to the front (most recent)
        or when we evict the least recently used node.
        """
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _add_to_front(self, node):
        """
        Add a node right after the head (most recently used position).
        
        The front of the list represents the most recently accessed items.
        """
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
    
    def get(self, key):
        """
        Get the value of a key if it exists in the cache.
        
        Marks the key as recently used by moving it to the front.
        
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
        self._add_to_front(node)
        
        return node.value
    
    def put(self, key, value):
        """
        Insert or update a key-value pair in the cache.
        
        If the key exists, updates its value and marks it as recently used.
        If the cache is full, evicts the least recently used item first.
        
        Args:
            key: The key to insert/update
            value: The value to associate with the key
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
                # Evict least recently used (node right before tail)
                lru_node = self.tail.prev
                self._remove(lru_node)
                del self.cache[lru_node.key]
            
            # Add new node
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_front(new_node)
    
    def display(self):
        """
        Display the current state of the cache from most to least recent.
        
        Useful for debugging and understanding what's happening.
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
    
    print("Creating cache with capacity 3\n")
    
    print("Operations:")
    print("-" * 40)
    
    cache.put(1, "apple")
    print(f"put(1, 'apple')  -> {cache.display()}")
    
    cache.put(2, "banana")
    print(f"put(2, 'banana') -> {cache.display()}")
    
    cache.put(3, "cherry")
    print(f"put(3, 'cherry') -> {cache.display()}")
    
    print()
    result = cache.get(1)
    print(f"get(1)           -> {result}")
    print(f"Cache state      -> {cache.display()}")
    print("(Notice 1 moved to front)\n")
    
    cache.put(4, "date")
    print(f"put(4, 'date')   -> {cache.display()}")
    print("(2 was evicted - it was least recently used)\n")
    
    result = cache.get(2)
    print(f"get(2)           -> {result} (not found)")
    
    result = cache.get(3)
    print(f"get(3)           -> {result}")
    print(f"Cache state      -> {cache.display()}\n")
    
    cache.put(5, "elderberry")
    print(f"put(5, 'elderberry') -> {cache.display()}")
    print("(4 was evicted)")