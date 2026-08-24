"""
Date: 2026-08-24
Implemented a Bayesian A/B testing framework using conjugate priors to compare conversion rates and make actual probability statements about which variant is better.
"""

"""
Bayesian A/B Testing Module

I got tired of dealing with p-values and confidence intervals that nobody
understands correctly. This module uses Beta-Binomial conjugate priors to
do A/B testing the Bayesian way — you get actual probability statements
like "there's a 94% chance variant B is better than A."
"""

import random
import math
from collections import namedtuple


TestResult = namedtuple('TestResult', ['prob_b_beats_a', 'expected_loss_a', 'expected_loss_b'])


class BayesianABTest:
    """
    A/B test using Beta-Binomial conjugate priors.
    
    The Beta distribution is the conjugate prior for the Binomial likelihood,
    which makes the math clean. We start with a uniform prior (Beta(1,1))
    and update it with observed data.
    """
    
    def __init__(self, alpha_prior=1, beta_prior=1):
        """
        Initialize the A/B test with prior beliefs.
        
        Args:
            alpha_prior: Prior successes (default 1 = uniform prior)
            beta_prior: Prior failures (default 1 = uniform prior)
        """
        # Variant A
        self.alpha_a = alpha_prior
        self.beta_a = beta_prior
        
        # Variant B
        self.alpha_b = alpha_prior
        self.beta_b = beta_prior
    
    def update_variant_a(self, successes, trials):
        """Update variant A with observed data."""
        failures = trials - successes
        self.alpha_a += successes
        self.beta_a += failures
    
    def update_variant_b(self, successes, trials):
        """Update variant B with observed data."""
        failures = trials - successes
        self.alpha_b += successes
        self.beta_b += failures
    
    def sample_beta(self, alpha, beta, n_samples=10000):
        """
        Draw samples from a Beta distribution.
        
        Using the fact that if X ~ Gamma(alpha, 1) and Y ~ Gamma(beta, 1),
        then X/(X+Y) ~ Beta(alpha, beta). This avoids needing scipy.
        """
        samples = []
        for _ in range(n_samples):
            x = self._sample_gamma(alpha)
            y = self._sample_gamma(beta)
            samples.append(x / (x + y))
        return samples
    
    def _sample_gamma(self, shape):
        """
        Sample from Gamma distribution using Marsaglia and Tsang's method.
        
        This is a standard algorithm for gamma sampling. For small shapes
        we use a simpler method to avoid numerical issues.
        """
        if shape < 1:
            # Use the transformation Gamma(a) = Gamma(a+1) * U^(1/a)
            return self._sample_gamma(shape + 1) * random.random() ** (1.0 / shape)
        
        # Marsaglia and Tsang's method for shape >= 1
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
    
    def get_probability_b_beats_a(self, n_samples=10000):
        """
        Calculate the probability that variant B has a higher conversion rate than A.
        
        We do this by sampling from both posteriors and counting how often B > A.
        """
        samples_a = self.sample_beta(self.alpha_a, self.beta_a, n_samples)
        samples_b = self.sample_beta(self.alpha_b, self.beta_b, n_samples)
        
        wins = sum(1 for sa, sb in zip(samples_a, samples_b) if sb > sa)
        return wins / n_samples
    
    def get_expected_loss(self, n_samples=10000):
        """
        Calculate expected loss for choosing each variant.
        
        Expected loss is how much conversion rate we'd lose on average if we
        choose the wrong variant. Lower is better.
        """
        samples_a = self.sample_beta(self.alpha_a, self.beta_a, n_samples)
        samples_b = self.sample_beta(self.alpha_b, self.beta_b, n_samples)
        
        # Loss if we choose A: how much better B could have been
        loss_a = sum(max(0, sb - sa) for sa, sb in zip(samples_a, samples_b)) / n_samples
        
        # Loss if we choose B: how much better A could have been
        loss_b = sum(max(0, sa - sb) for sa, sb in zip(samples_a, samples_b)) / n_samples
        
        return loss_a, loss_b
    
    def analyze(self, n_samples=10000):
        """
        Run full analysis and return results.
        
        Returns a TestResult with probability B beats A and expected losses.
        """
        prob_b_beats_a = self.get_probability_b_beats_a(n_samples)
        loss_a, loss_b = self.get_expected_loss(n_samples)
        
        return TestResult(
            prob_b_beats_a=prob_b_beats_a,
            expected_loss_a=loss_a,
            expected_loss_b=loss_b
        )
    
    def get_credible_interval(self, variant='a', confidence=0.95, n_samples=10000):
        """Get a credible interval for the conversion rate."""
        if variant == 'a':
            samples = self.sample_beta(self.alpha_a, self.beta_a, n_samples)
        else:
            samples = self.sample_beta(self.alpha_b, self.beta_b, n_samples)
        
        samples.sort()
        lower_idx = int((1 - confidence) / 2 * n_samples)
        upper_idx = int((1 + confidence) / 2 * n_samples)
        
        return samples[lower_idx], samples[upper_idx]


if __name__ == "__main__":
    print("=== Bayesian A/B Test Demo ===\n")
    
    # Simulate a real A/B test scenario
    print("Scenario: Testing two landing page variants")
    print("-" * 50)
    
    test = BayesianABTest()
    
    # Variant A: 120 conversions out of 1000 visitors (12% conversion)
    test.update_variant_a(successes=120, trials=1000)
    print("Variant A: 120 conversions / 1000 visitors (12.0%)")
    
    # Variant B: 145 conversions out of 1000 visitors (14.5% conversion)
    test.update_variant_b(successes=145, trials=1000)
    print("Variant B: 145 conversions / 1000 visitors (14.5%)")
    print()
    
    # Run the analysis
    result = test.analyze(n_samples=50000)
    
    print("Analysis Results:")
    print("-" * 50)
    print(f"Probability B beats A: {result.prob_b_beats_a:.1%}")
    print(f"Expected loss if we choose A: {result.expected_loss_a:.4f}")
    print(f"Expected loss if we choose B: {result.expected_loss_b:.4f}")
    print()
    
    # Show credible intervals
    ci_a = test.get_credible_interval('a', confidence=0.95)
    ci_b = test.get_credible_interval('b', confidence=0.95)
    
    print("95% Credible Intervals:")
    print(f"  Variant A: [{ci_a[0]:.1%}, {ci_a[1]:.1%}]")
    print(f"  Variant B: [{ci_b[0]:.1%}, {ci_b[1]:.1%}]")
    print()
    
    # Decision recommendation
    if result.prob_b_beats_a > 0.95:
        print("✓ Recommendation: Choose variant B (high confidence)")
    elif result.prob_b_beats_a < 0.05:
        print("✓ Recommendation: Choose variant A (high confidence)")
    else:
        print("⚠ Recommendation: Keep testing, not enough evidence yet")