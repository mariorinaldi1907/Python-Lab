"""
Date: 2026-06-06
Built a topological sort algorithm that detects cycles in directed graphs — useful for dependency resolution and course scheduling problems.
"""

#!/usr/bin/env python3
"""
Topological Sort with Cycle Detection

I wanted a clean implementation of topological sort that doesn't just fail
silently when there's a cycle. This version uses DFS and explicitly tracks
the path to report back where cycles exist, which is way more useful for
debugging dependency issues.
"""

from collections import defaultdict, deque
from enum import Enum


class NodeState(Enum):
    """Track visit state during DFS to detect cycles."""
    UNVISITED = 0
    VISITING = 1  # Currently in the DFS stack (gray node)
    VISITED = 2   # Completely processed (black node)


class DirectedGraph:
    """
    A simple directed graph implementation for topological sorting.
    
    Stores adjacency list and provides methods to add edges and perform
    topological sort with cycle detection.
    """
    
    def __init__(self):
        self.graph = defaultdict(list)
        self.nodes = set()
    
    def add_edge(self, from_node, to_node):
        """Add a directed edge from from_node to to_node."""
        self.graph[from_node].append(to_node)
        self.nodes.add(from_node)
        self.nodes.add(to_node)
    
    def topological_sort(self):
        """
        Perform topological sort using DFS.
        
        Returns:
            tuple: (success: bool, result: list or str)
                If successful, result is the topologically sorted list.
                If cycle detected, result is an error message with cycle info.
        """
        state = {node: NodeState.UNVISITED for node in self.nodes}
        sorted_nodes = deque()  # Using deque for efficient prepending
        
        def dfs(node, path):
            """
            Recursive DFS that builds the topological order.
            
            The path parameter tracks current recursion path to identify
            exactly where the cycle occurs, not just that one exists.
            """
            if state[node] == NodeState.VISITING:
                # Found a back edge - there's a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                return False, f"Cycle detected: {' -> '.join(map(str, cycle))}"
            
            if state[node] == NodeState.VISITED:
                # Already processed this node
                return True, None
            
            # Mark as currently visiting
            state[node] = NodeState.VISITING
            path.append(node)
            
            # Visit all neighbors
            for neighbor in self.graph[node]:
                success, error = dfs(neighbor, path)
                if not success:
                    return False, error
            
            # Done with this node - mark as visited and add to result
            path.pop()
            state[node] = NodeState.VISITED
            sorted_nodes.appendleft(node)  # Prepend to get correct order
            
            return True, None
        
        # Try DFS from each unvisited node
        # This handles disconnected components too
        for node in self.nodes:
            if state[node] == NodeState.UNVISITED:
                success, error = dfs(node, [])
                if not success:
                    return False, error
        
        return True, list(sorted_nodes)


def demonstrate_course_scheduling():
    """
    Real-world example: course prerequisites.
    
    I'm modeling a simplified CS curriculum where some courses depend on others.
    This helps visualize why topological sort matters.
    """
    print("=== Course Scheduling Example ===\n")
    
    courses = DirectedGraph()
    
    # Define prerequisite relationships (prerequisite -> course)
    prereqs = [
        ("Intro to Programming", "Data Structures"),
        ("Data Structures", "Algorithms"),
        ("Data Structures", "Database Systems"),
        ("Algorithms", "Machine Learning"),
        ("Calculus I", "Calculus II"),
        ("Calculus II", "Machine Learning"),
        ("Linear Algebra", "Machine Learning"),
    ]
    
    for prereq, course in prereqs:
        courses.add_edge(prereq, course)
    
    success, result = courses.topological_sort()
    
    if success:
        print("Valid course order found!")
        print("You could take courses in this sequence:\n")
        for i, course in enumerate(result, 1):
            print(f"{i}. {course}")
    else:
        print(f"ERROR: {result}")
    
    print()


def demonstrate_cycle_detection():
    """Show what happens when there's a circular dependency."""
    print("=== Cycle Detection Example ===\n")
    
    tasks = DirectedGraph()
    
    # Creating a scenario with a cycle
    tasks.add_edge("Task A", "Task B")
    tasks.add_edge("Task B", "Task C")
    tasks.add_edge("Task C", "Task D")
    tasks.add_edge("Task D", "Task B")  # Oops! Circular dependency
    
    success, result = tasks.topological_sort()
    
    if success:
        print("Order:", result)
    else:
        print(f"Can't complete tasks: {result}")
        print("You'll need to break the circular dependency first!")
    
    print()


if __name__ == "__main__":
    print("Topological Sort with Cycle Detection")
    print("=" * 50)
    print()
    
    # Run the course scheduling demo
    demonstrate_course_scheduling()
    
    # Show what happens with a cycle
    demonstrate_cycle_detection()
    
    # Quick numeric example for simplicity
    print("=== Simple Numeric Example ===\n")
    g = DirectedGraph()
    edges = [(5, 2), (5, 0), (4, 0), (4, 1), (2, 3), (3, 1)]
    for u, v in edges:
        g.add_edge(u, v)
    
    success, result = g.topological_sort()
    print(f"Graph edges: {edges}")
    print(f"Topological order: {result}")