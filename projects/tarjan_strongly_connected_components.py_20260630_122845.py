"""
Date: 2026-06-30
Built Tarjan's algorithm to find strongly connected components in directed graphs — useful for analyzing dependency cycles and graph structure.
"""

#!/usr/bin/env python3
"""
Tarjan's algorithm for finding strongly connected components (SCCs) in a directed graph.

I wanted to understand how tools like package managers detect circular dependencies,
so I implemented this classic algorithm. It uses DFS with a clever stack trick to
identify SCCs in a single pass — pretty elegant once you get the intuition.
"""

from collections import defaultdict
from typing import List, Set, Dict, Tuple


class TarjanSCC:
    """
    Finds all strongly connected components in a directed graph using Tarjan's algorithm.
    
    A strongly connected component is a maximal set of vertices where every vertex
    is reachable from every other vertex in the set. This is useful for detecting
    cycles and understanding graph structure.
    """
    
    def __init__(self, graph: Dict[int, List[int]]):
        """
        Initialize with an adjacency list representation of a directed graph.
        
        Args:
            graph: Dictionary mapping each vertex to a list of vertices it points to.
        """
        self.graph = graph
        self.index_counter = 0
        # Track discovery time for each node
        self.index = {}
        # Track the smallest index reachable from each node
        self.lowlink = {}
        # Stack of nodes in current SCC search path
        self.stack = []
        self.on_stack = set()
        # Final result: list of SCCs
        self.sccs = []
    
    def find_sccs(self) -> List[List[int]]:
        """
        Find all strongly connected components in the graph.
        
        Returns:
            List of SCCs, where each SCC is a list of vertex IDs.
        """
        # Need to visit all nodes since graph might be disconnected
        all_nodes = set(self.graph.keys())
        for edges in self.graph.values():
            all_nodes.update(edges)
        
        for node in all_nodes:
            if node not in self.index:
                self._strongconnect(node)
        
        return self.sccs
    
    def _strongconnect(self, v: int) -> None:
        """
        Recursive DFS helper that does the actual SCC detection.
        
        The key insight: a node is the root of an SCC if its lowlink equals its index.
        When we find such a root, everything on the stack above it forms one SCC.
        
        Args:
            v: Current vertex being explored.
        """
        # Initialize discovery time and lowlink
        self.index[v] = self.index_counter
        self.lowlink[v] = self.index_counter
        self.index_counter += 1
        
        self.stack.append(v)
        self.on_stack.add(v)
        
        # Explore neighbors
        for w in self.graph.get(v, []):
            if w not in self.index:
                # First time seeing w, recurse
                self._strongconnect(w)
                # w might have found a back edge to an ancestor of v
                self.lowlink[v] = min(self.lowlink[v], self.lowlink[w])
            elif w in self.on_stack:
                # w is in current search path, so we found a cycle
                # Update lowlink to reflect we can reach an earlier node
                self.lowlink[v] = min(self.lowlink[v], self.index[w])
        
        # If v is a root node (lowlink == index), pop the SCC off the stack
        if self.lowlink[v] == self.index[v]:
            scc = []
            while True:
                w = self.stack.pop()
                self.on_stack.remove(w)
                scc.append(w)
                if w == v:
                    break
            self.sccs.append(scc)


def build_example_graph() -> Dict[int, List[int]]:
    """
    Create a sample directed graph with multiple SCCs for demonstration.
    
    The graph has three SCCs:
    - {0, 1, 2} form a cycle
    - {3, 4} form a cycle
    - {5} is alone
    - {6, 7} form a cycle
    """
    return {
        0: [1],
        1: [2],
        2: [0],      # Cycle: 0 -> 1 -> 2 -> 0
        3: [4],
        4: [3, 5],   # Cycle: 3 -> 4 -> 3, plus edge to 5
        5: [],       # Isolated node (but reachable from 4)
        6: [7, 3],
        7: [6],      # Cycle: 6 -> 7 -> 6
    }


def visualize_graph(graph: Dict[int, List[int]]) -> None:
    """Print a simple text representation of the graph."""
    print("Graph structure:")
    for node in sorted(graph.keys()):
        edges = graph[node]
        if edges:
            print(f"  {node} -> {edges}")
        else:
            print(f"  {node} -> (no outgoing edges)")


if __name__ == "__main__":
    print("=== Tarjan's Strongly Connected Components ===\n")
    
    # Build and display the example graph
    graph = build_example_graph()
    visualize_graph(graph)
    
    # Find SCCs
    tarjan = TarjanSCC(graph)
    sccs = tarjan.find_sccs()
    
    print(f"\nFound {len(sccs)} strongly connected component(s):\n")
    for i, scc in enumerate(sccs, 1):
        # Sort for consistent display
        scc_sorted = sorted(scc)
        print(f"  SCC {i}: {scc_sorted}")
        
        # Show which nodes form cycles vs singleton nodes
        if len(scc) > 1:
            print(f"         → These {len(scc)} nodes form a cycle")
        else:
            print(f"         → Singleton (no cycle)")
    
    # Demonstrate with a more complex example
    print("\n" + "="*50)
    print("\nTesting with a larger graph (simulating package dependencies):\n")
    
    # Simulating a dependency graph where packages can have circular deps
    dependency_graph = {
        'core': ['utils'],
        'utils': [],
        'api': ['core', 'auth'],
        'auth': ['core', 'crypto'],
        'crypto': ['utils'],
        'web': ['api', 'templates'],
        'templates': ['web'],  # Circular dependency!
        'cli': ['api', 'utils'],
    }
    
    # Convert string keys to integers for compatibility
    node_names = sorted(dependency_graph.keys())
    name_to_id = {name: i for i, name in enumerate(node_names)}
    id_to_name = {i: name for name, i in name_to_id.items()}
    
    int_graph = {
        name_to_id[src]: [name_to_id[dst] for dst in dsts]
        for src, dsts in dependency_graph.items()
    }
    
    tarjan2 = TarjanSCC(int_graph)
    sccs2 = tarjan2.find_sccs()
    
    print("Package dependencies:")
    for pkg, deps in sorted(dependency_graph.items()):
        print(f"  {pkg:12} depends on: {deps if deps else '(nothing)'}")
    
    print(f"\nDependency analysis - found {len(sccs2)} component(s):\n")
    for i, scc in enumerate(sccs2, 1):
        pkg_names = [id_to_name[node] for node in scc]
        if len(pkg_names) > 1:
            print(f"  ⚠️  Circular dependency detected: {sorted(pkg_names)}")
        else:
            print(f"  ✓   Clean: {pkg_names[0]}")
    
    print("\nDone! Tarjan's algorithm is O(V + E) — pretty efficient.")