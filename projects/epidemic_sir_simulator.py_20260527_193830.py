"""
Date: 2026-05-27
Simulated disease spread through a population using the SIR compartmental model — watching infection waves rise and fall is oddly mesmerizing.
"""

#!/usr/bin/env python3
"""
SIR Epidemic Model Simulator
Tracks susceptible, infected, and recovered individuals over time.
Uses discrete time steps with probabilistic state transitions.
"""

import random
import math


class Person:
    """
    Represents an individual in the population.
    Can be in one of three states: susceptible, infected, or recovered.
    """
    
    SUSCEPTIBLE = 'S'
    INFECTED = 'I'
    RECOVERED = 'R'
    
    def __init__(self):
        self.state = Person.SUSCEPTIBLE
        self.days_infected = 0


class EpidemicSimulator:
    """
    Simulates disease spread through a population using the SIR model.
    People interact randomly and can transmit the disease based on proximity and chance.
    """
    
    def __init__(self, population_size, initial_infected, transmission_rate, recovery_days):
        """
        Initialize the epidemic simulation.
        
        Args:
            population_size: Total number of people in the simulation
            initial_infected: How many people start infected
            transmission_rate: Probability of transmission per contact (0.0 to 1.0)
            recovery_days: How many days until an infected person recovers
        """
        self.population = [Person() for _ in range(population_size)]
        self.transmission_rate = transmission_rate
        self.recovery_days = recovery_days
        self.day = 0
        
        # Infect random initial people
        for person in random.sample(self.population, initial_infected):
            person.state = Person.INFECTED
            person.days_infected = 0
    
    def count_states(self):
        """Returns a tuple of (susceptible, infected, recovered) counts."""
        susceptible = sum(1 for p in self.population if p.state == Person.SUSCEPTIBLE)
        infected = sum(1 for p in self.population if p.state == Person.INFECTED)
        recovered = sum(1 for p in self.population if p.state == Person.RECOVERED)
        return susceptible, infected, recovered
    
    def step(self):
        """
        Advance the simulation by one day.
        Handles disease transmission and recovery.
        """
        self.day += 1
        
        # First, handle recovery for infected people
        for person in self.population:
            if person.state == Person.INFECTED:
                person.days_infected += 1
                if person.days_infected >= self.recovery_days:
                    person.state = Person.RECOVERED
        
        # Then handle transmission through random contacts
        # Each person has a chance to interact with a few others
        infected_people = [p for p in self.population if p.state == Person.INFECTED]
        susceptible_people = [p for p in self.population if p.state == Person.SUSCEPTIBLE]
        
        # Simulate random contacts - each infected person contacts several people per day
        contacts_per_day = 5
        for infected in infected_people:
            for _ in range(contacts_per_day):
                if not susceptible_people:
                    break
                contact = random.choice(self.population)
                
                # Only susceptible people can get infected
                if contact.state == Person.SUSCEPTIBLE:
                    if random.random() < self.transmission_rate:
                        contact.state = Person.INFECTED
                        contact.days_infected = 0
    
    def get_ascii_bar(self, count, max_count, width=40):
        """
        Create an ASCII bar chart representation.
        
        Args:
            count: The value to represent
            max_count: The maximum possible value (for scaling)
            width: Width of the bar in characters
        """
        if max_count == 0:
            return ""
        bar_length = int((count / max_count) * width)
        return "█" * bar_length
    
    def print_status(self):
        """Print the current state of the epidemic with ASCII visualization."""
        s, i, r = self.count_states()
        total = len(self.population)
        
        print(f"\n--- Day {self.day} ---")
        print(f"Susceptible: {s:4d} {self.get_ascii_bar(s, total)}")
        print(f"Infected:    {i:4d} {self.get_ascii_bar(i, total)}")
        print(f"Recovered:   {r:4d} {self.get_ascii_bar(r, total)}")
        
        # Calculate R_effective (rough approximation)
        if i > 0:
            print(f"Active infections: {i} ({100*i/total:.1f}%)")


def run_simulation(days=60, population=500, initial_infected=5, 
                   transmission_rate=0.08, recovery_days=10):
    """
    Run a complete epidemic simulation and print results.
    
    Args:
        days: Number of days to simulate
        population: Size of the population
        initial_infected: Initial number of infected people
        transmission_rate: Probability of transmission per contact
        recovery_days: Days until recovery
    """
    print("=" * 50)
    print("EPIDEMIC SIMULATION (SIR Model)")
    print("=" * 50)
    print(f"Population: {population}")
    print(f"Initial infected: {initial_infected}")
    print(f"Transmission rate: {transmission_rate}")
    print(f"Recovery period: {recovery_days} days")
    
    sim = EpidemicSimulator(population, initial_infected, transmission_rate, recovery_days)
    sim.print_status()
    
    # Run simulation and print periodic updates
    # I'm printing every 3 days to keep output manageable but still show the wave
    for day in range(1, days + 1):
        sim.step()
        if day % 3 == 0 or day == days:
            sim.print_status()
    
    print("\n" + "=" * 50)
    print("Simulation complete!")
    s, i, r = sim.count_states()
    print(f"Final state: {s} susceptible, {i} infected, {r} recovered")
    print(f"Attack rate: {100 * r / population:.1f}% of population infected")
    print("=" * 50)


if __name__ == "__main__":
    # Run a demo simulation with parameters that show a nice infection curve
    # I tweaked these values until the epidemic peaked around day 20-30
    run_simulation(
        days=60,
        population=500,
        initial_infected=3,
        transmission_rate=0.08,  # 8% chance per contact
        recovery_days=10
    )