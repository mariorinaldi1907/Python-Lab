"""
Date: 2026-08-06
Built Tarjan's SCC algorithm from scratch to detect cycles and connected components in directed graphs, using DFS with a single pass.
"""

#!/usr/bin/env python3
"""
Tarjan's Algorithm for finding Strongly Connected Components (SCCs) in a directed graph.

I've been meaning to implement this for a while — it's one of those classic graph algorithms
that's surprisingly elegant once you understand the low-link value concept.
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
        Initialize with an adjacency list representation of the graph.
        
        Args:
            graph: dict mapping vertex -> list of neighbors
        """
        self.graph = graph
        self.index_counter = 0
        self.stack = []
        self.lowlinks = {}
        self.index = {}
        self.on_stack = set()
        self.sccs = []
    
    def find_sccs(self):
        """
        Find all strongly connected components in the graph.
        
        Returns:
            List of lists, where each inner list is an SCC (set of vertices)
        """
        # Need to check all vertices since graph might be disconnected
        for vertex in self.graph:
            if vertex not in self.index:
                self._strongconnect(vertex)
        
        return self.sccs
    
    def _strongconnect(self, vertex):
        """
        Recursive DFS that assigns index and lowlink values.
        
        The lowlink value represents the smallest index reachable from this vertex.
        When lowlink == index, we've found the root of an SCC.
        """
        # Set the depth index for this vertex
        self.index[vertex] = self.index_counter
        self.lowlinks[vertex] = self.index_counter
        self.index_counter += 1
        
        self.stack.append(vertex)
        self.on_stack.add(vertex)
        
        # Check all neighbors
        for neighbor in self.graph.get(vertex, []):
            if neighbor not in self.index:
                # Neighbor hasn't been visited yet, recurse
                self._strongconnect(neighbor)
                # Update lowlink based on neighbor's lowlink
                self.lowlinks[vertex] = min(self.lowlinks[vertex], self.lowlinks[neighbor])
            elif neighbor in self.on_stack:
                # Neighbor is in current SCC (still on stack)
                self.lowlinks[vertex] = min(self.lowlinks[vertex], self.index[neighbor])
        
        # If this is a root node of an SCC, pop the stack to get the component
        if self.lowlinks[vertex] == self.index[vertex]:
            scc = []
            while True:
                node = self.stack.pop()
                self.on_stack.remove(node)
                scc.append(node)
                if node == vertex:
                    break
            self.sccs.append(scc)


def has_cycle(graph):
    """
    Check if a directed graph has any cycles by looking for non-trivial SCCs.
    
    Args:
        graph: adjacency list dict
        
    Returns:
        True if graph contains at least one cycle
    """
    tarjan = TarjanSCC(graph)
    sccs = tarjan.find_sccs()
    
    # A cycle exists if any SCC has more than one node
    return any(len(scc) > 1 for scc in sccs)


def build_graph_from_edges(edges):
    """
    Convert edge list to adjacency list representation.
    
    Args:
        edges: list of (source, destination) tuples
        
    Returns:
        dict mapping vertex -> list of neighbors
    """
    graph = defaultdict(list)
    vertices = set()
    
    for src, dst in edges:
        graph[src].append(dst)
        vertices.add(src)
        vertices.add(dst)
    
    # Ensure all vertices exist in graph even if they have no outgoing edges
    for v in vertices:
        if v not in graph:
            graph[v] = []
    
    return dict(graph)


if __name__ == "__main__":
    print("=== Tarjan's SCC Algorithm Demo ===\n")
    
    # Example 1: Graph with multiple SCCs
    print("Example 1: Graph with 3 distinct SCCs")
    edges1 = [
        (1, 2), (2, 3), (3, 1),  # First SCC: 1-2-3 cycle
        (4, 5), (5, 6), (6, 4),  # Second SCC: 4-5-6 cycle
        (7, 8),                   # Third SCC: 7-8 (no cycle back)
        (3, 4),                   # Connection between SCCs
        (6, 7)
    ]
    
    graph1 = build_graph_from_edges(edges1)
    tarjan1 = TarjanSCC(graph1)
    sccs1 = tarjan1.find_sccs()
    
    print(f"Graph edges: {edges1}")
    print(f"Found {len(sccs1)} strongly connected components:")
    for i, scc in enumerate(sccs1, 1):
        print(f"  SCC {i}: {sorted(scc)}")
    print(f"Has cycle: {has_cycle(graph1)}\n")
    
    # Example 2: DAG (no cycles)
    print("Example 2: Directed Acyclic Graph (DAG)")
    edges2 = [
        ('A', 'B'), ('A', 'C'),
        ('B', 'D'), ('C', 'D'),
        ('D', 'E')
    ]
    
    graph2 = build_graph_from_edges(edges2)
    tarjan2 = TarjanSCC(graph2)
    sccs2 = tarjan2.find_sccs()
    
    print(f"Graph edges: {edges2}")
    print(f"Found {len(sccs2)} strongly connected components:")
    for i, scc in enumerate(sccs2, 1):
        print(f"  SCC {i}: {scc}")
    print(f"Has cycle: {has_cycle(graph2)}\n")
    
    # Example 3: Single large SCC
    print("Example 3: Fully connected cycle")
    edges3 = [
        (1, 2), (2, 3), (3, 4), (4, 1),  # Complete cycle
        (2, 4), (3, 1)                     # Additional connections
    ]
    
    graph3 = build_graph_from_edges(edges3)
    tarjan3 = TarjanSCC(graph3)
    sccs3 = tarjan3.find_sccs()
    
    print(f"Graph edges: {edges3}")
    print(f"Found {len(sccs3)} strongly connected components:")
    for i, scc in enumerate(sccs3, 1):
        print(f"  SCC {i}: {sorted(scc)}")
    print(f"Has cycle: {has_cycle(graph3)}")