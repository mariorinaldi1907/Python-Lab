"""
Date: 2026-06-28
Implemented a proper LRU cache with O(1) get/put operations using a dictionary and doubly linked list — wanted to understand how @lru_cache actually works under the hood.
"""

"""
LRU Cache implementation using hashmap + doubly linked list.
I wanted to understand the mechanics behind Python's functools.lru_cache,
so I built one from scratch. The trick is maintaining both O(1) lookup
and O(1) removal/insertion by combining a dict with a doubly linked list.
"""


class Node:
    """
    Node for the doubly linked list. Each node holds a key-value pair
    and pointers to prev/next nodes.
    """
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    Least Recently Used (LRU) Cache with O(1) get and put operations.
    
    Uses a hashmap for O(1) lookups and a doubly linked list to track
    access order. Most recently used items are at the head, least recently
    used at the tail.
    """
    
    def __init__(self, capacity):
        """
        Initialize the LRU cache with a given capacity.
        
        Args:
            capacity: Maximum number of items the cache can hold
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.cache = {}  # key -> Node mapping
        
        # Using dummy head and tail nodes makes linked list operations cleaner
        # No need to handle edge cases when list is empty or has one element
        self.head = Node(0, 0)  # dummy head (most recent)
        self.tail = Node(0, 0)  # dummy tail (least recent)
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
        Add a node right after the head (most recently used position).
        """
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
    
    def get(self, key):
        """
        Get value for a key. Marks it as recently used.
        
        Args:
            key: The key to look up
            
        Returns:
            The value if key exists, -1 otherwise
        """
        if key in self.cache:
            node = self.cache[key]
            # Move to front since it was just accessed
            self._remove(node)
            self._add_to_head(node)
            return node.value
        return -1
    
    def put(self, key, value):
        """
        Insert or update a key-value pair. Evicts LRU item if at capacity.
        
        Args:
            key: The key to insert/update
            value: The value to store
        """
        if key in self.cache:
            # Update existing key - remove old node
            self._remove(self.cache[key])
        
        # Create new node and add to front
        new_node = Node(key, value)
        self._add_to_head(new_node)
        self.cache[key] = new_node
        
        # Check if we exceeded capacity
        if len(self.cache) > self.capacity:
            # Remove least recently used (right before tail)
            lru_node = self.tail.prev
            self._remove(lru_node)
            del self.cache[lru_node.key]
    
    def __str__(self):
        """
        String representation showing cache contents from most to least recent.
        """
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"{current.key}:{current.value}")
            current = current.next
        return f"LRUCache({self.capacity}) [{' -> '.join(items)}]"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a cache with capacity 3
    cache = LRUCache(3)
    print(f"Created cache with capacity 3\n")
    
    # Add some items
    print("Operations:")
    cache.put(1, "one")
    print(f"put(1, 'one')  -> {cache}")
    
    cache.put(2, "two")
    print(f"put(2, 'two')  -> {cache}")
    
    cache.put(3, "three")
    print(f"put(3, 'three') -> {cache}")
    
    # Access an item (moves it to front)
    print(f"\nget(1)         -> {cache.get(1)}")
    print(f"After access:  -> {cache}")
    
    # Add another item, should evict key 2 (least recently used)
    print(f"\nput(4, 'four') -> ", end="")
    cache.put(4, "four")
    print(cache)
    
    # Try to get the evicted item
    result = cache.get(2)
    print(f"get(2)         -> {result} (evicted!)")
    
    # Update an existing key
    print(f"\nput(3, 'THREE') -> ", end="")
    cache.put(3, "THREE")
    print(cache)
    
    # More operations to show LRU behavior
    print(f"\nget(4)         -> {cache.get(4)}")
    print(f"After access:  -> {cache}")
    
    cache.put(5, "five")
    print(f"put(5, 'five') -> {cache}")
    print("\nNotice key 1 was evicted (it was LRU)")