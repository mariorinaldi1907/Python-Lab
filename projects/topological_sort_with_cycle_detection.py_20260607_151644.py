"""
Date: 2026-06-07
Built a topological sort algorithm that detects cycles and returns a valid ordering for DAGs — wanted to finally understand how build systems resolve dependencies.
"""

#!/usr/bin/env python3
"""
Topological sort implementation using depth-first search.
Detects cycles and returns None if the graph isn't a DAG.
I built this to understand how dependency resolution works in build tools.
"""

from collections import defaultdict, deque
from enum import Enum


class NodeState(Enum):
    """Track visit state during DFS to detect cycles."""
    UNVISITED = 0
    VISITING = 1  # Currently in the DFS stack — if we see this again, it's a cycle
    VISITED = 2


class DirectedGraph:
    """
    A directed graph for topological sorting.
    Uses adjacency list representation because it's memory-efficient for sparse graphs.
    """
    
    def __init__(self):
        self.adj_list = defaultdict(list)
        self.nodes = set()
    
    def add_edge(self, from_node, to_node):
        """Add a directed edge from from_node to to_node."""
        self.adj_list[from_node].append(to_node)
        self.nodes.add(from_node)
        self.nodes.add(to_node)
    
    def topological_sort(self):
        """
        Perform topological sort using DFS.
        
        Returns:
            list: Nodes in topological order, or None if a cycle exists.
        
        The algorithm works by doing a DFS and adding nodes to the result
        *after* visiting all their dependencies. This ensures dependencies
        come before dependents in the final ordering.
        """
        state = {node: NodeState.UNVISITED for node in self.nodes}
        result = deque()  # Using deque because we'll prepend (appendleft)
        
        def dfs(node):
            """
            Recursive DFS helper.
            Returns False if a cycle is detected, True otherwise.
            """
            if state[node] == NodeState.VISITING:
                # We've encountered a node that's currently being explored
                # This means we've found a back edge, aka a cycle
                return False
            
            if state[node] == NodeState.VISITED:
                # Already processed this node completely
                return True
            
            state[node] = NodeState.VISITING
            
            # Visit all neighbors
            for neighbor in self.adj_list[node]:
                if not dfs(neighbor):
                    return False
            
            state[node] = NodeState.VISITED
            # Add to result after all dependencies are processed
            # Using appendleft because we want reverse postorder
            result.appendleft(node)
            return True
        
        # Try to visit all nodes in case graph is disconnected
        for node in self.nodes:
            if state[node] == NodeState.UNVISITED:
                if not dfs(node):
                    return None  # Cycle detected
        
        return list(result)
    
    def has_cycle(self):
        """Check if the graph contains a cycle."""
        return self.topological_sort() is None


def build_dependency_graph():
    """
    Build a sample dependency graph for a hypothetical build system.
    Think of it like: to build 'app', you first need 'compile' and 'link', etc.
    """
    g = DirectedGraph()
    
    # Build dependencies (A -> B means "B depends on A" or "A must come before B")
    g.add_edge('fetch_deps', 'compile')
    g.add_edge('compile', 'link')
    g.add_edge('link', 'package')
    g.add_edge('package', 'deploy')
    g.add_edge('run_tests', 'deploy')
    g.add_edge('compile', 'run_tests')
    g.add_edge('fetch_deps', 'generate_code')
    g.add_edge('generate_code', 'compile')
    
    return g


def build_cyclic_graph():
    """Build a graph with a cycle to demonstrate cycle detection."""
    g = DirectedGraph()
    
    g.add_edge('A', 'B')
    g.add_edge('B', 'C')
    g.add_edge('C', 'D')
    g.add_edge('D', 'B')  # Creates cycle: B -> C -> D -> B
    
    return g


if __name__ == "__main__":
    print("=== Topological Sort Demo ===\n")
    
    # Test 1: Valid DAG (build system dependencies)
    print("Test 1: Build system dependency graph (DAG)")
    print("-" * 50)
    dag = build_dependency_graph()
    
    result = dag.topological_sort()
    if result:
        print("✓ Valid topological ordering found:")
        for i, task in enumerate(result, 1):
            print(f"  {i}. {task}")
    else:
        print("✗ Cycle detected — no valid ordering exists")
    
    print("\n")
    
    # Test 2: Graph with cycle
    print("Test 2: Graph with a cycle")
    print("-" * 50)
    cyclic = build_cyclic_graph()
    
    result = cyclic.topological_sort()
    if result:
        print("✓ Valid topological ordering found:")
        for i, node in enumerate(result, 1):
            print(f"  {i}. {node}")
    else:
        print("✗ Cycle detected — no valid ordering exists")
        print("  (Expected: graph has cycle B -> C -> D -> B)")
    
    print("\n")
    
    # Test 3: Simple linear chain
    print("Test 3: Simple linear dependency chain")
    print("-" * 50)
    linear = DirectedGraph()
    linear.add_edge('step1', 'step2')
    linear.add_edge('step2', 'step3')
    linear.add_edge('step3', 'step4')
    
    result = linear.topological_sort()
    if result:
        print("✓ Valid topological ordering found:")
        print(f"  {' -> '.join(result)}")
    else:
        print("✗ Cycle detected")
    
    print("\n")
    
    # Test 4: Disconnected components
    print("Test 4: Graph with disconnected components")
    print("-" * 50)
    disconnected = DirectedGraph()
    disconnected.add_edge('A', 'B')
    disconnected.add_edge('B', 'C')
    disconnected.add_edge('X', 'Y')
    disconnected.add_edge('Y', 'Z')
    
    result = disconnected.topological_sort()
    if result:
        print("✓ Valid topological ordering found:")
        print(f"  {result}")
        print("  (Note: disconnected components can appear in any relative order)")
    else:
        print("✗ Cycle detected")