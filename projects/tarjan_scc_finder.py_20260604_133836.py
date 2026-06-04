"""
Date: 2026-06-04
Built Tarjan's SCC algorithm from scratch because I needed to understand how cycle detection works in directed graphs at a deeper level.
"""

#!/usr/bin/env python3
"""
Tarjan's algorithm for finding Strongly Connected Components (SCCs) in a directed graph.

I wanted to really understand how this works under the hood, especially the low-link
value tracking. This is way more elegant than running DFS multiple times.
"""

from collections import defaultdict


class TarjanSCC:
    """
    Find all strongly connected components in a directed graph using Tarjan's algorithm.
    
    A strongly connected component is a maximal set of vertices where every vertex
    is reachable from every other vertex in the set.
    """
    
    def __init__(self, graph):
        """
        Initialize with an adjacency list representation of the graph.
        
        Args:
            graph: dict mapping vertex -> list of adjacent vertices
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
            List of SCCs, where each SCC is a list of vertices.
        """
        # Need to check all nodes in case graph is disconnected
        for vertex in self.graph:
            if vertex not in self.index:
                self._strongconnect(vertex)
        
        return self.sccs
    
    def _strongconnect(self, vertex):
        """
        Recursive DFS that tracks low-link values to identify SCCs.
        
        The low-link value is the smallest index reachable from this vertex,
        which lets us identify when we've completed an SCC.
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
                # Update low-link after returning from recursion
                self.lowlinks[vertex] = min(self.lowlinks[vertex], 
                                           self.lowlinks[neighbor])
            elif neighbor in self.on_stack:
                # Neighbor is in current SCC (back edge found)
                self.lowlinks[vertex] = min(self.lowlinks[vertex], 
                                           self.index[neighbor])
        
        # If this is a root node of an SCC, pop the stack to extract it
        if self.lowlinks[vertex] == self.index[vertex]:
            scc = []
            while True:
                node = self.stack.pop()
                self.on_stack.remove(node)
                scc.append(node)
                if node == vertex:
                    break
            self.sccs.append(scc)


def detect_cycles(graph):
    """
    Detect if a directed graph contains any cycles.
    
    A cycle exists if any SCC contains more than one node, or if a node
    has an edge to itself.
    
    Args:
        graph: adjacency list representation
        
    Returns:
        bool: True if cycles exist, False otherwise
    """
    finder = TarjanSCC(graph)
    sccs = finder.find_sccs()
    
    # Any SCC with size > 1 means there's a cycle
    for scc in sccs:
        if len(scc) > 1:
            return True
        # Also check for self-loops
        if scc[0] in graph.get(scc[0], []):
            return True
    
    return False


def build_condensation_graph(graph, sccs):
    """
    Build a condensation graph where each SCC becomes a single node.
    
    This is useful for analyzing the high-level structure of a graph.
    The condensation is always a DAG (directed acyclic graph).
    
    Args:
        graph: original adjacency list
        sccs: list of strongly connected components
        
    Returns:
        dict: condensation graph adjacency list (SCC index -> list of SCC indices)
    """
    # Map each vertex to its SCC index
    vertex_to_scc = {}
    for idx, scc in enumerate(sccs):
        for vertex in scc:
            vertex_to_scc[vertex] = idx
    
    # Build edges between SCCs
    condensation = defaultdict(set)
    for vertex in graph:
        scc_idx = vertex_to_scc[vertex]
        for neighbor in graph.get(vertex, []):
            neighbor_scc = vertex_to_scc[neighbor]
            if scc_idx != neighbor_scc:
                condensation[scc_idx].add(neighbor_scc)
    
    # Convert sets to lists for cleaner output
    return {k: list(v) for k, v in condensation.items()}


if __name__ == "__main__":
    # Example graph with multiple SCCs
    # Visual representation:
    #   0 -> 1 -> 2 -> 0 (cycle)
    #   2 -> 3 -> 4 (path)
    #   4 -> 3 (back edge creating another cycle)
    #   5 -> 6 (separate component)
    
    test_graph = {
        0: [1],
        1: [2],
        2: [0, 3],
        3: [4],
        4: [3],
        5: [6],
        6: []
    }
    
    print("Graph adjacency list:")
    for vertex, neighbors in sorted(test_graph.items()):
        print(f"  {vertex} -> {neighbors}")
    
    print("\n" + "="*50)
    
    finder = TarjanSCC(test_graph)
    sccs = finder.find_sccs()
    
    print(f"\nFound {len(sccs)} strongly connected components:")
    for idx, scc in enumerate(sccs):
        print(f"  SCC {idx}: {sorted(scc)}")
    
    print("\n" + "="*50)
    
    has_cycles = detect_cycles(test_graph)
    print(f"\nGraph contains cycles: {has_cycles}")
    
    print("\n" + "="*50)
    
    condensation = build_condensation_graph(test_graph, sccs)
    print("\nCondensation graph (each node is an SCC):")
    for scc_idx, neighbors in sorted(condensation.items()):
        print(f"  SCC {scc_idx} -> SCCs {neighbors}")
    
    print("\n" + "="*50)
    
    # Another example: simple DAG with no cycles
    dag = {
        'A': ['B', 'C'],
        'B': ['D'],
        'C': ['D'],
        'D': []
    }
    
    print("\nTesting a DAG (no cycles):")
    dag_finder = TarjanSCC(dag)
    dag_sccs = dag_finder.find_sccs()
    print(f"  SCCs in DAG: {dag_sccs}")
    print(f"  Has cycles: {detect_cycles(dag)}")