"""
Date: 2026-06-07
Made a cellular automaton that simulates wildfire propagation through different terrain types with wind effects and moisture levels — runs in terminal with ascii output.
"""

#!/usr/bin/env python3
"""
Forest Fire Simulation
A cellular automaton modeling wildfire spread with terrain variation, wind, and moisture.
Each cell can be: empty, tree, burning, or burnt. Fire spreads probabilistically.
"""

import random
import time
from typing import List, Tuple


class ForestFireSim:
    """
    Simulates wildfire spread across a grid with different terrain types.
    
    The simulation accounts for:
    - Terrain moisture (affects ignition probability)
    - Wind direction (biases spread direction)
    - Random chance (stochastic model)
    """
    
    # Cell states
    EMPTY = 0
    TREE = 1
    BURNING = 2
    BURNT = 3
    
    def __init__(self, width: int, height: int, tree_density: float = 0.65):
        """
        Initialize the forest grid.
        
        Args:
            width: Grid width
            height: Grid height
            tree_density: Probability a cell starts with a tree (0-1)
        """
        self.width = width
        self.height = height
        self.grid = [[self.EMPTY for _ in range(width)] for _ in range(height)]
        self.moisture = [[random.uniform(0.3, 1.0) for _ in range(width)] for _ in range(height)]
        
        # Populate forest with trees
        for y in range(height):
            for x in range(width):
                if random.random() < tree_density:
                    self.grid[y][x] = self.TREE
        
        # Wind: (dx, dy) representing direction bias
        self.wind = (random.choice([-1, 0, 1]), random.choice([-1, 0, 1]))
    
    def ignite(self, x: int, y: int):
        """Start a fire at the specified location."""
        if self.grid[y][x] == self.TREE:
            self.grid[y][x] = self.BURNING
    
    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """
        Get valid neighbor coordinates including diagonals.
        Wind direction increases probability of spread in that direction.
        """
        neighbors = []
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    # Wind effect: add wind-aligned neighbors multiple times
                    # to increase their selection probability
                    weight = 1
                    if (dx, dy) == self.wind:
                        weight = 3  # Wind pushes fire this direction
                    for _ in range(weight):
                        neighbors.append((nx, ny))
        return neighbors
    
    def step(self) -> bool:
        """
        Advance simulation by one time step.
        
        Returns:
            True if any fires are still burning, False otherwise
        """
        new_fires = []
        has_burning = False
        
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == self.BURNING:
                    has_burning = True
                    # Burning tree spreads to neighbors
                    neighbors = self.get_neighbors(x, y)
                    for nx, ny in neighbors:
                        if self.grid[ny][nx] == self.TREE:
                            # Base spread probability, reduced by moisture
                            spread_prob = 0.4 * (1.0 - self.moisture[ny][nx] * 0.5)
                            if random.random() < spread_prob:
                                new_fires.append((nx, ny))
                    
                    # Burning tree becomes burnt
                    self.grid[y][x] = self.BURNT
        
        # Apply new fires
        for x, y in new_fires:
            self.grid[y][x] = self.BURNING
        
        return has_burning or len(new_fires) > 0
    
    def render(self) -> str:
        """
        Render the current state as ASCII art.
        
        Returns:
            String representation of the grid
        """
        symbols = {
            self.EMPTY: ' .',
            self.TREE: ' T',
            self.BURNING: ' *',  # Asterisk for fire
            self.BURNT: ' #',
        }
        lines = []
        for row in self.grid:
            lines.append(''.join(symbols[cell] for cell in row))
        return '\n'.join(lines)
    
    def count_states(self) -> dict:
        """Count cells in each state for statistics."""
        counts = {self.EMPTY: 0, self.TREE: 0, self.BURNING: 0, self.BURNT: 0}
        for row in self.grid:
            for cell in row:
                counts[cell] += 1
        return counts


def run_simulation(width: int = 40, height: int = 20, max_steps: int = 50):
    """
    Run a complete forest fire simulation with visualization.
    
    Args:
        width: Grid width
        height: Grid height
        max_steps: Maximum simulation steps
    """
    print("=== Forest Fire Simulation ===")
    print(f"Grid: {width}x{height}")
    
    sim = ForestFireSim(width, height, tree_density=0.7)
    
    # Start fires at random locations (simulating lightning strikes)
    num_ignitions = random.randint(1, 3)
    for _ in range(num_ignitions):
        x, y = random.randint(0, width - 1), random.randint(0, height - 1)
        sim.ignite(x, y)
    
    print(f"Wind direction: {sim.wind}")
    print(f"Initial ignitions: {num_ignitions}")
    print("\nLegend: . = empty, T = tree, * = burning, # = burnt\n")
    
    step = 0
    while step < max_steps:
        print(f"--- Step {step} ---")
        print(sim.render())
        
        counts = sim.count_states()
        print(f"Trees: {counts[sim.TREE]}, Burning: {counts[sim.BURNING]}, Burnt: {counts[sim.BURNT]}")
        
        if not sim.step():
            print("\nFire extinguished!")
            break
        
        step += 1
        time.sleep(0.3)  # Slow down for visualization
        print()
    
    # Final stats
    final_counts = sim.count_states()
    total_trees = final_counts[sim.TREE] + final_counts[sim.BURNT]
    if total_trees > 0:
        burn_pct = (final_counts[sim.BURNT] / total_trees) * 100
        print(f"\nSimulation complete: {burn_pct:.1f}% of forest burned")


if __name__ == "__main__":
    run_simulation(width=35, height=18, max_steps=40)