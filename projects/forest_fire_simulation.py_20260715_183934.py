"""
Date: 2026-07-15
Simulated a forest fire spreading through a grid with probabilistic ignition, wind effects, and regrowth to explore cellular automaton dynamics.
"""

#!/usr/bin/env python3
"""
Forest Fire Simulation
A cellular automaton where fire spreads through a forest grid based on
probability, wind direction, and neighbor states. Trees can regrow over time.
"""

import random
import time
from typing import List, Tuple


class ForestFireSimulation:
    """
    Simulates fire spreading through a forest grid.
    
    Each cell can be: EMPTY (0), TREE (1), BURNING (2), or ASH (3).
    Fire spreads to neighboring trees based on ignition probability and wind.
    """
    
    EMPTY = 0
    TREE = 1
    BURNING = 2
    ASH = 3
    
    def __init__(self, width: int, height: int, tree_density: float = 0.6,
                 ignition_prob: float = 0.3, wind_direction: Tuple[int, int] = (1, 0)):
        """
        Initialize the forest grid.
        
        Args:
            width: Grid width
            height: Grid height
            tree_density: Initial probability a cell contains a tree (0-1)
            ignition_prob: Base probability fire spreads to adjacent tree (0-1)
            wind_direction: (dx, dy) tuple indicating wind direction and strength
        """
        self.width = width
        self.height = height
        self.ignition_prob = ignition_prob
        self.wind_direction = wind_direction
        self.grid = [[self.TREE if random.random() < tree_density else self.EMPTY
                     for _ in range(width)] for _ in range(height)]
        self.step_count = 0
    
    def ignite_random_tree(self) -> bool:
        """Start a fire at a random tree location. Returns True if successful."""
        trees = [(y, x) for y in range(self.height) for x in range(self.width)
                 if self.grid[y][x] == self.TREE]
        if trees:
            y, x = random.choice(trees)
            self.grid[y][x] = self.BURNING
            return True
        return False
    
    def get_neighbors(self, y: int, x: int) -> List[Tuple[int, int]]:
        """Get valid neighbor coordinates (4-directional)."""
        neighbors = []
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ny, nx = y + dy, x + dx
            if 0 <= ny < self.height and 0 <= nx < self.width:
                neighbors.append((ny, nx, dy, dx))
        return neighbors
    
    def step(self):
        """
        Advance simulation by one step.
        
        Fire spreads to neighboring trees probabilistically, with wind
        increasing spread chance in its direction. Burning cells turn to ash.
        Trees have a small chance to regrow in empty spaces.
        """
        new_grid = [row[:] for row in self.grid]  # Deep copy
        
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == self.BURNING:
                    # Burning cell turns to ash
                    new_grid[y][x] = self.ASH
                    
                    # Try to spread fire to neighbors
                    for ny, nx, dy, dx in self.get_neighbors(y, x):
                        if self.grid[ny][nx] == self.TREE:
                            # Wind boosts ignition probability in its direction
                            wind_boost = 0.0
                            if self.wind_direction:
                                wind_dx, wind_dy = self.wind_direction
                                # If neighbor is downwind, increase spread chance
                                if (dx == wind_dx and dy == wind_dy):
                                    wind_boost = 0.2
                            
                            if random.random() < (self.ignition_prob + wind_boost):
                                new_grid[ny][nx] = self.BURNING
                
                elif self.grid[y][x] == self.EMPTY:
                    # Small chance for tree regrowth in empty spaces
                    if random.random() < 0.01:
                        new_grid[y][x] = self.TREE
        
        self.grid = new_grid
        self.step_count += 1
    
    def get_statistics(self) -> dict:
        """Return counts of each cell type."""
        counts = {self.EMPTY: 0, self.TREE: 0, self.BURNING: 0, self.ASH: 0}
        for row in self.grid:
            for cell in row:
                counts[cell] += 1
        return counts
    
    def display(self):
        """Print the current grid state to console."""
        symbols = {
            self.EMPTY: '.',
            self.TREE: '♣',
            self.BURNING: '🔥',
            self.ASH: '·'
        }
        print(f"\n=== Step {self.step_count} ===")
        for row in self.grid:
            print(' '.join(symbols.get(cell, '?') for cell in row))
        
        stats = self.get_statistics()
        total = sum(stats.values())
        print(f"\nTrees: {stats[self.TREE]} | Burning: {stats[self.BURNING]} | "
              f"Ash: {stats[self.ASH]} | Empty: {stats[self.EMPTY]}")


def run_simulation(steps: int = 25, width: int = 30, height: int = 15):
    """
    Run a forest fire simulation for a given number of steps.
    
    The fire starts at a random tree and spreads based on wind and probability.
    """
    print("🌲 Forest Fire Simulation 🔥")
    print(f"Grid: {width}x{height} | Wind: East | Steps: {steps}\n")
    
    # Wind blowing east (right) makes fire spread faster in that direction
    sim = ForestFireSimulation(
        width=width,
        height=height,
        tree_density=0.65,
        ignition_prob=0.25,
        wind_direction=(1, 0)  # Eastward wind
    )
    
    # Start the fire
    if not sim.ignite_random_tree():
        print("No trees to ignite!")
        return
    
    sim.display()
    
    # Run simulation
    for _ in range(steps):
        time.sleep(0.3)  # Slow down for visibility
        sim.step()
        sim.display()
        
        # Stop if fire is extinguished
        stats = sim.get_statistics()
        if stats[sim.BURNING] == 0:
            print("\n🔥 Fire extinguished!")
            break


if __name__ == "__main__":
    run_simulation(steps=30, width=35, height=18)