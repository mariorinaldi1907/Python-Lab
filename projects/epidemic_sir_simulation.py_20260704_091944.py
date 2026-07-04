"""
Date: 2026-07-04
Implemented a spatial SIR (Susceptible-Infected-Recovered) epidemic simulator that runs on a 2D grid and prints ASCII heatmaps over time — helps me understand how diseases spread locally.
"""

#!/usr/bin/env python3
"""
Spatial SIR epidemic model simulator.

Simulates disease spread on a 2D grid where individuals can be:
- Susceptible (S): can catch the disease
- Infected (I): currently sick and can spread it
- Recovered (R): immune after recovery

The spatial component means infection spreads to neighbors, not just randomly.
"""

import random
import time
from collections import namedtuple
from typing import List, Tuple


# Using namedtuple for clean parameter passing
SimParams = namedtuple('SimParams', [
    'grid_size',
    'initial_infected',
    'transmission_rate',  # probability of S->I when near infected
    'recovery_rate',      # probability of I->R each step
    'max_steps'
])


class EpidemicGrid:
    """
    2D grid-based epidemic simulator using SIR model.
    
    Each cell is in one of three states: 0=S, 1=I, 2=R
    Infection spreads to neighboring cells (8-neighborhood).
    """
    
    def __init__(self, params: SimParams):
        """Initialize grid with mostly susceptible, few infected."""
        self.params = params
        self.size = params.grid_size
        
        # Start with all susceptible (state 0)
        self.grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        
        # Randomly infect initial_infected individuals
        self._seed_infection()
        
        # Track statistics over time
        self.history = {
            'susceptible': [],
            'infected': [],
            'recovered': []
        }
    
    def _seed_infection(self):
        """Place initial infected individuals randomly on grid."""
        positions = [(i, j) for i in range(self.size) for j in range(self.size)]
        infected_positions = random.sample(positions, self.params.initial_infected)
        
        for i, j in infected_positions:
            self.grid[i][j] = 1  # Set to infected
    
    def _get_neighbors(self, i: int, j: int) -> List[Tuple[int, int]]:
        """Return list of valid neighbor coordinates (8-neighborhood)."""
        neighbors = []
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue
                ni, nj = i + di, j + dj
                if 0 <= ni < self.size and 0 <= nj < self.size:
                    neighbors.append((ni, nj))
        return neighbors
    
    def step(self):
        """
        Execute one time step of the simulation.
        
        Two-phase update to avoid order-of-update artifacts:
        1. Calculate all state changes
        2. Apply them simultaneously
        """
        new_grid = [row[:] for row in self.grid]  # Deep copy
        
        for i in range(self.size):
            for j in range(self.size):
                current_state = self.grid[i][j]
                
                if current_state == 0:  # Susceptible
                    # Check if any neighbors are infected
                    neighbors = self._get_neighbors(i, j)
                    infected_neighbors = sum(1 for ni, nj in neighbors if self.grid[ni][nj] == 1)
                    
                    # Probability increases with more infected neighbors
                    # Using 1 - (1 - p)^n formula for multiple exposure events
                    if infected_neighbors > 0:
                        exposure_prob = 1 - (1 - self.params.transmission_rate) ** infected_neighbors
                        if random.random() < exposure_prob:
                            new_grid[i][j] = 1  # Become infected
                
                elif current_state == 1:  # Infected
                    # Random chance of recovery each step
                    if random.random() < self.params.recovery_rate:
                        new_grid[i][j] = 2  # Recover
        
        self.grid = new_grid
        self._record_stats()
    
    def _record_stats(self):
        """Count and record current population in each state."""
        s_count = sum(row.count(0) for row in self.grid)
        i_count = sum(row.count(1) for row in self.grid)
        r_count = sum(row.count(2) for row in self.grid)
        
        self.history['susceptible'].append(s_count)
        self.history['infected'].append(i_count)
        self.history['recovered'].append(r_count)
    
    def print_grid(self):
        """Print grid as ASCII art with color-coded states."""
        symbols = {0: '·', 1: '█', 2: '░'}  # S, I, R
        
        for row in self.grid:
            print(''.join(symbols[cell] for cell in row))
    
    def print_stats(self, step: int):
        """Print current statistics in readable format."""
        total = self.size * self.size
        s = self.history['susceptible'][-1]
        i = self.history['infected'][-1]
        r = self.history['recovered'][-1]
        
        print(f"Step {step:3d} | S: {s:4d} ({100*s/total:5.1f}%) | "
              f"I: {i:4d} ({100*i/total:5.1f}%) | R: {r:4d} ({100*r/total:5.1f}%)")


def run_simulation(params: SimParams, visualize: bool = True, delay: float = 0.3):
    """
    Run the epidemic simulation with given parameters.
    
    Args:
        params: Simulation parameters
        visualize: Whether to print grid at each step
        delay: Seconds to pause between steps (for visualization)
    """
    grid = EpidemicGrid(params)
    grid._record_stats()  # Record initial state
    
    print(f"Starting simulation on {params.grid_size}x{params.grid_size} grid")
    print(f"Initial infected: {params.initial_infected}")
    print(f"Transmission rate: {params.transmission_rate:.2f}, Recovery rate: {params.recovery_rate:.2f}")
    print("=" * 60)
    
    for step in range(params.max_steps):
        if visualize:
            print(f"\n--- Step {step} ---")
            grid.print_grid()
        
        grid.print_stats(step)
        
        # Stop if no more infected individuals
        if grid.history['infected'][-1] == 0:
            print(f"\nEpidemic ended at step {step} (no more infected)")
            break
        
        grid.step()
        
        if visualize and step < params.max_steps - 1:
            time.sleep(delay)
    
    # Final summary
    print("\n" + "=" * 60)
    print("FINAL RESULTS:")
    grid.print_stats(step)
    print(f"Peak infected: {max(grid.history['infected'])} individuals")
    print(f"Attack rate: {100 * grid.history['recovered'][-1] / (params.grid_size ** 2):.1f}%")


if __name__ == "__main__":
    # Setting up parameters that give interesting dynamics
    # I tuned these to get a realistic-looking outbreak curve
    params = SimParams(
        grid_size=30,
        initial_infected=3,
        transmission_rate=0.15,   # 15% chance per infected neighbor per step
        recovery_rate=0.05,       # 5% chance to recover each step (avg ~20 steps sick)
        max_steps=100
    )
    
    run_simulation(params, visualize=True, delay=0.2)