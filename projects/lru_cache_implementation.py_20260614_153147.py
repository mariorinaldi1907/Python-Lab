"""
Date: 2026-06-14
Implemented an LRU (Least Recently Used) cache with O(1) get/put operations using a combination of a doubly linked list and dictionary — wanted to understand the data structure behind memoization.
"""

"""
LRU Cache implementation using a doubly linked list + hashmap.
Get and Put operations are both O(1) time complexity.
"""


class Node:
    """
    Doubly linked list node that stores key-value pairs.
    Need to store the key so we can remove it from the hashmap during eviction.
    """
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    LRU Cache with fixed capacity. Evicts least recently used items when full.
    Uses a hashmap for O(1) lookups and a doubly linked list to track access order.
    """
    
    def __init__(self, capacity):
        """
        Initialize cache with given capacity.
        Head and tail are dummy nodes to simplify edge cases.
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.cache = {}  # key -> Node mapping
        
        # Dummy head and tail make insert/delete operations cleaner
        # Most recent items go near head, least recent near tail
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove(self, node):
        """
        Remove a node from the doubly linked list.
        Doesn't remove from hashmap — that's the caller's job.
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
    
    def get(self, key):
        """
        Get value for key. Returns -1 if key doesn't exist.
        Moves accessed node to front since it's now most recently used.
        """
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        # Move to front since we just accessed it
        self._remove(node)
        self._add_to_front(node)
        return node.value
    
    def put(self, key, value):
        """
        Insert or update key-value pair.
        If at capacity, evicts the least recently used item (node before tail).
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
            # Remove least recently used (node before tail)
            lru = self.tail.prev
            self._remove(lru)
            del self.cache[lru.key]  # This is why we store the key in the node
    
    def display(self):
        """
        Display current cache contents from most to least recently used.
        Useful for debugging and visualizing the cache state.
        """
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
    
    print("Creating cache with capacity=3")
    print(f"Cache: {cache.display()}\n")
    
    print("Adding items: put(1, 'one'), put(2, 'two'), put(3, 'three')")
    cache.put(1, "one")
    cache.put(2, "two")
    cache.put(3, "three")
    print(f"Cache: {cache.display()}\n")
    
    print("Getting key 1 (moves it to front)")
    value = cache.get(1)
    print(f"get(1) = {value}")
    print(f"Cache: {cache.display()}\n")
    
    print("Adding key 4 (should evict key 2 — the LRU item)")
    cache.put(4, "four")
    print(f"Cache: {cache.display()}\n")
    
    print("Trying to get evicted key 2")
    value = cache.get(2)
    print(f"get(2) = {value} (returns -1 because it was evicted)")
    print(f"Cache: {cache.display()}\n")
    
    print("Updating key 3 to 'THREE' (should move it to front)")
    cache.put(3, "THREE")
    print(f"Cache: {cache.display()}\n")
    
    print("Adding key 5 (should evict key 1 — currently the LRU)")
    cache.put(5, "five")
    print(f"Cache: {cache.display()}\n")
    
    print("Final state verification:")
    for key in [1, 3, 4, 5]:
        result = cache.get(key)
        status = f"'{result}'" if result != -1 else "MISS"
        print(f"  get({key}) = {status}")