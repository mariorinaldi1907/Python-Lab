"""
Date: 2026-06-22
Built a topological sort algorithm that detects cycles and gracefully handles graphs with multiple components — useful for dependency resolution problems.
"""

#!/usr/bin/env python3
"""
Topological sort implementation using depth-first search.

I built this because I kept running into dependency management problems
and wanted a clean way to order tasks. The cycle detection is especially
useful since it tells you exactly which nodes form the problematic cycle.
"""

from collections import defaultdict, deque
from enum import Enum


class NodeState(Enum):
    """Track visit state during DFS to detect cycles."""
    UNVISITED = 0
    VISITING = 1  # Currently in the DFS stack
    VISITED = 2   # Completely processed


class DirectedGraph:
    """
    Simple directed graph representation using adjacency lists.
    
    I chose adjacency lists over a matrix because most dependency graphs
    are sparse — you don't have every node depending on every other node.
    """
    
    def __init__(self):
        self.adjacency_list = defaultdict(list)
        self.nodes = set()
    
    def add_edge(self, from_node, to_node):
        """Add a directed edge from_node -> to_node."""
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
    
    Returns a tuple: (sorted_list, has_cycle, cycle_nodes)
    - sorted_list: topologically sorted nodes (empty if cycle detected)
    - has_cycle: True if a cycle was detected
    - cycle_nodes: list of nodes forming a cycle (empty if no cycle)
    
    The key insight: in DFS, we add a node to the result *after* visiting
    all its descendants. Then we reverse the list at the end. This ensures
    dependencies come before dependents.
    """
    state = {node: NodeState.UNVISITED for node in graph.get_all_nodes()}
    result = []
    cycle_path = []
    
    def dfs(node, path):
        """
        DFS helper that tracks the current path for cycle detection.
        
        Using VISITING state lets us catch back-edges (cycles) cleanly.
        If we encounter a VISITING node, we've found a cycle.
        """
        if state[node] == NodeState.VISITING:
            # Found a cycle! Extract it from the path.
            cycle_start = path.index(node)
            cycle_path.extend(path[cycle_start:] + [node])
            return False
        
        if state[node] == NodeState.VISITED:
            return True
        
        state[node] = NodeState.VISITING
        path.append(node)
        
        for neighbor in graph.get_neighbors(node):
            if not dfs(neighbor, path):
                return False
        
        path.pop()
        state[node] = NodeState.VISITED
        result.append(node)
        return True
    
    # Visit all nodes to handle disconnected components
    for node in graph.get_all_nodes():
        if state[node] == NodeState.UNVISITED:
            if not dfs(node, []):
                return [], True, cycle_path
    
    # Reverse because we added nodes in post-order
    result.reverse()
    return result, False, []


def format_dependencies(sorted_nodes):
    """Pretty print the sorted order with arrow notation."""
    if not sorted_nodes:
        return "No valid ordering (cycle detected)"
    return " → ".join(sorted_nodes)


if __name__ == "__main__":
    # Example 1: Course prerequisites (classic use case)
    print("=" * 60)
    print("Example 1: Course Prerequisites")
    print("=" * 60)
    
    courses = DirectedGraph()
    # Edge A -> B means "A must come before B" or "B depends on A"
    courses.add_edge("Intro to CS", "Data Structures")
    courses.add_edge("Intro to CS", "Algorithms")
    courses.add_edge("Data Structures", "Algorithms")
    courses.add_edge("Data Structures", "Operating Systems")
    courses.add_edge("Algorithms", "Machine Learning")
    courses.add_edge("Operating Systems", "Distributed Systems")
    
    sorted_courses, has_cycle, cycle = topological_sort(courses)
    
    if has_cycle:
        print(f"ERROR: Circular dependency detected: {' → '.join(cycle)}")
    else:
        print("Valid course order:")
        print(format_dependencies(sorted_courses))
    
    print()
    
    # Example 2: Build system with cycle (demonstrates error handling)
    print("=" * 60)
    print("Example 2: Build Tasks (with intentional cycle)")
    print("=" * 60)
    
    build = DirectedGraph()
    build.add_edge("compile", "link")
    build.add_edge("link", "test")
    build.add_edge("test", "package")
    build.add_edge("package", "compile")  # Oops! Creates a cycle
    
    sorted_tasks, has_cycle, cycle = topological_sort(build)
    
    if has_cycle:
        print(f"ERROR: Circular dependency detected!")
        print(f"Cycle: {' → '.join(cycle)}")
        print("Cannot determine build order — fix the circular dependency first.")
    else:
        print("Build order:")
        print(format_dependencies(sorted_tasks))
    
    print()
    
    # Example 3: Multiple disconnected components
    print("=" * 60)
    print("Example 3: Multiple Independent Projects")
    print("=" * 60)
    
    projects = DirectedGraph()
    # Project A tasks
    projects.add_edge("design_A", "implement_A")
    projects.add_edge("implement_A", "deploy_A")
    # Project B tasks (completely independent)
    projects.add_edge("spec_B", "code_B")
    projects.add_edge("code_B", "ship_B")
    
    sorted_projects, has_cycle, cycle = topological_sort(projects)
    
    if has_cycle:
        print(f"ERROR: Circular dependency: {' → '.join(cycle)}")
    else:
        print("Task order (multiple valid orderings exist):")
        print(format_dependencies(sorted_projects))
        print("\nNote: Independent projects can be interleaved in any way.")
    
    print()