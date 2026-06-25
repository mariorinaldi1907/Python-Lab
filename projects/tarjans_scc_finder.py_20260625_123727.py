"""
Date: 2026-06-25
Built Tarjan's SCC algorithm because I wanted to understand how compilers detect cyclic dependencies in module graphs.
"""

"""
Tarjan's algorithm for finding strongly connected components in a directed graph.
I coded this after reading about how build systems detect circular dependencies.
The algorithm is elegant — single DFS pass with a stack to track components.
"""

from collections import defaultdict


class TarjanSCC:
    """
    Find all strongly connected components in a directed graph using Tarjan's algorithm.
    
    A strongly connected component is a maximal set of vertices where every vertex
    is reachable from every other vertex in the set. This is super useful for
    detecting cycles and understanding graph structure.
    """
    
    def __init__(self, graph):
        """
        Initialize the SCC finder.
        
        Args:
            graph: dict mapping vertex -> list of neighbors (adjacency list)
        """
        self.graph = graph
        self.index_counter = 0
        self.stack = []
        self.lowlinks = {}  # Smallest index reachable from this node
        self.index = {}     # Discovery time of each node
        self.on_stack = set()
        self.sccs = []
        
    def find_sccs(self):
        """
        Main entry point. Returns list of SCCs (each SCC is a list of vertices).
        
        I run DFS from every unvisited node because the graph might be disconnected.
        """
        for vertex in self.graph:
            if vertex not in self.index:
                self._strong_connect(vertex)
        return self.sccs
    
    def _strong_connect(self, vertex):
        """
        Recursive DFS that does the heavy lifting.
        
        The key insight: we track the lowest index reachable from each vertex.
        When a vertex's lowlink equals its index, we've found an SCC root.
        """
        # Set the depth index for this vertex
        self.index[vertex] = self.index_counter
        self.lowlinks[vertex] = self.index_counter
        self.index_counter += 1
        self.stack.append(vertex)
        self.on_stack.add(vertex)
        
        # Consider successors of vertex
        if vertex in self.graph:
            for neighbor in self.graph[vertex]:
                if neighbor not in self.index:
                    # Neighbor not yet visited, recurse on it
                    self._strong_connect(neighbor)
                    # Update lowlink after returning from recursion
                    self.lowlinks[vertex] = min(self.lowlinks[vertex], 
                                               self.lowlinks[neighbor])
                elif neighbor in self.on_stack:
                    # Neighbor is in the current SCC (back edge found)
                    self.lowlinks[vertex] = min(self.lowlinks[vertex], 
                                               self.index[neighbor])
        
        # If vertex is a root node, pop the stack to get the SCC
        if self.lowlinks[vertex] == self.index[vertex]:
            component = []
            while True:
                node = self.stack.pop()
                self.on_stack.remove(node)
                component.append(node)
                if node == vertex:
                    break
            self.sccs.append(component)


def build_sample_graph():
    """
    Creates a test graph with some interesting SCCs.
    
    This graph has:
    - A 3-node cycle (0, 1, 2)
    - A 2-node cycle (3, 4)
    - A single node component (5)
    - Some connections between components
    """
    graph = {
        0: [1],
        1: [2],
        2: [0, 3],    # Back edge to 0 (cycle), forward to 3
        3: [4],
        4: [3, 5],    # Back edge to 3 (cycle), forward to 5
        5: [],        # Sink node
    }
    return graph


def visualize_graph(graph):
    """Pretty print the graph structure."""
    print("Graph structure (adjacency list):")
    for vertex in sorted(graph.keys()):
        neighbors = graph[vertex]
        arrow = ' -> ' if neighbors else ' (no outgoing edges)'
        print(f"  {vertex}{arrow}{neighbors if neighbors else ''}")
    print()


if __name__ == "__main__":
    print("=== Tarjan's Strongly Connected Components Finder ===\n")
    
    # Build and display the test graph
    graph = build_sample_graph()
    visualize_graph(graph)
    
    # Find SCCs
    tarjan = TarjanSCC(graph)
    sccs = tarjan.find_sccs()
    
    print(f"Found {len(sccs)} strongly connected component(s):\n")
    for i, component in enumerate(sccs, 1):
        # Sort for consistent display (the algorithm order is arbitrary)
        component_sorted = sorted(component)
        size = len(component)
        cycle_info = " (contains cycle)" if size > 1 else ""
        print(f"  SCC #{i}: {component_sorted}{cycle_info}")
    
    print("\n--- Testing another graph with complex cycles ---\n")
    
    # More complex example: a graph resembling a module dependency nightmare
    complex_graph = {
        'main': ['utils', 'config'],
        'utils': ['helpers'],
        'helpers': ['utils'],      # Mutual dependency (bad practice!)
        'config': ['parser'],
        'parser': ['validator'],
        'validator': ['parser'],   # Another cycle
        'db': ['models'],
        'models': [],
    }
    
    visualize_graph(complex_graph)
    
    tarjan2 = TarjanSCC(complex_graph)
    sccs2 = tarjan2.find_sccs()
    
    print(f"Found {len(sccs2)} strongly connected component(s):\n")
    for i, component in enumerate(sccs2, 1):
        component_sorted = sorted(component)
        size = len(component)
        if size > 1:
            print(f"  SCC #{i}: {component_sorted} ⚠️  CIRCULAR DEPENDENCY DETECTED")
        else:
            print(f"  SCC #{i}: {component_sorted}")
    
    print("\nNote: In real build systems, circular dependencies are often errors!")
    print("Each SCC with >1 node represents modules that depend on each other.")