"""
Date: 2026-05-29
Implemented a Bayesian A/B testing tool using conjugate priors because I wanted to actually understand what "probability of being better" means instead of just staring at p-values.
"""

#!/usr/bin/env python3
"""
Bayesian A/B Test Analyzer
Compares two variants using Beta-Binomial conjugate priors.
"""

import random
import math
from typing import Tuple, List


class BayesianABTest:
    """
    Analyzes A/B test results using Bayesian inference with Beta distributions.
    
    Uses Beta(alpha, beta) as conjugate prior for binomial likelihood.
    Each variant maintains its own posterior distribution.
    """
    
    def __init__(self, prior_alpha: float = 1.0, prior_beta: float = 1.0):
        """
        Initialize with uniform prior (default) or custom prior beliefs.
        
        Args:
            prior_alpha: Prior successes + 1 (alpha parameter)
            prior_beta: Prior failures + 1 (beta parameter)
        """
        self.prior_alpha = prior_alpha
        self.prior_beta = prior_beta
        
        # Variant A
        self.alpha_a = prior_alpha
        self.beta_a = prior_beta
        
        # Variant B
        self.alpha_b = prior_alpha
        self.beta_b = prior_beta
    
    def update(self, variant: str, successes: int, failures: int):
        """
        Update posterior distribution with observed data.
        
        Args:
            variant: 'A' or 'B'
            successes: Number of conversions/successes
            failures: Number of non-conversions/failures
        """
        if variant.upper() == 'A':
            self.alpha_a += successes
            self.beta_a += failures
        elif variant.upper() == 'B':
            self.alpha_b += successes
            self.beta_b += failures
        else:
            raise ValueError("Variant must be 'A' or 'B'")
    
    def get_posterior_mean(self, variant: str) -> float:
        """Calculate posterior mean (expected conversion rate)."""
        if variant.upper() == 'A':
            return self.alpha_a / (self.alpha_a + self.beta_a)
        else:
            return self.alpha_b / (self.alpha_b + self.beta_b)
    
    def get_posterior_variance(self, variant: str) -> float:
        """Calculate posterior variance."""
        if variant.upper() == 'A':
            a, b = self.alpha_a, self.beta_a
        else:
            a, b = self.alpha_b, self.beta_b
        
        return (a * b) / ((a + b) ** 2 * (a + b + 1))
    
    def get_credible_interval(self, variant: str, confidence: float = 0.95) -> Tuple[float, float]:
        """
        Calculate credible interval using quantile function approximation.
        
        This is a rough approximation using normal approximation to Beta.
        For production, you'd want scipy or numerical integration.
        """
        mean = self.get_posterior_mean(variant)
        std = math.sqrt(self.get_posterior_variance(variant))
        
        # Z-score for confidence level (approximate)
        z = 1.96 if confidence == 0.95 else 2.576  # 95% or 99%
        
        lower = max(0, mean - z * std)
        upper = min(1, mean + z * std)
        
        return (lower, upper)
    
    def sample_posterior(self, variant: str, n_samples: int = 10000) -> List[float]:
        """
        Sample from posterior Beta distribution using inverse transform sampling.
        
        This is educational — normally you'd use numpy's beta.rvs().
        """
        if variant.upper() == 'A':
            alpha, beta = self.alpha_a, self.beta_a
        else:
            alpha, beta = self.alpha_b, self.beta_b
        
        samples = []
        for _ in range(n_samples):
            # Generate Beta samples using Gamma ratio trick
            # Beta(a,b) = Gamma(a,1) / (Gamma(a,1) + Gamma(b,1))
            u = self._sample_gamma(alpha)
            v = self._sample_gamma(beta)
            samples.append(u / (u + v))
        
        return samples
    
    def _sample_gamma(self, shape: float) -> float:
        """
        Sample from Gamma distribution using Marsaglia and Tsang method.
        Scale parameter is 1 for our use case.
        """
        if shape < 1:
            # Use shape augmentation for shape < 1
            return self._sample_gamma(shape + 1) * (random.random() ** (1.0 / shape))
        
        d = shape - 1.0 / 3.0
        c = 1.0 / math.sqrt(9.0 * d)
        
        while True:
            x = random.gauss(0, 1)
            v = (1.0 + c * x) ** 3
            
            if v <= 0:
                continue
            
            u = random.random()
            if u < 1 - 0.0331 * x ** 4:
                return d * v
            
            if math.log(u) < 0.5 * x ** 2 + d * (1 - v + math.log(v)):
                return d * v
    
    def probability_b_better_than_a(self, n_samples: int = 10000) -> float:
        """
        Calculate P(conversion_rate_B > conversion_rate_A).
        
        This is the key Bayesian metric — direct probability statement.
        """
        samples_a = self.sample_posterior('A', n_samples)
        samples_b = self.sample_posterior('B', n_samples)
        
        wins = sum(1 for a, b in zip(samples_a, samples_b) if b > a)
        return wins / n_samples


if __name__ == "__main__":
    print("=== Bayesian A/B Test Analyzer ===\n")
    
    # Simulate an A/B test scenario
    # Variant A: 120 conversions out of 1000 visitors (12%)
    # Variant B: 145 conversions out of 1000 visitors (14.5%)
    
    test = BayesianABTest(prior_alpha=1, prior_beta=1)  # Uniform prior
    
    # Add observed data
    test.update('A', successes=120, failures=880)
    test.update('B', successes=145, failures=855)
    
    print("Observed Data:")
    print(f"  Variant A: 120/1000 conversions (12.0%)")
    print(f"  Variant B: 145/1000 conversions (14.5%)")
    print()
    
    # Posterior analysis
    print("Posterior Estimates:")
    mean_a = test.get_posterior_mean('A')
    mean_b = test.get_posterior_mean('B')
    print(f"  Variant A mean: {mean_a:.4f}")
    print(f"  Variant B mean: {mean_b:.4f}")
    print()
    
    ci_a = test.get_credible_interval('A', confidence=0.95)
    ci_b = test.get_credible_interval('B', confidence=0.95)
    print("95% Credible Intervals:")
    print(f"  Variant A: [{ci_a[0]:.4f}, {ci_a[1]:.4f}]")
    print(f"  Variant B: [{ci_b[0]:.4f}, {ci_b[1]:.4f}]")
    print()
    
    # The money question
    prob_b_wins = test.probability_b_better_than_a(n_samples=50000)
    print(f"Probability B is better than A: {prob_b_wins:.2%}")
    print()
    
    if prob_b_wins > 0.95:
        print("✓ Strong evidence for B (>95% probability)")
    elif prob_b_wins > 0.90:
        print("→ Moderate evidence for B (>90% probability)")
    else:
        print("⚠ Inconclusive — need more data or B isn't actually better")
    
    print("\n" + "="*50)
    print("This beats p-values because we get a direct probability")
    print("that B is better, not 'probability of data given no effect'.")