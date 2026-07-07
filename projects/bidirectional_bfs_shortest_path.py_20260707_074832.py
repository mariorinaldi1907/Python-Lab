"""
Date: 2026-07-07
Built a bidirectional breadth-first search that searches from both ends simultaneously, which I've been wanting to try since it can cut search time in half for dense graphs.
"""

#!/usr/bin/env python3
"""
Bidirectional BFS for finding shortest paths in unweighted graphs.

The idea here is to run BFS from both the start and end nodes at the same time,
meeting somewhere in the middle. This can be much faster than single-direction BFS
because the search space grows exponentially with distance, so two smaller searches
beat one big one.
"""

from collections import deque, defaultdict
from typing import Dict, List, Set, Optional, Tuple


class Graph:
    """
    Simple undirected graph using adjacency lists.
    
    I'm keeping this unweighted since bidirectional BFS shines most here,
    though the concept works for weighted graphs with Dijkstra too.
    """
    
    def __init__(self):
        self.adjacency_list = defaultdict(list)
    
    def add_edge(self, u: int, v: int):
        """Add an undirected edge between u and v."""
        self.adjacency_list[u].append(v)
        self.adjacency_list[v].append(u)
    
    def get_neighbors(self, node: int) -> List[int]:
        """Return all neighbors of a given node."""
        return self.adjacency_list[node]


def bidirectional_bfs(graph: Graph, start: int, end: int) -> Optional[List[int]]:
    """
    Find shortest path between start and end using bidirectional BFS.
    
    Returns the path as a list of nodes, or None if no path exists.
    
    The trick is maintaining two separate BFS searches that expand alternately.
    When they meet (same node visited from both sides), we reconstruct the path
    by combining the forward and backward parent chains.
    """
    if start == end:
        return [start]
    
    # Track visited nodes and their parents for both directions
    forward_visited = {start: None}
    backward_visited = {end: None}
    
    # Queues for both BFS frontiers
    forward_queue = deque([start])
    backward_queue = deque([end])
    
    # This will be the meeting point if/when the searches collide
    intersection_node = None
    
    while forward_queue and backward_queue:
        # Expand forward search one level
        intersection_node = _expand_level(
            graph, forward_queue, forward_visited, backward_visited
        )
        if intersection_node is not None:
            break
        
        # Expand backward search one level
        intersection_node = _expand_level(
            graph, backward_queue, backward_visited, forward_visited
        )
        if intersection_node is not None:
            # Since we found it from backward search, swap for reconstruction
            break
    
    if intersection_node is None:
        return None  # No path exists
    
    # Reconstruct the full path from start to end through the intersection
    return _reconstruct_path(
        start, end, intersection_node, forward_visited, backward_visited
    )


def _expand_level(
    graph: Graph,
    queue: deque,
    visited: Dict[int, Optional[int]],
    other_visited: Dict[int, Optional[int]]
) -> Optional[int]:
    """
    Expand one level of BFS and check for intersection with the other search.
    
    Returns the intersection node if found, otherwise None.
    I process all nodes at the current level before moving to the next,
    which keeps the two searches roughly balanced in terms of depth.
    """
    level_size = len(queue)
    
    for _ in range(level_size):
        current = queue.popleft()
        
        for neighbor in graph.get_neighbors(current):
            if neighbor in visited:
                continue  # Already visited from this side
            
            visited[neighbor] = current
            
            # Check if the other search has seen this node
            if neighbor in other_visited:
                return neighbor  # Found the intersection!
            
            queue.append(neighbor)
    
    return None


def _reconstruct_path(
    start: int,
    end: int,
    intersection: int,
    forward_visited: Dict[int, Optional[int]],
    backward_visited: Dict[int, Optional[int]]
) -> List[int]:
    """
    Rebuild the complete path by following parent pointers from both sides.
    
    The forward path goes from start to intersection,
    the backward path goes from end to intersection (which we reverse).
    """
    # Build path from start to intersection
    forward_path = []
    node = intersection
    while node is not None:
        forward_path.append(node)
        node = forward_visited[node]
    forward_path.reverse()
    
    # Build path from intersection to end (via backward search)
    backward_path = []
    node = backward_visited[intersection]  # Start with intersection's parent
    while node is not None:
        backward_path.append(node)
        node = backward_visited[node]
    
    # Combine them (intersection is already in forward_path)
    return forward_path + backward_path


if __name__ == "__main__":
    # Create a sample graph that looks like a social network
    # where finding connections between distant people would benefit
    # from bidirectional search
    
    g = Graph()
    
    # Building a graph with multiple paths between nodes
    edges = [
        (0, 1), (0, 2), (1, 3), (2, 3), (2, 4),
        (3, 5), (4, 5), (5, 6), (6, 7), (5, 8),
        (8, 9), (7, 10), (9, 10), (10, 11)
    ]
    
    for u, v in edges:
        g.add_edge(u, v)
    
    print("Graph edges added:", len(edges))
    print()
    
    # Test case 1: Path exists
    start, end = 0, 11
    path = bidirectional_bfs(g, start, end)
    
    if path:
        print(f"Shortest path from {start} to {end}:")
        print(" -> ".join(map(str, path)))
        print(f"Path length: {len(path) - 1} edges")
    else:
        print(f"No path found from {start} to {end}")
    
    print()
    
    # Test case 2: Start equals end
    start, end = 5, 5
    path = bidirectional_bfs(g, start, end)
    print(f"Path from {start} to itself: {path}")
    
    print()
    
    # Test case 3: No path exists (disconnected node)
    g.add_edge(99, 100)  # Add isolated component
    start, end = 0, 99
    path = bidirectional_bfs(g, start, end)
    print(f"Path from {start} to {end} (disconnected): {path}")