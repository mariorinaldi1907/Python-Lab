"""
Date: 2026-05-31
Created a cellular automaton simulating wildfire spread across a forest grid with wind effects, density variations, and real-time ASCII visualization.
"""

#!/usr/bin/env python3
"""
Forest Fire Simulation
A cellular automaton modeling how fire spreads through a forest.
Trees can ignite from neighbors, wind affects spread direction, and density matters.
"""

import random
import time
from enum import Enum


class CellState(Enum):
    """Represents the state of a single cell in the forest grid."""
    EMPTY = 0
    TREE = 1
    BURNING = 2
    ASH = 3


class ForestFireSimulation:
    """
    Simulates fire spreading through a forest grid.
    
    The fire spreads based on:
    - Proximity to burning trees
    - Wind direction (increases spread probability in wind direction)
    - Tree density (affects initial forest layout)
    """
    
    def __init__(self, width=50, height=25, tree_density=0.65, wind_direction='E'):
        """
        Initialize the forest simulation.
        
        Args:
            width: Grid width
            height: Grid height
            tree_density: Probability a cell starts with a tree (0.0-1.0)
            wind_direction: One of 'N', 'S', 'E', 'W', 'NONE'
        """
        self.width = width
        self.height = height
        self.tree_density = tree_density
        self.wind_direction = wind_direction
        self.grid = [[CellState.EMPTY for _ in range(width)] for _ in range(height)]
        self.generation = 0
        
        # Wind affects spread probability - stronger in wind direction
        self.wind_vectors = {
            'N': (-1, 0),
            'S': (1, 0),
            'E': (0, 1),
            'W': (0, -1),
            'NONE': (0, 0)
        }
        
        self._initialize_forest()
    
    def _initialize_forest(self):
        """Populate the grid with trees based on density, then ignite a starter fire."""
        # Plant trees randomly
        for row in range(self.height):
            for col in range(self.width):
                if random.random() < self.tree_density:
                    self.grid[row][col] = CellState.TREE
        
        # Start a fire in the middle-left area (because fires usually start somewhere specific)
        start_row = self.height // 2
        start_col = self.width // 4
        if self.grid[start_row][start_col] == CellState.TREE:
            self.grid[start_row][start_col] = CellState.BURNING
        else:
            # Find nearest tree to ignite if starting point is empty
            for offset in range(1, max(self.width, self.height)):
                for dr in range(-offset, offset + 1):
                    for dc in range(-offset, offset + 1):
                        r, c = start_row + dr, start_col + dc
                        if 0 <= r < self.height and 0 <= c < self.width:
                            if self.grid[r][c] == CellState.TREE:
                                self.grid[r][c] = CellState.BURNING
                                return
    
    def step(self):
        """
        Advance the simulation by one time step.
        
        Rules:
        - Burning trees become ash
        - Trees catch fire from burning neighbors (probability-based)
        - Wind increases ignition chance in its direction
        """
        new_grid = [row[:] for row in self.grid]  # Deep copy
        
        for row in range(self.height):
            for col in range(self.width):
                if self.grid[row][col] == CellState.BURNING:
                    # Burning trees turn to ash
                    new_grid[row][col] = CellState.ASH
                    
                    # Try to ignite neighbors
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0:
                                continue
                            
                            nr, nc = row + dr, col + dc
                            if 0 <= nr < self.height and 0 <= nc < self.width:
                                if self.grid[nr][nc] == CellState.TREE:
                                    # Base ignition probability
                                    ignite_prob = 0.4
                                    
                                    # Wind boosts probability in its direction
                                    wind_dy, wind_dx = self.wind_vectors[self.wind_direction]
                                    if (dr, dc) == (wind_dy, wind_dx):
                                        ignite_prob = 0.85  # Much higher with wind
                                    elif dr == wind_dy or dc == wind_dx:
                                        ignite_prob = 0.6  # Moderate boost
                                    
                                    if random.random() < ignite_prob:
                                        new_grid[nr][nc] = CellState.BURNING
        
        self.grid = new_grid
        self.generation += 1
    
    def is_active(self):
        """Check if there are still burning trees (simulation ongoing)."""
        for row in self.grid:
            if CellState.BURNING in row:
                return True
        return False
    
    def render(self):
        """
        Return ASCII representation of the current grid state.
        
        Symbols:
        - ' ' = empty
        - '🌲' = tree (using emoji for fun, falls back to 'T' on some terminals)
        - '🔥' = burning
        - '·' = ash
        """
        symbols = {
            CellState.EMPTY: ' ',
            CellState.TREE: 'T',
            CellState.BURNING: 'F',
            CellState.ASH: '.'
        }
        
        lines = []
        lines.append(f"Generation {self.generation} | Wind: {self.wind_direction}")
        lines.append("+" + "-" * self.width + "+")
        
        for row in self.grid:
            line = "|" + "".join(symbols[cell] for cell in row) + "|"
            lines.append(line)
        
        lines.append("+" + "-" * self.width + "+")
        
        # Stats
        tree_count = sum(row.count(CellState.TREE) for row in self.grid)
        burning_count = sum(row.count(CellState.BURNING) for row in self.grid)
        ash_count = sum(row.count(CellState.ASH) for row in self.grid)
        lines.append(f"Trees: {tree_count} | Burning: {burning_count} | Ash: {ash_count}")
        
        return "\n".join(lines)


def run_simulation(width=50, height=20, tree_density=0.6, wind='E', delay=0.15):
    """
    Run a forest fire simulation until the fire burns out.
    
    Args:
        width: Grid width
        height: Grid height
        tree_density: Forest density (0.0-1.0)
        wind: Wind direction ('N', 'S', 'E', 'W', 'NONE')
        delay: Seconds between frames
    """
    sim = ForestFireSimulation(width=width, height=height, 
                               tree_density=tree_density, 
                               wind_direction=wind)
    
    while sim.is_active() and sim.generation < 200:  # Safety limit
        print("\033[2J\033[H")  # Clear screen (ANSI escape)
        print(sim.render())
        time.sleep(delay)
        sim.step()
    
    # Show final state
    print("\033[2J\033[H")
    print(sim.render())
    print("\n🔚 Fire burned out!")


if __name__ == "__main__":
    print("Forest Fire Simulation")
    print("=" * 50)
    print("Watch as fire spreads through a forest with wind effects.")
    print("Starting in 2 seconds...\n")
    time.sleep(2)
    
    # Run with eastward wind — you'll see the fire pushed right
    run_simulation(width=60, height=20, tree_density=0.65, wind='E', delay=0.2)