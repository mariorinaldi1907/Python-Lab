"""
Date: 2026-08-26
Built Tarjan's algorithm to find strongly connected components in directed graphs — uses DFS with low-link values to detect cycles and component boundaries in one pass.
"""

"""
Tarjan's algorithm for finding strongly connected components (SCCs) in a directed graph.

I've always found this algorithm elegant — it does everything in a single DFS pass
by tracking discovery times and low-link values. Way cooler than running Kosaraju's
which needs two full passes through the graph.
"""

from collections import defaultdict


class TarjanSCC:
    """
    Finds strongly connected components using Tarjan's algorithm.
    
    A strongly connected component is a maximal set of vertices where
    every vertex is reachable from every other vertex in the set.
    """
    
    def __init__(self, graph):
        """
        Initialize with a directed graph.
        
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
            List of SCCs, where each SCC is a list of vertices
        """
        # Need to check every vertex in case graph is disconnected
        for vertex in self.graph:
            if vertex not in self.index:
                self._strongconnect(vertex)
        
        return self.sccs
    
    def _strongconnect(self, vertex):
        """
        Recursive DFS that tracks low-link values to identify SCCs.
        
        The low-link value is the smallest index reachable from this vertex.
        When a vertex's low-link equals its index, it's the root of an SCC.
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
                # After returning, update our low-link if neighbor found something lower
                self.lowlinks[vertex] = min(self.lowlinks[vertex], self.lowlinks[neighbor])
            elif neighbor in self.on_stack:
                # Neighbor is on stack, meaning it's in the current SCC being explored
                # Update low-link to indicate we can reach that earlier vertex
                self.lowlinks[vertex] = min(self.lowlinks[vertex], self.index[neighbor])
        
        # If this vertex is a root node (low-link == index), pop the SCC off the stack
        if self.lowlinks[vertex] == self.index[vertex]:
            scc = []
            while True:
                node = self.stack.pop()
                self.on_stack.remove(node)
                scc.append(node)
                if node == vertex:
                    break
            self.sccs.append(scc)


def build_example_graph():
    """
    Create a directed graph with multiple SCCs for demonstration.
    
    This graph has 3 SCCs: [0,1,2], [3], [4,5,6]
    """
    graph = {
        0: [1],
        1: [2],
        2: [0],      # Forms cycle with 0,1,2
        3: [1, 2],   # Points into first SCC but isn't part of it
        4: [3, 5],
        5: [6],
        6: [4],      # Forms cycle with 4,5,6
    }
    return graph


def print_graph(graph):
    """Pretty print the graph structure."""
    print("Graph structure:")
    for vertex in sorted(graph.keys()):
        neighbors = graph[vertex]
        print(f"  {vertex} -> {neighbors}")
    print()


def visualize_sccs(sccs):
    """Print the discovered SCCs in a readable format."""
    print(f"Found {len(sccs)} strongly connected component(s):")
    for i, scc in enumerate(sccs, 1):
        # Sort for consistent output
        scc_sorted = sorted(scc)
        print(f"  SCC {i}: {scc_sorted}")
        # A single-node SCC with no self-loop is trivial
        if len(scc) == 1:
            print(f"         (trivial - single vertex)")
        else:
            print(f"         (non-trivial - contains cycles)")


if __name__ == "__main__":
    print("=== Tarjan's SCC Algorithm Demo ===\n")
    
    # Build and display the example graph
    graph = build_example_graph()
    print_graph(graph)
    
    # Run Tarjan's algorithm
    tarjan = TarjanSCC(graph)
    sccs = tarjan.find_sccs()
    
    # Show results
    visualize_sccs(sccs)
    
    print("\n--- Testing with a more complex graph ---\n")
    
    # Another example: a graph with self-loops and isolated components
    complex_graph = {
        0: [1],
        1: [2, 3],
        2: [0],      # Cycle: 0->1->2->0
        3: [4],
        4: [5],
        5: [3],      # Cycle: 3->4->5->3
        6: [6],      # Self-loop
        7: [8],
        8: [],       # Dead end
    }
    
    print_graph(complex_graph)
    
    tarjan2 = TarjanSCC(complex_graph)
    sccs2 = tarjan2.find_sccs()
    visualize_sccs(sccs2)
    
    print("\nNote: SCCs are found in reverse topological order of the condensation graph!")