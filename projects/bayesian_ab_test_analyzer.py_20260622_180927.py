"""
Date: 2026-06-22
Implemented a Bayesian A/B testing framework using conjugate priors to compare conversion rates and calculate probabilities of superiority.
"""

#!/usr/bin/env python3
"""
Bayesian A/B Test Analyzer

Uses Beta-Binomial conjugate priors to analyze A/B test results.
I got tired of p-values and frequentist confusion, so I built this to get
actual probability statements like "A is better than B with 95% probability".
"""

import random
from math import gamma, log, exp


class BetaDistribution:
    """
    Represents a Beta distribution with parameters alpha and beta.
    
    In A/B testing context:
    - alpha represents successes + 1 (prior successes)
    - beta represents failures + 1 (prior failures)
    """
    
    def __init__(self, alpha=1.0, beta=1.0):
        """Initialize with uniform prior (alpha=1, beta=1) by default."""
        self.alpha = alpha
        self.beta = beta
    
    def update(self, successes, trials):
        """
        Update the distribution with new data (Bayesian update).
        
        This is the magic of conjugate priors — just add to alpha and beta.
        """
        failures = trials - successes
        self.alpha += successes
        self.beta += failures
    
    def mean(self):
        """Expected value of the Beta distribution."""
        return self.alpha / (self.alpha + self.beta)
    
    def variance(self):
        """Variance of the Beta distribution."""
        a, b = self.alpha, self.beta
        return (a * b) / ((a + b) ** 2 * (a + b + 1))
    
    def sample(self):
        """
        Draw a random sample from the Beta distribution.
        
        Using the fact that if X ~ Gamma(alpha) and Y ~ Gamma(beta),
        then X/(X+Y) ~ Beta(alpha, beta).
        """
        x = random.gammavariate(self.alpha, 1)
        y = random.gammavariate(self.beta, 1)
        return x / (x + y)
    
    def credible_interval(self, confidence=0.95):
        """
        Calculate credible interval using sampling.
        
        I'm using sampling instead of inverse CDF because it's simpler
        and the Beta inverse CDF gets messy without scipy.
        """
        samples = [self.sample() for _ in range(10000)]
        samples.sort()
        lower_idx = int((1 - confidence) / 2 * len(samples))
        upper_idx = int((1 + confidence) / 2 * len(samples))
        return samples[lower_idx], samples[upper_idx]


class ABTest:
    """
    Bayesian A/B test with two variants.
    
    Calculates probability that A beats B and provides decision support.
    """
    
    def __init__(self, prior_alpha=1.0, prior_beta=1.0):
        """Initialize with optional informative prior."""
        self.variant_a = BetaDistribution(prior_alpha, prior_beta)
        self.variant_b = BetaDistribution(prior_alpha, prior_beta)
    
    def add_data(self, variant, successes, trials):
        """
        Add observed data for a variant.
        
        variant: 'A' or 'B'
        successes: number of conversions
        trials: number of visitors
        """
        if variant.upper() == 'A':
            self.variant_a.update(successes, trials)
        elif variant.upper() == 'B':
            self.variant_b.update(successes, trials)
        else:
            raise ValueError("Variant must be 'A' or 'B'")
    
    def probability_a_beats_b(self, num_samples=50000):
        """
        Calculate P(conversion_rate_A > conversion_rate_B).
        
        This is the key Bayesian insight — we can directly state the probability
        that A is better, not just reject a null hypothesis.
        """
        wins = 0
        for _ in range(num_samples):
            sample_a = self.variant_a.sample()
            sample_b = self.variant_b.sample()
            if sample_a > sample_b:
                wins += 1
        return wins / num_samples
    
    def expected_loss(self, variant, num_samples=50000):
        """
        Calculate expected loss of choosing this variant if it's wrong.
        
        This helps with decision-making under uncertainty — even if A has 60%
        probability of being better, the loss might be small enough to ship B anyway.
        """
        losses = []
        for _ in range(num_samples):
            sample_a = self.variant_a.sample()
            sample_b = self.variant_b.sample()
            
            if variant.upper() == 'A':
                # Loss is how much worse A is if B is actually better
                loss = max(0, sample_b - sample_a)
            else:
                loss = max(0, sample_a - sample_b)
            losses.append(loss)
        
        return sum(losses) / len(losses)
    
    def summary(self):
        """Print a complete summary of the A/B test results."""
        print("=" * 60)
        print("Bayesian A/B Test Results")
        print("=" * 60)
        
        ci_a = self.variant_a.credible_interval(0.95)
        ci_b = self.variant_b.credible_interval(0.95)
        
        print(f"\nVariant A:")
        print(f"  Posterior Mean: {self.variant_a.mean():.4f}")
        print(f"  95% Credible Interval: [{ci_a[0]:.4f}, {ci_a[1]:.4f}]")
        
        print(f"\nVariant B:")
        print(f"  Posterior Mean: {self.variant_b.mean():.4f}")
        print(f"  95% Credible Interval: [{ci_b[0]:.4f}, {ci_b[1]:.4f}]")
        
        prob_a_wins = self.probability_a_beats_b()
        print(f"\nP(A > B) = {prob_a_wins:.1%}")
        print(f"P(B > A) = {1 - prob_a_wins:.1%}")
        
        loss_a = self.expected_loss('A')
        loss_b = self.expected_loss('B')
        
        print(f"\nExpected Loss:")
        print(f"  If we choose A: {loss_a:.4f}")
        print(f"  If we choose B: {loss_b:.4f}")
        
        # Decision recommendation
        print("\nRecommendation:")
        if prob_a_wins > 0.95:
            print("  ✓ Ship variant A with high confidence")
        elif prob_a_wins < 0.05:
            print("  ✓ Ship variant B with high confidence")
        elif abs(loss_a - loss_b) < 0.005:
            print("  → Difference is minimal, choose based on other factors")
        else:
            print("  ⚠ Collect more data for a clearer decision")
        
        print("=" * 60)


if __name__ == "__main__":
    # Simulate a real A/B test scenario I ran on a landing page
    print("Simulating landing page button color test...\n")
    
    test = ABTest(prior_alpha=1, prior_beta=1)  # Uninformative prior
    
    # Variant A: Blue button - 523 conversions out of 10,000 visitors
    test.add_data('A', successes=523, trials=10000)
    
    # Variant B: Green button - 547 conversions out of 10,000 visitors
    test.add_data('B', successes=547, trials=10000)
    
    test.summary()
    
    print("\n\nNow let's see what happens with less data:")
    print("(Early stopping can be dangerous!)\n")
    
    test_early = ABTest()
    test_early.add_data('A', successes=52, trials=1000)
    test_early.add_data('B', successes=55, trials=1000)
    test_early.summary()