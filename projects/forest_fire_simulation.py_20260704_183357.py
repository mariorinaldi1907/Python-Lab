"""
Date: 2026-07-04
Created a cellular automaton that simulates how wildfires spread through a forest grid with configurable wind, ignition probability, and tree density — wanted to visualize how small parameter changes create drastically different outcomes.
"""

#!/usr/bin/env python3
"""
Forest Fire Spread Simulation
A cellular automaton that models wildfire propagation through a forest grid.
Trees can catch fire from neighbors, with probabilities affected by wind direction.
"""

import random
import time
from enum import Enum


class CellState(Enum):
    """Represents the state of a single cell in the forest grid."""
    EMPTY = 0
    TREE = 1
    BURNING = 2
    BURNT = 3


class ForestFireSimulation:
    """
    Simulates wildfire spreading through a forest using cellular automaton rules.
    
    Wind direction affects the probability of fire spreading to neighboring cells.
    Each timestep, burning trees spread fire probabilistically and then burn out.
    """
    
    def __init__(self, width, height, tree_density=0.7, wind_direction=(1, 0), 
                 base_spread_prob=0.5, wind_boost=0.3):
        """
        Initialize the forest grid.
        
        Args:
            width: Grid width
            height: Grid height
            tree_density: Probability that each cell starts with a tree (0-1)
            wind_direction: (dx, dy) tuple indicating wind direction
            base_spread_prob: Base probability of fire spreading to a neighbor
            wind_boost: Additional probability when spreading in wind direction
        """
        self.width = width
        self.height = height
        self.base_spread_prob = base_spread_prob
        self.wind_boost = wind_boost
        
        # Normalize wind direction to get the primary direction vector
        wind_mag = max(abs(wind_direction[0]), abs(wind_direction[1]), 0.1)
        self.wind_dir = (wind_direction[0] / wind_mag, wind_direction[1] / wind_mag)
        
        # Initialize grid with trees based on density
        self.grid = [[CellState.EMPTY for _ in range(width)] for _ in range(height)]
        for y in range(height):
            for x in range(width):
                if random.random() < tree_density:
                    self.grid[y][x] = CellState.TREE
        
        self.step_count = 0
    
    def ignite(self, x, y):
        """Start a fire at the specified coordinates."""
        if 0 <= x < self.width and 0 <= y < self.height:
            if self.grid[y][x] == CellState.TREE:
                self.grid[y][x] = CellState.BURNING
                return True
        return False
    
    def get_neighbors(self, x, y):
        """Get valid neighboring cell coordinates (8-directional)."""
        neighbors = []
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbors.append((nx, ny, dx, dy))
        return neighbors
    
    def calculate_spread_probability(self, dx, dy):
        """
        Calculate fire spread probability based on direction relative to wind.
        
        Wind increases spread probability when fire moves in wind direction.
        """
        # Dot product to see how aligned this direction is with wind
        alignment = (dx * self.wind_dir[0] + dy * self.wind_dir[1])
        
        # Positive alignment (with wind) gets a boost
        if alignment > 0:
            return min(1.0, self.base_spread_prob + self.wind_boost * alignment)
        else:
            return self.base_spread_prob
    
    def step(self):
        """
        Advance simulation by one timestep.
        
        Burning cells attempt to spread fire to tree neighbors, then burn out.
        """
        self.step_count += 1
        new_fires = []  # Track new fires to avoid modifying grid while iterating
        
        # Find all currently burning cells
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == CellState.BURNING:
                    # Try to spread fire to neighbors
                    for nx, ny, dx, dy in self.get_neighbors(x, y):
                        if self.grid[ny][nx] == CellState.TREE:
                            spread_prob = self.calculate_spread_probability(dx, dy)
                            if random.random() < spread_prob:
                                new_fires.append((nx, ny))
        
        # Apply new fires
        for x, y in new_fires:
            self.grid[y][x] = CellState.BURNING
        
        # Burn out all previously burning cells
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == CellState.BURNING and (x, y) not in new_fires:
                    self.grid[y][x] = CellState.BURNT
    
    def is_active(self):
        """Check if there are any burning cells (fire still spreading)."""
        for row in self.grid:
            if CellState.BURNING in row:
                return True
        return False
    
    def count_states(self):
        """Return counts of each cell state."""
        counts = {state: 0 for state in CellState}
        for row in self.grid:
            for cell in row:
                counts[cell] += 1
        return counts
    
    def display(self):
        """Print the current grid state to console."""
        symbols = {
            CellState.EMPTY: ' .',
            CellState.TREE: ' T',
            CellState.BURNING: ' 🔥',  # for fun, though it might not render everywhere
            CellState.BURNT: ' X'
        }
        
        print(f"\n=== Step {self.step_count} ===")
        for row in self.grid:
            print(''.join(symbols[cell] for cell in row))
        
        counts = self.count_states()
        print(f"Trees: {counts[CellState.TREE]}, Burning: {counts[CellState.BURNING]}, "
              f"Burnt: {counts[CellState.BURNT]}")


if __name__ == "__main__":
    # Demo: simulate a forest fire with eastern wind
    print("Forest Fire Simulation")
    print("=" * 50)
    
    random.seed(42)  # Reproducible results
    
    # Create a 30x15 forest with eastern wind
    sim = ForestFireSimulation(
        width=30, 
        height=15, 
        tree_density=0.65,
        wind_direction=(1, 0),  # Blowing east
        base_spread_prob=0.4,
        wind_boost=0.35
    )
    
    # Start fire in the western part of the forest
    sim.ignite(5, 7)
    
    # Run until fire burns out
    sim.display()
    
    while sim.is_active():
        time.sleep(0.3)  # Slow down for visibility
        sim.step()
        sim.display()
    
    print("\nFire has burned out!")
    final_counts = sim.count_states()
    total_trees_initial = final_counts[CellState.TREE] + final_counts[CellState.BURNT]
    if total_trees_initial > 0:
        burn_percentage = (final_counts[CellState.BURNT] / total_trees_initial) * 100
        print(f"Burned {burn_percentage:.1f}% of the forest")