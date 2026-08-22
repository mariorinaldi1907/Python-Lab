"""
Date: 2026-08-22
Implemented a Bayesian A/B testing tool with Beta distributions to get actual probabilities instead of confusing p-values — includes credible intervals and probability of superiority.
"""

#!/usr/bin/env python3
"""
Bayesian A/B Test Analyzer
Simple tool for analyzing A/B test results using Bayesian inference.
Uses Beta-Binomial conjugate prior because the math is clean and interpretable.
"""

import random
import math
from typing import Tuple, Dict


class BayesianABTest:
    """
    Bayesian A/B test analyzer using Beta distributions.
    
    Beta distribution is perfect for conversion rates because:
    - Domain is [0, 1] which matches probabilities
    - Conjugate prior to binomial, so updates are trivial
    - Intuitive parameters: alpha=successes+1, beta=failures+1
    """
    
    def __init__(self, alpha_prior: float = 1.0, beta_prior: float = 1.0):
        """
        Initialize with prior beliefs.
        
        Args:
            alpha_prior: Prior successes + 1 (uniform prior uses 1)
            beta_prior: Prior failures + 1 (uniform prior uses 1)
        """
        self.alpha_prior = alpha_prior
        self.beta_prior = beta_prior
    
    def update_posterior(self, successes: int, failures: int) -> Tuple[float, float]:
        """
        Update Beta distribution with observed data.
        
        This is why Bayesian methods rock - just add the counts.
        No complicated likelihood functions needed.
        """
        alpha_post = self.alpha_prior + successes
        beta_post = self.beta_prior + failures
        return alpha_post, beta_post
    
    def beta_mean(self, alpha: float, beta: float) -> float:
        """Mean of Beta(alpha, beta) distribution."""
        return alpha / (alpha + beta)
    
    def beta_variance(self, alpha: float, beta: float) -> float:
        """Variance of Beta(alpha, beta) distribution."""
        denom = (alpha + beta) ** 2 * (alpha + beta + 1)
        return (alpha * beta) / denom
    
    def credible_interval(self, alpha: float, beta: float, 
                         confidence: float = 0.95) -> Tuple[float, float]:
        """
        Calculate credible interval using quantile approximation.
        
        Using normal approximation for simplicity. For small sample sizes,
        you'd want to use the actual Beta quantile function, but this works
        fine for reasonable data sizes.
        """
        mean = self.beta_mean(alpha, beta)
        std = math.sqrt(self.beta_variance(alpha, beta))
        
        # Z-score for confidence level (1.96 for 95%)
        z = 1.96 if abs(confidence - 0.95) < 0.01 else 2.576
        
        lower = max(0, mean - z * std)
        upper = min(1, mean + z * std)
        return lower, upper
    
    def probability_b_beats_a(self, alpha_a: float, beta_a: float,
                             alpha_b: float, beta_b: float,
                             samples: int = 10000) -> float:
        """
        Calculate P(B > A) using Monte Carlo sampling.
        
        This is the money question: "What's the probability that variant B
        is actually better than A?" Can't get this from frequentist methods.
        """
        wins = 0
        for _ in range(samples):
            # Sample from both posteriors
            sample_a = self._beta_sample(alpha_a, beta_a)
            sample_b = self._beta_sample(alpha_b, beta_b)
            if sample_b > sample_a:
                wins += 1
        
        return wins / samples
    
    def _beta_sample(self, alpha: float, beta: float) -> float:
        """
        Sample from Beta distribution using gamma relationship.
        
        Beta(α,β) = Gamma(α,1) / (Gamma(α,1) + Gamma(β,1))
        Standard library has gammavariate, so we use this trick.
        """
        x = random.gammavariate(alpha, 1)
        y = random.gammavariate(beta, 1)
        return x / (x + y)
    
    def analyze(self, conversions_a: int, trials_a: int,
               conversions_b: int, trials_b: int) -> Dict:
        """
        Full analysis of A/B test results.
        
        Returns all the stats you actually care about in one shot.
        """
        failures_a = trials_a - conversions_a
        failures_b = trials_b - conversions_b
        
        alpha_a, beta_a = self.update_posterior(conversions_a, failures_a)
        alpha_b, beta_b = self.update_posterior(conversions_b, failures_b)
        
        return {
            'variant_a': {
                'conversion_rate': self.beta_mean(alpha_a, beta_a),
                'credible_interval': self.credible_interval(alpha_a, beta_a),
            },
            'variant_b': {
                'conversion_rate': self.beta_mean(alpha_b, beta_b),
                'credible_interval': self.credible_interval(alpha_b, beta_b),
            },
            'prob_b_beats_a': self.probability_b_beats_a(alpha_a, beta_a, 
                                                         alpha_b, beta_b),
        }


def format_percent(value: float) -> str:
    """Format as percentage with 2 decimal places."""
    return f"{value * 100:.2f}%"


if __name__ == "__main__":
    print("=" * 60)
    print("Bayesian A/B Test Analyzer")
    print("=" * 60)
    
    # Simulate a real A/B test scenario
    # Variant A: Control, 850 conversions out of 10,000 visitors
    # Variant B: New design, 920 conversions out of 10,000 visitors
    
    conversions_a = 850
    trials_a = 10000
    
    conversions_b = 920
    trials_b = 10000
    
    print(f"\nTest Data:")
    print(f"  Variant A: {conversions_a}/{trials_a} conversions "
          f"({format_percent(conversions_a/trials_a)})")
    print(f"  Variant B: {conversions_b}/{trials_b} conversions "
          f"({format_percent(conversions_b/trials_b)})")
    
    # Run the analysis
    tester = BayesianABTest()
    results = tester.analyze(conversions_a, trials_a, conversions_b, trials_b)
    
    print(f"\n{'Posterior Analysis':^60}")
    print("-" * 60)
    
    # Variant A results
    a_rate = results['variant_a']['conversion_rate']
    a_ci = results['variant_a']['credible_interval']
    print(f"\nVariant A:")
    print(f"  Estimated conversion rate: {format_percent(a_rate)}")
    print(f"  95% credible interval: [{format_percent(a_ci[0])}, "
          f"{format_percent(a_ci[1])}]")
    
    # Variant B results
    b_rate = results['variant_b']['conversion_rate']
    b_ci = results['variant_b']['credible_interval']
    print(f"\nVariant B:")
    print(f"  Estimated conversion rate: {format_percent(b_rate)}")
    print(f"  95% credible interval: [{format_percent(b_ci[0])}, "
          f"{format_percent(b_ci[1])}]")
    
    # The key metric
    prob_b_wins = results['prob_b_beats_a']
    print(f"\n{'Decision Metrics':^60}")
    print("-" * 60)
    print(f"Probability B beats A: {format_percent(prob_b_wins)}")
    
    # Interpretation
    if prob_b_wins > 0.95:
        decision = "Strong evidence for B — ship it!"
    elif prob_b_wins > 0.90:
        decision = "Moderate evidence for B — probably safe to ship"
    elif prob_b_wins < 0.05:
        decision = "Strong evidence for A — keep the original"
    else:
        decision = "Inconclusive — need more data or the difference is tiny"
    
    print(f"Recommendation: {decision}")
    
    print("\n" + "=" * 60)
    print("This beats p-values because you get actual probability of success,")
    print("not 'probability of seeing this data if there's no effect' nonsense.")
    print("=" * 60)