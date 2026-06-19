"""
Date: 2026-06-19
Built a topological sorter that detects cycles in directed graphs — useful for dependency resolution and build systems.
"""

#!/usr/bin/env python3
"""
Topological Sort Implementation with Cycle Detection

I kept running into dependency hell with some personal projects,
so I implemented Kahn's algorithm to handle topological ordering.
Also throws helpful errors when circular dependencies are detected.
"""

from collections import defaultdict, deque
from typing import List, Set, Dict, Optional


class Graph:
    """
    Directed graph implementation for topological sorting.
    
    Uses adjacency list representation because it's memory-efficient
    for sparse graphs (which most dependency graphs are).
    """
    
    def __init__(self):
        self.adjacency_list = defaultdict(list)
        self.vertices = set()
    
    def add_edge(self, from_vertex, to_vertex):
        """
        Add a directed edge from from_vertex -> to_vertex.
        
        Args:
            from_vertex: Source vertex
            to_vertex: Destination vertex
        """
        self.adjacency_list[from_vertex].append(to_vertex)
        self.vertices.add(from_vertex)
        self.vertices.add(to_vertex)
    
    def get_in_degrees(self) -> Dict:
        """
        Calculate in-degree for each vertex.
        
        In-degree = number of incoming edges. We need this for Kahn's algorithm
        to know which nodes have no dependencies.
        
        Returns:
            Dictionary mapping vertex -> in-degree count
        """
        in_degree = {vertex: 0 for vertex in self.vertices}
        
        for vertex in self.adjacency_list:
            for neighbor in self.adjacency_list[vertex]:
                in_degree[neighbor] += 1
        
        return in_degree
    
    def topological_sort(self) -> Optional[List]:
        """
        Perform topological sort using Kahn's algorithm.
        
        The idea: keep removing vertices with no incoming edges,
        then remove their outgoing edges. If we can't remove all vertices,
        there's a cycle.
        
        Returns:
            List of vertices in topological order, or None if cycle detected
        """
        in_degree = self.get_in_degrees()
        
        # Start with all vertices that have no dependencies
        queue = deque([v for v in self.vertices if in_degree[v] == 0])
        sorted_order = []
        
        while queue:
            current = queue.popleft()
            sorted_order.append(current)
            
            # Remove this vertex's edges and update in-degrees
            for neighbor in self.adjacency_list[current]:
                in_degree[neighbor] -= 1
                
                # If neighbor now has no dependencies, add it to queue
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # If we processed all vertices, no cycle exists
        if len(sorted_order) == len(self.vertices):
            return sorted_order
        else:
            return None
    
    def find_cycle(self) -> Optional[List]:
        """
        DFS-based cycle detection for better error reporting.
        
        Returns:
            A list representing a cycle if found, None otherwise
        """
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {vertex: WHITE for vertex in self.vertices}
        parent = {vertex: None for vertex in self.vertices}
        
        def dfs_visit(vertex, path):
            color[vertex] = GRAY
            path.append(vertex)
            
            for neighbor in self.adjacency_list[vertex]:
                if color[neighbor] == GRAY:
                    # Found a back edge - extract the cycle
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]
                
                if color[neighbor] == WHITE:
                    result = dfs_visit(neighbor, path[:])
                    if result:
                        return result
            
            color[vertex] = BLACK
            return None
        
        for vertex in self.vertices:
            if color[vertex] == WHITE:
                cycle = dfs_visit(vertex, [])
                if cycle:
                    return cycle
        
        return None


def demo_build_system():
    """
    Demo: simulating a build system with dependencies.
    """
    print("=== Build System Dependency Resolution ===\n")
    
    g = Graph()
    
    # Define some build tasks and their dependencies
    # Format: (task, depends_on)
    dependencies = [
        ("compile_utils", "preprocess"),
        ("compile_core", "compile_utils"),
        ("compile_ui", "compile_core"),
        ("link", "compile_ui"),
        ("link", "compile_core"),
        ("test", "link"),
        ("package", "test"),
    ]
    
    for task, depends_on in dependencies:
        # depends_on must complete before task
        g.add_edge(depends_on, task)
    
    print("Dependencies:")
    for task, dep in dependencies:
        print(f"  {task} depends on {dep}")
    
    result = g.topological_sort()
    
    if result:
        print(f"\n✓ Valid build order found:")
        for i, task in enumerate(result, 1):
            print(f"  {i}. {task}")
    else:
        print("\n✗ Circular dependency detected!")
        cycle = g.find_cycle()
        if cycle:
            print(f"  Cycle: {' -> '.join(cycle)}")


def demo_circular_dependency():
    """
    Demo: showing what happens with a circular dependency.
    """
    print("\n\n=== Circular Dependency Detection ===\n")
    
    g = Graph()
    
    # Creating a cycle: A -> B -> C -> A
    g.add_edge("module_a", "module_b")
    g.add_edge("module_b", "module_c")
    g.add_edge("module_c", "module_a")  # This creates the cycle
    
    print("Dependencies:")
    print("  module_a -> module_b")
    print("  module_b -> module_c")
    print("  module_c -> module_a")
    
    result = g.topological_sort()
    
    if result:
        print(f"\n✓ Order: {' -> '.join(result)}")
    else:
        print("\n✗ Circular dependency detected!")
        cycle = g.find_cycle()
        if cycle:
            print(f"  Cycle found: {' -> '.join(cycle)}")


if __name__ == "__main__":
    demo_build_system()
    demo_circular_dependency()