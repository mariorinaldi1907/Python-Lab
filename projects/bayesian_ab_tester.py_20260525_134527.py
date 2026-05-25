"""
Date: 2026-05-25
Implemented a Bayesian A/B testing framework using conjugate priors to compare conversion rates and calculate probability of superiority.
"""

#!/usr/bin/env python3
"""
Bayesian A/B Testing Module

Uses Beta-Binomial conjugate priors to analyze A/B test results.
Way more intuitive than p-values — just tells you the probability
that variant B beats variant A.
"""

import random
from math import gamma, log, exp


class BetaDistribution:
    """
    Represents a Beta distribution for Bayesian inference on proportions.
    
    Beta(alpha, beta) is the conjugate prior for the Binomial likelihood.
    """
    
    def __init__(self, alpha=1.0, beta=1.0):
        """
        Initialize Beta distribution.
        
        Args:
            alpha: Success count + prior (default 1 = uniform prior)
            beta: Failure count + prior (default 1 = uniform prior)
        """
        self.alpha = alpha
        self.beta = beta
    
    def update(self, successes, failures):
        """
        Update the distribution with observed data (Bayesian updating).
        
        Args:
            successes: Number of conversions/successes
            failures: Number of non-conversions/failures
        """
        self.alpha += successes
        self.beta += failures
    
    def mean(self):
        """Expected value of the distribution."""
        return self.alpha / (self.alpha + self.beta)
    
    def mode(self):
        """Most likely value (only valid if alpha, beta > 1)."""
        if self.alpha > 1 and self.beta > 1:
            return (self.alpha - 1) / (self.alpha + self.beta - 2)
        return self.mean()
    
    def variance(self):
        """Variance of the distribution."""
        a_plus_b = self.alpha + self.beta
        return (self.alpha * self.beta) / (a_plus_b**2 * (a_plus_b + 1))
    
    def sample(self):
        """
        Generate a random sample from this Beta distribution.
        
        Uses the fact that if X ~ Gamma(alpha) and Y ~ Gamma(beta),
        then X/(X+Y) ~ Beta(alpha, beta).
        """
        x = random.gammavariate(self.alpha, 1.0)
        y = random.gammavariate(self.beta, 1.0)
        return x / (x + y)


class ABTest:
    """
    Bayesian A/B test analyzer for conversion rate experiments.
    """
    
    def __init__(self, prior_alpha=1.0, prior_beta=1.0):
        """
        Initialize an A/B test with specified priors.
        
        Args:
            prior_alpha: Prior belief parameter (alpha)
            prior_beta: Prior belief parameter (beta)
            
        Using uniform prior (1, 1) by default = no prior knowledge.
        """
        self.variant_a = BetaDistribution(prior_alpha, prior_beta)
        self.variant_b = BetaDistribution(prior_alpha, prior_beta)
    
    def add_data(self, variant, conversions, total):
        """
        Add observed data for a variant.
        
        Args:
            variant: 'A' or 'B'
            conversions: Number of successful conversions
            total: Total number of trials/visitors
        """
        failures = total - conversions
        
        if variant.upper() == 'A':
            self.variant_a.update(conversions, failures)
        elif variant.upper() == 'B':
            self.variant_b.update(conversions, failures)
        else:
            raise ValueError("variant must be 'A' or 'B'")
    
    def probability_b_beats_a(self, num_samples=10000):
        """
        Calculate P(B > A) using Monte Carlo sampling.
        
        This is the key metric: what's the probability that variant B
        has a higher conversion rate than variant A?
        
        Args:
            num_samples: Number of Monte Carlo samples to draw
            
        Returns:
            Probability that B's true rate exceeds A's true rate
        """
        b_wins = 0
        
        for _ in range(num_samples):
            sample_a = self.variant_a.sample()
            sample_b = self.variant_b.sample()
            if sample_b > sample_a:
                b_wins += 1
        
        return b_wins / num_samples
    
    def expected_loss(self, variant, num_samples=10000):
        """
        Calculate expected loss if we choose the given variant.
        
        Expected loss = expected difference in conversion rate if we
        choose the wrong variant. Useful for decision-making.
        
        Args:
            variant: 'A' or 'B'
            num_samples: Number of Monte Carlo samples
            
        Returns:
            Expected loss (always non-negative)
        """
        losses = []
        
        for _ in range(num_samples):
            sample_a = self.variant_a.sample()
            sample_b = self.variant_b.sample()
            
            if variant.upper() == 'A':
                # If we choose A but B is better, we lose (B - A)
                loss = max(0, sample_b - sample_a)
            else:
                # If we choose B but A is better, we lose (A - B)
                loss = max(0, sample_a - sample_b)
            
            losses.append(loss)
        
        return sum(losses) / len(losses)
    
    def summary(self):
        """Print a summary of the test results."""
        print("=" * 60)
        print("Bayesian A/B Test Summary")
        print("=" * 60)
        print(f"Variant A: {self.variant_a.alpha - 1:.0f} conversions, "
              f"{self.variant_a.beta - 1:.0f} failures")
        print(f"  → Estimated rate: {self.variant_a.mean():.4f}")
        print(f"  → 95% credible interval: ~[{self.variant_a.mean() - 1.96 * self.variant_a.variance()**0.5:.4f}, "
              f"{self.variant_a.mean() + 1.96 * self.variant_a.variance()**0.5:.4f}]")
        
        print(f"\nVariant B: {self.variant_b.alpha - 1:.0f} conversions, "
              f"{self.variant_b.beta - 1:.0f} failures")
        print(f"  → Estimated rate: {self.variant_b.mean():.4f}")
        print(f"  → 95% credible interval: ~[{self.variant_b.mean() - 1.96 * self.variant_b.variance()**0.5:.4f}, "
              f"{self.variant_b.mean() + 1.96 * self.variant_b.variance()**0.5:.4f}]")
        
        prob_b_wins = self.probability_b_beats_a()
        print(f"\n{'='*60}")
        print(f"P(B > A) = {prob_b_wins:.2%}")
        
        loss_a = self.expected_loss('A')
        loss_b = self.expected_loss('B')
        print(f"\nExpected loss if choosing A: {loss_a:.4f}")
        print(f"Expected loss if choosing B: {loss_b:.4f}")
        
        # Decision recommendation
        if prob_b_wins > 0.95:
            print("\n✓ Strong evidence for B — I'd ship it.")
        elif prob_b_wins < 0.05:
            print("\n✓ Strong evidence for A — stick with it.")
        else:
            print("\n⚠ Results inconclusive — might need more data.")


if __name__ == "__main__":
    # Simulate a realistic A/B test scenario
    print("Running a simulated A/B test...\n")
    
    # Scenario: testing a new checkout button design
    test = ABTest(prior_alpha=1, prior_beta=1)
    
    # Variant A (control): 120 conversions out of 1000 visitors
    test.add_data('A', conversions=120, total=1000)
    
    # Variant B (new design): 145 conversions out of 1000 visitors
    test.add_data('B', conversions=145, total=1000)
    
    test.summary()
    
    print("\n" + "="*60)
    print("Why I like this approach:")
    print("  • No p-value confusion — just direct probability statements")
    print("  • Can peek at results anytime without 'p-hacking' issues")
    print("  • Expected loss helps make actual business decisions")
    print("="*60)