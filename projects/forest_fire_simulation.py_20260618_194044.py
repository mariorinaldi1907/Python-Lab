"""
Date: 2026-06-18
Made a forest fire spread simulator using a 2D grid where fire propagates to neighboring trees based on probability — runs in the terminal with ASCII art.
"""

#!/usr/bin/env python3
"""
Forest Fire Simulation
A cellular automaton where fires spread through a forest grid.
Trees can catch fire from burning neighbors, and eventually burn out to empty space.
"""

import random
import time
from typing import List, Tuple


class ForestFireSimulation:
    """
    Simulates fire spreading through a forest using cellular automaton rules.
    
    Cell states:
    - EMPTY (0): burnt out or never had a tree
    - TREE (1): healthy tree
    - FIRE (2): burning tree
    """
    
    EMPTY = 0
    TREE = 1
    FIRE = 2
    
    def __init__(self, width: int, height: int, tree_density: float = 0.6, 
                 spread_probability: float = 0.7):
        """
        Initialize the forest grid.
        
        Args:
            width: Grid width
            height: Grid height
            tree_density: Probability a cell starts with a tree (0.0 - 1.0)
            spread_probability: Chance fire spreads to adjacent tree (0.0 - 1.0)
        """
        self.width = width
        self.height = height
        self.spread_prob = spread_probability
        
        # Initialize grid with random trees
        self.grid = [[self.TREE if random.random() < tree_density else self.EMPTY
                      for _ in range(width)] for _ in range(height)]
        
        # Track if simulation is still active
        self.active = False
    
    def ignite_random_tree(self) -> bool:
        """
        Start a fire at a random tree location.
        
        Returns:
            True if a tree was ignited, False if no trees available
        """
        # Find all tree positions
        trees = [(y, x) for y in range(self.height) 
                 for x in range(self.width) if self.grid[y][x] == self.TREE]
        
        if not trees:
            return False
        
        # Ignite a random tree
        y, x = random.choice(trees)
        self.grid[y][x] = self.FIRE
        self.active = True
        return True
    
    def get_neighbors(self, y: int, x: int) -> List[Tuple[int, int]]:
        """
        Get valid neighboring cell coordinates (4-directional).
        
        Args:
            y: Row index
            x: Column index
            
        Returns:
            List of (y, x) tuples for valid neighbors
        """
        neighbors = []
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ny, nx = y + dy, x + dx
            if 0 <= ny < self.height and 0 <= nx < self.width:
                neighbors.append((ny, nx))
        return neighbors
    
    def step(self):
        """
        Execute one simulation step.
        
        Rules:
        - Burning cells spread fire to adjacent trees based on spread_probability
        - Burning cells turn to empty after spreading
        """
        new_grid = [row[:] for row in self.grid]  # Copy current state
        has_fire = False
        
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == self.FIRE:
                    # Fire burns out this turn
                    new_grid[y][x] = self.EMPTY
                    
                    # Try to spread to neighbors
                    for ny, nx in self.get_neighbors(y, x):
                        if self.grid[ny][nx] == self.TREE:
                            # Fire spreads with probability
                            if random.random() < self.spread_prob:
                                new_grid[ny][nx] = self.FIRE
                                has_fire = True
        
        self.grid = new_grid
        self.active = has_fire
    
    def count_cells(self) -> Tuple[int, int, int]:
        """
        Count cells in each state.
        
        Returns:
            Tuple of (empty_count, tree_count, fire_count)
        """
        empty = sum(row.count(self.EMPTY) for row in self.grid)
        trees = sum(row.count(self.TREE) for row in self.grid)
        fires = sum(row.count(self.FIRE) for row in self.grid)
        return empty, trees, fires
    
    def display(self):
        """Print the current grid state to console."""
        symbols = {
            self.EMPTY: ' .',
            self.TREE: ' T',
            self.FIRE: ' F'
        }
        
        print("\n" + "=" * (self.width * 2 + 2))
        for row in self.grid:
            print("|" + "".join(symbols[cell] for cell in row) + "|")
        print("=" * (self.width * 2 + 2))
        
        empty, trees, fires = self.count_cells()
        print(f"Trees: {trees}  |  Fires: {fires}  |  Burnt: {empty}")


def run_simulation(width: int = 30, height: int = 20, tree_density: float = 0.65,
                   spread_prob: float = 0.6, delay: float = 0.3):
    """
    Run a complete forest fire simulation with visual output.
    
    Args:
        width: Grid width
        height: Grid height
        tree_density: Initial tree coverage
        spread_prob: Fire spread probability
        delay: Seconds between frames
    """
    sim = ForestFireSimulation(width, height, tree_density, spread_prob)
    
    print("FOREST FIRE SIMULATION")
    print("T = Tree, F = Fire, . = Empty/Burnt")
    print(f"Spread probability: {spread_prob:.0%}")
    
    # Show initial state
    sim.display()
    time.sleep(delay * 2)
    
    # Ignite the forest
    if not sim.ignite_random_tree():
        print("No trees to ignite!")
        return
    
    step_count = 0
    while sim.active:
        step_count += 1
        print(f"\n--- Step {step_count} ---")
        sim.display()
        sim.step()
        time.sleep(delay)
    
    # Show final state
    print(f"\n--- FINAL (Step {step_count + 1}) ---")
    sim.display()
    
    _, trees_left, _ = sim.count_cells()
    total_cells = width * height
    burnt_percentage = ((total_cells - trees_left) / total_cells) * 100
    print(f"\nSimulation complete! {burnt_percentage:.1f}% of forest affected.")


if __name__ == "__main__":
    # Run a demo simulation with reasonable parameters
    # I like watching these — small grid so it fits in terminal nicely
    run_simulation(width=25, height=15, tree_density=0.7, 
                   spread_prob=0.65, delay=0.4)