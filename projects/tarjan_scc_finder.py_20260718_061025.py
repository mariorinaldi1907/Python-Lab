"""
Date: 2026-07-18
Built Tarjan's SCC algorithm because I needed to understand circular dependencies in directed graphs — uses DFS with a stack to find all strongly connected components in linear time.
"""

#!/usr/bin/env python3
"""
Tarjan's algorithm for finding strongly connected components (SCCs) in a directed graph.
I wanted something that could help me visualize dependency cycles in complex systems.
This runs in O(V + E) time which is pretty sweet for graph analysis.
"""

from collections import defaultdict


class TarjanSCC:
    """
    Finds all strongly connected components using Tarjan's algorithm.
    
    A strongly connected component is a maximal set of vertices where
    every vertex is reachable from every other vertex in the set.
    """
    
    def __init__(self, graph):
        """
        Initialize with a directed graph.
        
        Args:
            graph: dict mapping vertices to lists of neighbors
        """
        self.graph = graph
        self.index_counter = 0
        self.stack = []
        self.lowlinks = {}  # lowest index reachable from this vertex
        self.index = {}  # discovery time of each vertex
        self.on_stack = set()
        self.sccs = []
    
    def find_sccs(self):
        """
        Main entry point - finds all SCCs in the graph.
        
        Returns:
            List of SCCs, where each SCC is a list of vertices
        """
        # Need to check all vertices because graph might be disconnected
        for vertex in self.graph:
            if vertex not in self.index:
                self._strongconnect(vertex)
        
        return self.sccs
    
    def _strongconnect(self, vertex):
        """
        Recursive DFS that does the actual work of finding SCCs.
        
        The algorithm maintains a stack of vertices that might be in the
        current SCC. When we find a root of an SCC (lowlink == index),
        we pop everything above it off the stack - that's our SCC.
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
                # Neighbor hasn't been visited yet - recurse on it
                self._strongconnect(neighbor)
                # After recursion, update our lowlink based on what we learned
                self.lowlinks[vertex] = min(self.lowlinks[vertex], 
                                           self.lowlinks[neighbor])
            elif neighbor in self.on_stack:
                # Neighbor is in current SCC (back edge found!)
                # Update lowlink to the neighbor's index since it's reachable
                self.lowlinks[vertex] = min(self.lowlinks[vertex], 
                                           self.index[neighbor])
        
        # If this vertex is a root of an SCC, pop the SCC off the stack
        if self.lowlinks[vertex] == self.index[vertex]:
            scc = []
            while True:
                node = self.stack.pop()
                self.on_stack.remove(node)
                scc.append(node)
                if node == vertex:
                    break
            self.sccs.append(scc)


def build_sample_graph():
    """
    Creates a sample directed graph with some interesting cycles.
    
    This represents a dependency graph where edges mean "depends on".
    There are a few cycles in here that should be detected as SCCs.
    """
    graph = {
        'A': ['B'],
        'B': ['C', 'E'],
        'C': ['D'],
        'D': ['B'],  # B-C-D forms a cycle
        'E': ['F', 'A'],  # E-A-B-E forms a larger cycle
        'F': ['G'],
        'G': ['E'],  # E-F-G forms a cycle
        'H': ['I'],  # Separate component
        'I': ['H'],  # H-I forms a cycle
        'J': [],  # Singleton (no outgoing edges)
    }
    return graph


if __name__ == "__main__":
    print("Tarjan's Algorithm - Finding Strongly Connected Components")
    print("=" * 60)
    
    # Build and display the graph
    graph = build_sample_graph()
    print("\nInput Graph (adjacency list):")
    for vertex, neighbors in sorted(graph.items()):
        print(f"  {vertex} -> {neighbors}")
    
    # Find SCCs
    tarjan = TarjanSCC(graph)
    sccs = tarjan.find_sccs()
    
    print(f"\nFound {len(sccs)} strongly connected components:")
    print()
    
    # Print each SCC with some context
    for i, scc in enumerate(sccs, 1):
        scc_sorted = sorted(scc)
        print(f"SCC #{i}: {scc_sorted}")
        
        # Show why this is an SCC (what edges exist within it)
        if len(scc) > 1:
            internal_edges = []
            for vertex in scc:
                for neighbor in graph.get(vertex, []):
                    if neighbor in scc:
                        internal_edges.append(f"{vertex}->{neighbor}")
            if internal_edges:
                print(f"  Internal edges: {', '.join(internal_edges)}")
        else:
            print(f"  (singleton - no cycles)")
        print()
    
    # Some interesting analysis
    cyclic_components = [scc for scc in sccs if len(scc) > 1]
    if cyclic_components:
        print(f"⚠️  Found {len(cyclic_components)} component(s) with cycles!")
        print("These represent circular dependencies that might need attention.")
    else:
        print("✓ No cycles found - this is a DAG (Directed Acyclic Graph)")