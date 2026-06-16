"""
Date: 2026-06-16
Built an LRU cache from scratch to understand how least-recently-used eviction works under the hood — used a hashmap for fast lookups and a doubly linked list to track access order.
"""

"""
LRU Cache implementation using a doubly-linked list and dictionary.

I wanted to understand how LRU caches work internally, so I built one from scratch.
The key insight is using a hashmap for O(1) lookups and a doubly-linked list to 
maintain access order. Most recently used items stay at the head, least at the tail.
"""


class Node:
    """
    Node in a doubly-linked list. Stores key, value, and pointers.
    
    The key is stored here (not just value) because when we evict from the tail,
    we need to know which key to delete from the hashmap.
    """
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    Least Recently Used (LRU) Cache with O(1) get and put operations.
    
    When capacity is exceeded, the least recently used item is evicted.
    Every get() or put() operation marks that key as "recently used".
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
        self.cache = {}  # Maps key -> Node
        
        # Dummy head and tail make list operations simpler (no null checks)
        self.head = Node(0, 0)  # Most recently used end
        self.tail = Node(0, 0)  # Least recently used end
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove(self, node):
        """
        Remove a node from the doubly-linked list.
        
        This doesn't delete from the cache dict, just unlinks from the list.
        """
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _add_to_head(self, node):
        """
        Add a node right after the head (marks it as most recently used).
        """
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
    
    def get(self, key):
        """
        Retrieve a value from the cache. Marks the key as recently used.
        
        Args:
            key: The key to look up
            
        Returns:
            The value if found, -1 otherwise
        """
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        # Move to head since we just accessed it
        self._remove(node)
        self._add_to_head(node)
        return node.value
    
    def put(self, key, value):
        """
        Insert or update a key-value pair in the cache.
        
        If the key exists, update its value and mark as recently used.
        If the cache is full, evict the least recently used item first.
        
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
                # Evict LRU item (the one before tail)
                lru_node = self.tail.prev
                self._remove(lru_node)
                del self.cache[lru_node.key]
            
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)
    
    def __str__(self):
        """
        String representation showing cache contents in MRU to LRU order.
        """
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"{current.key}:{current.value}")
            current = current.next
        return f"LRUCache[{' -> '.join(items)}]"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a cache with capacity 3
    cache = LRUCache(3)
    
    print("Cache capacity: 3\n")
    
    print("put(1, 'apple')")
    cache.put(1, "apple")
    print(f"Cache: {cache}\n")
    
    print("put(2, 'banana')")
    cache.put(2, "banana")
    print(f"Cache: {cache}\n")
    
    print("put(3, 'cherry')")
    cache.put(3, "cherry")
    print(f"Cache: {cache}\n")
    
    print("get(1) ->", cache.get(1))
    print(f"Cache after access: {cache}")
    print("(Notice 1 moved to front as most recently used)\n")
    
    print("put(4, 'date')")
    print("(This will evict key 2, the least recently used)")
    cache.put(4, "date")
    print(f"Cache: {cache}\n")
    
    print("get(2) ->", cache.get(2))
    print("(Returns -1 because 2 was evicted)\n")
    
    print("get(3) ->", cache.get(3))
    print(f"Cache after access: {cache}\n")
    
    print("put(5, 'elderberry')")
    print("(This will evict key 1)")
    cache.put(5, "elderberry")
    print(f"Cache: {cache}\n")
    
    print("Updating existing key:")
    print("put(4, 'dragonfruit')")
    cache.put(4, "dragonfruit")
    print(f"Cache: {cache}")
    print("(Value updated and moved to front)")