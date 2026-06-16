"""
Date: 2026-06-16
Implemented a Bayesian A/B test analyzer using beta distributions to calculate probabilities that one variant beats another — felt like this approach gives more intuitive results than traditional hypothesis testing.
"""

#!/usr/bin/env python3
"""
Bayesian A/B Testing Module

Uses Beta distributions to model conversion rates and calculate the probability
that variant B beats variant A. I like this approach because it gives direct
probabilities instead of confusing p-values.
"""

import random
from math import gamma, log, exp


class BetaDistribution:
    """
    Represents a Beta distribution for modeling conversion rates.
    
    The Beta distribution is perfect for A/B testing because it's conjugate
    to the Binomial — basically means updating beliefs with new data is super clean.
    """
    
    def __init__(self, alpha=1, beta=1):
        """
        Initialize with prior parameters.
        
        Args:
            alpha: successes + 1 (using uninformed prior by default)
            beta: failures + 1
        """
        self.alpha = alpha
        self.beta = beta
    
    def update(self, successes, failures):
        """
        Update the distribution with observed data.
        
        This is the conjugate prior magic — just add the new data directly.
        """
        self.alpha += successes
        self.beta += failures
    
    def mean(self):
        """Expected value of the distribution."""
        return self.alpha / (self.alpha + self.beta)
    
    def variance(self):
        """Variance of the distribution."""
        a, b = self.alpha, self.beta
        return (a * b) / ((a + b) ** 2 * (a + b + 1))
    
    def sample(self, n=1):
        """
        Draw random samples from this Beta distribution.
        
        Using the standard library's random.betavariate — good enough for
        practical A/B testing simulations.
        """
        return [random.betavariate(self.alpha, self.beta) for _ in range(n)]
    
    def __repr__(self):
        return f"Beta(α={self.alpha}, β={self.beta})"


class ABTest:
    """
    Bayesian A/B test comparing two conversion rates.
    
    I built this because I wanted a cleaner way to analyze experiments without
    worrying about sample size calculations and p-value misinterpretations.
    """
    
    def __init__(self, name_a="A", name_b="B"):
        """
        Initialize an A/B test with two variants.
        
        Args:
            name_a: label for control variant
            name_b: label for treatment variant
        """
        self.name_a = name_a
        self.name_b = name_b
        self.variant_a = BetaDistribution()
        self.variant_b = BetaDistribution()
    
    def add_observations(self, variant, successes, failures):
        """
        Add observed data to one of the variants.
        
        Args:
            variant: 'A' or 'B'
            successes: number of conversions
            failures: number of non-conversions
        """
        if variant.upper() == 'A':
            self.variant_a.update(successes, failures)
        elif variant.upper() == 'B':
            self.variant_b.update(successes, failures)
        else:
            raise ValueError(f"Unknown variant: {variant}")
    
    def probability_b_beats_a(self, simulations=10000):
        """
        Calculate P(B > A) using Monte Carlo simulation.
        
        This is the key insight of Bayesian A/B testing: we can directly answer
        "what's the probability that B is better than A?" instead of weird
        null hypothesis gymnastics.
        """
        samples_a = self.variant_a.sample(simulations)
        samples_b = self.variant_b.sample(simulations)
        
        wins = sum(1 for a, b in zip(samples_a, samples_b) if b > a)
        return wins / simulations
    
    def expected_lift(self, simulations=10000):
        """
        Calculate the expected relative improvement of B over A.
        
        Returns the mean lift as a percentage.
        """
        samples_a = self.variant_a.sample(simulations)
        samples_b = self.variant_b.sample(simulations)
        
        # Avoid division by zero
        lifts = [(b - a) / a if a > 0 else 0 for a, b in zip(samples_a, samples_b)]
        return sum(lifts) / len(lifts) * 100
    
    def report(self):
        """
        Print a summary of the test results.
        """
        print(f"\n{'='*60}")
        print(f"Bayesian A/B Test Results")
        print(f"{'='*60}")
        print(f"\n{self.name_a}: {self.variant_a}")
        print(f"  Mean conversion rate: {self.variant_a.mean():.4f}")
        print(f"  Std deviation: {self.variance.sqrt():.4f}")
        
        print(f"\n{self.name_b}: {self.variant_b}")
        print(f"  Mean conversion rate: {self.variant_b.mean():.4f}")
        print(f"  Std deviation: {self.variant_b.variance()**0.5:.4f}")
        
        prob = self.probability_b_beats_a()
        lift = self.expected_lift()
        
        print(f"\n{'─'*60}")
        print(f"P({self.name_b} > {self.name_a}): {prob:.2%}")
        print(f"Expected lift: {lift:+.2f}%")
        print(f"{'─'*60}")
        
        # Give a practical interpretation
        if prob > 0.95:
            print(f"✓ Strong evidence that {self.name_b} is better")
        elif prob > 0.90:
            print(f"→ Moderate evidence that {self.name_b} is better")
        elif prob < 0.05:
            print(f"✓ Strong evidence that {self.name_a} is better")
        elif prob < 0.10:
            print(f"→ Moderate evidence that {self.name_a} is better")
        else:
            print("○ Results are inconclusive — need more data")
        print()


if __name__ == "__main__":
    # Demo: testing a new checkout button design
    print("Simulating an A/B test for a website redesign...")
    
    test = ABTest(name_a="Old Design", name_b="New Design")
    
    # Control group: 1000 visitors, 87 conversions
    test.add_observations('A', successes=87, failures=913)
    
    # Treatment group: 1000 visitors, 102 conversions
    test.add_observations('B', successes=102, failures=898)
    
    test.report()
    
    # Show what happens with more extreme data
    print("\n" + "="*60)
    print("Running a second test with clearer winner...")
    print("="*60)
    
    test2 = ABTest(name_a="Control", name_b="Treatment")
    test2.add_observations('A', successes=50, failures=950)
    test2.add_observations('B', successes=85, failures=915)
    
    test2.report()