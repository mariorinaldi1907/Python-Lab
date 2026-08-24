"""
Date: 2026-08-24
Built an LRU cache from scratch to understand how dict ordering and capacity eviction actually work under the hood.
"""

"""
LRU Cache implementation using a hash map and doubly linked list.

The hash map gives O(1) access to nodes, and the doubly linked list
maintains the order of usage. Most recently used items go to the front,
and when we hit capacity, we evict from the back.
"""


class Node:
    """
    Doubly linked list node that stores a key-value pair.
    
    We need to store the key here (not just value) because when we evict
    from the tail, we need to know which key to remove from the hash map.
    """
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    Least Recently Used cache with fixed capacity.
    
    Uses a doubly linked list to track usage order and a hash map
    for O(1) lookups. When capacity is exceeded, evicts the least
    recently used item (tail of the list).
    """
    
    def __init__(self, capacity):
        """
        Initialize the LRU cache with given capacity.
        
        Args:
            capacity: Maximum number of items the cache can hold
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.cache = {}  # maps keys to nodes
        
        # Dummy head and tail make list operations cleaner
        # (no special cases for empty list or single element)
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove_node(self, node):
        """Remove a node from the doubly linked list."""
        node.prev.next = node.next
        node.next.prev = node.prev
    
    def _add_to_front(self, node):
        """Add a node right after the dummy head (most recently used position)."""
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
    
    def _move_to_front(self, node):
        """Move an existing node to the front (mark as recently used)."""
        self._remove_node(node)
        self._add_to_front(node)
    
    def get(self, key):
        """
        Retrieve a value from the cache.
        
        Args:
            key: The key to look up
            
        Returns:
            The value associated with the key, or None if not found
        """
        if key not in self.cache:
            return None
        
        node = self.cache[key]
        self._move_to_front(node)  # Mark as recently used
        return node.value
    
    def put(self, key, value):
        """
        Insert or update a key-value pair in the cache.
        
        If the key exists, updates its value and marks it as recently used.
        If the cache is at capacity, evicts the least recently used item first.
        
        Args:
            key: The key to insert/update
            value: The value to store
        """
        if key in self.cache:
            # Update existing key
            node = self.cache[key]
            node.value = value
            self._move_to_front(node)
        else:
            # Insert new key
            if len(self.cache) >= self.capacity:
                # Evict least recently used (node before dummy tail)
                lru_node = self.tail.prev
                self._remove_node(lru_node)
                del self.cache[lru_node.key]
            
            # Add new node
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_front(new_node)
    
    def __repr__(self):
        """Return a string representation showing cache order (MRU to LRU)."""
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"{current.key}:{current.value}")
            current = current.next
        return f"LRUCache([{', '.join(items)}])"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a cache with capacity 3
    cache = LRUCache(capacity=3)
    print(f"Created cache with capacity 3\n")
    
    # Add some items
    print("Adding items...")
    cache.put("user:1", "Alice")
    print(f"put('user:1', 'Alice') -> {cache}")
    
    cache.put("user:2", "Bob")
    print(f"put('user:2', 'Bob') -> {cache}")
    
    cache.put("user:3", "Charlie")
    print(f"put('user:3', 'Charlie') -> {cache}")
    
    # Access an item (makes it recently used)
    print(f"\nget('user:1') -> {cache.get('user:1')}")
    print(f"After access: {cache}")
    
    # Add another item (should evict user:2, the LRU)
    print(f"\nAdding 4th item (should evict 'user:2')...")
    cache.put("user:4", "Diana")
    print(f"put('user:4', 'Diana') -> {cache}")
    
    # Try to get evicted item
    print(f"\nget('user:2') -> {cache.get('user:2')} (was evicted)")
    
    # Update existing item
    print(f"\nUpdating existing item...")
    cache.put("user:3", "Charlie Updated")
    print(f"put('user:3', 'Charlie Updated') -> {cache}")
    
    # Demonstrate the order
    print(f"\nFinal cache state (MRU -> LRU): {cache}")
    
    print("\n=== Edge Case: Capacity 1 ===")
    tiny_cache = LRUCache(capacity=1)
    tiny_cache.put("a", 1)
    print(f"put('a', 1) -> {tiny_cache}")
    tiny_cache.put("b", 2)
    print(f"put('b', 2) -> {tiny_cache} (evicted 'a')")
    print(f"get('a') -> {tiny_cache.get('a')} (not found)")