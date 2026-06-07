"""
Date: 2026-06-07
Built an LRU cache from scratch using a doubly linked list and dictionary to get O(1) lookups and evictions — wanted to understand how functools.lru_cache actually works under the hood.
"""

"""
LRU (Least Recently Used) Cache Implementation

I wanted to understand how caching works at a fundamental level, so I built
this from scratch. Uses a doubly linked list to maintain access order and
a hash map for O(1) lookups. When capacity is exceeded, we evict the least
recently used item (the tail of our list).
"""


class DLLNode:
    """Node for doubly linked list - stores key/value and prev/next pointers."""
    
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    LRU Cache with O(1) get and put operations.
    
    The trick here is maintaining two data structures:
    1. A hash map for fast lookups
    2. A doubly linked list to track access order (most recent at head)
    
    When we access or add an item, we move it to the front.
    When capacity is exceeded, we remove from the tail.
    """
    
    def __init__(self, capacity):
        """
        Initialize cache with given capacity.
        
        Using dummy head/tail nodes to avoid edge case checks when
        adding/removing nodes. Makes the code cleaner.
        """
        self.capacity = capacity
        self.cache = {}  # key -> DLLNode
        
        # Dummy head and tail to simplify list operations
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
        """Add a node right after the head (marks it as most recently used)."""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
    
    def _move_to_head(self, node):
        """Move an existing node to the head (when it's accessed)."""
        self._remove_node(node)
        self._add_to_head(node)
    
    def _evict_tail(self):
        """Remove the least recently used item (the node before tail)."""
        lru_node = self.tail.prev
        self._remove_node(lru_node)
        return lru_node
    
    def get(self, key):
        """
        Get value for a key. Returns -1 if not found.
        
        If the key exists, we need to mark it as recently used by
        moving it to the head of our list.
        """
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        self._move_to_head(node)
        return node.value
    
    def put(self, key, value):
        """
        Add or update a key-value pair.
        
        If key exists: update value and move to head.
        If new key and at capacity: evict LRU item first.
        """
        if key in self.cache:
            # Update existing key
            node = self.cache[key]
            node.value = value
            self._move_to_head(node)
        else:
            # Add new key
            new_node = DLLNode(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)
            
            # Check capacity and evict if needed
            if len(self.cache) > self.capacity:
                lru_node = self._evict_tail()
                del self.cache[lru_node.key]
    
    def display(self):
        """Display current cache state (for debugging/demo purposes)."""
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"{current.key}:{current.value}")
            current = current.next
        return " -> ".join(items) if items else "(empty)"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a cache with capacity 3
    cache = LRUCache(3)
    
    print("Creating cache with capacity 3")
    print(f"Cache state: {cache.display()}\n")
    
    # Add some items
    print("put(1, 'one')")
    cache.put(1, "one")
    print(f"Cache state: {cache.display()}\n")
    
    print("put(2, 'two')")
    cache.put(2, "two")
    print(f"Cache state: {cache.display()}\n")
    
    print("put(3, 'three')")
    cache.put(3, "three")
    print(f"Cache state: {cache.display()}\n")
    
    # Access an item (moves it to front)
    print("get(1) ->", cache.get(1))
    print(f"Cache state: {cache.display()} (1 moved to front)\n")
    
    # Add another item (should evict key 2, the LRU)
    print("put(4, 'four') - this exceeds capacity")
    cache.put(4, "four")
    print(f"Cache state: {cache.display()} (2 was evicted)\n")
    
    # Try to get evicted item
    print("get(2) ->", cache.get(2), "(not found, was evicted)\n")
    
    # Update existing item
    print("put(3, 'THREE') - updating existing key")
    cache.put(3, "THREE")
    print(f"Cache state: {cache.display()} (3 updated and moved to front)\n")
    
    print("get(4) ->", cache.get(4))
    print(f"Cache state: {cache.display()}\n")
    
    print("get(1) ->", cache.get(1))
    print(f"Final cache state: {cache.display()}")