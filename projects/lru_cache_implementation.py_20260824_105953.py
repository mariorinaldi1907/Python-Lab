"""
Date: 2026-08-24
Built an LRU cache from scratch using a hashmap and doubly linked list because I wanted to understand how the @lru_cache decorator actually works under the hood.
"""

"""
LRU (Least Recently Used) Cache Implementation
Uses a combination of a hashmap and doubly linked list for O(1) operations.
"""


class Node:
    """
    Doubly linked list node to maintain access order.
    Each node holds a key-value pair plus pointers to prev/next nodes.
    """
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    LRU Cache with fixed capacity. When full, evicts least recently used item.
    
    Uses a hashmap for O(1) lookups and a doubly linked list to track recency.
    Most recent items are near the head, least recent near the tail.
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
        self.cache = {}  # maps key -> Node
        
        # Dummy head and tail to simplify edge cases
        # Real nodes go between these sentinels
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove(self, node):
        """
        Remove a node from the linked list (doesn't touch the hashmap).
        Used when we need to move a node to the front or evict it.
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
        Retrieve value for key. Marks the item as recently used.
        
        Args:
            key: The key to look up
            
        Returns:
            The value if found, None otherwise
        """
        if key not in self.cache:
            return None
        
        node = self.cache[key]
        # Move to front since we just accessed it
        self._remove(node)
        self._add_to_front(node)
        return node.value
    
    def put(self, key, value):
        """
        Insert or update a key-value pair. Marks it as recently used.
        If cache is full, evicts the least recently used item.
        
        Args:
            key: The key to insert/update
            value: The value to store
        """
        if key in self.cache:
            # Update existing key - remove old node
            self._remove(self.cache[key])
        
        new_node = Node(key, value)
        self.cache[key] = new_node
        self._add_to_front(new_node)
        
        # Evict LRU item if over capacity
        if len(self.cache) > self.capacity:
            # LRU is right before the tail
            lru = self.tail.prev
            self._remove(lru)
            del self.cache[lru.key]
    
    def __len__(self):
        """Return current number of items in cache."""
        return len(self.cache)
    
    def __repr__(self):
        """Show cache contents from most to least recently used."""
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"{current.key}: {current.value}")
            current = current.next
        return f"LRUCache({', '.join(items)})"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a cache that holds 3 items
    cache = LRUCache(capacity=3)
    
    print("Creating cache with capacity=3")
    print(f"Initial state: {cache}\n")
    
    # Add some items
    print("Adding items:")
    cache.put("user:1", {"name": "Alice", "age": 30})
    print(f"  put('user:1', Alice) -> {cache}")
    
    cache.put("user:2", {"name": "Bob", "age": 25})
    print(f"  put('user:2', Bob) -> {cache}")
    
    cache.put("user:3", {"name": "Charlie", "age": 35})
    print(f"  put('user:3', Charlie) -> {cache}\n")
    
    # Access an item (moves it to front)
    print("Accessing user:1:")
    result = cache.get("user:1")
    print(f"  get('user:1') -> {result['name']}")
    print(f"  Cache order: {cache}\n")
    
    # Add another item, should evict user:2 (LRU)
    print("Adding user:4 (should evict user:2):")
    cache.put("user:4", {"name": "Diana", "age": 28})
    print(f"  put('user:4', Diana) -> {cache}\n")
    
    # Try to access evicted item
    print("Trying to access evicted user:2:")
    result = cache.get("user:2")
    print(f"  get('user:2') -> {result}\n")
    
    # Update an existing key
    print("Updating user:3:")
    cache.put("user:3", {"name": "Charlie", "age": 36})
    print(f"  put('user:3', Charlie age=36) -> {cache}\n")
    
    print(f"Final cache size: {len(cache)}")