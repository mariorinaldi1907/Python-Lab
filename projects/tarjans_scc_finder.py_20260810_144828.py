"""
Date: 2026-08-10
Built Tarjan's SCC algorithm because I wanted to understand how compilers detect circular dependencies and optimize code flow analysis.
"""

#!/usr/bin/env python3
"""
Tarjan's algorithm for finding strongly connected components (SCCs) in a directed graph.

I chose this over Kosaraju's because it only requires one DFS pass instead of two,
and I find the low-link value approach really elegant. Plus, it's fun to implement
a stack-based algorithm that's both recursive and iterative at the same time.
"""

from collections import defaultdict
from typing import List, Set, Dict, Tuple


class TarjanSCC:
    """
    Finds all strongly connected components in a directed graph using Tarjan's algorithm.
    
    A strongly connected component is a maximal set of vertices where every vertex
    is reachable from every other vertex in the set.
    """
    
    def __init__(self, graph: Dict[int, List[int]]):
        """
        Initialize with an adjacency list representation of a directed graph.
        
        Args:
            graph: Dictionary mapping each vertex to a list of its neighbors
        """
        self.graph = graph
        self.index_counter = 0  # Tracks DFS discovery order
        self.stack = []  # Maintains vertices in current SCC candidate
        self.lowlinks = {}  # Lowest index reachable from each vertex
        self.index = {}  # Discovery time of each vertex
        self.on_stack = set()  # Quick lookup for stack membership
        self.sccs = []  # Will store all discovered SCCs
    
    def find_sccs(self) -> List[Set[int]]:
        """
        Main entry point - finds all SCCs in the graph.
        
        Returns:
            List of sets, where each set contains vertices in one SCC
        """
        # Need to check all vertices because graph might be disconnected
        for vertex in self.graph:
            if vertex not in self.index:
                self._strongconnect(vertex)
        
        return self.sccs
    
    def _strongconnect(self, vertex: int):
        """
        Recursive DFS that builds SCCs using the low-link value technique.
        
        The key insight: a vertex is the root of an SCC if its lowlink equals
        its index (meaning it can't reach anything discovered earlier).
        
        Args:
            vertex: Current vertex being explored
        """
        # Set the depth index for this vertex
        self.index[vertex] = self.index_counter
        self.lowlinks[vertex] = self.index_counter
        self.index_counter += 1
        self.stack.append(vertex)
        self.on_stack.add(vertex)
        
        # Explore all neighbors
        if vertex in self.graph:
            for neighbor in self.graph[vertex]:
                if neighbor not in self.index:
                    # Neighbor hasn't been visited yet, recurse on it
                    self._strongconnect(neighbor)
                    # After returning, check if neighbor's lowlink is smaller
                    self.lowlinks[vertex] = min(self.lowlinks[vertex], 
                                                self.lowlinks[neighbor])
                elif neighbor in self.on_stack:
                    # Neighbor is in current SCC candidate
                    # Update lowlink to the neighbor's index (not lowlink!)
                    # because we found a back edge
                    self.lowlinks[vertex] = min(self.lowlinks[vertex], 
                                                self.index[neighbor])
        
        # If vertex is a root of an SCC, pop the stack to collect all vertices in it
        if self.lowlinks[vertex] == self.index[vertex]:
            scc = set()
            while True:
                node = self.stack.pop()
                self.on_stack.remove(node)
                scc.add(node)
                if node == vertex:
                    break
            self.sccs.append(scc)


def build_graph_from_edges(edges: List[Tuple[int, int]]) -> Dict[int, List[int]]:
    """
    Helper to convert edge list to adjacency list.
    
    Args:
        edges: List of (source, destination) tuples
        
    Returns:
        Adjacency list as a dictionary
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


def visualize_sccs(sccs: List[Set[int]]):
    """
    Pretty-print the SCCs in a readable format.
    
    Args:
        sccs: List of strongly connected components
    """
    print(f"Found {len(sccs)} strongly connected component(s):\n")
    
    for i, scc in enumerate(sccs, 1):
        sorted_scc = sorted(scc)
        if len(scc) == 1:
            print(f"  SCC {i}: {{{sorted_scc[0]}}} (singleton)")
        else:
            print(f"  SCC {i}: {{{', '.join(map(str, sorted_scc))}}} (size: {len(scc)})")


if __name__ == "__main__":
    print("=== Tarjan's SCC Algorithm Demo ===\n")
    
    # Example 1: Classic graph with multiple SCCs
    # This is the graph I always draw when explaining SCCs on a whiteboard
    print("Example 1: Graph with multiple components")
    edges1 = [
        (0, 1), (1, 2), (2, 0),  # First cycle: 0 -> 1 -> 2 -> 0
        (1, 3), (3, 4), (4, 5), (5, 3),  # Second cycle: 3 -> 4 -> 5 -> 3
        (2, 6), (6, 7), (7, 6),  # Third cycle: 6 -> 7 -> 6
        (7, 8)  # 8 is a singleton (no cycle)
    ]
    
    graph1 = build_graph_from_edges(edges1)
    tarjan1 = TarjanSCC(graph1)
    sccs1 = tarjan1.find_sccs()
    visualize_sccs(sccs1)
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: Single large SCC
    print("Example 2: Fully connected cycle")
    edges2 = [
        (0, 1), (1, 2), (2, 3), (3, 4), (4, 0)
    ]
    
    graph2 = build_graph_from_edges(edges2)
    tarjan2 = TarjanSCC(graph2)
    sccs2 = tarjan2.find_sccs()
    visualize_sccs(sccs2)
    
    print("\n" + "="*50 + "\n")
    
    # Example 3: No cycles (DAG)
    print("Example 3: DAG (no cycles)")
    edges3 = [
        (0, 1), (0, 2), (1, 3), (2, 3), (3, 4)
    ]
    
    graph3 = build_graph_from_edges(edges3)
    tarjan3 = TarjanSCC(graph3)
    sccs3 = tarjan3.find_sccs()
    visualize_sccs(sccs3)