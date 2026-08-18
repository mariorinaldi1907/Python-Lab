"""
Date: 2026-08-18
Simulated disease spread on a 2D grid where agents move randomly and infect neighbors, tracking susceptible/infected/recovered over time.
"""

#!/usr/bin/env python3
"""
Epidemic spread simulator using a spatial SIR (Susceptible-Infected-Recovered) model.
Agents move randomly on a grid, and infections spread based on proximity.
"""

import random
from collections import defaultdict


class Agent:
    """Represents a single person in the simulation with position and health state."""
    
    def __init__(self, x, y, state='S'):
        """
        Initialize an agent.
        
        Args:
            x: X coordinate on grid
            y: Y coordinate on grid
            state: Health state - 'S' (susceptible), 'I' (infected), 'R' (recovered)
        """
        self.x = x
        self.y = y
        self.state = state
        self.days_infected = 0  # Track how long they've been sick
    
    def move(self, grid_size):
        """Move randomly to an adjacent cell (including diagonals)."""
        dx = random.choice([-1, 0, 1])
        dy = random.choice([-1, 0, 1])
        self.x = max(0, min(grid_size - 1, self.x + dx))
        self.y = max(0, min(grid_size - 1, self.y + dy))


class EpidemicSimulator:
    """Simulates disease spread on a 2D grid with moving agents."""
    
    def __init__(self, grid_size=20, num_agents=100, infection_radius=1.5, 
                 infection_prob=0.3, recovery_days=7):
        """
        Set up the simulation parameters.
        
        Args:
            grid_size: Size of the square grid
            num_agents: Total number of agents
            infection_radius: Distance within which infection can spread
            infection_prob: Probability of infection per contact
            recovery_days: Days until an infected agent recovers
        """
        self.grid_size = grid_size
        self.infection_radius = infection_radius
        self.infection_prob = infection_prob
        self.recovery_days = recovery_days
        
        # Create agents at random positions
        self.agents = []
        for _ in range(num_agents):
            x = random.randint(0, grid_size - 1)
            y = random.randint(0, grid_size - 1)
            self.agents.append(Agent(x, y, state='S'))
        
        # Start with one infected person (patient zero)
        if self.agents:
            self.agents[0].state = 'I'
        
        self.day = 0
        self.history = []  # Track statistics over time
    
    def get_distance(self, agent1, agent2):
        """Calculate Euclidean distance between two agents."""
        dx = agent1.x - agent2.x
        dy = agent1.y - agent2.y
        return (dx*dx + dy*dy) ** 0.5
    
    def spread_infection(self):
        """Check all agent pairs and spread infection based on proximity."""
        # Build spatial index for efficiency (group by grid cell)
        cell_map = defaultdict(list)
        for agent in self.agents:
            cell_map[(agent.x, agent.y)].append(agent)
        
        newly_infected = []
        
        for agent in self.agents:
            if agent.state != 'I':
                continue
            
            # Check nearby cells (not just same cell, but neighbors too)
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    cell = (agent.x + dx, agent.y + dy)
                    for other in cell_map.get(cell, []):
                        if other.state == 'S':
                            dist = self.get_distance(agent, other)
                            if dist <= self.infection_radius:
                                if random.random() < self.infection_prob:
                                    newly_infected.append(other)
        
        # Apply new infections (do this separately to avoid modifying during iteration)
        for agent in newly_infected:
            agent.state = 'I'
    
    def update_agents(self):
        """Move agents and update their infection status."""
        for agent in self.agents:
            # Move everyone
            agent.move(self.grid_size)
            
            # Update infection progress
            if agent.state == 'I':
                agent.days_infected += 1
                if agent.days_infected >= self.recovery_days:
                    agent.state = 'R'
                    agent.days_infected = 0
    
    def get_statistics(self):
        """Count agents in each state."""
        counts = {'S': 0, 'I': 0, 'R': 0}
        for agent in self.agents:
            counts[agent.state] += 1
        return counts
    
    def run_simulation(self, days=50):
        """Run the simulation for a specified number of days."""
        print(f"Starting epidemic simulation: {len(self.agents)} agents on {self.grid_size}x{self.grid_size} grid")
        print(f"Infection radius: {self.infection_radius}, Probability: {self.infection_prob}, Recovery: {self.recovery_days} days\n")
        
        for day in range(days):
            self.day = day
            stats = self.get_statistics()
            self.history.append(stats)
            
            # Print every 5 days to avoid spam
            if day % 5 == 0 or stats['I'] == 0:
                print(f"Day {day:3d} | Susceptible: {stats['S']:3d} | Infected: {stats['I']:3d} | Recovered: {stats['R']:3d}")
            
            # Stop early if no more infections
            if stats['I'] == 0:
                print(f"\nEpidemic ended on day {day}. No more active infections.")
                break
            
            # Update simulation
            self.spread_infection()
            self.update_agents()
        
        self.print_summary()
    
    def print_summary(self):
        """Print final statistics about the epidemic."""
        final = self.get_statistics()
        total = len(self.agents)
        print(f"\n{'='*60}")
        print(f"FINAL RESULTS:")
        print(f"  Total population: {total}")
        print(f"  Never infected: {final['S']} ({100*final['S']/total:.1f}%)")
        print(f"  Currently sick: {final['I']} ({100*final['I']/total:.1f}%)")
        print(f"  Recovered: {final['R']} ({100*final['R']/total:.1f}%)")
        print(f"  Peak infections: {max(day['I'] for day in self.history)}")
        print(f"{'='*60}")


if __name__ == "__main__":
    # Run a demo simulation with moderate parameters
    random.seed(42)  # For reproducible results
    
    sim = EpidemicSimulator(
        grid_size=25,
        num_agents=150,
        infection_radius=1.8,
        infection_prob=0.25,
        recovery_days=6
    )
    
    sim.run_simulation(days=60)