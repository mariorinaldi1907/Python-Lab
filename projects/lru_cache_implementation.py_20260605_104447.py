"""
Date: 2026-06-05
Built a proper LRU cache with O(1) get/put operations using a doubly linked list and dictionary because I wanted to really understand the data structure behind Python's functools decorator.
"""

"""
LRU (Least Recently Used) Cache Implementation

I wanted to implement this from scratch to understand how caching actually works.
The trick is using a doubly linked list to maintain order and a hashmap for O(1) lookups.
"""


class Node:
    """
    Doubly linked list node to track cache entries.
    
    Each node holds a key-value pair plus pointers to prev/next nodes.
    This lets us move nodes around in O(1) time when they're accessed.
    """
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    LRU Cache with O(1) get and put operations.
    
    The cache evicts the least recently used item when it hits capacity.
    I'm using dummy head/tail nodes to avoid edge case headaches.
    """
    
    def __init__(self, capacity):
        """
        Initialize the cache with a fixed capacity.
        
        Args:
            capacity: Maximum number of items the cache can hold
        """
        self.capacity = capacity
        self.cache = {}  # Maps keys to nodes for O(1) lookup
        
        # Dummy head and tail make insertion/deletion way easier
        # Most recently used items go near head, LRU items near tail
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove(self, node):
        """
        Remove a node from the doubly linked list.
        
        This doesn't delete the node, just unlinks it from the list.
        Used when we need to move a node or evict it.
        """
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _add_to_head(self, node):
        """
        Add a node right after the head (most recently used position).
        
        Whenever we access or add an item, it becomes the most recent.
        """
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
    
    def get(self, key):
        """
        Retrieve a value from the cache.
        
        If the key exists, move it to the front (mark as recently used).
        Returns -1 if key doesn't exist — following LeetCode convention here.
        
        Args:
            key: The key to look up
            
        Returns:
            The value associated with the key, or -1 if not found
        """
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        # Move to front since we just accessed it
        self._remove(node)
        self._add_to_head(node)
        return node.value
    
    def put(self, key, value):
        """
        Insert or update a key-value pair in the cache.
        
        If key exists, update its value and move to front.
        If cache is full, evict the LRU item (node before tail).
        
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
            # Create new node
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)
            
            # Evict LRU item if we're over capacity
            if len(self.cache) > self.capacity:
                lru_node = self.tail.prev
                self._remove(lru_node)
                del self.cache[lru_node.key]
    
    def display(self):
        """
        Print the current cache contents from most to least recently used.
        
        Just for debugging/visualization purposes.
        """
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"{current.key}:{current.value}")
            current = current.next
        print(f"Cache (MRU -> LRU): [{' -> '.join(items)}]")


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a cache with capacity 3
    cache = LRUCache(3)
    print("Created cache with capacity 3\n")
    
    # Add some items
    print("Adding items:")
    cache.put(1, "apple")
    print("  put(1, 'apple')")
    cache.display()
    
    cache.put(2, "banana")
    print("  put(2, 'banana')")
    cache.display()
    
    cache.put(3, "cherry")
    print("  put(3, 'cherry')")
    cache.display()
    
    # Access an item (moves it to front)
    print("\nAccessing key 1:")
    value = cache.get(1)
    print(f"  get(1) = '{value}'")
    cache.display()
    
    # Add another item, should evict key 2 (LRU)
    print("\nAdding key 4 (capacity full, will evict LRU):")
    cache.put(4, "date")
    print("  put(4, 'date')")
    cache.display()
    
    # Try to get evicted item
    print("\nTrying to access evicted key 2:")
    value = cache.get(2)
    print(f"  get(2) = {value} (key was evicted)")
    cache.display()
    
    # Update existing key
    print("\nUpdating key 3:")
    cache.put(3, "coconut")
    print("  put(3, 'coconut')")
    cache.display()
    
    # Add another item to show eviction again
    print("\nAdding key 5:")
    cache.put(5, "elderberry")
    print("  put(5, 'elderberry')")
    cache.display()
    print("\n(Key 1 was evicted as the LRU)")