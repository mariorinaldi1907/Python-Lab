"""
Date: 2026-06-19
Built an LRU cache with O(1) get/put operations to finally understand the doubly-linked list + hashmap pattern everyone talks about.
"""

"""
LRU (Least Recently Used) Cache Implementation
Mario's take on the classic interview question — but actually understanding it this time.
"""

class Node:
    """
    Doubly-linked list node. Stores key-value pair plus pointers to prev/next.
    We need the key here because when evicting from the tail, we need to know
    which key to remove from the hashmap.
    """
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    LRU Cache with O(1) get and put operations.
    
    Uses a doubly-linked list to maintain access order (most recent at head)
    and a hashmap for O(1) lookups. When capacity is exceeded, we evict the
    least recently used item from the tail.
    """
    
    def __init__(self, capacity):
        """
        Initialize the cache with a fixed capacity.
        
        Args:
            capacity (int): Maximum number of items the cache can hold
        """
        self.capacity = capacity
        self.cache = {}  # key -> Node mapping
        
        # Dummy head and tail make edge cases way simpler
        # We'll maintain items between these sentinels
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove(self, node):
        """
        Remove a node from the doubly-linked list.
        This doesn't touch the hashmap — just the list structure.
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
    
    def _move_to_head(self, node):
        """
        Move an existing node to the head position.
        Called when we access an item — it becomes most recently used.
        """
        self._remove(node)
        self._add_to_head(node)
    
    def _evict_tail(self):
        """
        Remove the least recently used item (the one before tail sentinel).
        Returns the evicted node so we can clean up the hashmap.
        """
        lru_node = self.tail.prev
        self._remove(lru_node)
        return lru_node
    
    def get(self, key):
        """
        Get value from cache. Returns -1 if key doesn't exist.
        Moves the accessed item to the head (most recently used).
        
        Args:
            key: The key to look up
            
        Returns:
            The value associated with the key, or -1 if not found
        """
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        self._move_to_head(node)
        return node.value
    
    def put(self, key, value):
        """
        Insert or update a key-value pair in the cache.
        If the key exists, update its value and move to head.
        If it's new and we're at capacity, evict the LRU item first.
        
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
            # New key — create a node and add to cache
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)
            
            # Check if we exceeded capacity
            if len(self.cache) > self.capacity:
                # Evict LRU item
                lru_node = self._evict_tail()
                del self.cache[lru_node.key]
    
    def display_cache_state(self):
        """
        Debug helper to see current cache state from MRU to LRU.
        """
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"{current.key}:{current.value}")
            current = current.next
        return " -> ".join(items) if items else "(empty)"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a cache with capacity of 3
    cache = LRUCache(3)
    
    print("Creating cache with capacity = 3\n")
    
    print("put(1, 'apple')")
    cache.put(1, "apple")
    print(f"Cache state: {cache.display_cache_state()}\n")
    
    print("put(2, 'banana')")
    cache.put(2, "banana")
    print(f"Cache state: {cache.display_cache_state()}\n")
    
    print("put(3, 'cherry')")
    cache.put(3, "cherry")
    print(f"Cache state: {cache.display_cache_state()}\n")
    
    print("get(1) ->", cache.get(1))
    print(f"Cache state: {cache.display_cache_state()}")
    print("^ Notice 1 moved to front (most recently used)\n")
    
    print("put(4, 'date') — this exceeds capacity!")
    cache.put(4, "date")
    print(f"Cache state: {cache.display_cache_state()}")
    print("^ Key 2 was evicted (least recently used)\n")
    
    print("get(2) ->", cache.get(2))
    print("^ Returns -1 because it was evicted\n")
    
    print("get(3) ->", cache.get(3))
    print(f"Cache state: {cache.display_cache_state()}")
    print("^ Key 3 moved to front\n")
    
    print("put(1, 'apricot') — updating existing key")
    cache.put(1, "apricot")
    print(f"Cache state: {cache.display_cache_state()}")
    print("^ Value updated and moved to front\n")
    
    print("Final cache contents:")
    for key in [1, 3, 4]:
        print(f"  get({key}) = {cache.get(key)}")