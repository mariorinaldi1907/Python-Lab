"""
Date: 2026-07-30
Built an LRU cache to really understand how caching works under the hood — uses a hash map for O(1) lookups and a doubly linked list for O(1) evictions.
"""

"""
LRU Cache Implementation
========================
A Least Recently Used (LRU) cache with O(1) get and put operations.
Uses a doubly linked list to maintain access order and a hash map for fast lookups.

I wanted to understand how caching actually works instead of just using functools.lru_cache.
This was a fun exercise in combining data structures to get specific time complexities.
"""


class Node:
    """Doubly linked list node to track key-value pairs in access order."""
    
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    LRU Cache that evicts least recently used items when capacity is reached.
    
    The trick here is maintaining both a hashmap (for O(1) access) and a doubly
    linked list (for O(1) reordering). Most recently used items are at the head,
    least recently used at the tail.
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
        self.cache = {}  # Maps keys to nodes
        
        # Dummy head and tail make insertion/deletion logic cleaner
        # (no special cases for empty lists or single items)
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove(self, node):
        """Remove a node from the doubly linked list."""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _add_to_head(self, node):
        """Add a node right after the head (most recently used position)."""
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
    
    def get(self, key):
        """
        Get value by key and mark it as recently used.
        
        Args:
            key: The key to look up
            
        Returns:
            The value if found, -1 otherwise
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
        Insert or update a key-value pair. Evicts LRU item if at capacity.
        
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
                # Evict the least recently used (tail's prev)
                lru_node = self.tail.prev
                self._remove(lru_node)
                del self.cache[lru_node.key]
            
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)
    
    def display(self):
        """Display current cache contents in access order (for debugging)."""
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"{current.key}: {current.value}")
            current = current.next
        return " -> ".join(items) if items else "(empty)"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a cache that holds 3 items
    cache = LRUCache(capacity=3)
    
    print("Created cache with capacity 3\n")
    
    print("Inserting items...")
    cache.put("user:1", "Alice")
    print(f"put('user:1', 'Alice') -> {cache.display()}")
    
    cache.put("user:2", "Bob")
    print(f"put('user:2', 'Bob') -> {cache.display()}")
    
    cache.put("user:3", "Charlie")
    print(f"put('user:3', 'Charlie') -> {cache.display()}")
    
    print("\nAccessing 'user:1' (moves it to front)...")
    value = cache.get("user:1")
    print(f"get('user:1') = {value}")
    print(f"Cache order: {cache.display()}")
    
    print("\nAdding 'user:4' (should evict 'user:2' since it's LRU)...")
    cache.put("user:4", "Diana")
    print(f"put('user:4', 'Diana') -> {cache.display()}")
    
    print("\nTrying to get evicted key 'user:2'...")
    value = cache.get("user:2")
    print(f"get('user:2') = {value} (returns -1 because it was evicted)")
    
    print("\nUpdating existing key 'user:3'...")
    cache.put("user:3", "Charlie Updated")
    print(f"put('user:3', 'Charlie Updated') -> {cache.display()}")
    
    print("\n=== Demo Complete ===")