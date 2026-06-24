"""
Date: 2026-06-24
Built a topological sort algorithm to handle dependency ordering problems, with proper cycle detection so it won't get stuck on circular dependencies.
"""

#!/usr/bin/env python3
"""
Topological Sort with Cycle Detection

I wrote this to solve dependency ordering problems — like figuring out
which courses to take first, or which build targets depend on others.
Uses DFS with a three-color marking system to detect cycles cleanly.
"""

from collections import defaultdict
from enum import Enum


class NodeState(Enum):
    """Track visit state during DFS traversal."""
    UNVISITED = 0
    VISITING = 1  # Currently in the DFS stack — if we see this again, it's a cycle
    VISITED = 2   # Completely processed


class DirectedGraph:
    """
    A simple directed graph representation for topological sorting.
    
    I went with an adjacency list because it's memory-efficient for sparse graphs,
    which is what you usually see in dependency problems.
    """
    
    def __init__(self):
        self.adjacency_list = defaultdict(list)
        self.nodes = set()
    
    def add_edge(self, from_node, to_node):
        """Add a directed edge from from_node -> to_node."""
        self.adjacency_list[from_node].append(to_node)
        self.nodes.add(from_node)
        self.nodes.add(to_node)
    
    def get_neighbors(self, node):
        """Get all nodes that this node points to."""
        return self.adjacency_list[node]
    
    def get_all_nodes(self):
        """Return all nodes in the graph."""
        return self.nodes


def topological_sort(graph):
    """
    Perform topological sort using DFS.
    
    Returns a list of nodes in topological order (dependencies first),
    or None if a cycle is detected.
    
    The three-color approach:
    - WHITE (UNVISITED): haven't seen this node yet
    - GRAY (VISITING): currently exploring this node's descendants
    - BLACK (VISITED): done with this node and all its descendants
    
    If we encounter a GRAY node during DFS, we've found a back edge = cycle.
    """
    state = {node: NodeState.UNVISITED for node in graph.get_all_nodes()}
    result = []
    cycle_detected = False
    
    def dfs(node):
        """
        Recursive DFS that builds the topological order.
        
        I'm using nonlocal here because I need to flag cycles from within
        the recursion without throwing exceptions everywhere.
        """
        nonlocal cycle_detected
        
        if cycle_detected:
            return
        
        if state[node] == NodeState.VISITING:
            # We're visiting a node that's already in our current path — cycle!
            cycle_detected = True
            return
        
        if state[node] == NodeState.VISITED:
            # Already processed this entire subtree
            return
        
        state[node] = NodeState.VISITING
        
        # Visit all neighbors first (dependencies)
        for neighbor in graph.get_neighbors(node):
            dfs(neighbor)
            if cycle_detected:
                return
        
        state[node] = NodeState.VISITED
        # Add to result AFTER visiting all descendants
        # This ensures dependencies come before dependents
        result.append(node)
    
    # Try starting DFS from each unvisited node
    # This handles disconnected components in the graph
    for node in graph.get_all_nodes():
        if state[node] == NodeState.UNVISITED:
            dfs(node)
            if cycle_detected:
                return None
    
    # Reverse because we added nodes in post-order
    # (leaves first, roots last), but we want roots first
    return list(reversed(result))


def find_cycle(graph):
    """
    Find and return a cycle in the graph if one exists.
    
    This is mostly for debugging — helps you understand WHY the sort failed.
    Returns a list of nodes forming a cycle, or None if acyclic.
    """
    state = {node: NodeState.UNVISITED for node in graph.get_all_nodes()}
    parent = {}
    cycle_nodes = []
    
    def dfs(node, path):
        if state[node] == NodeState.VISITING:
            # Found a cycle — extract it from the path
            cycle_start_idx = path.index(node)
            return path[cycle_start_idx:] + [node]
        
        if state[node] == NodeState.VISITED:
            return None
        
        state[node] = NodeState.VISITING
        
        for neighbor in graph.get_neighbors(node):
            result = dfs(neighbor, path + [node])
            if result:
                return result
        
        state[node] = NodeState.VISITED
        return None
    
    for node in graph.get_all_nodes():
        if state[node] == NodeState.UNVISITED:
            result = dfs(node, [])
            if result:
                return result
    
    return None


if __name__ == "__main__":
    print("=== Topological Sort Demo ===\n")
    
    # Example 1: Course prerequisites (acyclic — should work)
    print("Example 1: University course prerequisites")
    courses = DirectedGraph()
    courses.add_edge("Calculus I", "Calculus II")
    courses.add_edge("Calculus II", "Differential Equations")
    courses.add_edge("Intro to Programming", "Data Structures")
    courses.add_edge("Data Structures", "Algorithms")
    courses.add_edge("Calculus I", "Linear Algebra")
    courses.add_edge("Linear Algebra", "Machine Learning")
    courses.add_edge("Algorithms", "Machine Learning")
    
    order = topological_sort(courses)
    if order:
        print("Valid course order:")
        for i, course in enumerate(order, 1):
            print(f"  {i}. {course}")
    else:
        print("ERROR: Circular dependencies detected!")
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: Build system with a cycle (should fail)
    print("Example 2: Build dependencies with a cycle")
    build = DirectedGraph()
    build.add_edge("main.o", "app")
    build.add_edge("utils.o", "app")
    build.add_edge("app", "test")
    build.add_edge("test", "utils.o")  # Oops! test needs utils.o, but utils.o is built from app
    
    order = topological_sort(build)
    if order:
        print("Valid build order:")
        for i, target in enumerate(order, 1):
            print(f"  {i}. {target}")
    else:
        print("ERROR: Circular dependencies detected!")
        cycle = find_cycle(build)
        if cycle:
            print("Cycle found:", " -> ".join(cycle))
    
    print("\n" + "="*50 + "\n")
    
    # Example 3: Simple task dependencies
    print("Example 3: Morning routine tasks")
    routine = DirectedGraph()
    routine.add_edge("wake up", "brush teeth")
    routine.add_edge("wake up", "make coffee")
    routine.add_edge("brush teeth", "get dressed")
    routine.add_edge("make coffee", "drink coffee")
    routine.add_edge("get dressed", "leave house")
    routine.add_edge("drink coffee", "leave house")
    
    order = topological_sort(routine)
    if order:
        print("Valid task order:")
        for i, task in enumerate(order, 1):
            print(f"  {i}. {task}")
    else:
        print("ERROR: Circular dependencies detected!")