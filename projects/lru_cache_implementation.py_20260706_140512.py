"""
Date: 2026-07-06
Implemented an LRU (Least Recently Used) cache with O(1) get/put operations using a doubly linked list and dictionary, because I wanted to really understand the mechanics behind caching strategies.
"""

"""
LRU Cache Implementation
========================
A from-scratch implementation of an LRU (Least Recently Used) cache.
Uses a doubly linked list to maintain access order and a hashmap for O(1) lookups.
"""


class Node:
    """
    Doubly linked list node to store cache entries.
    Each node holds a key-value pair plus pointers to neighbors.
    """
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    LRU Cache with O(1) get and put operations.
    
    The trick here is maintaining two things:
    1. A hashmap for fast key lookups
    2. A doubly linked list to track access order (most recent at head, least at tail)
    
    When capacity is exceeded, we evict from the tail (least recently used).
    """
    
    def __init__(self, capacity):
        """
        Initialize the cache with a fixed capacity.
        
        Args:
            capacity: Maximum number of items the cache can hold
        """
        self.capacity = capacity
        self.cache = {}  # key -> Node mapping
        
        # Dummy head and tail make insertion/deletion logic cleaner
        # No need to check for None when adding/removing nodes
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove(self, node):
        """
        Remove a node from the doubly linked list.
        This doesn't delete from the hashmap, just unlinks from the list.
        """
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _add_to_head(self, node):
        """
        Add a node right after the dummy head (most recently used position).
        """
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
    
    def get(self, key):
        """
        Retrieve a value from the cache.
        If the key exists, move it to the front (mark as recently used).
        
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
        If at capacity, evict the least recently used item first.
        
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
            # New key
            if len(self.cache) >= self.capacity:
                # Evict least recently used (node right before tail)
                lru = self.tail.prev
                self._remove(lru)
                del self.cache[lru.key]
            
            # Add new node
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)
    
    def display(self):
        """
        Display current cache state from most to least recently used.
        Useful for debugging and demonstrations.
        """
        current = self.head.next
        items = []
        while current != self.tail:
            items.append(f"{current.key}:{current.value}")
            current = current.next
        print(f"Cache (MRU -> LRU): [{' -> '.join(items)}]")


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a cache with capacity of 3
    cache = LRUCache(3)
    
    print("Initializing cache with capacity=3\n")
    
    # Add some items
    print("put(1, 'apple')")
    cache.put(1, "apple")
    cache.display()
    
    print("\nput(2, 'banana')")
    cache.put(2, "banana")
    cache.display()
    
    print("\nput(3, 'cherry')")
    cache.put(3, "cherry")
    cache.display()
    
    # Access an existing item (moves to front)
    print("\nget(1) ->", cache.get(1))
    cache.display()
    
    # Add a 4th item (should evict key=2, the LRU)
    print("\nput(4, 'date') — this should evict key=2")
    cache.put(4, "date")
    cache.display()
    
    # Try to get the evicted item
    print("\nget(2) ->", cache.get(2), "(evicted!)")
    
    # Update an existing key
    print("\nput(3, 'chocolate') — updating key=3")
    cache.put(3, "chocolate")
    cache.display()
    
    # Access order demonstration
    print("\nget(4) ->", cache.get(4))
    cache.display()
    
    print("\nget(1) ->", cache.get(1))
    cache.display()
    
    print("\n✓ Demo complete!")