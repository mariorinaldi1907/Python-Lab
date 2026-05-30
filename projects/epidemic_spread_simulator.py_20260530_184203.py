"""
Date: 2026-05-30
Implemented a spatial epidemic simulator where agents move randomly on a grid and transition through Susceptible→Exposed→Infected→Recovered states with configurable parameters.
"""

#!/usr/bin/env python3
"""
Spatial SEIR Epidemic Simulator

Simulates disease spread on a 2D grid where agents move randomly.
Each agent can be in one of four states: Susceptible, Exposed, Infected, or Recovered.
Transmission happens when a susceptible agent is within infection_radius of an infected agent.
"""

import random
import math
from collections import defaultdict


class Agent:
    """Represents a single person in the simulation."""
    
    def __init__(self, x, y, state='S'):
        """
        Initialize an agent at position (x, y) with a given disease state.
        
        Args:
            x: X coordinate
            y: Y coordinate
            state: One of 'S' (susceptible), 'E' (exposed), 'I' (infected), 'R' (recovered)
        """
        self.x = x
        self.y = y
        self.state = state
        self.days_in_state = 0  # Track how long they've been in current state
    
    def move(self, grid_size, step_size=1.0):
        """Random walk movement - agent moves in a random direction."""
        angle = random.uniform(0, 2 * math.pi)
        new_x = self.x + step_size * math.cos(angle)
        new_y = self.y + step_size * math.sin(angle)
        
        # Keep within bounds (wrap around)
        self.x = new_x % grid_size
        self.y = new_y % grid_size
    
    def update_state(self, exposed_period=3, infected_period=7):
        """
        Progress through disease states based on time.
        E→I after exposed_period days, I→R after infected_period days.
        """
        self.days_in_state += 1
        
        if self.state == 'E' and self.days_in_state >= exposed_period:
            self.state = 'I'
            self.days_in_state = 0
        elif self.state == 'I' and self.days_in_state >= infected_period:
            self.state = 'R'
            self.days_in_state = 0


class EpidemicSimulator:
    """Runs the spatial epidemic simulation."""
    
    def __init__(self, population=200, grid_size=100.0, initial_infected=5,
                 infection_radius=3.0, transmission_prob=0.3):
        """
        Set up the simulation parameters.
        
        Args:
            population: Total number of agents
            grid_size: Size of the square grid
            initial_infected: Number of initially infected agents
            infection_radius: Distance within which transmission can occur
            transmission_prob: Probability of transmission per contact per day
        """
        self.grid_size = grid_size
        self.infection_radius = infection_radius
        self.transmission_prob = transmission_prob
        self.day = 0
        
        # Create agents randomly distributed on the grid
        self.agents = []
        for i in range(population):
            x = random.uniform(0, grid_size)
            y = random.uniform(0, grid_size)
            state = 'I' if i < initial_infected else 'S'
            self.agents.append(Agent(x, y, state))
    
    def distance(self, agent1, agent2):
        """Calculate Euclidean distance between two agents."""
        dx = agent1.x - agent2.x
        dy = agent1.y - agent2.y
        return math.sqrt(dx**2 + dy**2)
    
    def check_transmissions(self):
        """
        Check for disease transmission between agents.
        Only infected agents can transmit to susceptible agents within infection_radius.
        """
        infected = [a for a in self.agents if a.state == 'I']
        susceptible = [a for a in self.agents if a.state == 'S']
        
        for s_agent in susceptible:
            for i_agent in infected:
                if self.distance(s_agent, i_agent) <= self.infection_radius:
                    # Transmission happens probabilistically
                    if random.random() < self.transmission_prob:
                        s_agent.state = 'E'
                        s_agent.days_in_state = 0
                        break  # Once exposed, stop checking other infected agents
    
    def step(self):
        """Advance the simulation by one day."""
        self.day += 1
        
        # Move all agents
        for agent in self.agents:
            agent.move(self.grid_size)
        
        # Check for new transmissions
        self.check_transmissions()
        
        # Update disease progression
        for agent in self.agents:
            agent.update_state()
    
    def get_counts(self):
        """Return count of agents in each state."""
        counts = defaultdict(int)
        for agent in self.agents:
            counts[agent.state] += 1
        return counts
    
    def print_status(self):
        """Print current day and state counts."""
        counts = self.get_counts()
        print(f"Day {self.day:3d} | S: {counts['S']:3d} | E: {counts['E']:3d} | "
              f"I: {counts['I']:3d} | R: {counts['R']:3d}")
    
    def is_active(self):
        """Check if epidemic is still active (exposed or infected agents exist)."""
        counts = self.get_counts()
        return counts['E'] > 0 or counts['I'] > 0


def run_simulation(days=60, verbose=True):
    """
    Run a complete epidemic simulation.
    
    Args:
        days: Maximum number of days to simulate
        verbose: If True, print status every day
    
    Returns:
        The simulator object after completion
    """
    sim = EpidemicSimulator(
        population=200,
        grid_size=100.0,
        initial_infected=3,
        infection_radius=4.0,
        transmission_prob=0.25
    )
    
    if verbose:
        print("=" * 60)
        print("Spatial SEIR Epidemic Simulation")
        print("=" * 60)
        sim.print_status()
    
    for _ in range(days):
        sim.step()
        if verbose:
            sim.print_status()
        
        # Stop early if epidemic has ended
        if not sim.is_active():
            if verbose:
                print("\nEpidemic has ended (no more exposed or infected agents).")
            break
    
    if verbose:
        print("=" * 60)
        final_counts = sim.get_counts()
        attack_rate = (final_counts['R'] / len(sim.agents)) * 100
        print(f"Final attack rate: {attack_rate:.1f}% of population infected")
    
    return sim


if __name__ == "__main__":
    # Run a demo simulation
    random.seed(42)  # For reproducibility
    run_simulation(days=60, verbose=True)