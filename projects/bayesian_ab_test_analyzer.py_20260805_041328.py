"""
Date: 2026-08-05
Created a Bayesian inference tool for A/B testing that uses Beta-Binomial conjugate priors to estimate conversion rates and compute probability of superiority — tired of misinterpreting p-values.
"""

#!/usr/bin/env env python3
"""
Bayesian A/B Test Analyzer
Uses Beta-Binomial conjugate priors for conversion rate estimation.
I got tired of p-values being misinterpreted in A/B tests, so I built this.
"""

import random
import math
from typing import Tuple, List


class BetaDistribution:
    """
    Represents a Beta distribution for Bayesian updating.
    
    The Beta distribution is conjugate to the Binomial, which makes it
    perfect for modeling conversion rates. Alpha and beta are the shape
    parameters that get updated as we see more data.
    """
    
    def __init__(self, alpha: float = 1.0, beta: float = 1.0):
        """
        Initialize with prior parameters.
        Alpha=1, Beta=1 gives us a uniform prior (no assumptions).
        """
        self.alpha = alpha
        self.beta = beta
    
    def update(self, successes: int, failures: int):
        """
        Update the distribution with observed data.
        This is where the Bayesian magic happens - conjugate priors mean
        the posterior is also Beta distributed.
        """
        self.alpha += successes
        self.beta += failures
    
    def mean(self) -> float:
        """Expected value of the distribution."""
        return self.alpha / (self.alpha + self.beta)
    
    def mode(self) -> float:
        """Most likely value (peak of the distribution)."""
        if self.alpha > 1 and self.beta > 1:
            return (self.alpha - 1) / (self.alpha + self.beta - 2)
        return self.mean()  # fallback for edge cases
    
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
        x = random.gammavariate(self.alpha, 1)
        y = random.gammavariate(self.beta, 1)
        return x / (x + y)
    
    def credible_interval(self, confidence: float = 0.95) -> Tuple[float, float]:
        """
        Compute a credible interval using quantile approximation.
        Not exact, but good enough for practical purposes.
        """
        # Simple normal approximation for large alpha + beta
        mean = self.mean()
        std = math.sqrt(self.variance())
        z = 1.96 if confidence == 0.95 else 2.576  # quick lookup
        return (max(0, mean - z * std), min(1, mean + z * std))


class ABTestAnalyzer:
    """
    Analyzes A/B test results using Bayesian inference.
    """
    
    def __init__(self, prior_alpha: float = 1.0, prior_beta: float = 1.0):
        """
        Initialize with priors for both variants.
        Default uniform prior means we start with no assumptions.
        """
        self.variant_a = BetaDistribution(prior_alpha, prior_beta)
        self.variant_b = BetaDistribution(prior_alpha, prior_beta)
    
    def update_variant_a(self, conversions: int, non_conversions: int):
        """Update posterior for variant A with observed data."""
        self.variant_a.update(conversions, non_conversions)
    
    def update_variant_b(self, conversions: int, non_conversions: int):
        """Update posterior for variant B with observed data."""
        self.variant_b.update(conversions, non_conversions)
    
    def probability_b_beats_a(self, num_samples: int = 10000) -> float:
        """
        Estimate P(B > A) using Monte Carlo sampling.
        
        This is the key metric: what's the probability that variant B
        actually has a higher conversion rate than A? Way more interpretable
        than a p-value.
        """
        b_wins = 0
        for _ in range(num_samples):
            sample_a = self.variant_a.sample()
            sample_b = self.variant_b.sample()
            if sample_b > sample_a:
                b_wins += 1
        return b_wins / num_samples
    
    def expected_loss(self, num_samples: int = 10000) -> Tuple[float, float]:
        """
        Calculate expected loss for choosing each variant.
        
        Expected loss = how much conversion rate we'd lose on average
        if we picked the wrong variant. Helps with decision-making.
        """
        loss_a = 0  # loss from choosing A when B might be better
        loss_b = 0  # loss from choosing B when A might be better
        
        for _ in range(num_samples):
            sample_a = self.variant_a.sample()
            sample_b = self.variant_b.sample()
            
            # If we choose A, we lose (B - A) when B is better
            loss_a += max(0, sample_b - sample_a)
            # If we choose B, we lose (A - B) when A is better
            loss_b += max(0, sample_a - sample_b)
        
        return (loss_a / num_samples, loss_b / num_samples)
    
    def summary(self) -> dict:
        """Get a summary of the analysis."""
        return {
            'variant_a_mean': self.variant_a.mean(),
            'variant_b_mean': self.variant_b.mean(),
            'variant_a_ci': self.variant_a.credible_interval(),
            'variant_b_ci': self.variant_b.credible_interval(),
            'prob_b_beats_a': self.probability_b_beats_a(),
            'expected_loss': self.expected_loss()
        }


if __name__ == "__main__":
    print("=== Bayesian A/B Test Analyzer Demo ===\n")
    
    # Simulating a real A/B test scenario
    # Variant A: Original landing page
    # Variant B: New design with bigger CTA button
    
    analyzer = ABTestAnalyzer(prior_alpha=1, prior_beta=1)
    
    # Variant A results: 120 conversions out of 1000 visitors
    conversions_a = 120
    visitors_a = 1000
    analyzer.update_variant_a(conversions_a, visitors_a - conversions_a)
    
    # Variant B results: 145 conversions out of 1000 visitors
    conversions_b = 145
    visitors_b = 1000
    analyzer.update_variant_b(conversions_b, visitors_b - conversions_b)
    
    print(f"Variant A: {conversions_a}/{visitors_a} conversions ({conversions_a/visitors_a:.1%})")
    print(f"Variant B: {conversions_b}/{visitors_b} conversions ({conversions_b/visitors_b:.1%})")
    print()
    
    summary = analyzer.summary()
    
    print(f"Variant A estimated conversion rate: {summary['variant_a_mean']:.3%}")
    print(f"  95% credible interval: [{summary['variant_a_ci'][0]:.3%}, {summary['variant_a_ci'][1]:.3%}]")
    print()
    
    print(f"Variant B estimated conversion rate: {summary['variant_b_mean']:.3%}")
    print(f"  95% credible interval: [{summary['variant_b_ci'][0]:.3%}, {summary['variant_b_ci'][1]:.3%}]")
    print()
    
    prob_b_wins = summary['prob_b_beats_a']
    print(f"Probability that B beats A: {prob_b_wins:.1%}")
    print()
    
    loss_a, loss_b = summary['expected_loss']
    print(f"Expected loss from choosing A: {loss_a:.4f} ({loss_a*100:.2f} percentage points)")
    print(f"Expected loss from choosing B: {loss_b:.4f} ({loss_b*100:.2f} percentage points)")
    print()
    
    # Decision logic
    if prob_b_wins > 0.95:
        print("✓ Strong evidence for B. Ship it!")
    elif prob_b_wins > 0.90:
        print("→ Moderate evidence for B. Consider shipping or collecting more data.")
    elif prob_b_wins < 0.10:
        print("✗ Evidence suggests A is better. Stick with original.")
    else:
        print("? Inconclusive. Need more data or the difference doesn't matter much.")