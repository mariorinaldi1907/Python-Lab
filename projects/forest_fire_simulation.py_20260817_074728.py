"""
Date: 2026-08-17
Simulated how fires spread through a grid-based forest using simple probabilistic rules — trees grow, lightning strikes, and fires propagate to neighbors.
"""

"""
Forest Fire Simulation - A cellular automaton model

Each cell can be in one of three states:
- Empty (0): bare ground
- Tree (1): living tree
- Fire (2): burning tree

Rules per tick:
1. Burning trees become empty
2. Trees catch fire if any neighbor is burning
3. Trees spontaneously ignite with probability p_lightning
4. Empty cells grow new trees with probability p_growth
"""

import random
import time
from typing import List, Tuple


class ForestFireSimulation:
    """
    A grid-based forest fire cellular automaton.
    
    I wanted to see how different probabilities affect fire spread patterns.
    Turns out even tiny lightning probabilities can cause periodic cascades.
    """
    
    EMPTY = 0
    TREE = 1
    FIRE = 2
    
    def __init__(self, width: int, height: int, p_growth: float = 0.01, p_lightning: float = 0.0001):
        """
        Initialize the forest grid.
        
        Args:
            width: Grid width
            height: Grid height
            p_growth: Probability that an empty cell grows a tree each step
            p_lightning: Probability that a tree spontaneously ignites
        """
        self.width = width
        self.height = height
        self.p_growth = p_growth
        self.p_lightning = p_lightning
        
        # Start with a random distribution of trees
        self.grid = [[self.TREE if random.random() < 0.5 else self.EMPTY 
                      for _ in range(width)] for _ in range(height)]
        
        self.step_count = 0
    
    def get_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Return the four orthogonal neighbors of a cell (no diagonals)."""
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.height and 0 <= nc < self.width:
                neighbors.append((nr, nc))
        return neighbors
    
    def has_burning_neighbor(self, row: int, col: int) -> bool:
        """Check if any orthogonal neighbor is on fire."""
        for nr, nc in self.get_neighbors(row, col):
            if self.grid[nr][nc] == self.FIRE:
                return True
        return False
    
    def update(self):
        """
        Advance the simulation by one time step.
        
        I process the grid in two passes to avoid order-dependence:
        first determine all changes, then apply them simultaneously.
        """
        new_grid = [[self.EMPTY for _ in range(self.width)] for _ in range(self.height)]
        
        for row in range(self.height):
            for col in range(self.width):
                cell = self.grid[row][col]
                
                if cell == self.FIRE:
                    # Burning trees turn to empty ground
                    new_grid[row][col] = self.EMPTY
                
                elif cell == self.TREE:
                    # Trees can catch fire from neighbors or lightning
                    if self.has_burning_neighbor(row, col) or random.random() < self.p_lightning:
                        new_grid[row][col] = self.FIRE
                    else:
                        new_grid[row][col] = self.TREE
                
                elif cell == self.EMPTY:
                    # Empty cells can grow new trees
                    if random.random() < self.p_growth:
                        new_grid[row][col] = self.TREE
                    else:
                        new_grid[row][col] = self.EMPTY
        
        self.grid = new_grid
        self.step_count += 1
    
    def count_cells(self) -> Tuple[int, int, int]:
        """Return (empty_count, tree_count, fire_count)."""
        empty = tree = fire = 0
        for row in self.grid:
            for cell in row:
                if cell == self.EMPTY:
                    empty += 1
                elif cell == self.TREE:
                    tree += 1
                elif cell == self.FIRE:
                    fire += 1
        return empty, tree, fire
    
    def display(self):
        """Print the current grid state using ASCII characters."""
        symbols = {self.EMPTY: '.', self.TREE: 'T', self.FIRE: 'F'}
        print(f"\n--- Step {self.step_count} ---")
        for row in self.grid:
            print(''.join(symbols[cell] for cell in row))
        
        empty, tree, fire = self.count_cells()
        total = self.width * self.height
        print(f"Empty: {empty}/{total} | Trees: {tree}/{total} | Fire: {fire}/{total}")


def run_simulation(steps: int = 50, width: int = 40, height: int = 20, 
                   p_growth: float = 0.01, p_lightning: float = 0.00008,
                   display_interval: int = 10):
    """
    Run a forest fire simulation and display periodic snapshots.
    
    Args:
        steps: Number of time steps to simulate
        width: Grid width
        height: Grid height
        p_growth: Tree growth probability per step
        p_lightning: Lightning strike probability per tree per step
        display_interval: How often to print the grid (every N steps)
    """
    sim = ForestFireSimulation(width, height, p_growth, p_lightning)
    
    print("Forest Fire Simulation")
    print("======================")
    print(f"Grid: {width}x{height}")
    print(f"Growth rate: {p_growth}, Lightning rate: {p_lightning}")
    print("\nLegend: . = empty, T = tree, F = fire\n")
    
    sim.display()
    
    for step in range(1, steps + 1):
        sim.update()
        
        if step % display_interval == 0 or step == steps:
            sim.display()
            time.sleep(0.3)  # Brief pause so you can actually watch it


if __name__ == "__main__":
    # Run a demo with parameters tuned to show interesting fire dynamics
    # Higher lightning = more frequent fires, higher growth = denser forest
    run_simulation(steps=100, width=50, height=25, 
                   p_growth=0.015, p_lightning=0.0001, 
                   display_interval=5)