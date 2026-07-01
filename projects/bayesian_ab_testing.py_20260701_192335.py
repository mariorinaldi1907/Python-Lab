"""
Date: 2026-07-01
Created a Bayesian A/B testing module that uses beta distributions to calculate probabilities and expected loss — helps me make actual data-driven decisions instead of guessing from p-values.
"""

#!/usr/bin/env python3
"""
Bayesian A/B Testing Module

Uses Beta distributions to model conversion rates and calculate
probabilities that one variant is better than another. Much more
intuitive than p-values IMO.
"""

import random
import math
from typing import Tuple, List


class BetaDistribution:
    """
    Represents a Beta distribution for modeling conversion rates.
    
    The Beta(alpha, alpha) distribution is the conjugate prior for
    binomial likelihood, which makes Bayesian updating super clean.
    """
    
    def __init__(self, alpha: float = 1.0, beta: float = 1.0):
        """
        Initialize with prior parameters.
        
        Args:
            alpha: Number of successes + 1 (uniform prior uses 1)
            beta: Number of failures + 1
        """
        self.alpha = alpha
        self.beta = beta
    
    def update(self, successes: int, failures: int):
        """
        Update the distribution with observed data.
        
        This is literally just adding counts — Bayesian updating
        is beautiful when you use conjugate priors.
        """
        self.alpha += successes
        self.beta += failures
    
    def sample(self) -> float:
        """Draw a random sample from this Beta distribution."""
        return random.betavariate(self.alpha, self.beta)
    
    def mean(self) -> float:
        """Expected value of the distribution."""
        return self.alpha / (self.alpha + self.beta)
    
    def std(self) -> float:
        """Standard deviation of the distribution."""
        a, b = self.alpha, self.beta
        variance = (a * b) / ((a + b) ** 2 * (a + b + 1))
        return math.sqrt(variance)


class ABTest:
    """
    Bayesian A/B test with two variants.
    
    Uses Monte Carlo sampling to calculate probability that A beats B
    and expected loss for choosing the wrong variant.
    """
    
    def __init__(self, name_a: str = "A", name_b: str = "B"):
        """Initialize test with two variants."""
        self.name_a = name_a
        self.name_b = name_b
        self.variant_a = BetaDistribution()
        self.variant_b = BetaDistribution()
    
    def add_data(self, variant: str, successes: int, failures: int):
        """
        Add observed data to a variant.
        
        Args:
            variant: Either "A" or "B"
            successes: Number of conversions
            failures: Number of non-conversions
        """
        if variant.upper() == "A":
            self.variant_a.update(successes, failures)
        elif variant.upper() == "B":
            self.variant_b.update(successes, failures)
        else:
            raise ValueError(f"Unknown variant: {variant}")
    
    def probability_b_beats_a(self, samples: int = 10000) -> float:
        """
        Calculate P(B > A) using Monte Carlo sampling.
        
        This is way more intuitive than a p-value. If this returns 0.95,
        there's a 95% chance B is actually better than A.
        """
        b_wins = sum(
            self.variant_b.sample() > self.variant_a.sample()
            for _ in range(samples)
        )
        return b_wins / samples
    
    def expected_loss(self, samples: int = 10000) -> Tuple[float, float]:
        """
        Calculate expected loss for choosing each variant.
        
        Expected loss is how much conversion rate you'd lose on average
        if you pick the wrong variant. Helps with risk assessment.
        
        Returns:
            (loss_if_choose_a, loss_if_choose_b)
        """
        loss_a = 0.0
        loss_b = 0.0
        
        for _ in range(samples):
            sample_a = self.variant_a.sample()
            sample_b = self.variant_b.sample()
            
            # If we choose A but B was better, we lose (B - A)
            if sample_b > sample_a:
                loss_a += sample_b - sample_a
            else:
                loss_b += sample_a - sample_b
        
        return loss_a / samples, loss_b / samples
    
    def report(self):
        """Print a summary of the test results."""
        prob_b_wins = self.probability_b_beats_a()
        loss_a, loss_b = self.expected_loss()
        
        print(f"\n{'='*60}")
        print(f"Bayesian A/B Test Results")
        print(f"{'='*60}")
        print(f"\nVariant {self.name_a}:")
        print(f"  Mean conversion rate: {self.variant_a.mean():.4f}")
        print(f"  Std deviation: {self.variant_a.std():.4f}")
        print(f"  Data: α={self.variant_a.alpha:.0f}, β={self.variant_a.beta:.0f}")
        
        print(f"\nVariant {self.name_b}:")
        print(f"  Mean conversion rate: {self.variant_b.mean():.4f}")
        print(f"  Std deviation: {self.variant_b.std():.4f}")
        print(f"  Data: α={self.variant_b.alpha:.0f}, β={self.variant_b.beta:.0f}")
        
        print(f"\n{'─'*60}")
        print(f"P({self.name_b} > {self.name_a}) = {prob_b_wins:.4f}")
        print(f"\nExpected Loss:")
        print(f"  If you choose {self.name_a}: {loss_a:.6f}")
        print(f"  If you choose {self.name_b}: {loss_b:.6f}")
        
        # Give a recommendation based on common thresholds
        if prob_b_wins > 0.95 and loss_b < 0.001:
            print(f"\n✓ Strong evidence for {self.name_b}")
        elif prob_b_wins < 0.05 and loss_a < 0.001:
            print(f"\n✓ Strong evidence for {self.name_a}")
        else:
            print("\n⚠ Not enough evidence to make a clear decision yet")
        
        print(f"{'='*60}\n")


if __name__ == "__main__":
    # Simulate an actual A/B test I might run on a landing page
    print("Simulating A/B test: Original vs. New Landing Page")
    print("Metric: Sign-up conversion rate\n")
    
    test = ABTest(name_a="Original", name_b="New Design")
    
    # Original design: 120 conversions out of 1000 visitors
    test.add_data("A", successes=120, failures=880)
    
    # New design: 145 conversions out of 1000 visitors
    # Looks better, but is it significantly better?
    test.add_data("B", successes=145, failures=855)
    
    test.report()
    
    # Show how to interpret the results
    print("Interpretation:")
    print("- The probability tells you how confident we are that B is better")
    print("- Expected loss tells you the cost of making the wrong choice")
    print("- Unlike p-values, these numbers are directly interpretable!")