"""
Date: 2026-07-05
Built Tarjan's SCC algorithm from scratch to find strongly connected components in directed graphs — useful for cycle detection and analyzing dependencies.
"""

"""
Tarjan's algorithm for finding strongly connected components in a directed graph.
I wanted something efficient for detecting cycles in dependency graphs, and
Tarjan's single-pass approach seemed elegant. Uses DFS with a stack to track
the component being built.
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
        Initialize with a graph represented as an adjacency list.
        
        Args:
            graph: dict mapping vertex -> list of neighbors
        """
        self.graph = graph
        self.index_counter = 0
        self.stack = []
        self.lowlinks = {}  # Tracks the smallest index reachable from this node
        self.index = {}     # Discovery time of each node
        self.on_stack = set()
        self.sccs = []
        
    def find_sccs(self):
        """
        Find all strongly connected components in the graph.
        
        Returns:
            list of lists, where each inner list is a strongly connected component
        """
        # Run DFS from every unvisited node
        for vertex in self.graph:
            if vertex not in self.index:
                self._strongconnect(vertex)
        
        return self.sccs
    
    def _strongconnect(self, vertex):
        """
        Recursive DFS helper that builds SCCs using low-link values.
        
        The low-link value is the smallest index of any node reachable from this
        vertex, including the vertex itself. When a vertex's low-link equals its
        index, we've found the root of an SCC.
        """
        # Set the depth index for vertex
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
                # Update low-link after returning from recursion
                self.lowlinks[vertex] = min(self.lowlinks[vertex], 
                                           self.lowlinks[neighbor])
            elif neighbor in self.on_stack:
                # Neighbor is in the current SCC being built
                self.lowlinks[vertex] = min(self.lowlinks[vertex], 
                                           self.index[neighbor])
        
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
    Check if a directed graph has any cycles.
    
    A cycle exists if any SCC has more than one node, or if any single-node
    SCC has a self-loop.
    
    Args:
        graph: adjacency list representation
        
    Returns:
        bool indicating whether the graph contains a cycle
    """
    tarjan = TarjanSCC(graph)
    sccs = tarjan.find_sccs()
    
    for scc in sccs:
        if len(scc) > 1:
            return True
        # Check for self-loop
        if len(scc) == 1 and scc[0] in graph.get(scc[0], []):
            return True
    
    return False


if __name__ == "__main__":
    # Example 1: Simple graph with one SCC
    print("Example 1: Triangle cycle")
    graph1 = {
        'A': ['B'],
        'B': ['C'],
        'C': ['A'],
        'D': ['E'],
        'E': []
    }
    
    tarjan1 = TarjanSCC(graph1)
    sccs1 = tarjan1.find_sccs()
    print(f"Graph: {graph1}")
    print(f"SCCs found: {sccs1}")
    print(f"Has cycle: {has_cycle(graph1)}")
    print()
    
    # Example 2: More complex graph with multiple SCCs
    print("Example 2: Complex dependency graph")
    graph2 = {
        1: [2],
        2: [3],
        3: [1],      # Creates SCC {1, 2, 3}
        4: [2, 3, 5],
        5: [4, 6],   # Creates SCC {4, 5}
        6: [3, 7],
        7: [6],      # Creates SCC {6, 7}
        8: [7, 5]
    }
    
    tarjan2 = TarjanSCC(graph2)
    sccs2 = tarjan2.find_sccs()
    print(f"SCCs found: {sccs2}")
    print(f"Number of components: {len(sccs2)}")
    print(f"Has cycle: {has_cycle(graph2)}")
    print()
    
    # Example 3: DAG (no cycles)
    print("Example 3: Directed acyclic graph")
    graph3 = {
        'A': ['B', 'C'],
        'B': ['D'],
        'C': ['D'],
        'D': []
    }
    
    tarjan3 = TarjanSCC(graph3)
    sccs3 = tarjan3.find_sccs()
    print(f"Graph: {graph3}")
    print(f"SCCs found: {sccs3}")
    print(f"Has cycle: {has_cycle(graph3)}")
```