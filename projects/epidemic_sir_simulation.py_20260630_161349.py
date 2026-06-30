"""
Date: 2026-06-30
Implemented a spatial SIR (Susceptible-Infected-Recovered) epidemic simulator where agents move around a 2D grid and spread infection through proximity — helps visualize how diseases propagate through populations.
"""

#!/usr/bin/env python3
"""
SIR Epidemic Model Simulation
A simple spatial epidemic simulator where agents move randomly on a grid
and can infect each other when they get close enough.
"""

import random
import math
from collections import defaultdict


class Agent:
    """Represents a single person in the simulation with position and health status."""
    
    def __init__(self, x, y, status='S'):
        """
        Initialize an agent with position and health status.
        
        Args:
            x: X coordinate on the grid
            y: Y coordinate on the grid
            status: 'S' (Susceptible), 'I' (Infected), or 'R' (Recovered)
        """
        self.x = x
        self.y = y
        self.status = status
        self.days_infected = 0  # Track how long they've been sick
    
    def move(self, grid_size, step_size=1.0):
        """Move randomly in any direction, staying within grid bounds."""
        angle = random.uniform(0, 2 * math.pi)
        dx = step_size * math.cos(angle)
        dy = step_size * math.sin(angle)
        
        self.x = max(0, min(grid_size, self.x + dx))
        self.y = max(0, min(grid_size, self.y + dy))
    
    def distance_to(self, other):
        """Calculate Euclidean distance to another agent."""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


class EpidemicSimulation:
    """Manages the entire epidemic simulation with multiple agents."""
    
    def __init__(self, num_agents=100, grid_size=50, infection_radius=2.0,
                 infection_prob=0.3, recovery_days=7):
        """
        Set up the simulation parameters.
        
        Args:
            num_agents: Total number of agents in the simulation
            grid_size: Size of the square grid (0 to grid_size in both dimensions)
            infection_radius: Distance within which infection can spread
            infection_prob: Probability of infection when in contact
            recovery_days: Days infected before recovering (gaining immunity)
        """
        self.grid_size = grid_size
        self.infection_radius = infection_radius
        self.infection_prob = infection_prob
        self.recovery_days = recovery_days
        self.day = 0
        
        # Create agents randomly distributed across the grid
        self.agents = []
        for _ in range(num_agents):
            x = random.uniform(0, grid_size)
            y = random.uniform(0, grid_size)
            self.agents.append(Agent(x, y, 'S'))
        
        # Start with a few infected individuals (patient zero and friends)
        num_initial_infected = max(1, num_agents // 50)
        for i in range(num_initial_infected):
            self.agents[i].status = 'I'
    
    def step(self):
        """Simulate one day: agents move, infections spread, and people recover."""
        # Move all agents
        for agent in self.agents:
            agent.move(self.grid_size)
        
        # Check for new infections
        # Only susceptible agents can become infected
        susceptible = [a for a in self.agents if a.status == 'S']
        infected = [a for a in self.agents if a.status == 'I']
        
        for s_agent in susceptible:
            # Check if any infected agent is close enough
            for i_agent in infected:
                if s_agent.distance_to(i_agent) <= self.infection_radius:
                    # Roll the dice for infection
                    if random.random() < self.infection_prob:
                        s_agent.status = 'I'
                        break  # Once infected, no need to check others
        
        # Update infected agents and check for recovery
        for agent in self.agents:
            if agent.status == 'I':
                agent.days_infected += 1
                if agent.days_infected >= self.recovery_days:
                    agent.status = 'R'
                    agent.days_infected = 0  # Reset counter
        
        self.day += 1
    
    def get_counts(self):
        """Return current counts of Susceptible, Infected, and Recovered."""
        counts = defaultdict(int)
        for agent in self.agents:
            counts[agent.status] += 1
        return counts['S'], counts['I'], counts['R']
    
    def is_active(self):
        """Check if the epidemic is still ongoing (any infected agents remain)."""
        return any(agent.status == 'I' for agent in self.agents)
    
    def print_status(self):
        """Print current day and population statistics."""
        s, i, r = self.get_counts()
        total = len(self.agents)
        print(f"Day {self.day:3d} | S: {s:3d} ({100*s/total:5.1f}%) | "
              f"I: {i:3d} ({100*i/total:5.1f}%) | "
              f"R: {r:3d} ({100*r/total:5.1f}%)")


def run_simulation(days=60, **kwargs):
    """
    Run a complete epidemic simulation for a specified number of days.
    
    Args:
        days: Maximum number of days to simulate
        **kwargs: Additional parameters to pass to EpidemicSimulation
    """
    sim = EpidemicSimulation(**kwargs)
    
    print("=== Epidemic Simulation Starting ===")
    print(f"Population: {len(sim.agents)}, Grid: {sim.grid_size}x{sim.grid_size}")
    print(f"Infection radius: {sim.infection_radius}, Probability: {sim.infection_prob}")
    print(f"Recovery time: {sim.recovery_days} days\n")
    
    sim.print_status()
    
    # Run until no more infected or we hit the day limit
    while sim.is_active() and sim.day < days:
        sim.step()
        # Print every 5 days to avoid too much output
        if sim.day % 5 == 0 or not sim.is_active():
            sim.print_status()
    
    print("\n=== Simulation Complete ===")
    s, i, r = sim.get_counts()
    print(f"Final state after {sim.day} days:")
    print(f"  Never infected: {s} ({100*s/len(sim.agents):.1f}%)")
    print(f"  Still infected: {i} ({100*i/len(sim.agents):.1f}%)")
    print(f"  Recovered (immune): {r} ({100*r/len(sim.agents):.1f}%)")


if __name__ == "__main__":
    # Run a simulation with default parameters
    # These values give interesting epidemic dynamics without taking forever
    run_simulation(
        days=100,
        num_agents=150,
        grid_size=40,
        infection_radius=2.5,
        infection_prob=0.25,
        recovery_days=10
    )