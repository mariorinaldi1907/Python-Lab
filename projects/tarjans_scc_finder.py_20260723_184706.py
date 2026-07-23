"""
Date: 2026-07-23
Built Tarjan's SCC algorithm because I needed to understand cyclic dependencies in directed graphs — returns all strongly connected components with their node indices.
"""

#!/usr/bin/env python3
"""
Tarjan's algorithm for finding Strongly Connected Components (SCCs) in a directed graph.
Uses an iterative DFS approach with explicit stack management to avoid recursion limits.
Mario - 2025
"""

from collections import defaultdict


class TarjanSCC:
    """
    Finds all strongly connected components in a directed graph using Tarjan's algorithm.
    
    A strongly connected component is a maximal set of vertices where every vertex
    is reachable from every other vertex in the set.
    """
    
    def __init__(self, num_vertices):
        """
        Initialize the graph structure.
        
        Args:
            num_vertices: Number of vertices in the graph (0-indexed)
        """
        self.num_vertices = num_vertices
        self.graph = defaultdict(list)
        
    def add_edge(self, u, v):
        """
        Add a directed edge from u to v.
        
        Args:
            u: Source vertex
            v: Destination vertex
        """
        self.graph[u].append(v)
    
    def find_sccs(self):
        """
        Find all strongly connected components using Tarjan's algorithm.
        
        Returns:
            List of SCCs, where each SCC is a list of vertex indices
        """
        # Tarjan's algorithm needs to track discovery time and lowest reachable ancestor
        index_counter = [0]  # Using list to make it mutable in nested scope
        stack = []
        on_stack = [False] * self.num_vertices
        indices = [-1] * self.num_vertices
        low_link = [-1] * self.num_vertices
        sccs = []
        
        def strong_connect(v):
            """
            Iterative DFS that explores from vertex v and finds SCCs.
            This replaces the recursive version to handle large graphs.
            """
            # Manual stack for DFS: (vertex, neighbor_index, is_returning)
            dfs_stack = [(v, 0, False)]
            
            while dfs_stack:
                current, neighbor_idx, returning = dfs_stack.pop()
                
                if not returning:
                    # First time visiting this vertex
                    if indices[current] == -1:
                        indices[current] = index_counter[0]
                        low_link[current] = index_counter[0]
                        index_counter[0] += 1
                        stack.append(current)
                        on_stack[current] = True
                    
                    # Process neighbors
                    neighbors = self.graph[current]
                    if neighbor_idx < len(neighbors):
                        next_vertex = neighbors[neighbor_idx]
                        
                        # Push return continuation
                        dfs_stack.append((current, neighbor_idx + 1, False))
                        
                        if indices[next_vertex] == -1:
                            # Neighbor not visited, explore it
                            dfs_stack.append((current, neighbor_idx, True))
                            dfs_stack.append((next_vertex, 0, False))
                        elif on_stack[next_vertex]:
                            # Neighbor is in current SCC
                            low_link[current] = min(low_link[current], indices[next_vertex])
                    else:
                        # All neighbors processed, check if this is an SCC root
                        if low_link[current] == indices[current]:
                            scc = []
                            while True:
                                w = stack.pop()
                                on_stack[w] = False
                                scc.append(w)
                                if w == current:
                                    break
                            sccs.append(scc)
                else:
                    # Returning from a recursive call
                    prev_vertex = dfs_stack[-1][0] if dfs_stack else current
                    if dfs_stack:
                        dfs_stack.pop()
                        low_link[prev_vertex] = min(low_link[prev_vertex], low_link[current])
                        dfs_stack.append((prev_vertex, neighbor_idx, False))
        
        # Find SCCs starting from each unvisited vertex
        for vertex in range(self.num_vertices):
            if indices[vertex] == -1:
                strong_connect(vertex)
        
        return sccs


def create_example_graph():
    """
    Creates a sample directed graph with known SCCs for demonstration.
    
    The graph has 8 vertices with the following structure:
    - SCC 1: {0, 1, 2} - forms a cycle
    - SCC 2: {3, 4, 7} - another cycle
    - SCC 3: {5}       - single vertex
    - SCC 4: {6}       - single vertex
    """
    graph = TarjanSCC(8)
    
    # First SCC: 0 <-> 1 <-> 2 <-> 0
    graph.add_edge(0, 1)
    graph.add_edge(1, 2)
    graph.add_edge(2, 0)
    
    # Connection to second component
    graph.add_edge(1, 3)
    
    # Second SCC: 3 <-> 4, 4 -> 7 -> 3
    graph.add_edge(3, 4)
    graph.add_edge(4, 3)
    graph.add_edge(4, 7)
    graph.add_edge(7, 3)
    
    # Isolated vertices with edges
    graph.add_edge(3, 5)
    graph.add_edge(5, 6)
    
    return graph


if __name__ == "__main__":
    print("Tarjan's SCC Algorithm Demo")
    print("=" * 50)
    
    # Create and analyze the example graph
    graph = create_example_graph()
    sccs = graph.find_sccs()
    
    print(f"\nFound {len(sccs)} strongly connected components:\n")
    
    for i, scc in enumerate(sccs, 1):
        print(f"SCC {i}: {sorted(scc)}")
    
    # Verify the properties of SCCs
    print("\n" + "=" * 50)
    print("SCC Properties:")
    print(f"  - Total vertices: {graph.num_vertices}")
    print(f"  - Total SCCs: {len(sccs)}")
    print(f"  - Vertices accounted for: {sum(len(scc) for scc in sccs)}")
    
    # Show which SCCs are non-trivial (more than one vertex)
    non_trivial = [scc for scc in sccs if len(scc) > 1]
    print(f"  - Non-trivial SCCs (cycles): {len(non_trivial)}")
    if non_trivial:
        print(f"    {[sorted(scc) for scc in non_trivial]}")