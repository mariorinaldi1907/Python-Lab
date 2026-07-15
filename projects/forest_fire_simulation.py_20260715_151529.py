"""
Date: 2026-07-15
Wrote a cellular automaton that simulates wildfire spread through a forest with configurable wind direction, tree density, and burn rates — prints ASCII frames to watch it evolve.
"""

#!/usr/bin/env python3
"""
Forest Fire Cellular Automaton Simulation

A simple CA where forest fires spread based on neighboring trees,
wind direction, and random ignition. Runs in the terminal with
ASCII visualization.

States:
- Empty (.)
- Tree (T)
- Burning (F)
- Ash (X)
"""

import random
import time
import sys


class ForestFireCA:
    """
    Cellular automaton simulating forest fire spread.
    
    The simulation uses simple rules:
    - Trees can catch fire from burning neighbors
    - Wind affects spread probability in a direction
    - Fires burn out after one step, leaving ash
    - Empty cells can regrow trees slowly
    """
    
    EMPTY = 0
    TREE = 1
    BURNING = 2
    ASH = 3
    
    def __init__(self, width=60, height=20, tree_density=0.6, wind_dir=(1, 0)):
        """
        Initialize the forest grid.
        
        Args:
            width: Grid width
            height: Grid height
            tree_density: Probability of initial tree placement (0-1)
            wind_dir: (dx, dy) tuple for wind direction influence
        """
        self.width = width
        self.height = height
        self.wind_dir = wind_dir
        self.grid = [[self.EMPTY for _ in range(width)] for _ in range(height)]
        
        # Plant initial trees randomly
        for y in range(height):
            for x in range(width):
                if random.random() < tree_density:
                    self.grid[y][x] = self.TREE
        
        # Start a fire somewhere in the middle-ish to make it interesting
        start_y = height // 2 + random.randint(-3, 3)
        start_x = width // 4 + random.randint(-5, 5)
        if 0 <= start_y < height and 0 <= start_x < width:
            self.grid[start_y][start_x] = self.BURNING
    
    def get_neighbors(self, x, y):
        """Get all valid neighboring cells (8-directional)."""
        neighbors = []
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbors.append((nx, ny, dx, dy))
        return neighbors
    
    def step(self):
        """
        Advance the simulation by one time step.
        
        Fire spreads to adjacent trees with probability influenced by wind.
        Burning cells turn to ash. Ash can eventually become empty and regrow.
        """
        new_grid = [[self.EMPTY for _ in range(self.width)] for _ in range(self.height)]
        
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]
                
                if cell == self.EMPTY:
                    # Small chance for a tree to grow
                    if random.random() < 0.01:
                        new_grid[y][x] = self.TREE
                    else:
                        new_grid[y][x] = self.EMPTY
                
                elif cell == self.TREE:
                    # Check if any neighbor is burning
                    caught_fire = False
                    for nx, ny, dx, dy in self.get_neighbors(x, y):
                        if self.grid[ny][nx] == self.BURNING:
                            # Base probability of catching fire
                            base_prob = 0.4
                            
                            # Wind influence: increase prob if wind direction matches
                            wind_boost = 0.0
                            if self.wind_dir[0] * dx + self.wind_dir[1] * dy > 0:
                                wind_boost = 0.3
                            
                            if random.random() < base_prob + wind_boost:
                                caught_fire = True
                                break
                    
                    new_grid[y][x] = self.BURNING if caught_fire else self.TREE
                
                elif cell == self.BURNING:
                    # Fire burns out to ash
                    new_grid[y][x] = self.ASH
                
                elif cell == self.ASH:
                    # Ash eventually becomes empty
                    if random.random() < 0.1:
                        new_grid[y][x] = self.EMPTY
                    else:
                        new_grid[y][x] = self.ASH
        
        self.grid = new_grid
    
    def render(self):
        """Return a string representation of the current grid state."""
        symbols = {
            self.EMPTY: '.',
            self.TREE: 'T',
            self.BURNING: 'F',
            self.ASH: 'X'
        }
        lines = []
        for row in self.grid:
            lines.append(''.join(symbols[cell] for cell in row))
        return '\n'.join(lines)
    
    def count_states(self):
        """Count how many cells are in each state."""
        counts = {self.EMPTY: 0, self.TREE: 0, self.BURNING: 0, self.ASH: 0}
        for row in self.grid:
            for cell in row:
                counts[cell] += 1
        return counts


def run_simulation(steps=50, width=60, height=20, delay=0.15):
    """
    Run the forest fire simulation for a number of steps.
    
    Args:
        steps: Number of simulation steps to run
        width: Grid width
        height: Grid height
        delay: Seconds to pause between frames
    """
    # Wind blowing right and slightly down
    forest = ForestFireCA(width=width, height=height, tree_density=0.65, wind_dir=(1, 0.2))
    
    print("Forest Fire Simulation")
    print("=" * width)
    print("T=Tree  F=Fire  X=Ash  .=Empty")
    print("Wind direction: East (right)\n")
    
    for step_num in range(steps):
        # Clear screen (works on most terminals)
        print("\033[2J\033[H", end='')
        
        print(f"Step {step_num + 1}/{steps}")
        print(forest.render())
        
        counts = forest.count_states()
        print(f"\nTrees: {counts[forest.TREE]}  Burning: {counts[forest.BURNING]}  "
              f"Ash: {counts[forest.ASH]}  Empty: {counts[forest.EMPTY]}")
        
        # Stop if no more fire
        if counts[forest.BURNING] == 0 and step_num > 5:
            print("\nFire has burned out!")
            break
        
        time.sleep(delay)
        forest.step()


if __name__ == "__main__":
    try:
        run_simulation(steps=80, width=70, height=22, delay=0.12)
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user.")
        sys.exit(0)