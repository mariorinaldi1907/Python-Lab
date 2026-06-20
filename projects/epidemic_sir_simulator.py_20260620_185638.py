"""
Date: 2026-06-20
Implemented a stochastic SIR (Susceptible-Infected-Recovered) epidemic simulator that runs in the terminal and shows how diseases spread through populations with configurable parameters.
"""

#!/usr/bin/env python3
"""
SIR Epidemic Model Simulator
A stochastic simulation of disease spread through a population.
Each timestep, infected individuals have a chance to infect susceptible neighbors
and recover after a certain period.
"""

import random
from collections import defaultdict


class Person:
    """Represents an individual in the population with a disease state."""
    
    def __init__(self, person_id):
        """
        Initialize a person as susceptible.
        
        Args:
            person_id: Unique identifier for this person
        """
        self.id = person_id
        self.state = 'S'  # S = Susceptible, I = Infected, R = Recovered
        self.days_infected = 0
    
    def infect(self):
        """Change state to infected."""
        if self.state == 'S':
            self.state = 'I'
            self.days_infected = 0
    
    def try_recover(self, recovery_days):
        """
        Attempt to recover if infected long enough.
        
        Args:
            recovery_days: Number of days before recovery is possible
        """
        if self.state == 'I':
            self.days_infected += 1
            if self.days_infected >= recovery_days:
                self.state = 'R'
    
    def is_infected(self):
        """Check if person is currently infected."""
        return self.state == 'I'
    
    def is_susceptible(self):
        """Check if person can be infected."""
        return self.state == 'S'


class EpidemicSimulator:
    """Simulates disease spread through a population using the SIR model."""
    
    def __init__(self, population_size, initial_infected, infection_rate, recovery_days):
        """
        Initialize the simulation.
        
        Args:
            population_size: Total number of people
            initial_infected: Number of people infected at start
            infection_rate: Probability of transmission per contact (0-1)
            recovery_days: Days until an infected person recovers
        """
        self.people = [Person(i) for i in range(population_size)]
        self.infection_rate = infection_rate
        self.recovery_days = recovery_days
        self.day = 0
        
        # Infect random initial people
        for person in random.sample(self.people, initial_infected):
            person.infect()
        
        # Track history for plotting
        self.history = defaultdict(list)
        self._record_stats()
    
    def _record_stats(self):
        """Record current state counts for historical tracking."""
        counts = {'S': 0, 'I': 0, 'R': 0}
        for person in self.people:
            counts[person.state] += 1
        
        self.history['S'].append(counts['S'])
        self.history['I'].append(counts['I'])
        self.history['R'].append(counts['R'])
    
    def _simulate_contacts(self):
        """
        Simulate random contacts between people.
        Each infected person contacts a few random others and may transmit.
        """
        infected = [p for p in self.people if p.is_infected()]
        
        for infected_person in infected:
            # Each infected person contacts 3-8 random people per day
            num_contacts = random.randint(3, 8)
            contacts = random.sample(self.people, num_contacts)
            
            for contact in contacts:
                if contact.is_susceptible() and random.random() < self.infection_rate:
                    contact.infect()
    
    def step(self):
        """Advance the simulation by one day."""
        self.day += 1
        
        # Recovery happens first (people who were already infected)
        for person in self.people:
            person.try_recover(self.recovery_days)
        
        # Then new infections occur
        self._simulate_contacts()
        
        # Record stats after everything
        self._record_stats()
    
    def run(self, days):
        """
        Run the simulation for a specified number of days.
        
        Args:
            days: Number of days to simulate
        """
        for _ in range(days):
            self.step()
            if self.history['I'][-1] == 0:
                # No more infected people, epidemic is over
                break
    
    def get_stats(self):
        """Get current population statistics."""
        return {
            'day': self.day,
            'susceptible': self.history['S'][-1],
            'infected': self.history['I'][-1],
            'recovered': self.history['R'][-1]
        }
    
    def print_chart(self, max_width=60):
        """
        Print a simple ASCII chart of the epidemic progression.
        
        Args:
            max_width: Maximum width of the chart in characters
        """
        total_pop = len(self.people)
        
        print("\n=== Epidemic Progression ===\n")
        print(f"Day | {'Susceptible':<15} | {'Infected':<15} | {'Recovered':<15}")
        print("-" * 70)
        
        # Sample every few days if we have too many
        step = max(1, len(self.history['S']) // 20)
        
        for day in range(0, len(self.history['S']), step):
            s_count = self.history['S'][day]
            i_count = self.history['I'][day]
            r_count = self.history['R'][day]
            
            # Create simple bar chart
            s_bar = '█' * int((s_count / total_pop) * max_width)
            i_bar = '█' * int((i_count / total_pop) * max_width)
            r_bar = '█' * int((r_count / total_pop) * max_width)
            
            print(f"{day:3d} | {s_bar:<15} | {i_bar:<15} | {r_bar:<15}")
        
        # Print final stats
        final = self.get_stats()
        print("\n=== Final Statistics ===")
        print(f"Total days: {final['day']}")
        print(f"Never infected: {final['susceptible']} ({100*final['susceptible']/total_pop:.1f}%)")
        print(f"Still infected: {final['infected']} ({100*final['infected']/total_pop:.1f}%)")
        print(f"Recovered: {final['recovered']} ({100*final['recovered']/total_pop:.1f}%)")


if __name__ == "__main__":
    # Set up a simulation with reasonable parameters
    # Roughly modeling something like flu in a small community
    sim = EpidemicSimulator(
        population_size=200,
        initial_infected=5,
        infection_rate=0.08,  # 8% chance per contact
        recovery_days=7        # recover after 7 days
    )
    
    print("Starting epidemic simulation...")
    print(f"Population: 200 people")
    print(f"Initial infected: 5")
    print(f"Infection rate: 8% per contact")
    print(f"Recovery time: 7 days")
    
    # Run for up to 100 days (will stop early if epidemic ends)
    sim.run(days=100)
    
    # Display results
    sim.print_chart()