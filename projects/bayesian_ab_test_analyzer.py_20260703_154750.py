"""
Date: 2026-07-03
Created a Bayesian A/B testing tool that updates beliefs using conjugate priors and computes probability of superiority between variants.
"""

#!/usr/bin/env python3
"""
Bayesian A/B Test Analyzer

Uses Beta-Binomial conjugate priors to estimate conversion rates
and calculate the probability that variant B beats variant A.
Much more intuitive than p-values IMO.
"""

import math
from typing import Tuple, Dict
import random


class BetaDistribution:
    """
    Represents a Beta distribution with alpha and beta parameters.
    
    In A/B testing context:
    - alpha = successes + 1 (using uniform prior)
    - beta = failures + 1
    """
    
    def __init__(self, alpha: float = 1.0, beta: float = 1.0):
        """Initialize with prior parameters (default: uniform prior)."""
        self.alpha = alpha
        self.beta = beta
    
    def update(self, successes: int, failures: int):
        """Update the distribution with observed data (Bayesian update)."""
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
        Draw a random sample using the fact that if X~Gamma(α) and Y~Gamma(β),
        then X/(X+Y) ~ Beta(α,β).
        """
        # Using gamma distribution to sample from beta
        x = random.gammavariate(self.alpha, 1)
        y = random.gammavariate(self.beta, 1)
        return x / (x + y)
    
    def credible_interval(self, confidence: float = 0.95) -> Tuple[float, float]:
        """
        Compute credible interval using quantile approximation.
        Not exact but good enough for practical use.
        """
        # Using normal approximation for simplicity
        # For more accuracy, would implement inverse CDF
        mean = self.mean()
        std = self.std()
        z = 1.96 if confidence == 0.95 else 2.576  # rough approximation
        lower = max(0, mean - z * std)
        upper = min(1, mean + z * std)
        return (lower, upper)


class ABTest:
    """
    Bayesian A/B test analyzer.
    
    Tracks two variants and computes probability that B beats A.
    """
    
    def __init__(self, prior_alpha: float = 1.0, prior_beta: float = 1.0):
        """
        Initialize with uniform prior by default.
        Can use informative priors if you have domain knowledge.
        """
        self.variant_a = BetaDistribution(prior_alpha, prior_beta)
        self.variant_b = BetaDistribution(prior_alpha, prior_beta)
        self.samples_a = 0
        self.samples_b = 0
    
    def update_a(self, successes: int, failures: int):
        """Update variant A with new observations."""
        self.variant_a.update(successes, failures)
        self.samples_a += successes + failures
    
    def update_b(self, successes: int, failures: int):
        """Update variant B with new observations."""
        self.variant_b.update(successes, failures)
        self.samples_b += successes + failures
    
    def probability_b_beats_a(self, n_samples: int = 10000) -> float:
        """
        Monte Carlo estimation of P(B > A).
        
        Draw samples from both distributions and count how often B wins.
        This is the key insight of Bayesian A/B testing.
        """
        b_wins = 0
        for _ in range(n_samples):
            sample_a = self.variant_a.sample()
            sample_b = self.variant_b.sample()
            if sample_b > sample_a:
                b_wins += 1
        return b_wins / n_samples
    
    def expected_loss(self, n_samples: int = 10000) -> Dict[str, float]:
        """
        Calculate expected loss for choosing each variant.
        
        Loss = how much conversion rate we'd lose on average
        if we picked the wrong variant.
        """
        loss_a = 0
        loss_b = 0
        
        for _ in range(n_samples):
            sample_a = self.variant_a.sample()
            sample_b = self.variant_b.sample()
            # If we choose A but B is better, we lose (B - A)
            loss_a += max(0, sample_b - sample_a)
            # If we choose B but A is better, we lose (A - B)
            loss_b += max(0, sample_a - sample_b)
        
        return {
            'choose_a': loss_a / n_samples,
            'choose_b': loss_b / n_samples
        }
    
    def summary(self) -> str:
        """Generate a human-readable summary of the test."""
        prob_b_wins = self.probability_b_beats_a()
        losses = self.expected_loss()
        
        summary = [
            "=== Bayesian A/B Test Results ===",
            f"\nVariant A: {self.samples_a} samples",
            f"  Estimated conversion: {self.variant_a.mean():.4f}",
            f"  95% credible interval: {self.variant_a.credible_interval()}",
            f"\nVariant B: {self.samples_b} samples",
            f"  Estimated conversion: {self.variant_b.mean():.4f}",
            f"  95% credible interval: {self.variant_b.credible_interval()}",
            f"\nP(B > A) = {prob_b_wins:.2%}",
            f"\nExpected Loss:",
            f"  If we choose A: {losses['choose_a']:.6f}",
            f"  If we choose B: {losses['choose_b']:.6f}",
        ]
        
        if prob_b_wins > 0.95:
            summary.append("\n✓ Strong evidence that B is better!")
        elif prob_b_wins < 0.05:
            summary.append("\n✓ Strong evidence that A is better!")
        else:
            summary.append("\n⚠ Not enough evidence yet, keep testing.")
        
        return "\n".join(summary)


if __name__ == "__main__":
    print("Simulating a real A/B test scenario...\n")
    
    # Scenario: testing two landing page designs
    # True conversion rates (unknown to our analyzer):
    # A: 10%, B: 12%
    
    test = ABTest()
    
    # Simulate some initial data
    print("Week 1 results:")
    test.update_a(successes=98, failures=902)   # ~10% conversion
    test.update_b(successes=115, failures=885)  # ~12% conversion
    print(test.summary())
    
    print("\n" + "="*50 + "\n")
    
    # More data comes in
    print("Week 2 results (cumulative):")
    test.update_a(successes=105, failures=1095)  # more data
    test.update_b(successes=118, failures=882)   # more data
    print(test.summary())
    
    # Demo of starting fresh with informative prior
    print("\n" + "="*50)
    print("\nExample with informative prior (if you have domain knowledge):")
    # If we know conversion rates are typically around 10%, we can encode that
    informed_test = ABTest(prior_alpha=10, prior_beta=90)
    informed_test.update_a(successes=50, failures=450)
    informed_test.update_b(successes=60, failures=440)
    print(informed_test.summary())