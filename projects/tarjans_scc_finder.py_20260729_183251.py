"""
Date: 2026-07-29
Built Tarjan's SCC algorithm because I needed to detect cycles in a dependency graph and figured I'd make it reusable.
"""

#!/usr/bin/env python3
"""
Tarjan's algorithm for finding Strongly Connected Components (SCCs) in a directed graph.
I implemented this after dealing with circular dependencies in one of my projects.
SCCs are maximal sets of vertices where every vertex is reachable from every other vertex.
"""

from collections import defaultdict


class TarjanSCC:
    """
    Finds all strongly connected components in a directed graph using Tarjan's algorithm.
    
    Uses a single DFS pass with a stack to identify SCCs in O(V + E) time.
    The algorithm tracks discovery time and the lowest reachable ancestor for each node.
    """
    
    def __init__(self, graph):
        """
        Initialize with a graph represented as an adjacency list.
        
        Args:
            graph: dict mapping each node to a list of its neighbors
        """
        self.graph = graph
        self.index_counter = 0
        self.stack = []
        self.on_stack = set()
        
        # Track discovery time and lowest reachable ancestor
        self.indices = {}
        self.lowlinks = {}
        
        self.sccs = []
    
    def find_sccs(self):
        """
        Find all strongly connected components in the graph.
        
        Returns:
            list of lists, where each inner list is one SCC
        """
        # Need to check all nodes since graph might be disconnected
        for node in self.graph:
            if node not in self.indices:
                self._strong_connect(node)
        
        return self.sccs
    
    def _strong_connect(self, node):
        """
        Recursive DFS that identifies SCCs.
        
        The key insight: a node is the root of an SCC if its lowlink equals its index.
        This means we couldn't reach any earlier node from this subtree.
        """
        # Set the depth index for this node
        self.indices[node] = self.index_counter
        self.lowlinks[node] = self.index_counter
        self.index_counter += 1
        
        self.stack.append(node)
        self.on_stack.add(node)
        
        # Check all neighbors
        for neighbor in self.graph.get(node, []):
            if neighbor not in self.indices:
                # Neighbor hasn't been visited yet, recurse
                self._strong_connect(neighbor)
                # Update lowlink based on what the neighbor could reach
                self.lowlinks[node] = min(self.lowlinks[node], self.lowlinks[neighbor])
            elif neighbor in self.on_stack:
                # Neighbor is in current SCC (back edge found)
                self.lowlinks[node] = min(self.lowlinks[node], self.indices[neighbor])
        
        # If this node is a root of an SCC, pop the stack to form the component
        if self.lowlinks[node] == self.indices[node]:
            scc = []
            while True:
                w = self.stack.pop()
                self.on_stack.remove(w)
                scc.append(w)
                if w == node:
                    break
            self.sccs.append(scc)


def has_cycle(graph):
    """
    Check if a directed graph contains any cycles.
    
    A cycle exists if any SCC has more than one node, or if any single-node SCC
    has a self-loop.
    
    Args:
        graph: adjacency list representation
        
    Returns:
        bool indicating whether the graph has cycles
    """
    tarjan = TarjanSCC(graph)
    sccs = tarjan.find_sccs()
    
    for scc in sccs:
        if len(scc) > 1:
            return True
        # Check for self-loop
        if len(scc) == 1:
            node = scc[0]
            if node in graph.get(node, []):
                return True
    
    return False


def build_graph_from_edges(edges):
    """
    Convenience function to build adjacency list from edge list.
    
    Args:
        edges: list of (from_node, to_node) tuples
        
    Returns:
        dict representing the graph as an adjacency list
    """
    graph = defaultdict(list)
    
    for from_node, to_node in edges:
        graph[from_node].append(to_node)
    
    # Ensure all nodes exist in the graph, even if they have no outgoing edges
    for from_node, to_node in edges:
        if to_node not in graph:
            graph[to_node] = []
    
    return dict(graph)


if __name__ == "__main__":
    print("=== Tarjan's SCC Algorithm Demo ===\n")
    
    # Example 1: Simple cycle
    print("Example 1: Triangle cycle")
    edges1 = [
        (1, 2),
        (2, 3),
        (3, 1),
        (3, 4)
    ]
    graph1 = build_graph_from_edges(edges1)
    tarjan1 = TarjanSCC(graph1)
    sccs1 = tarjan1.find_sccs()
    
    print(f"Graph edges: {edges1}")
    print(f"SCCs found: {sccs1}")
    print(f"Has cycle: {has_cycle(graph1)}")
    print()
    
    # Example 2: Multiple components
    print("Example 2: Two separate cycles")
    edges2 = [
        ('A', 'B'),
        ('B', 'C'),
        ('C', 'A'),
        ('D', 'E'),
        ('E', 'F'),
        ('F', 'D'),
    ]
    graph2 = build_graph_from_edges(edges2)
    tarjan2 = TarjanSCC(graph2)
    sccs2 = tarjan2.find_sccs()
    
    print(f"Graph edges: {edges2}")
    print(f"SCCs found: {sccs2}")
    print(f"Has cycle: {has_cycle(graph2)}")
    print()
    
    # Example 3: DAG (no cycles)
    print("Example 3: Directed Acyclic Graph")
    edges3 = [
        ('start', 'A'),
        ('start', 'B'),
        ('A', 'C'),
        ('B', 'C'),
        ('C', 'end')
    ]
    graph3 = build_graph_from_edges(edges3)
    tarjan3 = TarjanSCC(graph3)
    sccs3 = tarjan3.find_sccs()
    
    print(f"Graph edges: {edges3}")
    print(f"SCCs found: {sccs3}")
    print(f"Has cycle: {has_cycle(graph3)}")
    print()
    
    # Example 4: Complex graph with multiple SCCs
    print("Example 4: Complex graph")
    edges4 = [
        (1, 2),
        (2, 3),
        (3, 1),  # First SCC
        (2, 4),
        (4, 5),
        (5, 6),
        (6, 4),  # Second SCC
        (6, 7),  # Singleton
    ]
    graph4 = build_graph_from_edges(edges4)
    tarjan4 = TarjanSCC(graph4)
    sccs4 = tarjan4.find_sccs()
    
    print(f"Graph edges: {edges4}")
    print(f"SCCs found: {sccs4}")
    print(f"Has cycle: {has_cycle(graph4)}")