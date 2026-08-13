"""
Date: 2026-08-13
Implemented an LRU (Least Recently Used) cache to understand how constant-time eviction actually works — uses a doubly-linked list for ordering and a dict for O(1) lookups.
"""

"""
LRU Cache implementation using doubly-linked list + hashmap.

I wanted to understand how caching works at a fundamental level, so I built this
instead of just using functools.lru_cache. The trick is maintaining insertion
order while still getting O(1) get/put operations.
"""


class Node:
    """
    Doubly-linked list node. Stores key so we can remove from hashmap during eviction.
    """
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    Least Recently Used cache with fixed capacity.
    
    When capacity is reached, evicts the least recently accessed item.
    Both get() and put() count as "using" an item, moving it to the front.
    """
    
    def __init__(self, capacity):
        """
        Initialize cache with given capacity.
        
        Args:
            capacity: Maximum number of items to store
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.cache = {}  # key -> Node mapping for O(1) lookup
        
        # Dummy head/tail nodes make insertion/deletion logic cleaner
        # No edge cases when list is empty or has one element
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove(self, node):
        """
        Remove a node from the doubly-linked list.
        Doesn't remove from hashmap — that's the caller's job.
        """
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _add_to_front(self, node):
        """
        Add node right after head (most recently used position).
        """
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
    
    def get(self, key):
        """
        Retrieve value for key, marking it as recently used.
        
        Args:
            key: The key to look up
            
        Returns:
            The value if found, None otherwise
        """
        if key not in self.cache:
            return None
        
        node = self.cache[key]
        # Move to front since it was just accessed
        self._remove(node)
        self._add_to_front(node)
        return node.value
    
    def put(self, key, value):
        """
        Insert or update a key-value pair.
        
        If key exists, updates value and moves to front.
        If cache is full, evicts least recently used item first.
        
        Args:
            key: The key to insert/update
            value: The value to store
        """
        if key in self.cache:
            # Update existing key
            self._remove(self.cache[key])
            del self.cache[key]
        
        # Create new node and add to front
        new_node = Node(key, value)
        self._add_to_front(new_node)
        self.cache[key] = new_node
        
        # Evict LRU item if over capacity
        if len(self.cache) > self.capacity:
            # Least recently used is right before tail
            lru_node = self.tail.prev
            self._remove(lru_node)
            del self.cache[lru_node.key]
    
    def __len__(self):
        """Return current number of items in cache."""
        return len(self.cache)
    
    def __repr__(self):
        """
        Show cache contents from most to least recently used.
        Helpful for debugging and visualization.
        """
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"{current.key}:{current.value}")
            current = current.next
        return f"LRUCache({' -> '.join(items)})"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create cache that holds 3 items max
    cache = LRUCache(capacity=3)
    
    print("Adding three items (capacity=3):")
    cache.put("user_1", {"name": "Alice", "age": 30})
    cache.put("user_2", {"name": "Bob", "age": 25})
    cache.put("user_3", {"name": "Charlie", "age": 35})
    print(f"Cache state: {cache}")
    print(f"Size: {len(cache)}\n")
    
    print("Accessing user_1 (moves to front):")
    user = cache.get("user_1")
    print(f"Retrieved: {user}")
    print(f"Cache state: {cache}\n")
    
    print("Adding user_4 (triggers eviction of LRU item 'user_2'):")
    cache.put("user_4", {"name": "Diana", "age": 28})
    print(f"Cache state: {cache}")
    print(f"Size: {len(cache)}\n")
    
    print("Trying to get evicted user_2:")
    result = cache.get("user_2")
    print(f"Result: {result} (None means not in cache)\n")
    
    print("Updating user_3 (moves to front):")
    cache.put("user_3", {"name": "Charlie", "age": 36})
    print(f"Cache state: {cache}\n")
    
    print("Adding two more users (will evict user_1, then user_4):")
    cache.put("user_5", {"name": "Eve", "age": 32})
    print(f"After user_5: {cache}")
    cache.put("user_6", {"name": "Frank", "age": 29})
    print(f"After user_6: {cache}")
    print(f"\nFinal cache contains only the 3 most recently used items!")
```