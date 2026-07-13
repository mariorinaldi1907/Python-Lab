"""
Date: 2026-07-13
Created a Bayesian A/B testing tool that uses beta-binomial conjugates to analyze conversion rates and compute win probabilities without p-values.
"""

"""
Bayesian A/B Testing Module

I got tired of p-values and wanted to see what Bayesian analysis looks like
for conversion rate testing. This uses beta distributions as priors and
posteriors for binary outcomes (clicked/didn't click, converted/didn't convert).

The beauty of beta-binomial conjugacy is that updating beliefs is just addition.
"""

import random
import math
from typing import Tuple, List


class BetaDistribution:
    """
    Represents a Beta distribution for Bayesian inference on probabilities.
    
    Beta(alpha, beta) is the conjugate prior for binomial likelihood.
    When alpha=beta=1, it's a uniform prior (all probabilities equally likely).
    """
    
    def __init__(self, alpha: float = 1.0, beta: float = 1.0):
        """Initialize with prior parameters (default: uniform prior)."""
        self.alpha = alpha
        self.beta = beta
    
    def update(self, successes: int, failures: int):
        """
        Update the distribution with observed data.
        
        This is where the Bayesian magic happens — posterior is just
        prior + data because of conjugacy.
        """
        self.alpha += successes
        self.beta += failures
    
    def mean(self) -> float:
        """Expected value of the distribution."""
        return self.alpha / (self.alpha + self.beta)
    
    def mode(self) -> float:
        """Most likely value (only valid when alpha, beta > 1)."""
        if self.alpha > 1 and self.beta > 1:
            return (self.alpha - 1) / (self.alpha + self.beta - 2)
        return self.mean()
    
    def variance(self) -> float:
        """Variance of the distribution."""
        ab = self.alpha + self.beta
        return (self.alpha * self.beta) / (ab * ab * (ab + 1))
    
    def sample(self) -> float:
        """
        Draw a random sample from this beta distribution.
        
        Using the fact that if X ~ Gamma(alpha) and Y ~ Gamma(beta),
        then X/(X+Y) ~ Beta(alpha, beta).
        """
        x = random.gammavariate(self.alpha, 1)
        y = random.gammavariate(self.beta, 1)
        return x / (x + y)
    
    def credible_interval(self, confidence: float = 0.95) -> Tuple[float, float]:
        """
        Compute credible interval (Bayesian confidence interval).
        
        Uses a simple quantile approach. For production, I'd use
        scipy's beta.ppf, but we're standard library only here.
        """
        # Generate samples to approximate the credible interval
        samples = sorted([self.sample() for _ in range(10000)])
        lower_idx = int(len(samples) * (1 - confidence) / 2)
        upper_idx = int(len(samples) * (1 + confidence) / 2)
        return samples[lower_idx], samples[upper_idx]


class ABTest:
    """
    Bayesian A/B test comparing two conversion rates.
    
    Much more intuitive than frequentist tests — we get direct
    probability statements like "A is better than B with 94% probability".
    """
    
    def __init__(self, prior_alpha: float = 1.0, prior_beta: float = 1.0):
        """Initialize with priors for both variants."""
        self.variant_a = BetaDistribution(prior_alpha, prior_beta)
        self.variant_b = BetaDistribution(prior_alpha, prior_beta)
    
    def add_data(self, variant: str, successes: int, trials: int):
        """
        Add observed data for a variant.
        
        variant: 'A' or 'B'
        successes: number of conversions
        trials: total number of users/impressions
        """
        failures = trials - successes
        
        if variant.upper() == 'A':
            self.variant_a.update(successes, failures)
        elif variant.upper() == 'B':
            self.variant_b.update(successes, failures)
        else:
            raise ValueError("Variant must be 'A' or 'B'")
    
    def probability_a_beats_b(self, n_samples: int = 50000) -> float:
        """
        Calculate probability that A's conversion rate > B's.
        
        This is the key metric in Bayesian A/B testing. We sample from
        both posteriors and count how often A wins.
        """
        a_wins = sum(
            self.variant_a.sample() > self.variant_b.sample()
            for _ in range(n_samples)
        )
        return a_wins / n_samples
    
    def expected_loss(self, n_samples: int = 50000) -> Tuple[float, float]:
        """
        Expected loss if we choose each variant.
        
        This tells us: "If I pick A, how much conversion rate am I
        expected to lose if B is actually better?"
        """
        samples_a = [self.variant_a.sample() for _ in range(n_samples)]
        samples_b = [self.variant_b.sample() for _ in range(n_samples)]
        
        # Expected loss of choosing A = E[max(B - A, 0)]
        loss_a = sum(max(b - a, 0) for a, b in zip(samples_a, samples_b)) / n_samples
        
        # Expected loss of choosing B = E[max(A - B, 0)]
        loss_b = sum(max(a - b, 0) for a, b in zip(samples_a, samples_b)) / n_samples
        
        return loss_a, loss_b
    
    def summary(self):
        """Print a comprehensive summary of the test."""
        print("=" * 60)
        print("Bayesian A/B Test Results")
        print("=" * 60)
        
        print("\nVariant A:")
        print(f"  Posterior: Beta({self.variant_a.alpha:.1f}, {self.variant_a.beta:.1f})")
        print(f"  Mean conversion rate: {self.variant_a.mean():.4f}")
        ci_a = self.variant_a.credible_interval()
        print(f"  95% credible interval: [{ci_a[0]:.4f}, {ci_a[1]:.4f}]")
        
        print("\nVariant B:")
        print(f"  Posterior: Beta({self.variant_b.alpha:.1f}, {self.variant_b.beta:.1f})")
        print(f"  Mean conversion rate: {self.variant_b.mean():.4f}")
        ci_b = self.variant_b.credible_interval()
        print(f"  95% credible interval: [{ci_b[0]:.4f}, {ci_b[1]:.4f}]")
        
        prob_a_wins = self.probability_a_beats_b()
        print(f"\nP(A > B) = {prob_a_wins:.2%}")
        print(f"P(B > A) = {(1 - prob_a_wins):.2%}")
        
        loss_a, loss_b = self.expected_loss()
        print(f"\nExpected loss if choosing A: {loss_a:.4f}")
        print(f"Expected loss if choosing B: {loss_b:.4f}")
        
        # Decision rule: I usually go with <1% expected loss
        if loss_a < 0.01:
            print("\n✓ Recommendation: Deploy variant A")
        elif loss_b < 0.01:
            print("\n✓ Recommendation: Deploy variant B")
        else:
            print("\n⚠ Recommendation: Keep testing, results inconclusive")


if __name__ == "__main__":
    # Simulating a real A/B test I might run on a landing page
    print("Demo: Testing two call-to-action buttons\n")
    
    # Start with a weakly informative prior (like 5% conversion)
    test = ABTest(prior_alpha=2, prior_beta=38)
    
    # Variant A (old button): 250 conversions out of 5000 users
    test.add_data('A', successes=250, trials=5000)
    
    # Variant B (new button): 295 conversions out of 5000 users
    test.add_data('B', successes=295, trials=5000)
    
    test.summary()
    
    print("\n" + "=" * 60)
    print("Why I prefer this over p-values:")
    print("  • Direct probability statements about which variant is better")
    print("  • Can make decisions based on expected loss, not arbitrary α")
    print("  • Incorporates prior knowledge if I have it")
    print("  • Easy to update as more data comes in")