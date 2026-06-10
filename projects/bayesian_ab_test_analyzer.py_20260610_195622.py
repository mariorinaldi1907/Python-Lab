"""
Date: 2026-06-10
Created a Bayesian A/B testing tool that updates beliefs using beta distributions and calculates probability of one variant beating another — way more intuitive than p-values.
"""

#!/usr/bin/env python3
"""
Bayesian A/B Test Analyzer
Uses beta distributions to model conversion rates and compare variants.
Much more interpretable than frequentist hypothesis testing IMO.
"""

import random
import math
from typing import Tuple, List


class BetaDistribution:
    """
    Represents a Beta distribution for modeling conversion rates.
    Beta(alpha, alpha) is the conjugate prior for binomial likelihood,
    which makes Bayesian updating super clean mathematically.
    """
    
    def __init__(self, alpha: float = 1.0, beta: float = 1.0):
        """
        Initialize Beta distribution with parameters.
        
        Args:
            alpha: Number of successes + 1 (uniform prior when alpha=1)
            beta: Number of failures + 1 (uniform prior when beta=1)
        """
        self.alpha = alpha
        self.beta = beta
    
    def update(self, successes: int, failures: int):
        """
        Update the distribution with new observed data.
        This is the Bayesian updating step - prior + data = posterior.
        """
        self.alpha += successes
        self.beta += failures
    
    def mean(self) -> float:
        """Expected value of the beta distribution."""
        return self.alpha / (self.alpha + self.beta)
    
    def variance(self) -> float:
        """Variance of the beta distribution."""
        a_plus_b = self.alpha + self.beta
        return (self.alpha * self.beta) / (a_plus_b ** 2 * (a_plus_b + 1))
    
    def sample(self) -> float:
        """
        Draw a random sample from this beta distribution.
        Using the fact that if X~Gamma(alpha) and Y~Gamma(beta),
        then X/(X+Y) ~ Beta(alpha, beta).
        """
        # Generate two gamma samples
        x = self._gamma_sample(self.alpha)
        y = self._gamma_sample(self.beta)
        return x / (x + y)
    
    def _gamma_sample(self, shape: float) -> float:
        """
        Sample from Gamma distribution using Marsaglia and Tsang's method.
        Not the fastest implementation but works with stdlib only.
        """
        if shape >= 1:
            d = shape - 1.0 / 3.0
            c = 1.0 / math.sqrt(9.0 * d)
            while True:
                z = random.gauss(0, 1)
                u = random.random()
                v = (1.0 + c * z) ** 3
                if z > -1.0 / c and math.log(u) < 0.5 * z * z + d - d * v + d * math.log(v):
                    return d * v
        else:
            # For shape < 1, use the property Gamma(shape) = Gamma(shape+1) * U^(1/shape)
            return self._gamma_sample(shape + 1) * (random.random() ** (1.0 / shape))


class ABTestAnalyzer:
    """
    Analyzes A/B tests using Bayesian inference.
    Tracks conversion data for two variants and calculates probabilities.
    """
    
    def __init__(self, prior_alpha: float = 1.0, prior_beta: float = 1.0):
        """
        Initialize analyzer with prior beliefs.
        
        Args:
            prior_alpha: Prior successes (1 = uniform/uninformative prior)
            prior_beta: Prior failures (1 = uniform/uninformative prior)
        """
        self.variant_a = BetaDistribution(prior_alpha, prior_beta)
        self.variant_b = BetaDistribution(prior_alpha, prior_beta)
    
    def update_variant_a(self, conversions: int, non_conversions: int):
        """Update beliefs about variant A with observed data."""
        self.variant_a.update(conversions, non_conversions)
    
    def update_variant_b(self, conversions: int, non_conversions: int):
        """Update beliefs about variant B with observed data."""
        self.variant_b.update(conversions, non_conversions)
    
    def probability_b_beats_a(self, num_samples: int = 10000) -> float:
        """
        Calculate P(B > A) using Monte Carlo sampling.
        This is way more intuitive than a p-value - it directly answers
        "what's the probability that B is actually better?"
        
        Args:
            num_samples: Number of Monte Carlo samples (more = more accurate)
        
        Returns:
            Probability that variant B has higher conversion rate than A
        """
        b_wins = 0
        for _ in range(num_samples):
            sample_a = self.variant_a.sample()
            sample_b = self.variant_b.sample()
            if sample_b > sample_a:
                b_wins += 1
        
        return b_wins / num_samples
    
    def expected_loss(self, choose_a: bool, num_samples: int = 10000) -> float:
        """
        Calculate expected loss if we choose variant A or B.
        This helps quantify the risk of making the wrong decision.
        
        Args:
            choose_a: If True, calculate loss from choosing A; else B
            num_samples: Number of Monte Carlo samples
        
        Returns:
            Expected loss (in conversion rate points)
        """
        total_loss = 0.0
        for _ in range(num_samples):
            sample_a = self.variant_a.sample()
            sample_b = self.variant_b.sample()
            
            if choose_a:
                # Loss if we choose A but B is better
                loss = max(0, sample_b - sample_a)
            else:
                # Loss if we choose B but A is better
                loss = max(0, sample_a - sample_b)
            
            total_loss += loss
        
        return total_loss / num_samples
    
    def get_summary(self) -> dict:
        """Get summary statistics for both variants."""
        return {
            'variant_a_mean': self.variant_a.mean(),
            'variant_a_std': math.sqrt(self.variant_a.variance()),
            'variant_b_mean': self.variant_b.mean(),
            'variant_b_std': math.sqrt(self.variant_b.variance()),
        }


if __name__ == "__main__":
    print("=== Bayesian A/B Test Analyzer Demo ===\n")
    
    # Simulate an A/B test where B is slightly better
    # In reality you'd feed this real data from your experiment
    print("Simulating A/B test data...")
    print("Variant A: 850 conversions out of 10,000 visitors (8.5%)")
    print("Variant B: 920 conversions out of 10,000 visitors (9.2%)")
    print()
    
    analyzer = ABTestAnalyzer(prior_alpha=1.0, prior_beta=1.0)
    
    # Update with observed data
    analyzer.update_variant_a(conversions=850, non_conversions=9150)
    analyzer.update_variant_b(conversions=920, non_conversions=9080)
    
    # Get summary statistics
    summary = analyzer.get_summary()
    print(f"Variant A estimated rate: {summary['variant_a_mean']:.4f} ± {summary['variant_a_std']:.4f}")
    print(f"Variant B estimated rate: {summary['variant_b_mean']:.4f} ± {summary['variant_b_std']:.4f}")
    print()
    
    # Calculate probability B beats A
    prob_b_wins = analyzer.probability_b_beats_a(num_samples=20000)
    print(f"P(B > A) = {prob_b_wins:.4f}")
    print(f"P(A > B) = {1 - prob_b_wins:.4f}")
    print()
    
    # Calculate expected losses
    loss_if_choose_a = analyzer.expected_loss(choose_a=True, num_samples=20000)
    loss_if_choose_b = analyzer.expected_loss(choose_a=False, num_samples=20000)
    
    print(f"Expected loss if we choose A: {loss_if_choose_a:.6f}")
    print(f"Expected loss if we choose B: {loss_if_choose_b:.6f}")
    print()
    
    if prob_b_wins > 0.95:
        print("✓ Strong evidence that B is better. Go with B!")
    elif prob_b_wins > 0.90:
        print("→ Moderate evidence for B. Probably safe to choose B.")
    elif prob_b_wins < 0.10:
        print("✓ Strong evidence that A is better. Stick with A!")
    elif prob_b_wins < 0.05:
        print("→ Moderate evidence for A. Probably safe to choose A.")
    else:
        print("? Inconclusive. Need more data or the difference is negligible.")