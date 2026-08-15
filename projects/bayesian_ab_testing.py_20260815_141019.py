"""
Date: 2026-08-15
Implemented a Bayesian A/B testing framework using conjugate priors to compare conversion rates and calculate probability of superiority — handles real-world testing scenarios without p-value headaches.
"""

#!/usr/bin/env python3
"""
Bayesian A/B Testing Framework

This module implements Bayesian inference for A/B testing using Beta-Binomial
conjugate priors. I got tired of dealing with p-values and multiple testing
corrections, so I built this to get direct probability statements about which
variant is better.

The Beta distribution is perfect for modeling conversion rates because it's
bounded between 0 and 1, and it plays nicely with binomial data (successes/trials).
"""

import random
import math
from typing import Tuple, List


class BetaDistribution:
    """
    Represents a Beta distribution for Bayesian inference.
    
    The Beta distribution is parameterized by alpha (successes + prior) and 
    beta (failures + prior). I'm using it as a conjugate prior for binomial data.
    """
    
    def __init__(self, alpha: float = 1.0, beta: float = 1.0):
        """
        Initialize Beta distribution.
        
        Args:
            alpha: Shape parameter (think of it as prior successes + 1)
            beta: Shape parameter (think of it as prior failures + 1)
        
        Default (1, 1) gives us a uniform prior - no assumptions about the data.
        """
        self.alpha = alpha
        self.beta = beta
    
    def update(self, successes: int, failures: int):
        """
        Update the distribution with observed data (Bayesian update).
        
        This is the magic of conjugate priors - super simple update rule.
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
    
    def std(self) -> float:
        """Standard deviation."""
        return math.sqrt(self.variance())
    
    def sample(self) -> float:
        """
        Draw a random sample from the Beta distribution.
        
        Using the fact that if X ~ Gamma(alpha) and Y ~ Gamma(beta),
        then X/(X+Y) ~ Beta(alpha, beta). Python's random.gammavariate
        makes this easy.
        """
        x = random.gammavariate(self.alpha, 1)
        y = random.gammavariate(self.beta, 1)
        return x / (x + y)
    
    def credible_interval(self, samples: int = 10000, confidence: float = 0.95) -> Tuple[float, float]:
        """
        Calculate credible interval using sampling.
        
        Unlike confidence intervals, we can actually say "there's a 95% probability
        the true value is in this range" - which is what people think CIs mean anyway.
        """
        draws = sorted([self.sample() for _ in range(samples)])
        lower_idx = int((1 - confidence) / 2 * samples)
        upper_idx = int((1 + confidence) / 2 * samples)
        return draws[lower_idx], draws[upper_idx]


class ABTest:
    """
    Bayesian A/B test comparing two conversion rates.
    
    Way more intuitive than null hypothesis testing - we get direct probability
    statements about which variant is better.
    """
    
    def __init__(self, prior_alpha: float = 1.0, prior_beta: float = 1.0):
        """
        Initialize A/B test with prior beliefs.
        
        Args:
            prior_alpha: Prior successes (uniform prior is 1, 1)
            prior_beta: Prior failures
        """
        self.variant_a = BetaDistribution(prior_alpha, prior_beta)
        self.variant_b = BetaDistribution(prior_alpha, prior_beta)
    
    def add_data_a(self, successes: int, trials: int):
        """Add observed data for variant A."""
        failures = trials - successes
        self.variant_a.update(successes, failures)
    
    def add_data_b(self, successes: int, trials: int):
        """Add observed data for variant B."""
        failures = trials - successes
        self.variant_b.update(successes, failures)
    
    def probability_b_beats_a(self, samples: int = 50000) -> float:
        """
        Calculate P(B > A) via Monte Carlo sampling.
        
        This is the key metric - direct probability that B has a higher conversion
        rate than A. No p-values, no significance thresholds, just probability.
        """
        b_wins = sum(
            self.variant_b.sample() > self.variant_a.sample()
            for _ in range(samples)
        )
        return b_wins / samples
    
    def expected_loss(self, samples: int = 50000) -> Tuple[float, float]:
        """
        Calculate expected loss if we choose the wrong variant.
        
        Returns:
            (loss_if_choose_a, loss_if_choose_b)
        
        Expected loss is the opportunity cost of picking the wrong variant.
        I use this to decide when to stop the test - if the expected loss is tiny,
        just ship it.
        """
        losses_a = []
        losses_b = []
        
        for _ in range(samples):
            sample_a = self.variant_a.sample()
            sample_b = self.variant_b.sample()
            
            # Loss if we choose A but B is better
            losses_a.append(max(0, sample_b - sample_a))
            # Loss if we choose B but A is better
            losses_b.append(max(0, sample_a - sample_b))
        
        return sum(losses_a) / samples, sum(losses_b) / samples
    
    def summary(self) -> str:
        """Generate a human-readable summary of the test results."""
        prob_b_wins = self.probability_b_beats_a()
        loss_a, loss_b = self.expected_loss()
        
        ci_a = self.variant_a.credible_interval()
        ci_b = self.variant_b.credible_interval()
        
        lines = [
            "="*60,
            "Bayesian A/B Test Results",
            "="*60,
            f"Variant A: {self.variant_a.mean():.4f} (95% CI: [{ci_a[0]:.4f}, {ci_a[1]:.4f}])",
            f"Variant B: {self.variant_b.mean():.4f} (95% CI: [{ci_b[0]:.4f}, {ci_b[1]:.4f}])",
            "",
            f"P(B > A) = {prob_b_wins:.2%}",
            f"Expected loss if choose A: {loss_a:.4f}",
            f"Expected loss if choose B: {loss_b:.4f}",
            "",
        ]
        
        # Decision logic based on expected loss
        if loss_a < 0.001 and loss_b < 0.001:
            lines.append("Decision: Variants are practically equivalent - pick either!")
        elif loss_b < 0.005:  # Less than 0.5% expected loss
            lines.append("Decision: Choose B (low risk)")
        elif loss_a < 0.005:
            lines.append("Decision: Choose A (low risk)")
        else:
            lines.append("Decision: Keep testing - results not conclusive yet")
        
        lines.append("="*60)
        return "\n".join(lines)


if __name__ == "__main__":
    # Simulating a real A/B test scenario
    # Let's say we're testing a new checkout button color
    
    print("Scenario: Testing new checkout button design")
    print("Variant A (control): Blue button")
    print("Variant B (treatment): Green button\n")
    
    # Initialize test with uniform prior
    test = ABTest()
    
    # Simulate some data - variant B is actually slightly better (12% vs 10%)
    # In reality this would come from real user data
    print("Adding day 1 data...")
    test.add_data_a(successes=50, trials=500)   # 10% conversion
    test.add_data_b(successes=55, trials=500)   # 11% conversion
    print(test.summary())
    
    print("\nAdding day 2 data...")
    test.add_data_a(successes=102, trials=1000)  # 10.2% conversion
    test.add_data_b(successes=118, trials=1000)  # 11.8% conversion
    print(test.summary())
    
    print("\nAdding day 3 data (more traffic)...")
    test.add_data_a(successes=205, trials=2000)  # 10.25% conversion
    test.add_data_b(successes=242, trials=2000)  # 12.1% conversion
    print(test.summary())
    
    # Show the distributions
    print("\nFinal conversion rate estimates:")
    print(f"A: {test.variant_a.mean():.2%} ± {test.variant_a.std():.2%}")
    print(f"B: {test.variant_b.mean():.2%} ± {test.variant_b.std():.2%}")