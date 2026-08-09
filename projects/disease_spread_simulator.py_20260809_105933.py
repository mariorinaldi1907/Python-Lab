"""
Date: 2026-08-09
Simulated disease spread using a spatial SIR model where agents move randomly on a grid and infect nearby susceptible individuals — wanted to see how mobility affects outbreak dynamics.
"""

#!/usr/bin/env python3
"""
Disease Spread Simulator (SIR Model on a Grid)

A simple spatial epidemic simulation where agents move randomly on a grid.
Each agent can be Susceptible, Infected, or Recovered.
Infection spreads when infected agents are near susceptible ones.
"""

import random
from enum import Enum
from typing import List, Tuple


class State(Enum):
    """Health states for agents in the SIR model."""
    SUSCEPTIBLE = 'S'
    INFECTED = 'I'
    RECOVERED = 'R'


class Agent:
    """
    Represents a single person in the simulation.
    
    Agents have a position, health state, and infection timer.
    They move randomly around the grid each step.
    """
    
    def __init__(self, x: int, y: int, state: State = State.SUSCEPTIBLE):
        self.x = x
        self.y = y
        self.state = state
        self.infection_timer = 0  # counts down while infected
    
    def move(self, grid_width: int, grid_height: int):
        """Move randomly to an adjacent cell (including diagonals)."""
        dx = random.randint(-1, 1)
        dy = random.randint(-1, 1)
        self.x = max(0, min(grid_width - 1, self.x + dx))
        self.y = max(0, min(grid_height - 1, self.y + dy))
    
    def update_infection(self, recovery_time: int):
        """Advance infection state — recover after recovery_time steps."""
        if self.state == State.INFECTED:
            self.infection_timer += 1
            if self.infection_timer >= recovery_time:
                self.state = State.RECOVERED
                self.infection_timer = 0


class EpidemicSimulation:
    """
    Grid-based SIR epidemic simulation.
    
    Agents move randomly, infected agents can spread disease to nearby
    susceptible agents, and infected agents recover after a set time.
    """
    
    def __init__(self, width: int, height: int, num_agents: int, 
                 infection_radius: float, infection_prob: float, recovery_time: int):
        self.width = width
        self.height = height
        self.infection_radius = infection_radius
        self.infection_prob = infection_prob
        self.recovery_time = recovery_time
        self.agents: List[Agent] = []
        self.step_count = 0
        
        # Initialize agents at random positions
        for _ in range(num_agents):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            self.agents.append(Agent(x, y, State.SUSCEPTIBLE))
        
        # Start with one infected agent (patient zero)
        if self.agents:
            self.agents[0].state = State.INFECTED
    
    def _distance(self, a1: Agent, a2: Agent) -> float:
        """Calculate Euclidean distance between two agents."""
        return ((a1.x - a2.x) ** 2 + (a1.y - a2.y) ** 2) ** 0.5
    
    def step(self):
        """Execute one simulation step: movement, infection spread, recovery."""
        # Move all agents
        for agent in self.agents:
            agent.move(self.width, self.height)
        
        # Check for new infections — infected agents can infect nearby susceptible ones
        newly_infected = []
        for infected in [a for a in self.agents if a.state == State.INFECTED]:
            for susceptible in [a for a in self.agents if a.state == State.SUSCEPTIBLE]:
                if self._distance(infected, susceptible) <= self.infection_radius:
                    # Probabilistic infection
                    if random.random() < self.infection_prob:
                        newly_infected.append(susceptible)
        
        # Apply new infections (do this separately to avoid modifying during iteration)
        for agent in newly_infected:
            agent.state = State.INFECTED
        
        # Update infection timers and handle recovery
        for agent in self.agents:
            agent.update_infection(self.recovery_time)
        
        self.step_count += 1
    
    def get_counts(self) -> Tuple[int, int, int]:
        """Return (susceptible, infected, recovered) counts."""
        s = sum(1 for a in self.agents if a.state == State.SUSCEPTIBLE)
        i = sum(1 for a in self.agents if a.state == State.INFECTED)
        r = sum(1 for a in self.agents if a.state == State.RECOVERED)
        return s, i, r
    
    def print_status(self):
        """Print current simulation status with counts and simple bar chart."""
        s, i, r = self.get_counts()
        total = len(self.agents)
        
        print(f"Step {self.step_count:3d} | S:{s:3d} I:{i:3d} R:{r:3d}", end=" | ")
        
        # Simple ASCII visualization of proportions
        bar_width = 40
        s_bar = int((s / total) * bar_width)
        i_bar = int((i / total) * bar_width)
        r_bar = bar_width - s_bar - i_bar  # fill remainder
        
        print("S" * s_bar + "I" * i_bar + "R" * r_bar)
    
    def is_active(self) -> bool:
        """Check if outbreak is still ongoing (any infected agents remain)."""
        return any(a.state == State.INFECTED for a in self.agents)


if __name__ == "__main__":
    # Set up a simulation with reasonable parameters
    # Using a smaller grid with moderate infection dynamics
    sim = EpidemicSimulation(
        width=20,
        height=20,
        num_agents=100,
        infection_radius=2.0,  # infect if within 2 units
        infection_prob=0.3,    # 30% chance per contact per step
        recovery_time=10       # recover after 10 steps
    )
    
    print("=== Disease Spread Simulation ===")
    print("Grid: 20x20, Agents: 100")
    print("Infection radius: 2.0, Infection prob: 0.3, Recovery time: 10 steps")
    print("Legend: S=Susceptible, I=Infected, R=Recovered\n")
    
    sim.print_status()
    
    # Run until no more infected agents or max steps
    max_steps = 100
    while sim.is_active() and sim.step_count < max_steps:
        sim.step()
        # Print every 5 steps to keep output manageable
        if sim.step_count % 5 == 0:
            sim.print_status()
    
    # Final status
    if sim.step_count < max_steps:
        sim.print_status()
    
    s_final, i_final, r_final = sim.get_counts()
    print(f"\n=== Outbreak Complete ===")
    print(f"Total steps: {sim.step_count}")
    print(f"Attack rate: {r_final}/{len(sim.agents)} ({100*r_final/len(sim.agents):.1f}%)")