"""
Date: 2026-06-10
Implemented an LRU (Least Recently Used) cache using a hash map and doubly linked list to get O(1) get/put operations — helped me finally understand the internals of caching strategies.
"""

"""
LRU Cache Implementation
========================
A proper Least Recently Used cache that evicts the oldest item when capacity is exceeded.
Using a doubly linked list + dictionary to achieve O(1) for both get and put operations.
"""


class DLLNode:
    """
    Node for the doubly linked list.
    Stores key-value pairs and pointers to prev/next nodes.
    """
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    LRU Cache with O(1) get and put operations.
    
    The trick here is maintaining a doubly linked list where:
    - Head (dummy) -> most recently used
    - Tail (dummy) -> least recently used
    
    When we access or add an item, we move it to the front.
    When capacity is exceeded, we evict from the back.
    """
    
    def __init__(self, capacity):
        """
        Initialize the LRU cache with a given capacity.
        
        Args:
            capacity: Maximum number of items the cache can hold
        """
        self.capacity = capacity
        self.cache = {}  # key -> DLLNode mapping
        
        # Create dummy head and tail nodes to avoid edge case handling
        self.head = DLLNode()
        self.tail = DLLNode()
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove_node(self, node):
        """
        Remove a node from the doubly linked list.
        Just pointer manipulation, doesn't touch the cache dict.
        """
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _add_to_front(self, node):
        """
        Add a node right after the head (most recently used position).
        """
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
    
    def _move_to_front(self, node):
        """
        Move an existing node to the front (mark as recently used).
        """
        self._remove_node(node)
        self._add_to_front(node)
    
    def get(self, key):
        """
        Retrieve a value from the cache.
        If the key exists, move it to front (mark as recently used).
        
        Args:
            key: The key to look up
            
        Returns:
            The value if found, -1 otherwise
        """
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        self._move_to_front(node)
        return node.value
    
    def put(self, key, value):
        """
        Add or update a key-value pair in the cache.
        If at capacity and adding a new key, evict the LRU item.
        
        Args:
            key: The key to store
            value: The value to associate with the key
        """
        if key in self.cache:
            # Update existing key
            node = self.cache[key]
            node.value = value
            self._move_to_front(node)
        else:
            # Add new key
            if len(self.cache) >= self.capacity:
                # Evict the least recently used (node before tail)
                lru_node = self.tail.prev
                self._remove_node(lru_node)
                del self.cache[lru_node.key]
            
            # Create and add new node
            new_node = DLLNode(key, value)
            self.cache[key] = new_node
            self._add_to_front(new_node)
    
    def display_cache_state(self):
        """
        Debug helper to see the current order of items in the cache.
        Walks from head to tail showing the access order.
        """
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"{current.key}={current.value}")
            current = current.next
        return " -> ".join(items) if items else "(empty)"


if __name__ == "__main__":
    print("=== LRU Cache Demo ===\n")
    
    # Create a cache that holds 3 items max
    cache = LRUCache(capacity=3)
    
    print("Adding items to cache (capacity=3):")
    cache.put("a", 1)
    print(f"  put('a', 1) -> {cache.display_cache_state()}")
    
    cache.put("b", 2)
    print(f"  put('b', 2) -> {cache.display_cache_state()}")
    
    cache.put("c", 3)
    print(f"  put('c', 3) -> {cache.display_cache_state()}")
    
    print("\nAccessing 'a' (moves to front):")
    val = cache.get("a")
    print(f"  get('a') = {val}")
    print(f"  State: {cache.display_cache_state()}")
    
    print("\nAdding 'd' (should evict 'b', the LRU item):")
    cache.put("d", 4)
    print(f"  put('d', 4) -> {cache.display_cache_state()}")
    
    print("\nTrying to get evicted 'b':")
    val = cache.get("b")
    print(f"  get('b') = {val} (not found)")
    
    print("\nUpdating existing key 'c':")
    cache.put("c", 30)
    print(f"  put('c', 30) -> {cache.display_cache_state()}")
    
    print("\n=== All operations completed successfully ===")