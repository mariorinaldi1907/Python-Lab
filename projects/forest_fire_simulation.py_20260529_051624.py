"""
Date: 2026-05-29
Simulating forest fires spreading across a grid with wind direction and probabilistic ignition because I wanted to see emergent behavior from simple rules.
"""

#!/usr/bin/env python3
"""
Forest fire simulation on a 2D grid.
Trees can be empty, alive, burning, or burnt. Fire spreads probabilistically
to neighbors, influenced by wind direction.
"""

import random
import time
from typing import List, Tuple


class ForestFire:
    """
    Simulates fire spreading through a forest grid.
    
    Each cell can be: empty (0), tree (1), burning (2), or burnt (3).
    Fire spreads to adjacent trees based on spread_prob, with wind adding bias.
    """
    
    EMPTY = 0
    TREE = 1
    BURNING = 2
    BURNT = 3
    
    def __init__(self, width: int, height: int, tree_density: float = 0.7,
                 spread_prob: float = 0.6, wind: Tuple[int, int] = (0, 0)):
        """
        Initialize the forest grid.
        
        Args:
            width: Grid width
            height: Grid height
            tree_density: Probability a cell starts with a tree (0.0 to 1.0)
            spread_prob: Base probability fire spreads to adjacent tree
            wind: (dx, dy) wind direction vector, affects spread probability
        """
        self.width = width
        self.height = height
        self.spread_prob = spread_prob
        self.wind = wind
        
        # Generate initial forest with random trees
        self.grid = [
            [self.TREE if random.random() < tree_density else self.EMPTY
             for _ in range(width)]
            for _ in range(height)
        ]
        
        self.generation = 0
    
    def ignite(self, x: int, y: int):
        """Start a fire at the given coordinates."""
        if 0 <= y < self.height and 0 <= x < self.width:
            if self.grid[y][x] == self.TREE:
                self.grid[y][x] = self.BURNING
    
    def step(self):
        """
        Advance simulation by one time step.
        
        Burning cells turn to burnt, and fire spreads to neighbors
        based on spread probability and wind direction.
        """
        new_grid = [row[:] for row in self.grid]  # Deep copy
        
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == self.BURNING:
                    # Burning tree becomes burnt
                    new_grid[y][x] = self.BURNT
                    
                    # Try to spread fire to neighbors
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = x + dx, y + dy
                        
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            if self.grid[ny][nx] == self.TREE:
                                # Wind makes fire more likely to spread in wind direction
                                wind_boost = 0.0
                                if (dx, dy) == self.wind:
                                    wind_boost = 0.3
                                elif (dx, dy) == (-self.wind[0], -self.wind[1]):
                                    wind_boost = -0.2  # Against wind is harder
                                
                                effective_prob = min(1.0, self.spread_prob + wind_boost)
                                
                                if random.random() < effective_prob:
                                    new_grid[ny][nx] = self.BURNING
        
        self.grid = new_grid
        self.generation += 1
    
    def is_burning(self) -> bool:
        """Check if any cells are currently burning."""
        return any(cell == self.BURNING for row in self.grid for cell in row)
    
    def count_states(self) -> dict:
        """Return count of cells in each state."""
        counts = {self.EMPTY: 0, self.TREE: 0, self.BURNING: 0, self.BURNT: 0}
        for row in self.grid:
            for cell in row:
                counts[cell] += 1
        return counts
    
    def render(self) -> str:
        """
        Create ASCII representation of the forest.
        
        Uses different characters for each state to visualize the fire spread.
        """
        symbols = {
            self.EMPTY: ' ',
            self.TREE: '🌲',
            self.BURNING: '🔥',
            self.BURNT: '💀'
        }
        
        lines = []
        lines.append(f"Generation {self.generation}")
        lines.append("+" + "-" * (self.width * 2) + "+")
        
        for row in self.grid:
            line = "|" + "".join(symbols.get(cell, '?') for cell in row) + "|"
            lines.append(line)
        
        lines.append("+" + "-" * (self.width * 2) + "+")
        
        counts = self.count_states()
        lines.append(f"Trees: {counts[self.TREE]} | Burning: {counts[self.BURNING]} | "
                    f"Burnt: {counts[self.BURNT]} | Empty: {counts[self.EMPTY]}")
        
        return "\n".join(lines)


def run_simulation(width: int = 30, height: int = 20, delay: float = 0.3):
    """
    Run a complete forest fire simulation from ignition to burn-out.
    
    Starts fires at random locations and lets them spread until extinguished.
    Prints each generation to terminal with a small delay for visualization.
    """
    # Create forest with eastward wind
    forest = ForestFire(width, height, tree_density=0.65, 
                       spread_prob=0.5, wind=(1, 0))
    
    # Ignite a few random starting fires
    num_ignitions = 3
    for _ in range(num_ignitions):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        forest.ignite(x, y)
    
    print(forest.render())
    print("\nFire spreading...\n")
    time.sleep(delay * 2)
    
    # Run until fire burns out
    while forest.is_burning():
        forest.step()
        print("\033[H\033[J")  # Clear terminal (works on most systems)
        print(forest.render())
        time.sleep(delay)
    
    # Final summary
    counts = forest.count_states()
    total_cells = width * height
    burn_percentage = (counts[forest.BURNT] / total_cells) * 100
    
    print(f"\nSimulation complete after {forest.generation} generations")
    print(f"Burned {counts[forest.BURNT]} of {total_cells} cells ({burn_percentage:.1f}%)")


if __name__ == "__main__":
    # Run the simulation — watching fire spread is weirdly mesmerizing
    # Wind blows east (1, 0) so fire spreads faster to the right
    run_simulation(width=30, height=20, delay=0.3)