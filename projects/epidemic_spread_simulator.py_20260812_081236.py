"""
Date: 2026-08-12
Implemented a spatial epidemic simulator using the SIR model where agents move randomly and infect nearby susceptibles — wanted to see infection dynamics play out in 2D space.
"""

#!/usr/bin/env python3
"""
Epidemic spread simulator using a spatial SIR (Susceptible-Infected-Recovered) model.
Agents move randomly in 2D space and can infect others within a certain radius.
"""

import random
import math
from collections import defaultdict


class Agent:
    """
    Represents a single individual in the epidemic simulation.
    
    States: 'S' (susceptible), 'I' (infected), 'R' (recovered)
    """
    
    def __init__(self, x, y, state='S'):
        """
        Initialize an agent at position (x, y) with a given health state.
        
        Args:
            x: X-coordinate position
            y: Y-coordinate position
            state: Initial health state ('S', 'I', or 'R')
        """
        self.x = x
        self.y = y
        self.state = state
        self.infection_time = 0  # How long agent has been infected
    
    def move(self, world_size, step_size=0.5):
        """
        Random walk movement. Agents wander around their local area.
        
        Args:
            world_size: Size of the square world (wraps at edges)
            step_size: How far the agent can move in one step
        """
        # Random direction
        angle = random.uniform(0, 2 * math.pi)
        dx = step_size * math.cos(angle)
        dy = step_size * math.sin(angle)
        
        # Update position with wrapping (toroidal world)
        self.x = (self.x + dx) % world_size
        self.y = (self.y + dy) % world_size
    
    def distance_to(self, other):
        """Calculate Euclidean distance to another agent."""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


class EpidemicSimulator:
    """
    Simulates disease spread in a population with spatial dynamics.
    """
    
    def __init__(self, population=100, world_size=50.0, initial_infected=3,
                 infection_radius=2.0, infection_prob=0.3, recovery_time=10):
        """
        Set up the simulation parameters.
        
        Args:
            population: Total number of agents
            world_size: Size of the square world
            initial_infected: Number of initially infected agents
            infection_radius: Distance within which infection can spread
            infection_prob: Probability of transmission per contact
            recovery_time: Steps until an infected agent recovers
        """
        self.world_size = world_size
        self.infection_radius = infection_radius
        self.infection_prob = infection_prob
        self.recovery_time = recovery_time
        self.step_count = 0
        
        # Initialize agents randomly in the world
        self.agents = []
        for _ in range(population):
            x = random.uniform(0, world_size)
            y = random.uniform(0, world_size)
            self.agents.append(Agent(x, y, state='S'))
        
        # Infect a few random agents to start the epidemic
        for agent in random.sample(self.agents, initial_infected):
            agent.state = 'I'
    
    def step(self):
        """
        Run one time step of the simulation.
        
        1. Move all agents
        2. Check for infections
        3. Update infection timers and recover agents
        """
        # Move everyone
        for agent in self.agents:
            agent.move(self.world_size)
        
        # Check for new infections
        # Only susceptible agents can get infected
        susceptible = [a for a in self.agents if a.state == 'S']
        infected = [a for a in self.agents if a.state == 'I']
        
        for s_agent in susceptible:
            for i_agent in infected:
                # Check if they're close enough
                if s_agent.distance_to(i_agent) <= self.infection_radius:
                    # Probabilistic transmission
                    if random.random() < self.infection_prob:
                        s_agent.state = 'I'
                        break  # Once infected, stop checking
        
        # Update infected agents (increment time, check for recovery)
        for agent in self.agents:
            if agent.state == 'I':
                agent.infection_time += 1
                if agent.infection_time >= self.recovery_time:
                    agent.state = 'R'
                    agent.infection_time = 0  # Reset timer
        
        self.step_count += 1
    
    def get_counts(self):
        """
        Count how many agents are in each state.
        
        Returns:
            Dictionary with counts for 'S', 'I', 'R'
        """
        counts = defaultdict(int)
        for agent in self.agents:
            counts[agent.state] += 1
        return dict(counts)
    
    def run(self, steps=100, verbose=True):
        """
        Run the simulation for a given number of steps.
        
        Args:
            steps: Number of time steps to simulate
            verbose: Whether to print progress
        """
        if verbose:
            print(f"Starting epidemic simulation with {len(self.agents)} agents")
            print(f"World size: {self.world_size}, Infection radius: {self.infection_radius}")
            print(f"Infection probability: {self.infection_prob}, Recovery time: {self.recovery_time}\n")
        
        for _ in range(steps):
            self.step()
            counts = self.get_counts()
            
            # Print every 10 steps to avoid spam
            if verbose and self.step_count % 10 == 0:
                print(f"Step {self.step_count:3d} | S: {counts.get('S', 0):3d} | "
                      f"I: {counts.get('I', 0):3d} | R: {counts.get('R', 0):3d}")
            
            # Stop early if no more infected (epidemic burned out)
            if counts.get('I', 0) == 0:
                if verbose:
                    print(f"\nEpidemic ended at step {self.step_count} (no more infected)")
                break
        
        return self.get_counts()


if __name__ == "__main__":
    # Run a demo simulation
    print("=" * 60)
    print("EPIDEMIC SPREAD SIMULATION (SIR Model)")
    print("=" * 60 + "\n")
    
    # Create simulator with reasonable parameters
    sim = EpidemicSimulator(
        population=150,
        world_size=40.0,
        initial_infected=5,
        infection_radius=2.5,
        infection_prob=0.25,
        recovery_time=15
    )
    
    # Run for up to 200 steps
    final_counts = sim.run(steps=200, verbose=True)
    
    print("\n" + "=" * 60)
    print("FINAL STATISTICS")
    print("=" * 60)
    print(f"Total steps: {sim.step_count}")
    print(f"Final state distribution:")
    print(f"  Susceptible: {final_counts.get('S', 0)} ({100 * final_counts.get('S', 0) / len(sim.agents):.1f}%)")
    print(f"  Infected:    {final_counts.get('I', 0)} ({100 * final_counts.get('I', 0) / len(sim.agents):.1f}%)")
    print(f"  Recovered:   {final_counts.get('R', 0)} ({100 * final_counts.get('R', 0) / len(sim.agents):.1f}%)")