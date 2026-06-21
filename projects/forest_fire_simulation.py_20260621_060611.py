"""
Date: 2026-06-21
Created a cellular automaton simulating wildfire propagation across a grid with wind effects and probabilistic spreading mechanics.
"""

#!/usr/bin/env python3
"""
Forest Fire Simulation
A cellular automaton that models how wildfires spread through a forest.
Each cell can be: empty, tree, burning, or ash.
Wind direction affects spread probability.
"""

import random
import time
from typing import List, Tuple

# Cell states
EMPTY = 0
TREE = 1
BURNING = 2
ASH = 3

# Display characters for each state
SYMBOLS = {
    EMPTY: '.',
    TREE: '🌲',
    BURNING: '🔥',
    ASH: '▪'
}


class ForestFireSimulation:
    """
    Simulates fire spreading through a forest grid.
    
    Fire spreads to neighboring trees based on base probability,
    modified by wind direction and humidity levels.
    """
    
    def __init__(self, width: int, height: int, tree_density: float = 0.7,
                 base_spread_prob: float = 0.4, humidity: float = 0.5):
        """
        Initialize the forest grid.
        
        Args:
            width: Grid width
            height: Grid height
            tree_density: Probability of each cell starting as a tree (0-1)
            base_spread_prob: Base probability of fire spreading to adjacent tree
            humidity: Reduces spread probability (0=dry, 1=very humid)
        """
        self.width = width
        self.height = height
        self.base_spread_prob = base_spread_prob * (1 - humidity)
        self.grid = [[EMPTY for _ in range(width)] for _ in range(height)]
        self.wind_direction = (random.randint(-1, 1), random.randint(-1, 1))
        
        # Populate with trees randomly
        for y in range(height):
            for x in range(width):
                if random.random() < tree_density:
                    self.grid[y][x] = TREE
    
    def ignite(self, x: int, y: int):
        """Start a fire at the given coordinates."""
        if 0 <= x < self.width and 0 <= y < self.height:
            if self.grid[y][x] == TREE:
                self.grid[y][x] = BURNING
    
    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """
        Get valid neighboring coordinates (8-directional).
        
        Returns list of (x, y) tuples for neighbors within grid bounds.
        """
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbors.append((nx, ny, dx, dy))
        return neighbors
    
    def step(self):
        """
        Advance simulation by one time step.
        
        Burning cells attempt to ignite neighbors, then turn to ash.
        Wind direction increases spread probability in that direction.
        """
        new_grid = [row[:] for row in self.grid]  # Copy current state
        
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == BURNING:
                    # Fire spreads to neighbors
                    for nx, ny, dx, dy in self.get_neighbors(x, y):
                        if self.grid[ny][nx] == TREE:
                            # Calculate spread probability with wind modifier
                            wind_bonus = 0
                            if (dx, dy) == self.wind_direction:
                                wind_bonus = 0.3  # Wind helps fire spread this way
                            elif (dx, dy) == (-self.wind_direction[0], -self.wind_direction[1]):
                                wind_bonus = -0.2  # Against wind is harder
                            
                            spread_prob = min(1.0, self.base_spread_prob + wind_bonus)
                            
                            if random.random() < spread_prob:
                                new_grid[ny][nx] = BURNING
                    
                    # Burning tree becomes ash
                    new_grid[y][x] = ASH
        
        self.grid = new_grid
    
    def count_states(self) -> dict:
        """Return count of each cell state."""
        counts = {EMPTY: 0, TREE: 0, BURNING: 0, ASH: 0}
        for row in self.grid:
            for cell in row:
                counts[cell] += 1
        return counts
    
    def display(self):
        """Print the current grid state."""
        print("\n" + "─" * (self.width * 2))
        for row in self.grid:
            print("".join(SYMBOLS[cell] for cell in row))
        
        counts = self.count_states()
        print(f"Trees: {counts[TREE]} | Burning: {counts[BURNING]} | Ash: {counts[ASH]}")
    
    def has_fire(self) -> bool:
        """Check if any cells are currently burning."""
        return any(BURNING in row for row in self.grid)


def run_simulation(steps: int = 50, delay: float = 0.3):
    """
    Run a forest fire simulation demo.
    
    Creates a forest, starts fires at random locations, and shows
    how the fire spreads over time with wind effects.
    """
    print("🌲 Forest Fire Simulation 🔥")
    print("=" * 40)
    
    # Create a moderately dense forest with some humidity
    sim = ForestFireSimulation(width=30, height=20, tree_density=0.65,
                               base_spread_prob=0.5, humidity=0.3)
    
    # Wind direction affects how fire spreads
    wind_desc = {
        (-1, -1): "↖ NW", (0, -1): "↑ N", (1, -1): "↗ NE",
        (-1, 0): "← W", (0, 0): "calm", (1, 0): "→ E",
        (-1, 1): "↙ SW", (0, 1): "↓ S", (1, 1): "↘ SE"
    }
    print(f"Wind: {wind_desc.get(sim.wind_direction, 'variable')}\n")
    
    # Start fires at a few random locations
    for _ in range(3):
        sim.ignite(random.randint(0, sim.width - 1), random.randint(0, sim.height - 1))
    
    step = 0
    sim.display()
    
    while sim.has_fire() and step < steps:
        time.sleep(delay)
        step += 1
        print(f"\nStep {step}")
        sim.step()
        sim.display()
    
    print("\n🔥 Fire burned out!" if not sim.has_fire() else "\n⏰ Simulation ended")
    final = sim.count_states()
    total = sum(final.values())
    print(f"Final stats: {final[ASH]}/{total} cells burned "
          f"({100 * final[ASH] / total:.1f}% of forest)")


if __name__ == "__main__":
    # Run the simulation — watch the fire spread!
    # Wind direction is random each run, creating different patterns
    run_simulation(steps=50, delay=0.2)