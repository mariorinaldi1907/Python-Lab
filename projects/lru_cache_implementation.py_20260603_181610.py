"""
Date: 2026-06-03
Built an LRU cache from scratch to practice hash map + linked list combo — supports get/put with automatic eviction when capacity is hit.
"""

"""
LRU Cache implementation using a hash map and doubly linked list.
This was fun to build — I wanted to really understand how caches work under the hood.
The trick is keeping track of usage order with a linked list while getting O(1) lookups with a dict.
"""


class Node:
    """
    Doubly linked list node for maintaining order of cache entries.
    Each node stores a key-value pair plus pointers to prev/next nodes.
    """
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    Least Recently Used (LRU) Cache with O(1) get and put operations.
    
    When capacity is reached, the least recently used item gets evicted.
    Uses a hash map for O(1) lookups and a doubly linked list to track recency.
    """
    
    def __init__(self, capacity):
        """
        Initialize the LRU cache with a fixed capacity.
        
        Args:
            capacity: Maximum number of items the cache can hold
        """
        self.capacity = capacity
        self.cache = {}  # maps keys to nodes
        
        # Create dummy head and tail nodes to simplify edge cases
        # This way I don't have to check for None when adding/removing
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove(self, node):
        """
        Remove a node from the doubly linked list.
        Doesn't delete from cache dict — just unlinks from the list.
        """
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _add_to_front(self, node):
        """
        Add a node right after the head (most recently used position).
        This is where newly accessed items go.
        """
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
    
    def get(self, key):
        """
        Retrieve a value from the cache.
        If the key exists, mark it as recently used by moving to front.
        
        Args:
            key: The key to look up
            
        Returns:
            The value if key exists, -1 otherwise
        """
        if key not in self.cache:
            return -1
        
        # Move to front since it was just accessed
        node = self.cache[key]
        self._remove(node)
        self._add_to_front(node)
        return node.value
    
    def put(self, key, value):
        """
        Insert or update a key-value pair in the cache.
        If cache is at capacity, evict the least recently used item.
        
        Args:
            key: The key to insert/update
            value: The value to store
        """
        if key in self.cache:
            # Update existing key — remove old node
            self._remove(self.cache[key])
        
        # Create new node and add to front
        new_node = Node(key, value)
        self.cache[key] = new_node
        self._add_to_front(new_node)
        
        # Check if we exceeded capacity
        if len(self.cache) > self.capacity:
            # Evict least recently used (node right before tail)
            lru_node = self.tail.prev
            self._remove(lru_node)
            del self.cache[lru_node.key]
    
    def __str__(self):
        """
        String representation showing cache contents from most to least recent.
        Useful for debugging and visualizing the cache state.
        """
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"{current.key}: {current.value}")
            current = current.next
        return f"LRUCache({len(self.cache)}/{self.capacity}): [{' -> '.join(items)}]"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a cache with capacity 3
    cache = LRUCache(3)
    
    print("Creating cache with capacity 3\n")
    
    print("put(1, 'apple')")
    cache.put(1, "apple")
    print(cache)
    print()
    
    print("put(2, 'banana')")
    cache.put(2, "banana")
    print(cache)
    print()
    
    print("put(3, 'cherry')")
    cache.put(3, "cherry")
    print(cache)
    print()
    
    print("get(1):", cache.get(1))
    print("(key 1 moves to front)")
    print(cache)
    print()
    
    print("put(4, 'date')")
    print("(capacity exceeded — key 2 gets evicted)")
    cache.put(4, "date")
    print(cache)
    print()
    
    print("get(2):", cache.get(2))
    print("(returns -1 because it was evicted)")
    print()
    
    print("get(3):", cache.get(3))
    print("(key 3 moves to front)")
    print(cache)
    print()
    
    print("put(1, 'apricot')")
    print("(updating key 1 with new value)")
    cache.put(1, "apricot")
    print(cache)
    print()
    
    print("put(5, 'elderberry')")
    print("(key 4 gets evicted)")
    cache.put(5, "elderberry")
    print(cache)