"""
Date: 2026-08-13
Built a proper LRU cache with O(1) get/put operations to really understand how caching eviction policies work under the hood.
"""

"""
LRU Cache implementation using a doubly linked list + dictionary.
I wanted to understand how @lru_cache actually works internally, so I built this.
The trick is combining a hashmap (for O(1) lookups) with a DLL (for O(1) reordering).
"""


class Node:
    """
    Doubly linked list node to track access order.
    Most recently used items go to the front, least recently used fall to the back.
    """
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    Least Recently Used cache with O(1) get and put operations.
    
    When capacity is reached, the least recently accessed item gets evicted.
    Uses a doubly linked list to maintain access order and a dict for fast lookups.
    """
    
    def __init__(self, capacity):
        """
        Initialize the cache with a fixed capacity.
        
        Args:
            capacity: Maximum number of items to store before evicting
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.cache = {}  # key -> Node mapping for O(1) access
        
        # Dummy head and tail make insertion/deletion cleaner (no null checks)
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove(self, node):
        """
        Remove a node from the doubly linked list.
        This doesn't delete from the cache dict, just unlinks from the order tracking.
        """
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _add_to_front(self, node):
        """
        Add a node right after the head (most recently used position).
        Called when an item is accessed or newly inserted.
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
            The cached value, or -1 if not found
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
        Insert or update a key-value pair in the cache.
        
        If at capacity, evicts the least recently used item first.
        
        Args:
            key: The key to store
            value: The value to associate with the key
        """
        # If key already exists, update it and move to front
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self._remove(node)
            self._add_to_front(node)
            return
        
        # New key: create node and add to front
        new_node = Node(key, value)
        self.cache[key] = new_node
        self._add_to_front(new_node)
        
        # Check if we exceeded capacity
        if len(self.cache) > self.capacity:
            # Evict the LRU item (right before tail)
            lru = self.tail.prev
            self._remove(lru)
            del self.cache[lru.key]
    
    def display(self):
        """
        Display the current cache state in order (most to least recent).
        Useful for debugging and demos.
        """
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"{current.key}:{current.value}")
            current = current.next
        return " -> ".join(items) if items else "(empty)"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a cache that holds max 3 items
    cache = LRUCache(3)
    
    print("Creating cache with capacity 3")
    print(f"Cache state: {cache.display()}\n")
    
    print("Adding items: put(1, 'apple'), put(2, 'banana'), put(3, 'cherry')")
    cache.put(1, "apple")
    cache.put(2, "banana")
    cache.put(3, "cherry")
    print(f"Cache state: {cache.display()}\n")
    
    print("Accessing key 1 (moves it to front)")
    result = cache.get(1)
    print(f"get(1) = {result}")
    print(f"Cache state: {cache.display()}\n")
    
    print("Adding key 4 (should evict key 2, the LRU)")
    cache.put(4, "date")
    print(f"Cache state: {cache.display()}\n")
    
    print("Trying to get evicted key 2")
    result = cache.get(2)
    print(f"get(2) = {result} (not found!)")
    print(f"Cache state: {cache.display()}\n")
    
    print("Updating key 3 with new value")
    cache.put(3, "coconut")
    print(f"Cache state: {cache.display()}\n")
    
    print("Adding key 5 (should evict key 1, now the LRU)")
    cache.put(5, "elderberry")
    print(f"Cache state: {cache.display()}\n")
    
    print("Final verification:")
    print(f"get(1) = {cache.get(1)} (evicted)")
    print(f"get(3) = {cache.get(3)} (exists, moved to front)")
    print(f"get(4) = {cache.get(4)} (exists, moved to front)")
    print(f"get(5) = {cache.get(5)} (exists, moved to front)")
    print(f"\nFinal cache state: {cache.display()}")
```