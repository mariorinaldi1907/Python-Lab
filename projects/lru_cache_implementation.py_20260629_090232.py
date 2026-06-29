"""
Date: 2026-06-29
Implemented a proper LRU cache with O(1) get/put operations to really understand how caching works under the hood — uses a doubly linked list for ordering and a dict for fast lookups.
"""

"""
LRU Cache Implementation
========================
A least-recently-used cache that evicts the oldest item when capacity is reached.
Uses a doubly linked list to maintain access order and a dictionary for O(1) lookups.
"""


class DLLNode:
    """Node for a doubly linked list."""
    
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    LRU Cache with O(1) get and put operations.
    
    The cache maintains items in access order using a doubly linked list.
    Most recently used items are at the head, least recently used at the tail.
    When capacity is exceeded, we evict from the tail.
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
        self.cache = {}  # key -> DLLNode mapping for O(1) access
        
        # Dummy head and tail nodes simplify edge cases
        # Real nodes exist between head and tail
        self.head = DLLNode()
        self.tail = DLLNode()
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove_node(self, node):
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
    
    def _move_to_head(self, node):
        """Move an existing node to the head (mark as recently used)."""
        self._remove_node(node)
        self._add_to_head(node)
    
    def get(self, key):
        """
        Retrieve a value from the cache.
        
        Args:
            key: The key to look up
            
        Returns:
            The value if found, -1 otherwise
        """
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        self._move_to_head(node)  # Mark as recently used
        return node.value
    
    def put(self, key, value):
        """
        Insert or update a key-value pair in the cache.
        
        If the key exists, update its value and mark as recently used.
        If the key is new and cache is at capacity, evict the LRU item.
        
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
            new_node = DLLNode(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)
            
            # Check capacity and evict if necessary
            if len(self.cache) > self.capacity:
                # Remove the LRU item (right before tail)
                lru_node = self.tail.prev
                self._remove_node(lru_node)
                del self.cache[lru_node.key]
    
    def display_order(self):
        """
        Display the current order of items (most to least recently used).
        Useful for debugging and visualization.
        """
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"{current.key}:{current.value}")
            current = current.next
        return " -> ".join(items) if items else "empty"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a cache with capacity 3
    cache = LRUCache(3)
    
    print("Creating cache with capacity 3\n")
    
    print("Operations:")
    print("put(1, 'one')")
    cache.put(1, "one")
    print(f"Cache order: {cache.display_order()}\n")
    
    print("put(2, 'two')")
    cache.put(2, "two")
    print(f"Cache order: {cache.display_order()}\n")
    
    print("put(3, 'three')")
    cache.put(3, "three")
    print(f"Cache order: {cache.display_order()}\n")
    
    print("get(1) ->", cache.get(1))
    print(f"Cache order: {cache.display_order()}")
    print("(1 moved to front since we just accessed it)\n")
    
    print("put(4, 'four')")
    print("(This should evict key 2, since it's the LRU)")
    cache.put(4, "four")
    print(f"Cache order: {cache.display_order()}\n")
    
    print("get(2) ->", cache.get(2))
    print("(Returns -1 because 2 was evicted)\n")
    
    print("get(3) ->", cache.get(3))
    print(f"Cache order: {cache.display_order()}\n")
    
    print("put(3, 'THREE_UPDATED')")
    cache.put(3, "THREE_UPDATED")
    print(f"Cache order: {cache.display_order()}")
    print("(Updated value and moved to front)\n")
    
    print("=== Final State ===")
    print(f"Cache order: {cache.display_order()}")
    print(f"Size: {len(cache.cache)}/{cache.capacity}")