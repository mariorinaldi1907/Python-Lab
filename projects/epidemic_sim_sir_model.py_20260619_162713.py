"""
Date: 2026-06-19
Implemented a spatial SIR epidemic model where agents move randomly on a grid and spread infection through proximity — runs entirely in the terminal with ASCII visualization.
"""

#!/usr/bin/env python3
"""
Epidemic Simulator using the SIR (Susceptible-Infected-Recovered) model.

This simulates disease spread on a 2D grid where agents move randomly.
Infection spreads when susceptible agents come within a certain distance
of infected agents. I wanted to see how spatial dynamics affect epidemic curves.
"""

import random
import time
from collections import defaultdict
from math import sqrt


class Agent:
    """Represents a single person in the simulation."""
    
    def __init__(self, x, y, state='S'):
        """
        Initialize an agent at position (x, y) with health state.
        
        Args:
            x: x-coordinate on grid
            y: y-coordinate on grid
            state: 'S' (susceptible), 'I' (infected), or 'R' (recovered)
        """
        self.x = x
        self.y = y
        self.state = state
        self.days_infected = 0  # Track how long they've been sick
    
    def move(self, grid_size, step_size=1):
        """Random walk movement with boundary wrapping."""
        dx = random.choice([-step_size, 0, step_size])
        dy = random.choice([-step_size, 0, step_size])
        self.x = (self.x + dx) % grid_size
        self.y = (self.y + dy) % grid_size
    
    def distance_to(self, other):
        """Calculate Euclidean distance to another agent."""
        # Using toroidal distance since the grid wraps
        dx = min(abs(self.x - other.x), abs(self.x - other.x + 50), abs(self.x - other.x - 50))
        dy = min(abs(self.y - other.y), abs(self.y - other.y + 50), abs(self.y - other.y - 50))
        return sqrt(dx**2 + dy**2)


class EpidemicSimulator:
    """Runs the epidemic simulation with configurable parameters."""
    
    def __init__(self, population=100, grid_size=50, infection_radius=2.0,
                 infection_prob=0.3, recovery_days=7):
        """
        Set up the simulation parameters.
        
        Args:
            population: Number of agents to simulate
            grid_size: Size of the square grid
            infection_radius: Distance within which infection can spread
            infection_prob: Probability of infection on contact per day
            recovery_days: Days until an infected person recovers
        """
        self.grid_size = grid_size
        self.infection_radius = infection_radius
        self.infection_prob = infection_prob
        self.recovery_days = recovery_days
        
        # Create agents randomly distributed on the grid
        self.agents = []
        for _ in range(population):
            x = random.randint(0, grid_size - 1)
            y = random.randint(0, grid_size - 1)
            self.agents.append(Agent(x, y, state='S'))
        
        # Start with patient zero
        self.agents[0].state = 'I'
        
        self.day = 0
        self.history = {'S': [], 'I': [], 'R': []}
    
    def step(self):
        """Execute one day of the simulation."""
        self.day += 1
        
        # Move all agents
        for agent in self.agents:
            agent.move(self.grid_size)
        
        # Check for new infections
        infected_agents = [a for a in self.agents if a.state == 'I']
        susceptible_agents = [a for a in self.agents if a.state == 'S']
        
        for susceptible in susceptible_agents:
            for infected in infected_agents:
                if susceptible.distance_to(infected) <= self.infection_radius:
                    # Infection happens with some probability
                    if random.random() < self.infection_prob:
                        susceptible.state = 'I'
                        break  # Only need one contact to get infected
        
        # Update infected agents and check for recovery
        for agent in self.agents:
            if agent.state == 'I':
                agent.days_infected += 1
                if agent.days_infected >= self.recovery_days:
                    agent.state = 'R'
                    agent.days_infected = 0
        
        # Record statistics
        counts = {'S': 0, 'I': 0, 'R': 0}
        for agent in self.agents:
            counts[agent.state] += 1
        
        for state in ['S', 'I', 'R']:
            self.history[state].append(counts[state])
    
    def visualize(self):
        """Print a simple ASCII visualization of the current state."""
        # Create empty grid
        grid = [[' ' for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Place agents on grid (last one wins if overlap)
        for agent in self.agents:
            grid[agent.y][agent.x] = agent.state
        
        # Print with border
        print(f"\n=== Day {self.day} ===")
        print("+" + "-" * self.grid_size + "+")
        for row in grid:
            print("|" + "".join(row) + "|")
        print("+" + "-" * self.grid_size + "+")
    
    def print_stats(self):
        """Print current population statistics."""
        counts = {'S': 0, 'I': 0, 'R': 0}
        for agent in self.agents:
            counts[agent.state] += 1
        
        total = len(self.agents)
        print(f"Susceptible: {counts['S']:3d} ({100*counts['S']/total:5.1f}%)")
        print(f"Infected:    {counts['I']:3d} ({100*counts['I']/total:5.1f}%)")
        print(f"Recovered:   {counts['R']:3d} ({100*counts['R']/total:5.1f}%)")


if __name__ == "__main__":
    # Run a demo simulation
    print("Starting epidemic simulation...")
    print("S = Susceptible, I = Infected, R = Recovered\n")
    
    sim = EpidemicSimulator(
        population=80,
        grid_size=30,
        infection_radius=2.5,
        infection_prob=0.25,
        recovery_days=5
    )
    
    # Run for a bunch of days or until no more infected
    max_days = 50
    for day in range(max_days):
        sim.step()
        
        # Print visualization every few days
        if day % 5 == 0 or day < 3:
            sim.visualize()
            sim.print_stats()
            time.sleep(0.5)  # Slow it down so you can see what's happening
        
        # Stop if epidemic is over
        infected_count = sum(1 for a in sim.agents if a.state == 'I')
        if infected_count == 0:
            print(f"\nEpidemic ended on day {sim.day}")
            sim.visualize()
            sim.print_stats()
            break
    
    # Final summary
    print("\n=== Final Epidemic Curve ===")
    print(f"Peak infections: {max(sim.history['I'])} people on day {sim.history['I'].index(max(sim.history['I'])) + 1}")
    print(f"Total infected over time: {sim.history['R'][-1] + sum(1 for a in sim.agents if a.state == 'I')}")
    print(f"Never infected: {sim.history['S'][-1]}")