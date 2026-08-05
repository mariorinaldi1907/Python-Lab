"""
Date: 2026-08-05
Implemented a proper LRU cache with O(1) get/put operations using a dictionary and doubly linked list — wanted to understand how @lru_cache actually works under the hood.
"""

"""
LRU Cache implementation using a hashmap and doubly linked list.
This gives us O(1) access and O(1) eviction, which is the whole point.
"""

class Node:
    """
    Doubly linked list node to track access order.
    Most recently used is at the head, least recently used at the tail.
    """
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    LRU Cache that evicts the least recently used item when capacity is exceeded.
    
    The trick here is maintaining both fast lookup (dict) and fast eviction (linked list).
    Every access moves the item to the front, and when we're full, we drop from the back.
    """
    
    def __init__(self, capacity):
        """
        Initialize the cache with a fixed capacity.
        
        Args:
            capacity: Maximum number of items to store
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.cache = {}  # key -> Node mapping for O(1) lookup
        
        # Dummy head and tail make list operations way cleaner
        # No need to check for None everywhere
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove(self, node):
        """
        Remove a node from the doubly linked list.
        This doesn't delete from cache dict, just unlinks from the list.
        """
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _add_to_front(self, node):
        """
        Add a node right after the head (most recently used position).
        """
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
    
    def get(self, key):
        """
        Retrieve a value from the cache.
        
        Args:
            key: The key to lookup
            
        Returns:
            The value if found, -1 otherwise (following LeetCode convention)
        """
        if key not in self.cache:
            return -1
        
        # Move to front since we just accessed it
        node = self.cache[key]
        self._remove(node)
        self._add_to_front(node)
        return node.value
    
    def put(self, key, value):
        """
        Insert or update a key-value pair.
        
        Args:
            key: The key to insert/update
            value: The value to store
        """
        # If key exists, update it and move to front
        if key in self.cache:
            self._remove(self.cache[key])
        
        # Create new node and add to front
        new_node = Node(key, value)
        self._add_to_front(new_node)
        self.cache[key] = new_node
        
        # Evict LRU item if we exceeded capacity
        if len(self.cache) > self.capacity:
            # The least recently used is right before tail
            lru = self.tail.prev
            self._remove(lru)
            del self.cache[lru.key]
    
    def __str__(self):
        """
        String representation showing cache contents in access order.
        Useful for debugging and demos.
        """
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"{current.key}:{current.value}")
            current = current.next
        return f"LRUCache({len(self.cache)}/{self.capacity}) [{' -> '.join(items)}]"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a cache that holds 3 items
    cache = LRUCache(3)
    
    print("Creating cache with capacity 3")
    print(f"Initial state: {cache}\n")
    
    # Add some items
    print("Adding items...")
    cache.put(1, "apple")
    print(f"put(1, 'apple'): {cache}")
    
    cache.put(2, "banana")
    print(f"put(2, 'banana'): {cache}")
    
    cache.put(3, "cherry")
    print(f"put(3, 'cherry'): {cache}\n")
    
    # Access item 1 (moves to front)
    print("Accessing item 1...")
    value = cache.get(1)
    print(f"get(1) = '{value}': {cache}\n")
    
    # Add a 4th item - this should evict key 2 (LRU)
    print("Adding 4th item (should evict key 2)...")
    cache.put(4, "date")
    print(f"put(4, 'date'): {cache}\n")
    
    # Try to get the evicted item
    print("Trying to access evicted item 2...")
    value = cache.get(2)
    print(f"get(2) = {value} (expected -1)\n")
    
    # Update existing key
    print("Updating existing key 3...")
    cache.put(3, "coconut")
    print(f"put(3, 'coconut'): {cache}\n")
    
    # Access pattern demonstration
    print("Access pattern test:")
    cache.get(4)
    print(f"After get(4): {cache}")
    cache.get(1)
    print(f"After get(1): {cache}")
    cache.put(5, "elderberry")
    print(f"After put(5, 'elderberry'): {cache}")
    print("\nNotice how key 3 was evicted (it was LRU)")