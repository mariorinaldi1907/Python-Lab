"""
Date: 2026-07-25
Created a Bayesian inference tool for A/B testing that updates prior beliefs with observed conversion data and calculates probability of one variant beating another.
"""

"""
Bayesian A/B Test Analyzer
---------------------------
Uses Beta distributions to perform Bayesian inference on A/B test results.
I got tired of dealing with p-values and confidence intervals that don't 
actually tell you what you want to know, so I built this to get direct
probability statements about which variant is better.
"""

import random
import math
from typing import Tuple, List


class BetaDistribution:
    """
    Represents a Beta distribution for Bayesian inference on conversion rates.
    Beta(alpha, alpha) is the conjugate prior for binomial likelihood.
    """
    
    def __init__(self, alpha: float = 1.0, beta: float = 1.0):
        """
        Initialize a Beta distribution.
        
        Args:
            alpha: Shape parameter (often thought of as prior successes + 1)
            beta: Shape parameter (often thought of as prior failures + 1)
        """
        self.alpha = alpha
        self.beta = beta
    
    def update(self, successes: int, failures: int) -> None:
        """
        Update the distribution with observed data (Bayesian updating).
        
        Args:
            successes: Number of conversions observed
            failures: Number of non-conversions observed
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
        return self.mean()
    
    def variance(self) -> float:
        """Variance of the distribution."""
        a_plus_b = self.alpha + self.beta
        return (self.alpha * self.beta) / (a_plus_b ** 2 * (a_plus_b + 1))
    
    def sample(self) -> float:
        """
        Generate a random sample from this Beta distribution.
        Uses the ratio of two gamma variates method since we don't have numpy.
        """
        # Beta(a,b) = Gamma(a) / (Gamma(a) + Gamma(b))
        gamma_a = self._gamma_sample(self.alpha)
        gamma_b = self._gamma_sample(self.beta)
        return gamma_a / (gamma_a + gamma_b)
    
    def _gamma_sample(self, shape: float) -> float:
        """
        Generate a sample from Gamma(shape, 1) using Marsaglia & Tsang method.
        This is kind of annoying to implement without scipy, but it works.
        """
        if shape < 1:
            # Use the transformation Gamma(a) = Gamma(a+1) * U^(1/a)
            return self._gamma_sample(shape + 1) * (random.random() ** (1.0 / shape))
        
        # Marsaglia & Tsang's method for shape >= 1
        d = shape - 1.0 / 3.0
        c = 1.0 / math.sqrt(9.0 * d)
        
        while True:
            z = random.gauss(0, 1)
            v = (1.0 + c * z) ** 3
            
            if v <= 0:
                continue
            
            u = random.random()
            z_squared = z * z
            
            # Accept/reject criteria
            if u < 1.0 - 0.0331 * z_squared * z_squared:
                return d * v
            
            if math.log(u) < 0.5 * z_squared + d * (1.0 - v + math.log(v)):
                return d * v


class ABTestAnalyzer:
    """
    Bayesian A/B test analyzer using Beta-Binomial conjugate priors.
    Makes it easy to compare two variants and get actual probabilities.
    """
    
    def __init__(self, prior_alpha: float = 1.0, prior_beta: float = 1.0):
        """
        Initialize analyzer with uninformative priors by default.
        
        Args:
            prior_alpha: Prior "successes" (1 = uninformative)
            prior_beta: Prior "failures" (1 = uninformative)
        """
        self.variant_a = BetaDistribution(prior_alpha, prior_beta)
        self.variant_b = BetaDistribution(prior_alpha, prior_beta)
    
    def update(self, variant: str, conversions: int, visitors: int) -> None:
        """
        Update beliefs with observed data.
        
        Args:
            variant: Either 'A' or 'B'
            conversions: Number of successful conversions
            visitors: Total number of visitors
        """
        failures = visitors - conversions
        
        if variant.upper() == 'A':
            self.variant_a.update(conversions, failures)
        elif variant.upper() == 'B':
            self.variant_b.update(conversions, failures)
        else:
            raise ValueError(f"Variant must be 'A' or 'B', got {variant}")
    
    def probability_b_beats_a(self, num_samples: int = 10000) -> float:
        """
        Calculate P(B > A) using Monte Carlo sampling.
        This is the direct answer to "what's the probability B is better?"
        
        Args:
            num_samples: Number of Monte Carlo samples to use
            
        Returns:
            Probability that variant B has a higher conversion rate than A
        """
        b_wins = sum(
            self.variant_b.sample() > self.variant_a.sample()
            for _ in range(num_samples)
        )
        return b_wins / num_samples
    
    def get_summary(self) -> dict:
        """Get a summary of both variants' posterior distributions."""
        return {
            'A': {
                'mean': self.variant_a.mean(),
                'mode': self.variant_a.mode(),
                'variance': self.variant_a.variance(),
            },
            'B': {
                'mean': self.variant_b.mean(),
                'mode': self.variant_b.mode(),
                'variance': self.variant_b.variance(),
            }
        }


if __name__ == "__main__":
    # Real-world scenario: testing a new checkout button design
    print("=== Bayesian A/B Test Analysis ===\n")
    
    analyzer = ABTestAnalyzer(prior_alpha=1, prior_beta=1)
    
    # Variant A (control): old checkout button
    a_visitors = 1000
    a_conversions = 85
    analyzer.update('A', conversions=a_conversions, visitors=a_visitors)
    
    # Variant B (treatment): new checkout button
    b_visitors = 1000
    b_conversions = 102
    analyzer.update('B', conversions=b_conversions, visitors=b_visitors)
    
    print(f"Variant A: {a_conversions}/{a_visitors} conversions ({a_conversions/a_visitors:.2%})")
    print(f"Variant B: {b_conversions}/{b_visitors} conversions ({b_conversions/b_visitors:.2%})")
    print()
    
    # Get posterior summaries
    summary = analyzer.get_summary()
    print("Posterior Distributions:")
    print(f"  A - Mean: {summary['A']['mean']:.4f}, Mode: {summary['A']['mode']:.4f}")
    print(f"  B - Mean: {summary['B']['mean']:.4f}, Mode: {summary['B']['mode']:.4f}")
    print()
    
    # The key question: what's the probability B is actually better?
    prob_b_wins = analyzer.probability_b_beats_a(num_samples=20000)
    print(f"Probability B beats A: {prob_b_wins:.2%}")
    print()
    
    # Decision guidance based on probability thresholds
    if prob_b_wins > 0.95:
        print("✓ Strong evidence: Ship variant B!")
    elif prob_b_wins > 0.80:
        print("→ Moderate evidence: Consider shipping B, maybe collect more data")
    elif prob_b_wins < 0.20:
        print("✗ Evidence against B: Stick with A")
    else:
        print("? Inconclusive: Need more data to make a decision")