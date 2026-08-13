"""
Date: 2026-08-13
Built a Bayesian A/B testing tool that uses beta distributions to compare conversion rates and calculate probabilities of superiority — finally something I can use for side project analytics.
"""

#!/usr/bin/env python3
"""
Bayesian A/B Testing Framework

Uses Beta distributions to model conversion rates and calculate
the probability that variant B outperforms variant A.
Way more intuitive than p-values IMO.
"""

import random
import math
from typing import Tuple, List


class BetaDistribution:
    """
    Represents a Beta distribution, perfect for modeling conversion rates.
    
    The Beta distribution is conjugate prior for binomial likelihood,
    which makes Bayesian updating super clean.
    """
    
    def __init__(self, alpha: float = 1.0, beta: float = 1.0):
        """
        Initialize Beta distribution.
        
        Args:
            alpha: Success count + 1 (uniform prior starts at 1)
            beta: Failure count + 1
        """
        self.alpha = alpha
        self.beta = beta
    
    def update(self, successes: int, failures: int):
        """
        Update the distribution with new observations.
        This is the Bayesian update step.
        """
        self.alpha += successes
        self.beta += failures
    
    def mean(self) -> float:
        """Expected value of the distribution."""
        return self.alpha / (self.alpha + self.beta)
    
    def variance(self) -> float:
        """Variance of the distribution."""
        a, b = self.alpha, self.beta
        return (a * b) / ((a + b) ** 2 * (a + b + 1))
    
    def sample(self) -> float:
        """
        Draw a random sample from this Beta distribution.
        Using the fact that if X ~ Gamma(alpha) and Y ~ Gamma(beta),
        then X/(X+Y) ~ Beta(alpha, beta).
        """
        x = self._gamma_sample(self.alpha)
        y = self._gamma_sample(self.beta)
        return x / (x + y)
    
    def _gamma_sample(self, shape: float) -> float:
        """
        Sample from Gamma distribution using Marsaglia and Tsang's method.
        Only works for shape >= 1, but that's fine for our use case.
        """
        if shape < 1:
            # For shape < 1, use the transformation method
            return self._gamma_sample(shape + 1) * (random.random() ** (1.0 / shape))
        
        d = shape - 1.0 / 3.0
        c = 1.0 / math.sqrt(9.0 * d)
        
        while True:
            z = random.gauss(0, 1)
            v = (1.0 + c * z) ** 3
            
            if v <= 0:
                continue
            
            u = random.random()
            if u < 1 - 0.0331 * z ** 4:
                return d * v
            
            if math.log(u) < 0.5 * z ** 2 + d * (1 - v + math.log(v)):
                return d * v


class ABTest:
    """
    Bayesian A/B test comparing two conversion rates.
    """
    
    def __init__(self):
        """Initialize with uniform priors for both variants."""
        self.variant_a = BetaDistribution()
        self.variant_b = BetaDistribution()
    
    def add_observations(self, variant: str, successes: int, failures: int):
        """
        Add observed data to a variant.
        
        Args:
            variant: 'A' or 'B'
            successes: Number of conversions
            failures: Number of non-conversions
        """
        if variant.upper() == 'A':
            self.variant_a.update(successes, failures)
        elif variant.upper() == 'B':
            self.variant_b.update(successes, failures)
        else:
            raise ValueError("Variant must be 'A' or 'B'")
    
    def probability_b_beats_a(self, num_samples: int = 10000) -> float:
        """
        Calculate P(B > A) using Monte Carlo sampling.
        
        This is way more intuitive than a p-value. If this returns 0.95,
        there's a 95% chance B is actually better than A.
        """
        b_wins = sum(
            self.variant_b.sample() > self.variant_a.sample()
            for _ in range(num_samples)
        )
        return b_wins / num_samples
    
    def expected_loss(self, choose_b: bool, num_samples: int = 10000) -> float:
        """
        Expected loss if we choose B (or A).
        
        This tells you how much conversion rate you'd lose on average
        if you pick the wrong variant. Useful for risk assessment.
        """
        losses = []
        for _ in range(num_samples):
            a_sample = self.variant_a.sample()
            b_sample = self.variant_b.sample()
            
            if choose_b:
                # Loss from choosing B when A might be better
                loss = max(0, a_sample - b_sample)
            else:
                # Loss from choosing A when B might be better
                loss = max(0, b_sample - a_sample)
            
            losses.append(loss)
        
        return sum(losses) / len(losses)
    
    def get_summary(self) -> dict:
        """Get a summary of the current state."""
        return {
            'variant_a_mean': self.variant_a.mean(),
            'variant_b_mean': self.variant_b.mean(),
            'prob_b_beats_a': self.probability_b_beats_a(),
            'expected_loss_if_choose_a': self.expected_loss(choose_b=False),
            'expected_loss_if_choose_b': self.expected_loss(choose_b=True),
        }


if __name__ == "__main__":
    # Demo: simulating an A/B test for a landing page
    print("=== Bayesian A/B Test Demo ===\n")
    
    test = ABTest()
    
    # Variant A: 120 conversions out of 1000 visitors
    # Variant B: 145 conversions out of 1000 visitors
    print("Scenario: Testing two landing page designs")
    print("Variant A: 120 conversions, 880 non-conversions")
    print("Variant B: 145 conversions, 855 non-conversions\n")
    
    test.add_observations('A', successes=120, failures=880)
    test.add_observations('B', successes=145, failures=855)
    
    summary = test.get_summary()
    
    print(f"Variant A estimated conversion rate: {summary['variant_a_mean']:.4f}")
    print(f"Variant B estimated conversion rate: {summary['variant_b_mean']:.4f}")
    print(f"\nProbability that B beats A: {summary['prob_b_beats_a']:.2%}")
    print(f"\nExpected loss if we choose A: {summary['expected_loss_if_choose_a']:.4f}")
    print(f"Expected loss if we choose B: {summary['expected_loss_if_choose_b']:.4f}")
    
    # Decision recommendation
    if summary['prob_b_beats_a'] > 0.95:
        print("\n✓ Strong evidence for B. Ship it!")
    elif summary['prob_b_beats_a'] > 0.90:
        print("\n⚠ Good evidence for B, but maybe collect more data.")
    elif summary['prob_b_beats_a'] < 0.10:
        print("\n✓ Strong evidence for A. Keep the original.")
    else:
        print("\n⚠ Results are inconclusive. Need more data.")