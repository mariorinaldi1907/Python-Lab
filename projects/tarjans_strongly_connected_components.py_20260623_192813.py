"""
Date: 2026-06-23
Built Tarjan's algorithm for finding strongly connected components because I wanted to understand how graph condensation works under the hood.
"""

#!/usr/bin/env python3
"""
Tarjan's algorithm for finding strongly connected components (SCCs) in a directed graph.

I implemented this because I was curious about how tools like dependency analyzers
detect circular dependencies. Tarjan's approach uses a single DFS pass with a stack,
which is more elegant than Kosaraju's two-pass method.
"""

from collections import defaultdict


class TarjanSCC:
    """
    Finds all strongly connected components in a directed graph using Tarjan's algorithm.
    
    A strongly connected component is a maximal set of vertices where every vertex
    is reachable from every other vertex in the set.
    """
    
    def __init__(self, graph):
        """
        Initialize the SCC finder.
        
        Args:
            graph: dict mapping each vertex to a list of its neighbors
        """
        self.graph = graph
        self.index_counter = 0
        self.stack = []
        self.lowlinks = {}  # lowest index reachable from this vertex
        self.index = {}     # discovery time of each vertex
        self.on_stack = set()
        self.sccs = []
        
    def find_sccs(self):
        """
        Find all strongly connected components in the graph.
        
        Returns:
            list of lists, where each inner list is a strongly connected component
        """
        # We need to check all vertices because the graph might be disconnected
        for vertex in self.graph:
            if vertex not in self.index:
                self._strongconnect(vertex)
        
        return self.sccs
    
    def _strongconnect(self, vertex):
        """
        Recursive DFS that identifies SCCs.
        
        The key insight: when we finish exploring a vertex and its lowlink equals
        its index, we've found the root of an SCC. All vertices above it on the
        stack belong to that component.
        """
        # Set the depth index for this vertex
        self.index[vertex] = self.index_counter
        self.lowlinks[vertex] = self.index_counter
        self.index_counter += 1
        
        self.stack.append(vertex)
        self.on_stack.add(vertex)
        
        # Explore neighbors
        for neighbor in self.graph.get(vertex, []):
            if neighbor not in self.index:
                # Neighbor hasn't been visited yet, recurse
                self._strongconnect(neighbor)
                # Check if the subtree has a connection to an earlier vertex
                self.lowlinks[vertex] = min(self.lowlinks[vertex], self.lowlinks[neighbor])
            elif neighbor in self.on_stack:
                # Neighbor is in the current SCC (back edge in DFS tree)
                self.lowlinks[vertex] = min(self.lowlinks[vertex], self.index[neighbor])
        
        # If this is a root node of an SCC, pop the stack to extract the component
        if self.lowlinks[vertex] == self.index[vertex]:
            component = []
            while True:
                w = self.stack.pop()
                self.on_stack.remove(w)
                component.append(w)
                if w == vertex:
                    break
            self.sccs.append(component)


def build_graph_from_edges(edges):
    """
    Convert an edge list to an adjacency list representation.
    
    Args:
        edges: list of (source, destination) tuples
    
    Returns:
        dict mapping each vertex to a list of neighbors
    """
    graph = defaultdict(list)
    vertices = set()
    
    for src, dst in edges:
        graph[src].append(dst)
        vertices.add(src)
        vertices.add(dst)
    
    # Make sure isolated vertices exist in the graph
    for v in vertices:
        if v not in graph:
            graph[v] = []
    
    return dict(graph)


if __name__ == "__main__":
    # Example: a graph with several SCCs
    # I drew this out on paper first - it has 4 components
    edges = [
        (1, 2),
        (2, 3),
        (3, 1),  # First SCC: {1, 2, 3}
        (3, 4),
        (4, 5),
        (5, 6),
        (6, 4),  # Second SCC: {4, 5, 6}
        (6, 7),
        (7, 8),
        (8, 9),
        (9, 7),  # Third SCC: {7, 8, 9}
        (8, 10), # Fourth SCC: {10} (single vertex)
    ]
    
    print("Finding strongly connected components using Tarjan's algorithm\n")
    print("Graph edges:")
    for src, dst in edges:
        print(f"  {src} -> {dst}")
    
    graph = build_graph_from_edges(edges)
    
    tarjan = TarjanSCC(graph)
    sccs = tarjan.find_sccs()
    
    print(f"\nFound {len(sccs)} strongly connected components:\n")
    for i, component in enumerate(sccs, 1):
        # Sort for consistent output (Tarjan's order can vary)
        component.sort()
        print(f"  Component {i}: {component}")
    
    # Demonstrate with a simpler example - a single cycle
    print("\n" + "="*60)
    print("\nSimpler example: a single cycle")
    cycle_edges = [(1, 2), (2, 3), (3, 4), (4, 1)]
    
    print("Graph edges:")
    for src, dst in cycle_edges:
        print(f"  {src} -> {dst}")
    
    cycle_graph = build_graph_from_edges(cycle_edges)
    cycle_tarjan = TarjanSCC(cycle_graph)
    cycle_sccs = cycle_tarjan.find_sccs()
    
    print(f"\nFound {len(cycle_sccs)} strongly connected component:")
    for component in cycle_sccs:
        component.sort()
        print(f"  {component}")