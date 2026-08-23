"""
Date: 2026-08-23
Implemented Bayesian A/B testing with beta-binomial conjugate priors because I wanted a more intuitive way to compare conversion rates than classical hypothesis testing.
"""

#!/usr/bin/env python3
"""
Bayesian A/B Testing Module

Uses beta distributions as conjugate priors for binomial likelihood.
This gives us full posterior distributions instead of just p-values,
which makes way more sense when deciding between variants.
"""

import random
from math import gamma, lgamma
from typing import Tuple, List


class BetaDistribution:
    """
    Represents a Beta distribution, the conjugate prior for binomial data.
    
    Beta(alpha, beta) is perfect for modeling conversion rates because:
    - It's bounded [0, 1] like probabilities
    - Updating with new data is trivial (just add successes/failures)
    - We can sample from it easily for Monte Carlo comparisons
    """
    
    def __init__(self, alpha: float = 1.0, beta: float = 1.0):
        """
        Initialize Beta distribution.
        
        Args:
            alpha: Prior successes + 1 (default 1 = uniform prior)
            beta: Prior failures + 1 (default 1 = uniform prior)
        """
        self.alpha = alpha
        self.beta = beta
    
    def update(self, successes: int, failures: int) -> None:
        """Update posterior with observed data (Bayesian update is this simple!)"""
        self.alpha += successes
        self.beta += failures
    
    def mean(self) -> float:
        """Expected value of the distribution"""
        return self.alpha / (self.alpha + self.beta)
    
    def variance(self) -> float:
        """Variance of the distribution"""
        a, b = self.alpha, self.beta
        return (a * b) / ((a + b) ** 2 * (a + b + 1))
    
    def sample(self) -> float:
        """
        Draw a random sample using the fact that if X ~ Gamma(alpha) and 
        Y ~ Gamma(beta), then X/(X+Y) ~ Beta(alpha, beta).
        
        This is way faster than inverse transform sampling.
        """
        x = random.gammavariate(self.alpha, 1)
        y = random.gammavariate(self.beta, 1)
        return x / (x + y)
    
    def credible_interval(self, confidence: float = 0.95, samples: int = 10000) -> Tuple[float, float]:
        """
        Compute credible interval via sampling.
        This is the Bayesian equivalent of a confidence interval.
        """
        samples_list = [self.sample() for _ in range(samples)]
        samples_list.sort()
        
        lower_idx = int((1 - confidence) / 2 * samples)
        upper_idx = int((1 + confidence) / 2 * samples)
        
        return samples_list[lower_idx], samples_list[upper_idx]


class ABTest:
    """
    Bayesian A/B test comparing two conversion rates.
    
    Way more interpretable than p-values: we get actual probabilities
    like "there's a 94% chance variant B is better than A".
    """
    
    def __init__(self, prior_alpha: float = 1.0, prior_beta: float = 1.0):
        """
        Initialize A/B test with prior beliefs.
        
        Args:
            prior_alpha: Prior successes (1 = uniform/uninformative)
            prior_beta: Prior failures (1 = uniform/uninformative)
        """
        self.variant_a = BetaDistribution(prior_alpha, prior_beta)
        self.variant_b = BetaDistribution(prior_alpha, prior_beta)
    
    def add_observations(self, variant: str, successes: int, failures: int) -> None:
        """Add conversion data for a variant"""
        if variant.upper() == 'A':
            self.variant_a.update(successes, failures)
        elif variant.upper() == 'B':
            self.variant_b.update(successes, failures)
        else:
            raise ValueError("Variant must be 'A' or 'B'")
    
    def probability_b_beats_a(self, samples: int = 20000) -> float:
        """
        Monte Carlo estimate of P(B > A).
        
        This is the key metric: what's the probability that variant B
        actually has a higher conversion rate than A?
        """
        wins = sum(1 for _ in range(samples) if self.variant_b.sample() > self.variant_a.sample())
        return wins / samples
    
    def expected_lift(self, samples: int = 20000) -> float:
        """
        Expected relative improvement of B over A.
        Returns the mean of (B - A) / A.
        """
        lifts = []
        for _ in range(samples):
            a_sample = self.variant_a.sample()
            b_sample = self.variant_b.sample()
            if a_sample > 0:  # Avoid division by zero
                lifts.append((b_sample - a_sample) / a_sample)
        
        return sum(lifts) / len(lifts) if lifts else 0.0
    
    def summary(self) -> str:
        """Generate a readable summary of the test results"""
        prob_b_wins = self.probability_b_beats_a()
        lift = self.expected_lift()
        
        ci_a = self.variant_a.credible_interval()
        ci_b = self.variant_b.credible_interval()
        
        lines = [
            "=== Bayesian A/B Test Results ===",
            f"\nVariant A:",
            f"  Estimated conversion rate: {self.variant_a.mean():.4f}",
            f"  95% credible interval: ({ci_a[0]:.4f}, {ci_a[1]:.4f})",
            f"\nVariant B:",
            f"  Estimated conversion rate: {self.variant_b.mean():.4f}",
            f"  95% credible interval: ({ci_b[0]:.4f}, {ci_b[1]:.4f})",
            f"\nP(B > A): {prob_b_wins:.1%}",
            f"Expected lift from B: {lift:+.2%}",
        ]
        
        # Decision recommendation (my rule of thumb: need >95% to declare winner)
        if prob_b_wins > 0.95:
            lines.append("\n✓ Strong evidence for variant B")
        elif prob_b_wins < 0.05:
            lines.append("\n✓ Strong evidence for variant A")
        else:
            lines.append("\n⚠ Insufficient evidence to declare a winner")
        
        return "\n".join(lines)


if __name__ == "__main__":
    # Simulating a real A/B test I might run on a landing page
    print("Simulating an A/B test for a website landing page...\n")
    
    # Initialize test with uniform prior (no strong beliefs either way)
    test = ABTest(prior_alpha=1, prior_beta=1)
    
    # Variant A: Original design - 250 visitors, 45 conversions
    test.add_observations('A', successes=45, failures=205)
    
    # Variant B: New design - 250 visitors, 58 conversions
    test.add_observations('B', successes=58, failures=192)
    
    print(test.summary())
    
    # Let's also show what happens as we collect more data
    print("\n\n=== Collecting more data... ===\n")
    
    # Another week of data
    test.add_observations('A', successes=52, failures=248)
    test.add_observations('B', successes=71, failures=229)
    
    print(test.summary())
    
    # Show the power of the Bayesian approach with small sample sizes
    print("\n\n=== Early peek with limited data ===")
    early_test = ABTest()
    early_test.add_observations('A', successes=5, failures=45)
    early_test.add_observations('B', successes=8, failures=42)
    print(early_test.summary())