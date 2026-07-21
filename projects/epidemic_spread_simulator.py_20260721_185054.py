"""
Date: 2026-07-21
Implemented an SIR (Susceptible-Infected-Recovered) epidemic model to explore disease dynamics — runs multiple days and shows population changes.
"""

#!/usr/bin/env python3
"""
Simple SIR epidemic model simulation.
Tracks how a disease spreads through a population over time.
"""

import random
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Person:
    """
    Represents an individual in the simulation.
    
    Attributes:
        status: 'S' (susceptible), 'I' (infected), or 'R' (recovered)
        days_infected: Counter for how long person has been sick
    """
    status: str = 'S'
    days_infected: int = 0


class EpidemicSimulator:
    """
    Simulates disease spread using the SIR model.
    
    The model divides population into three groups:
    - Susceptible: Can catch the disease
    - Infected: Currently sick and can spread it
    - Recovered: Had it, now immune
    """
    
    def __init__(self, population_size: int, initial_infected: int,
                 infection_rate: float, recovery_days: int, contact_rate: int):
        """
        Initialize the epidemic simulation.
        
        Args:
            population_size: Total number of people
            initial_infected: How many start sick
            infection_rate: Probability of transmission per contact (0.0-1.0)
            recovery_days: Days until an infected person recovers
            contact_rate: Number of random contacts per person per day
        """
        self.population_size = population_size
        self.infection_rate = infection_rate
        self.recovery_days = recovery_days
        self.contact_rate = contact_rate
        
        # Create population - mostly susceptible, some infected
        self.people = [Person() for _ in range(population_size)]
        for i in range(initial_infected):
            self.people[i].status = 'I'
        
        # Track history for later analysis
        self.history = []
    
    def count_by_status(self) -> Tuple[int, int, int]:
        """
        Count how many people are in each state.
        
        Returns:
            Tuple of (susceptible_count, infected_count, recovered_count)
        """
        susceptible = sum(1 for p in self.people if p.status == 'S')
        infected = sum(1 for p in self.people if p.status == 'I')
        recovered = sum(1 for p in self.people if p.status == 'R')
        return susceptible, infected, recovered
    
    def simulate_day(self) -> None:
        """
        Simulate one day of the epidemic.
        
        Each infected person contacts random others and may spread the disease.
        Infected people recover after the specified number of days.
        """
        # First, handle infections through random contacts
        infected_indices = [i for i, p in enumerate(self.people) if p.status == 'I']
        
        for infected_idx in infected_indices:
            # Each infected person has random contacts
            for _ in range(self.contact_rate):
                contact_idx = random.randint(0, self.population_size - 1)
                contact = self.people[contact_idx]
                
                # Can only infect susceptible people
                if contact.status == 'S':
                    if random.random() < self.infection_rate:
                        contact.status = 'I'
                        contact.days_infected = 0
        
        # Then, update infection duration and handle recoveries
        for person in self.people:
            if person.status == 'I':
                person.days_infected += 1
                if person.days_infected >= self.recovery_days:
                    person.status = 'R'
    
    def run_simulation(self, days: int) -> List[Tuple[int, int, int, int]]:
        """
        Run the simulation for a specified number of days.
        
        Args:
            days: Number of days to simulate
        
        Returns:
            List of (day, susceptible, infected, recovered) tuples
        """
        self.history = []
        
        for day in range(days):
            s, i, r = self.count_by_status()
            self.history.append((day, s, i, r))
            
            # Stop early if no one is infected anymore
            if i == 0:
                break
            
            self.simulate_day()
        
        return self.history
    
    def print_report(self) -> None:
        """Print a formatted summary of the simulation."""
        print(f"\n{'Day':<5} {'Susceptible':<15} {'Infected':<15} {'Recovered':<15}")
        print("=" * 55)
        
        for day, s, i, r in self.history:
            # Create simple bar charts using characters
            s_bar = '█' * (s * 40 // self.population_size)
            i_bar = '█' * (i * 40 // self.population_size)
            r_bar = '█' * (r * 40 // self.population_size)
            
            print(f"{day:<5} {s:<4} {s_bar:<10} {i:<4} {i_bar:<10} {r:<4} {r_bar:<10}")


def main():
    """Run a demo simulation with reasonable parameters."""
    print("=" * 60)
    print("SIR EPIDEMIC MODEL SIMULATION")
    print("=" * 60)
    
    # Parameters that produce an interesting epidemic curve
    sim = EpidemicSimulator(
        population_size=200,      # Small town
        initial_infected=3,        # A few initial cases
        infection_rate=0.15,       # 15% chance per contact
        recovery_days=7,           # Sick for a week
        contact_rate=5             # Meet 5 people per day
    )
    
    print(f"\nStarting conditions:")
    print(f"  Population: {sim.population_size}")
    print(f"  Initial infected: 3")
    print(f"  Infection rate: 15% per contact")
    print(f"  Recovery time: 7 days")
    print(f"  Daily contacts: 5 people")
    
    # Run for 60 days or until epidemic ends
    sim.run_simulation(days=60)
    sim.print_report()
    
    # Final statistics
    final_s, final_i, final_r = sim.count_by_status()
    print(f"\n{'=' * 60}")
    print(f"Simulation ended on day {len(sim.history) - 1}")
    print(f"Final state: {final_s} susceptible, {final_i} infected, {final_r} recovered")
    print(f"Attack rate: {final_r / sim.population_size * 100:.1f}% of population got sick")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()