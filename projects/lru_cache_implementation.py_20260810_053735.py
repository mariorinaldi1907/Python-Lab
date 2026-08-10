"""
Date: 2026-08-10
Implemented a fully functional LRU cache with O(1) get/put operations using a doubly linked list and dictionary, because I was curious how eviction policies actually work in production systems.
"""

"""
LRU Cache implementation using doubly linked list + hashmap.
I wanted to understand how caching works at a low level, especially
the eviction strategy that keeps recently used items and drops old ones.
"""


class Node:
    """
    Doubly linked list node to maintain access order.
    Each node stores a key-value pair plus pointers to prev/next.
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
        Initialize the cache with a given capacity.
        
        Args:
            capacity: Maximum number of items the cache can hold
        """
        self.capacity = capacity
        self.cache = {}  # key -> Node mapping for O(1) lookup
        
        # Dummy head and tail nodes make insertion/removal cleaner
        # (no need to check for None pointers at boundaries)
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove(self, node):
        """
        Remove a node from the doubly linked list.
        Doesn't delete from hashmap, just unlinks from the list.
        """
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _add_to_head(self, node):
        """
        Add a node right after the dummy head (most recently used position).
        This is called whenever we access or insert an item.
        """
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
    
    def _move_to_head(self, node):
        """
        Move an existing node to the head (mark as recently used).
        Used when we access an item that's already in the cache.
        """
        self._remove(node)
        self._add_to_head(node)
    
    def _evict_tail(self):
        """
        Remove the least recently used item (node before dummy tail).
        Returns the evicted node so we can remove it from the hashmap too.
        """
        lru_node = self.tail.prev
        self._remove(lru_node)
        return lru_node
    
    def get(self, key):
        """
        Retrieve a value from the cache.
        
        Args:
            key: The key to look up
            
        Returns:
            The value if found, -1 otherwise (matching LeetCode convention)
        """
        if key not in self.cache:
            return -1
        
        # Move to head since we just accessed it
        node = self.cache[key]
        self._move_to_head(node)
        return node.value
    
    def put(self, key, value):
        """
        Insert or update a key-value pair in the cache.
        
        If the key exists, update its value and mark as recently used.
        If it's new and we're at capacity, evict the LRU item first.
        
        Args:
            key: The key to insert/update
            value: The value to store
        """
        if key in self.cache:
            # Update existing key
            node = self.cache[key]
            node.value = value
            self._move_to_head(node)
        else:
            # Insert new key
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)
            
            # Check if we exceeded capacity
            if len(self.cache) > self.capacity:
                # Evict least recently used
                lru_node = self._evict_tail()
                del self.cache[lru_node.key]
    
    def display(self):
        """
        Debug helper to show current cache state from most to least recent.
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
    cache = LRUCache(capacity=3)
    
    print("Creating cache with capacity=3")
    print(f"Cache state: {cache.display()}\n")
    
    # Add some items
    print("Put (1, 'apple')")
    cache.put(1, "apple")
    print(f"Cache state: {cache.display()}\n")
    
    print("Put (2, 'banana')")
    cache.put(2, "banana")
    print(f"Cache state: {cache.display()}\n")
    
    print("Put (3, 'cherry')")
    cache.put(3, "cherry")
    print(f"Cache state: {cache.display()}\n")
    
    # Access an item (moves it to front)
    print("Get key=1")
    result = cache.get(1)
    print(f"Result: {result}")
    print(f"Cache state: {cache.display()} (1 moved to front)\n")
    
    # Add another item — this should evict key=2 (least recently used)
    print("Put (4, 'date') — capacity exceeded, should evict key=2")
    cache.put(4, "date")
    print(f"Cache state: {cache.display()}\n")
    
    # Try to get the evicted item
    print("Get key=2 (should be evicted)")
    result = cache.get(2)
    print(f"Result: {result} (returns -1, item was evicted)\n")
    
    # Update an existing key
    print("Put (1, 'apricot') — updating existing key")
    cache.put(1, "apricot")
    print(f"Cache state: {cache.display()}\n")
    
    print("Get key=3")
    result = cache.get(3)
    print(f"Result: {result}")
    print(f"Cache state: {cache.display()}\n")