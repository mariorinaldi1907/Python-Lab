"""
Date: 2026-06-13
Implemented a Bayesian A/B testing framework using conjugate priors to compare conversion rates and get actual probability statements about which variant is better.
"""

"""
Bayesian A/B Testing Module

I got tired of interpreting p-values incorrectly, so I built this to do
proper Bayesian inference on A/B tests. Uses Beta distributions as conjugate
priors for binomial data (clicks, conversions, etc).

The cool thing about Bayesian A/B testing is you get statements like
"there's a 94% chance variant B is better than A" instead of the confusing
"we reject the null at p=0.05" dance.
"""

import random
from math import gamma, exp, log


class BetaDistribution:
    """
    Represents a Beta distribution for Bayesian inference on proportions.
    
    Beta(alpha, alpha) is the conjugate prior for binomial likelihood.
    Start with Beta(1,1) for uniform prior, or use domain knowledge.
    """
    
    def __init__(self, alpha=1, beta=1):
        """
        Initialize Beta distribution.
        
        Args:
            alpha: successes + prior alpha (default 1 for uniform prior)
            beta: failures + prior beta (default 1 for uniform prior)
        """
        self.alpha = alpha
        self.beta = beta
    
    def update(self, successes, failures):
        """
        Update the distribution with observed data.
        This is where the Bayesian magic happens - just add to parameters.
        """
        self.alpha += successes
        self.beta += failures
    
    def mean(self):
        """Expected value of the distribution."""
        return self.alpha / (self.alpha + self.beta)
    
    def mode(self):
        """Most likely value (peak of the distribution)."""
        if self.alpha > 1 and self.beta > 1:
            return (self.alpha - 1) / (self.alpha + self.beta - 2)
        return self.mean()
    
    def variance(self):
        """Variance of the distribution."""
        a, b = self.alpha, self.beta
        return (a * b) / ((a + b) ** 2 * (a + b + 1))
    
    def sample(self):
        """
        Draw a random sample from this Beta distribution.
        Uses the fact that if X ~ Gamma(alpha) and Y ~ Gamma(beta),
        then X/(X+Y) ~ Beta(alpha, beta).
        """
        x = random.gammavariate(self.alpha, 1)
        y = random.gammavariate(self.beta, 1)
        return x / (x + y)
    
    def credible_interval(self, confidence=0.95):
        """
        Compute credible interval using percentiles from samples.
        Not exact but good enough for practical use.
        """
        samples = sorted([self.sample() for _ in range(10000)])
        lower_idx = int((1 - confidence) / 2 * len(samples))
        upper_idx = int((1 + confidence) / 2 * len(samples))
        return samples[lower_idx], samples[upper_idx]


class BayesianABTest:
    """
    Framework for Bayesian A/B testing with binary outcomes.
    
    Much more intuitive than traditional frequentist tests because you get
    actual probability statements about hypotheses.
    """
    
    def __init__(self, prior_alpha=1, prior_beta=1):
        """
        Initialize A/B test with priors for both variants.
        
        Args:
            prior_alpha: prior belief about successes (1 = uninformative)
            prior_beta: prior belief about failures (1 = uninformative)
        """
        self.variant_a = BetaDistribution(prior_alpha, prior_beta)
        self.variant_b = BetaDistribution(prior_alpha, prior_beta)
    
    def add_data(self, variant, successes, trials):
        """
        Add observed data to a variant.
        
        Args:
            variant: 'A' or 'B'
            successes: number of conversions/clicks/etc
            trials: total number of attempts
        """
        failures = trials - successes
        if variant.upper() == 'A':
            self.variant_a.update(successes, failures)
        elif variant.upper() == 'B':
            self.variant_b.update(successes, failures)
        else:
            raise ValueError("Variant must be 'A' or 'B'")
    
    def probability_b_beats_a(self, n_samples=50000):
        """
        Calculate P(B > A) using Monte Carlo sampling.
        
        This is the key metric: "What's the probability that variant B
        actually has a higher conversion rate than A?"
        
        Returns:
            Probability that B's true rate is higher than A's
        """
        b_wins = sum(
            self.variant_b.sample() > self.variant_a.sample()
            for _ in range(n_samples)
        )
        return b_wins / n_samples
    
    def expected_loss(self, choose_b=True, n_samples=50000):
        """
        Expected loss if we choose the wrong variant.
        
        If we pick B but A is actually better, how much conversion rate
        do we lose on average? Useful for risk assessment.
        """
        losses = []
        for _ in range(n_samples):
            a_sample = self.variant_a.sample()
            b_sample = self.variant_b.sample()
            
            if choose_b:
                # If we choose B, loss is max(0, A - B)
                losses.append(max(0, a_sample - b_sample))
            else:
                # If we choose A, loss is max(0, B - A)
                losses.append(max(0, b_sample - a_sample))
        
        return sum(losses) / len(losses)
    
    def summary(self):
        """Print a comprehensive summary of the A/B test results."""
        print("=" * 60)
        print("Bayesian A/B Test Summary")
        print("=" * 60)
        
        print(f"\nVariant A:")
        print(f"  Mean conversion rate: {self.variant_a.mean():.4f}")
        ci_a = self.variant_a.credible_interval()
        print(f"  95% Credible Interval: [{ci_a[0]:.4f}, {ci_a[1]:.4f}]")
        
        print(f"\nVariant B:")
        print(f"  Mean conversion rate: {self.variant_b.mean():.4f}")
        ci_b = self.variant_b.credible_interval()
        print(f"  95% Credible Interval: [{ci_b[0]:.4f}, {ci_b[1]:.4f}]")
        
        prob_b_wins = self.probability_b_beats_a()
        print(f"\nP(B > A) = {prob_b_wins:.4f}")
        print(f"P(A > B) = {1 - prob_b_wins:.4f}")
        
        loss_if_choose_b = self.expected_loss(choose_b=True)
        loss_if_choose_a = self.expected_loss(choose_b=False)
        print(f"\nExpected loss if we choose B: {loss_if_choose_b:.6f}")
        print(f"Expected loss if we choose A: {loss_if_choose_a:.6f}")
        
        # Decision guidance
        print("\n" + "=" * 60)
        if prob_b_wins > 0.95:
            print("RECOMMENDATION: Strong evidence for B. Ship it!")
        elif prob_b_wins > 0.90:
            print("RECOMMENDATION: Good evidence for B. Probably safe to ship.")
        elif prob_b_wins < 0.05:
            print("RECOMMENDATION: Strong evidence for A. Stick with it.")
        elif prob_b_wins < 0.10:
            print("RECOMMENDATION: Good evidence for A. Keep the original.")
        else:
            print("RECOMMENDATION: Inconclusive. Need more data or doesn't matter much.")
        print("=" * 60)


if __name__ == "__main__":
    # Simulate an A/B test on a landing page
    # Let's say we're testing a new call-to-action button
    
    print("Simulating A/B Test: Original vs New CTA Button\n")
    
    # Create the test with uninformative priors
    test = BayesianABTest(prior_alpha=1, prior_beta=1)
    
    # Variant A (original): 1250 visitors, 85 conversions
    # That's about 6.8% conversion rate
    test.add_data('A', successes=85, trials=1250)
    
    # Variant B (new button): 1190 visitors, 98 conversions
    # That's about 8.2% conversion rate - looks promising!
    test.add_data('B', successes=98, trials=1190)
    
    # Show the full analysis
    test.summary()
    
    print("\n\nQuick example with even stronger evidence:")
    test2 = BayesianABTest()
    test2.add_data('A', successes=200, trials=5000)  # 4% conversion
    test2.add_data('B', successes=350, trials=5000)  # 7% conversion
    test2.summary()