"""
Date: 2026-06-12
Built Dijkstra's algorithm from scratch using heapq because I wanted to really understand how shortest path finding works under the hood.
"""

import heapq
from collections import defaultdict
from typing import Dict, List, Tuple, Optional


class Graph:
    """
    Weighted directed graph implemented with adjacency list.
    I'm using a defaultdict here because it makes adding edges cleaner
    without having to check if a node exists first.
    """
    
    def __init__(self):
        self.adjacency_list: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
        self.nodes = set()
    
    def add_edge(self, from_node: str, to_node: str, weight: float):
        """Add a weighted directed edge to the graph."""
        self.adjacency_list[from_node].append((to_node, weight))
        self.nodes.add(from_node)
        self.nodes.add(to_node)
    
    def get_neighbors(self, node: str) -> List[Tuple[str, float]]:
        """Get all neighbors and their edge weights for a given node."""
        return self.adjacency_list.get(node, [])


def dijkstra(graph: Graph, start: str, end: Optional[str] = None) -> Tuple[Dict[str, float], Dict[str, Optional[str]]]:
    """
    Dijkstra's shortest path algorithm using a min-heap.
    
    Returns a tuple of (distances, predecessors):
    - distances: dict mapping each node to its shortest distance from start
    - predecessors: dict for reconstructing the actual path (stores parent node)
    
    If end is specified, we can early-exit once we've found the shortest path to it.
    This was a fun optimization to add — no point exploring the whole graph if we
    only care about one destination.
    """
    # Initialize distances to infinity for all nodes except start
    distances = {node: float('inf') for node in graph.nodes}
    distances[start] = 0
    
    # Track predecessors to reconstruct the path later
    predecessors = {node: None for node in graph.nodes}
    
    # Min-heap: stores (distance, node) tuples
    # Python's heapq is a min-heap by default, which is perfect here
    heap = [(0, start)]
    
    # Track visited nodes so we don't process them twice
    visited = set()
    
    while heap:
        current_distance, current_node = heapq.heappop(heap)
        
        # If we've already processed this node, skip it
        # This can happen when we add the same node multiple times with different distances
        if current_node in visited:
            continue
        
        visited.add(current_node)
        
        # Early exit optimization if we only care about reaching a specific end node
        if end is not None and current_node == end:
            break
        
        # Explore all neighbors
        for neighbor, weight in graph.get_neighbors(current_node):
            if neighbor in visited:
                continue
            
            # Calculate potential new distance to neighbor
            new_distance = current_distance + weight
            
            # If we found a shorter path, update it
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                predecessors[neighbor] = current_node
                heapq.heappush(heap, (new_distance, neighbor))
    
    return distances, predecessors


def reconstruct_path(predecessors: Dict[str, Optional[str]], start: str, end: str) -> Optional[List[str]]:
    """
    Reconstruct the actual path from start to end using the predecessors dict.
    Returns None if no path exists (i.e., end is unreachable from start).
    
    I'm building the path backwards from end to start, then reversing it.
    """
    if predecessors[end] is None and start != end:
        return None  # No path exists
    
    path = []
    current = end
    
    while current is not None:
        path.append(current)
        current = predecessors[current]
    
    path.reverse()
    return path


if __name__ == "__main__":
    # Build a sample graph representing a simple road network
    # I'm using city names to make it more intuitive than just letters
    g = Graph()
    
    # Adding edges: (from, to, distance/weight)
    g.add_edge("San Francisco", "Los Angeles", 383)
    g.add_edge("San Francisco", "Sacramento", 87)
    g.add_edge("Sacramento", "Lake Tahoe", 103)
    g.add_edge("Los Angeles", "San Diego", 120)
    g.add_edge("Los Angeles", "Las Vegas", 270)
    g.add_edge("Sacramento", "Las Vegas", 420)
    g.add_edge("Lake Tahoe", "Las Vegas", 340)
    g.add_edge("San Diego", "Phoenix", 355)
    g.add_edge("Las Vegas", "Phoenix", 297)
    
    # Adding a disconnected node to test unreachable handling
    g.add_edge("Portland", "Seattle", 174)
    
    print("=" * 60)
    print("DIJKSTRA'S SHORTEST PATH ALGORITHM")
    print("=" * 60)
    
    start_city = "San Francisco"
    
    # Run Dijkstra from San Francisco
    distances, predecessors = dijkstra(g, start_city)
    
    print(f"\nShortest distances from {start_city}:")
    print("-" * 60)
    
    # Sort cities by distance for nicer output
    for city in sorted(distances.keys(), key=lambda x: distances[x]):
        dist = distances[city]
        if dist == float('inf'):
            print(f"{city:20} -> UNREACHABLE")
        else:
            path = reconstruct_path(predecessors, start_city, city)
            path_str = " -> ".join(path)
            print(f"{city:20} -> {dist:6.0f} miles | Path: {path_str}")
    
    # Demonstrate finding a specific path
    print("\n" + "=" * 60)
    print("SPECIFIC PATH EXAMPLE")
    print("=" * 60)
    
    target = "Phoenix"
    distances_to_target, preds_to_target = dijkstra(g, start_city, target)
    path_to_target = reconstruct_path(preds_to_target, start_city, target)
    
    if path_to_target:
        print(f"\nShortest path from {start_city} to {target}:")
        print(" -> ".join(path_to_target))
        print(f"Total distance: {distances_to_target[target]:.0f} miles")
    else:
        print(f"\nNo path exists from {start_city} to {target}")