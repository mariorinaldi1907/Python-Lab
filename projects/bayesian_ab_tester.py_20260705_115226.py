"""
Date: 2026-07-05
Created a Bayesian A/B testing module with beta distribution priors that lets me calculate probability of superiority and expected loss — way more intuitive than classical stats for conversion rate experiments.
"""

#!/usr/bin/env python3
"""
Bayesian A/B Testing with Beta-Binomial Model

I got tired of relying solely on p-values for A/B tests. This implements
a Bayesian approach using Beta distributions as conjugate priors for
binomial data (like conversion rates). Much more intuitive IMO.
"""

import math
import random
from typing import Tuple, List


class BetaDistribution:
    """
    Represents a Beta distribution for Bayesian inference on proportions.
    
    The Beta distribution is the conjugate prior for binomial/Bernoulli data,
    which makes updates super clean mathematically.
    """
    
    def __init__(self, alpha: float = 1.0, beta: float = 1.0):
        """
        Initialize with prior parameters.
        
        alpha=1, beta=1 gives a uniform prior (no prior knowledge).
        Higher values encode stronger prior beliefs.
        """
        self.alpha = alpha
        self.beta = beta
    
    def update(self, successes: int, failures: int):
        """
        Update the distribution given observed data.
        
        This is the magic of conjugate priors — the posterior is also Beta,
        just with updated parameters.
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
        x = random.gammavariate(self.alpha, 1)
        y = random.gammavariate(self.beta, 1)
        return x / (x + y)
    
    def pdf(self, x: float) -> float:
        """
        Probability density function at x.
        
        Not using scipy, so implementing the formula directly.
        """
        if x <= 0 or x >= 1:
            return 0.0
        
        # Beta PDF: x^(a-1) * (1-x)^(b-1) / B(a,b)
        # where B(a,b) is the beta function
        log_beta_ab = (math.lgamma(self.alpha) + math.lgamma(self.beta) - 
                       math.lgamma(self.alpha + self.beta))
        log_pdf = ((self.alpha - 1) * math.log(x) + 
                   (self.beta - 1) * math.log(1 - x) - log_beta_ab)
        return math.exp(log_pdf)


class ABTest:
    """
    Bayesian A/B test comparing two conversion rates.
    
    Much more flexible than traditional hypothesis testing — we can ask
    questions like "what's the probability that B is better than A?" instead
    of just rejecting/accepting null hypotheses.
    """
    
    def __init__(self, prior_alpha: float = 1.0, prior_beta: float = 1.0):
        """Initialize with identical priors for both variants."""
        self.variant_a = BetaDistribution(prior_alpha, prior_beta)
        self.variant_b = BetaDistribution(prior_alpha, prior_beta)
    
    def add_data(self, variant: str, successes: int, trials: int):
        """
        Add observed data for a variant.
        
        variant: 'A' or 'B'
        successes: number of conversions
        trials: total number of trials
        """
        failures = trials - successes
        
        if variant.upper() == 'A':
            self.variant_a.update(successes, failures)
        elif variant.upper() == 'B':
            self.variant_b.update(successes, failures)
        else:
            raise ValueError("Variant must be 'A' or 'B'")
    
    def probability_b_better(self, num_samples: int = 100000) -> float:
        """
        Estimate P(B > A) using Monte Carlo sampling.
        
        This is way easier than computing the exact integral, and accurate
        enough for practical decisions with enough samples.
        """
        b_wins = sum(
            self.variant_b.sample() > self.variant_a.sample()
            for _ in range(num_samples)
        )
        return b_wins / num_samples
    
    def expected_loss(self, choose_b: bool, num_samples: int = 100000) -> float:
        """
        Calculate expected loss if we choose a specific variant.
        
        Expected loss is: E[max(0, A - B)] if we choose B, or vice versa.
        Helps answer: "How much do we lose if we make the wrong choice?"
        """
        losses = []
        for _ in range(num_samples):
            sample_a = self.variant_a.sample()
            sample_b = self.variant_b.sample()
            
            if choose_b:
                # If we choose B, loss is when A was actually better
                loss = max(0, sample_a - sample_b)
            else:
                # If we choose A, loss is when B was actually better
                loss = max(0, sample_b - sample_a)
            
            losses.append(loss)
        
        return sum(losses) / len(losses)
    
    def summary(self) -> dict:
        """Get a summary of the current state of the test."""
        return {
            'variant_a_mean': self.variant_a.mean(),
            'variant_a_variance': self.variant_a.variance(),
            'variant_b_mean': self.variant_b.mean(),
            'variant_b_variance': self.variant_b.variance(),
            'prob_b_better': self.probability_b_better(),
            'expected_loss_if_choose_a': self.expected_loss(choose_b=False),
            'expected_loss_if_choose_b': self.expected_loss(choose_b=True),
        }


if __name__ == "__main__":
    print("=== Bayesian A/B Test Demo ===\n")
    
    # Simulating a real A/B test scenario
    # Let's say we're testing two landing page designs
    print("Scenario: Testing two landing page designs")
    print("Variant A: Control (current design)")
    print("Variant B: New design with simplified checkout\n")
    
    # Initialize test with uniform prior (no prior knowledge)
    test = ABTest(prior_alpha=1.0, prior_beta=1.0)
    
    # Add some realistic data
    # Variant A: 120 conversions out of 1000 visitors (12%)
    # Variant B: 145 conversions out of 1000 visitors (14.5%)
    print("Collecting data...")
    test.add_data('A', successes=120, trials=1000)
    test.add_data('B', successes=145, trials=1000)
    
    print(f"  Variant A: 120/1000 conversions (12.0%)")
    print(f"  Variant B: 145/1000 conversions (14.5%)\n")
    
    # Get the summary
    summary = test.summary()
    
    print("=== Results ===")
    print(f"Variant A estimated conversion rate: {summary['variant_a_mean']:.4f}")
    print(f"Variant B estimated conversion rate: {summary['variant_b_mean']:.4f}\n")
    
    print(f"Probability that B is better than A: {summary['prob_b_better']:.2%}\n")
    
    print("Expected Loss Analysis:")
    print(f"  If we choose A: {summary['expected_loss_if_choose_a']:.4f}")
    print(f"  If we choose B: {summary['expected_loss_if_choose_b']:.4f}\n")
    
    # Decision logic
    prob_threshold = 0.95
    if summary['prob_b_better'] > prob_threshold:
        print(f"✓ Recommendation: Choose Variant B")
        print(f"  (P(B > A) = {summary['prob_b_better']:.2%} > {prob_threshold:.0%})")
    elif summary['prob_b_better'] < (1 - prob_threshold):
        print(f"✓ Recommendation: Keep Variant A")
        print(f"  (P(A > B) = {1 - summary['prob_b_better']:.2%} > {prob_threshold:.0%})")
    else:
        print(f"⚠ Recommendation: Keep collecting data")
        print(f"  (Not enough evidence yet, P(B > A) = {summary['prob_b_better']:.2%})")