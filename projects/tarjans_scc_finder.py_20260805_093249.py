"""
Date: 2026-08-05
Built Tarjan's SCC algorithm because I wanted to understand how dependency analyzers detect circular imports in codebases.
"""

"""
Tarjan's Algorithm for finding Strongly Connected Components (SCCs) in directed graphs.

I wrote this to better understand how build systems and package managers detect
circular dependencies. Tarjan's is elegant because it does everything in one DFS pass.
"""

from collections import defaultdict


class TarjanSCC:
    """
    Implements Tarjan's algorithm for finding strongly connected components.
    
    A strongly connected component is a maximal set of vertices where every vertex
    is reachable from every other vertex in the set.
    """
    
    def __init__(self, graph):
        """
        Initialize the algorithm with a directed graph.
        
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
            List of lists, where each inner list is a strongly connected component.
        """
        # Need to check all vertices since graph might be disconnected
        for vertex in self.graph:
            if vertex not in self.index:
                self._strongconnect(vertex)
        
        return self.sccs
    
    def _strongconnect(self, vertex):
        """
        Recursive DFS helper that does the heavy lifting.
        
        The algorithm maintains two indices per vertex:
        - index: discovery time (when we first visit it)
        - lowlink: smallest index reachable from this vertex
        
        When index == lowlink, we've found the root of an SCC.
        """
        # Set the depth index for this vertex
        self.index[vertex] = self.index_counter
        self.lowlinks[vertex] = self.index_counter
        self.index_counter += 1
        self.stack.append(vertex)
        self.on_stack.add(vertex)
        
        # Consider successors of vertex
        for successor in self.graph.get(vertex, []):
            if successor not in self.index:
                # Successor hasn't been visited yet, recurse
                self._strongconnect(successor)
                # After returning, check if we found a lower lowlink
                self.lowlinks[vertex] = min(self.lowlinks[vertex], self.lowlinks[successor])
            elif successor in self.on_stack:
                # Successor is on stack, so it's in the current SCC
                # Update lowlink to its index (not lowlink, important distinction!)
                self.lowlinks[vertex] = min(self.lowlinks[vertex], self.index[successor])
        
        # If vertex is a root node, pop the stack to get the SCC
        if self.lowlinks[vertex] == self.index[vertex]:
            scc = []
            while True:
                w = self.stack.pop()
                self.on_stack.remove(w)
                scc.append(w)
                if w == vertex:
                    break
            self.sccs.append(scc)


def build_sample_graph():
    """
    Create a sample directed graph with multiple SCCs.
    
    This graph has 3 strongly connected components:
    - {0, 1, 2} form a cycle
    - {3, 4} form a cycle
    - {5} is alone (no self-loop)
    """
    graph = {
        0: [1],
        1: [2],
        2: [0],      # Cycle: 0 -> 1 -> 2 -> 0
        3: [4],
        4: [3, 5],   # Cycle: 3 -> 4 -> 3, plus edge to 5
        5: [],       # Dead end
    }
    return graph


def build_dependency_graph():
    """
    Create a graph representing a circular dependency scenario.
    
    Think of this as Python modules importing each other:
    - auth imports database and user
    - database imports models
    - models imports auth (circular!)
    - user imports models
    """
    modules = {
        'auth': ['database', 'user'],
        'database': ['models'],
        'models': ['auth'],  # Creates a cycle
        'user': ['models'],
        'config': [],  # Standalone module
    }
    return modules


if __name__ == "__main__":
    print("=" * 60)
    print("Tarjan's SCC Algorithm Demo")
    print("=" * 60)
    
    # Demo 1: Simple numbered graph
    print("\n1. Simple Graph (numbered vertices):")
    graph1 = build_sample_graph()
    
    print("\nGraph structure:")
    for vertex, edges in sorted(graph1.items()):
        print(f"  {vertex} -> {edges}")
    
    tarjan1 = TarjanSCC(graph1)
    sccs1 = tarjan1.find_sccs()
    
    print(f"\nFound {len(sccs1)} strongly connected components:")
    for i, scc in enumerate(sccs1, 1):
        print(f"  SCC {i}: {scc}")
    
    # Demo 2: Dependency graph (more realistic)
    print("\n" + "=" * 60)
    print("\n2. Module Dependency Graph:")
    graph2 = build_dependency_graph()
    
    print("\nModule imports:")
    for module, imports in sorted(graph2.items()):
        if imports:
            print(f"  {module} imports: {', '.join(imports)}")
        else:
            print(f"  {module} imports: (none)")
    
    tarjan2 = TarjanSCC(graph2)
    sccs2 = tarjan2.find_sccs()
    
    print(f"\nFound {len(sccs2)} strongly connected components:")
    for i, scc in enumerate(sccs2, 1):
        if len(scc) > 1:
            print(f"  SCC {i}: {scc} ⚠️  CIRCULAR DEPENDENCY!")
        else:
            print(f"  SCC {i}: {scc}")
    
    print("\n" + "=" * 60)
    print("\nKey insight: SCCs with multiple nodes indicate circular dependencies")
    print("in build systems, package managers, or module import chains.")
    print("=" * 60)