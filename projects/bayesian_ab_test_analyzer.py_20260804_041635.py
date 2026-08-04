"""
Date: 2026-08-04
Implemented a Bayesian A/B testing framework using conjugate priors to compare conversion rates and make decisions with actual probability statements instead of confusing p-values.
"""

#!/usr/bin/env python3
"""
Bayesian A/B Test Analyzer
===========================
A clean implementation of Bayesian inference for A/B testing using Beta distributions.
I got tired of interpreting p-values incorrectly, so I built this to get actual
probabilities like "there's a 94% chance variant B is better than A."
"""

import random
import math
from typing import Tuple, List


class BetaDistribution:
    """
    Represents a Beta distribution for modeling conversion rates.
    
    The Beta distribution is perfect for this because it's conjugate to the Binomial —
    which means updating beliefs with new data is just addition, super elegant.
    """
    
    def __init__(self, alpha: float = 1.0, beta: float = 1.0):
        """
        Initialize with prior parameters.
        Alpha=1, Beta=1 gives uniform prior (no assumptions).
        """
        self.alpha = alpha
        self.beta = beta
    
    def update(self, successes: int, failures: int):
        """Update the distribution with observed data."""
        self.alpha += successes
        self.beta += failures
    
    def mean(self) -> float:
        """Expected value of the distribution."""
        return self.alpha / (self.alpha + self.beta)
    
    def variance(self) -> float:
        """Variance of the distribution."""
        a, b = self.alpha, self.beta
        return (a * b) / ((a + b) ** 2 * (a + b + 1))
    
    def std(self) -> float:
        """Standard deviation."""
        return math.sqrt(self.variance())
    
    def sample(self) -> float:
        """
        Draw a random sample from this Beta distribution.
        Using the gamma-based trick since stdlib doesn't have beta sampling.
        """
        # Beta(a, b) can be generated from two Gamma distributions
        x = random.gammavariate(self.alpha, 1)
        y = random.gammavariate(self.beta, 1)
        return x / (x + y)
    
    def credible_interval(self, confidence: float = 0.95) -> Tuple[float, float]:
        """
        Compute credible interval using sampling.
        This is the Bayesian version of a confidence interval — actually interpretable!
        """
        samples = sorted([self.sample() for _ in range(10000)])
        lower_idx = int((1 - confidence) / 2 * len(samples))
        upper_idx = int((1 + confidence) / 2 * len(samples))
        return samples[lower_idx], samples[upper_idx]


class ABTest:
    """
    Main class for running Bayesian A/B tests.
    
    Compares two variants and gives you actual probabilities about which is better.
    """
    
    def __init__(self, prior_alpha: float = 1.0, prior_beta: float = 1.0):
        """Initialize with prior beliefs about conversion rates."""
        self.variant_a = BetaDistribution(prior_alpha, prior_beta)
        self.variant_b = BetaDistribution(prior_alpha, prior_beta)
    
    def add_observations(self, variant: str, successes: int, failures: int):
        """Add observed data for a variant."""
        if variant.upper() == 'A':
            self.variant_a.update(successes, failures)
        elif variant.upper() == 'B':
            self.variant_b.update(successes, failures)
        else:
            raise ValueError("Variant must be 'A' or 'B'")
    
    def probability_b_better(self, n_samples: int = 50000) -> float:
        """
        Calculate P(B > A) using Monte Carlo sampling.
        This is the key insight: we can directly answer "what's the probability B is better?"
        """
        b_wins = sum(
            self.variant_b.sample() > self.variant_a.sample()
            for _ in range(n_samples)
        )
        return b_wins / n_samples
    
    def expected_loss(self, choose_b: bool, n_samples: int = 50000) -> float:
        """
        Calculate expected loss if we choose B (or A if choose_b=False).
        This helps with decision-making: how much conversion rate are we risking?
        """
        losses = []
        for _ in range(n_samples):
            a_sample = self.variant_a.sample()
            b_sample = self.variant_b.sample()
            
            if choose_b:
                # If we choose B but A was actually better, we lose (a - b)
                loss = max(0, a_sample - b_sample)
            else:
                # If we choose A but B was actually better, we lose (b - a)
                loss = max(0, b_sample - a_sample)
            
            losses.append(loss)
        
        return sum(losses) / len(losses)
    
    def summary(self) -> dict:
        """Generate a complete summary of the test results."""
        prob_b_better = self.probability_b_better()
        
        return {
            'variant_a_mean': self.variant_a.mean(),
            'variant_a_std': self.variant_a.std(),
            'variant_a_ci': self.variant_a.credible_interval(),
            'variant_b_mean': self.variant_b.mean(),
            'variant_b_std': self.variant_b.std(),
            'variant_b_ci': self.variant_b.credible_interval(),
            'prob_b_better_than_a': prob_b_better,
            'expected_loss_choosing_b': self.expected_loss(choose_b=True),
            'expected_loss_choosing_a': self.expected_loss(choose_b=False),
        }


if __name__ == "__main__":
    print("Bayesian A/B Test Analyzer Demo")
    print("=" * 50)
    
    # Simulate a real A/B test scenario
    # Let's say we're testing two different landing pages
    print("\nScenario: Testing two landing page designs\n")
    
    test = ABTest(prior_alpha=1, prior_beta=1)  # Uniform prior
    
    # Variant A: 820 visitors, 123 conversions
    # Variant B: 850 visitors, 155 conversions
    print("Variant A: 123 conversions out of 820 visitors (15.0%)")
    print("Variant B: 155 conversions out of 850 visitors (18.2%)")
    
    test.add_observations('A', successes=123, failures=820-123)
    test.add_observations('B', successes=155, failures=850-155)
    
    results = test.summary()
    
    print(f"\n{'Results:':-^50}")
    print(f"\nVariant A:")
    print(f"  Estimated conversion rate: {results['variant_a_mean']:.1%}")
    print(f"  95% credible interval: ({results['variant_a_ci'][0]:.1%}, {results['variant_a_ci'][1]:.1%})")
    
    print(f"\nVariant B:")
    print(f"  Estimated conversion rate: {results['variant_b_mean']:.1%}")
    print(f"  95% credible interval: ({results['variant_b_ci'][0]:.1%}, {results['variant_b_ci'][1]:.1%})")
    
    print(f"\n{'Decision Analysis:':-^50}")
    print(f"Probability that B is better than A: {results['prob_b_better_than_a']:.1%}")
    print(f"Expected loss if we choose B: {results['expected_loss_choosing_b']:.2%}")
    print(f"Expected loss if we choose A: {results['expected_loss_choosing_a']:.2%}")
    
    # Make a recommendation
    print(f"\n{'Recommendation:':-^50}")
    if results['prob_b_better_than_a'] > 0.95:
        print("✓ Strong evidence for choosing Variant B")
    elif results['prob_b_better_than_a'] > 0.90:
        print("✓ Good evidence for choosing Variant B")
    elif results['prob_b_better_than_a'] < 0.05:
        print("✓ Strong evidence for choosing Variant A")
    elif results['prob_b_better_than_a'] < 0.10:
        print("✓ Good evidence for choosing Variant A")
    else:
        print("⚠ Inconclusive - consider collecting more data")
        print(f"  (Currently {results['prob_b_better_than_a']:.1%} confident B is better)")