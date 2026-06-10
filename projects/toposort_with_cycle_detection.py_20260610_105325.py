"""
Date: 2026-06-10
Built a topological sort algorithm that detects cycles in directed graphs — useful for dependency resolution and build systems.
"""

#!/usr/bin/env python3
"""
Topological Sort with Cycle Detection

I needed this for a personal project where I was resolving task dependencies.
Turns out topological sort is perfect for that — it orders nodes in a DAG so
that for every edge u -> v, u comes before v in the ordering.

The catch: if there's a cycle, no valid ordering exists. So I added cycle
detection using DFS with three states (unvisited, visiting, visited).
"""

from collections import defaultdict, deque
from enum import Enum


class NodeState(Enum):
    """Track node states during DFS traversal."""
    UNVISITED = 0
    VISITING = 1   # Currently in the DFS stack — if we see this again, it's a cycle
    VISITED = 2    # Fully processed


class DirectedGraph:
    """
    A simple directed graph implementation for topological sorting.
    
    I'm using an adjacency list because it's memory-efficient for sparse graphs,
    which is what you usually get with dependency graphs.
    """
    
    def __init__(self):
        self.graph = defaultdict(list)
        self.nodes = set()
    
    def add_edge(self, from_node, to_node):
        """Add a directed edge from from_node to to_node."""
        self.graph[from_node].append(to_node)
        self.nodes.add(from_node)
        self.nodes.add(to_node)
    
    def _dfs_visit(self, node, state, stack, has_cycle):
        """
        Recursive DFS helper that detects cycles and builds the topological order.
        
        The key insight: if we encounter a node in VISITING state, we've found
        a back edge, which means there's a cycle. I use a list for has_cycle
        because Python doesn't have nice mutable bool references.
        """
        state[node] = NodeState.VISITING
        
        for neighbor in self.graph[node]:
            if state[neighbor] == NodeState.VISITING:
                # Back edge detected — we're revisiting a node in our current path
                has_cycle[0] = True
                return
            elif state[neighbor] == NodeState.UNVISITED:
                self._dfs_visit(neighbor, state, stack, has_cycle)
                if has_cycle[0]:
                    return
        
        state[node] = NodeState.VISITED
        stack.append(node)  # Add to stack after all descendants are processed
    
    def topological_sort(self):
        """
        Perform topological sort using DFS.
        
        Returns:
            list: Nodes in topological order, or None if the graph contains a cycle.
        
        The algorithm works by doing a DFS and adding nodes to a stack in
        post-order (i.e., after visiting all descendants). Then we reverse
        the stack to get the topological order.
        """
        state = {node: NodeState.UNVISITED for node in self.nodes}
        stack = []
        has_cycle = [False]  # Using list as mutable container
        
        for node in self.nodes:
            if state[node] == NodeState.UNVISITED:
                self._dfs_visit(node, state, stack, has_cycle)
                if has_cycle[0]:
                    return None  # Graph has a cycle, can't be topologically sorted
        
        # The stack is in reverse topological order, so reverse it
        return stack[::-1]
    
    def kahn_topological_sort(self):
        """
        Alternative implementation using Kahn's algorithm (BFS-based).
        
        Returns:
            list: Nodes in topological order, or None if the graph contains a cycle.
        
        I like this one for its simplicity — repeatedly remove nodes with no
        incoming edges. If we can't remove all nodes, there must be a cycle.
        """
        # Calculate in-degrees
        in_degree = {node: 0 for node in self.nodes}
        for node in self.graph:
            for neighbor in self.graph[node]:
                in_degree[neighbor] += 1
        
        # Start with nodes that have no incoming edges
        queue = deque([node for node in self.nodes if in_degree[node] == 0])
        result = []
        
        while queue:
            node = queue.popleft()
            result.append(node)
            
            # Remove this node's edges and check if neighbors now have in-degree 0
            for neighbor in self.graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # If we processed all nodes, we have a valid ordering
        if len(result) == len(self.nodes):
            return result
        else:
            return None  # Cycle detected


def demo_build_system():
    """Simulate a simple build system with file dependencies."""
    print("=== Build System Dependency Resolution ===\n")
    
    # Create a dependency graph for compiling a simple project
    # Edge A -> B means "A depends on B" (B must be built before A)
    graph = DirectedGraph()
    graph.add_edge("main.o", "utils.o")
    graph.add_edge("main.o", "config.o")
    graph.add_edge("app", "main.o")
    graph.add_edge("app", "logger.o")
    graph.add_edge("logger.o", "config.o")
    
    print("Dependencies:")
    for node in sorted(graph.graph.keys()):
        deps = ", ".join(graph.graph[node])
        print(f"  {node} -> {deps}")
    
    print("\nBuild order (DFS-based):")
    order = graph.topological_sort()
    if order:
        print(" ", " -> ".join(order))
    else:
        print("  ERROR: Circular dependency detected!")
    
    print("\nBuild order (Kahn's algorithm):")
    order_kahn = graph.kahn_topological_sort()
    if order_kahn:
        print(" ", " -> ".join(order_kahn))
    else:
        print("  ERROR: Circular dependency detected!")


def demo_circular_dependency():
    """Show what happens when there's a cycle in the graph."""
    print("\n\n=== Circular Dependency Detection ===\n")
    
    graph = DirectedGraph()
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    graph.add_edge("C", "A")  # This creates a cycle!
    graph.add_edge("D", "B")
    
    print("Dependencies:")
    for node in sorted(graph.graph.keys()):
        deps = ", ".join(graph.graph[node])
        print(f"  {node} -> {deps}")
    
    print("\nAttempting topological sort (DFS):")
    order = graph.topological_sort()
    if order:
        print(" ", " -> ".join(order))
    else:
        print("  ❌ Cannot sort: cycle detected (A -> B -> C -> A)")
    
    print("\nAttempting topological sort (Kahn):")
    order_kahn = graph.kahn_topological_sort()
    if order_kahn:
        print(" ", " -> ".join(order_kahn))
    else:
        print("  ❌ Cannot sort: cycle detected")


if __name__ == "__main__":
    demo_build_system()
    demo_circular_dependency()