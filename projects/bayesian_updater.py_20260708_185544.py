"""
Date: 2026-07-08
Wrote a Bayesian inference tool using beta-binomial conjugate pairs to update beliefs from data, mostly because I wanted to analyze conversion rates properly.
"""

"""
Bayesian Updater using Beta-Binomial Conjugate Prior

I built this because I got tired of classical A/B testing not telling me
what I actually wanted to know — the probability that variant B is better.
Beta distribution is perfect for modeling click-through rates and conversions.
"""

import math
from typing import Tuple, List


def beta_pdf(x: float, alpha: float, beta: float) -> float:
    """
    Compute the probability density function of Beta distribution.
    
    Using the formula: f(x; α, β) = x^(α-1) * (1-x)^(β-1) / B(α, β)
    where B is the beta function (ratio of gamma functions).
    """
    if x <= 0 or x >= 1:
        return 0.0
    
    # Using log-space to avoid numerical overflow
    log_pdf = (alpha - 1) * math.log(x) + (beta - 1) * math.log(1 - x)
    log_pdf -= math.lgamma(alpha) + math.lgamma(beta) - math.lgamma(alpha + beta)
    return math.exp(log_pdf)


class BayesianUpdater:
    """
    Beta-Binomial Bayesian updater for binary outcomes (success/failure).
    
    The beta distribution is a conjugate prior for the binomial likelihood,
    which means posterior is also beta-distributed. This makes updates clean.
    """
    
    def __init__(self, prior_alpha: float = 1.0, prior_beta: float = 1.0):
        """
        Initialize with a prior Beta distribution.
        
        α=1, β=1 gives a uniform prior (no initial bias).
        Higher values represent stronger prior beliefs.
        """
        self.alpha = prior_alpha
        self.beta = prior_beta
        self.total_successes = 0
        self.total_trials = 0
    
    def update(self, successes: int, failures: int) -> None:
        """
        Update beliefs with new data (Bayesian learning).
        
        The beauty of conjugate priors: just add successes to α and failures to β.
        """
        self.alpha += successes
        self.beta += failures
        self.total_successes += successes
        self.total_trials += successes + failures
    
    def mean(self) -> float:
        """Expected value of the posterior distribution."""
        return self.alpha / (self.alpha + self.beta)
    
    def mode(self) -> float:
        """Most likely value (peak of the distribution)."""
        if self.alpha > 1 and self.beta > 1:
            return (self.alpha - 1) / (self.alpha + self.beta - 2)
        return self.mean()  # Fallback for edge cases
    
    def variance(self) -> float:
        """Variance of the posterior distribution."""
        a_plus_b = self.alpha + self.beta
        return (self.alpha * self.beta) / (a_plus_b ** 2 * (a_plus_b + 1))
    
    def credible_interval(self, confidence: float = 0.95) -> Tuple[float, float]:
        """
        Compute credible interval (Bayesian confidence interval).
        
        This is different from frequentist CI — it actually means there's
        a 95% probability the true parameter is in this range.
        """
        from math import isclose
        
        lower_tail = (1 - confidence) / 2
        upper_tail = 1 - lower_tail
        
        # Use numerical approximation for inverse CDF
        # Beta quantile function doesn't exist in stdlib, so we do binary search
        lower = self._inverse_cdf(lower_tail)
        upper = self._inverse_cdf(upper_tail)
        
        return (lower, upper)
    
    def _inverse_cdf(self, p: float, tolerance: float = 1e-6) -> float:
        """
        Find x such that CDF(x) = p using binary search.
        
        I know scipy has this built-in, but that's not in stdlib.
        Binary search converges fast enough for practical use.
        """
        low, high = 0.0, 1.0
        
        while high - low > tolerance:
            mid = (low + high) / 2
            if self._cdf(mid) < p:
                low = mid
            else:
                high = mid
        
        return (low + high) / 2
    
    def _cdf(self, x: float) -> float:
        """
        Cumulative distribution function (integral of PDF from 0 to x).
        
        Using the regularized incomplete beta function approximation.
        This isn't perfect but good enough for most practical cases.
        """
        if x <= 0:
            return 0.0
        if x >= 1:
            return 1.0
        
        # Approximate using numerical integration (trapezoidal rule)
        steps = 100
        dx = x / steps
        integral = 0.0
        
        for i in range(steps):
            x0 = i * dx
            x1 = (i + 1) * dx
            integral += (beta_pdf(x0, self.alpha, self.beta) + 
                        beta_pdf(x1, self.alpha, self.beta)) * dx / 2
        
        return integral
    
    def probability_better_than(self, threshold: float) -> float:
        """
        Probability that true parameter exceeds threshold.
        
        This answers questions like "what's the probability our conversion
        rate is actually above 10%?" — super useful for decision making.
        """
        return 1 - self._cdf(threshold)
    
    def __repr__(self) -> str:
        return (f"BayesianUpdater(α={self.alpha:.2f}, β={self.beta:.2f}, "
                f"mean={self.mean():.4f}, trials={self.total_trials})")


def compare_variants(variant_a: BayesianUpdater, 
                     variant_b: BayesianUpdater, 
                     samples: int = 10000) -> float:
    """
    Estimate probability that variant B is better than A using Monte Carlo.
    
    We sample from both posterior distributions and count how often B > A.
    This is way more intuitive than p-values for A/B testing.
    """
    import random
    
    b_wins = 0
    
    for _ in range(samples):
        # Sample from beta distributions using acceptance-rejection
        sample_a = random.betavariate(variant_a.alpha, variant_a.beta)
        sample_b = random.betavariate(variant_b.alpha, variant_b.beta)
        
        if sample_b > sample_a:
            b_wins += 1
    
    return b_wins / samples


if __name__ == "__main__":
    print("=== Bayesian A/B Test Analysis ===\n")
    
    # Scenario: testing two landing page variants
    variant_a = BayesianUpdater(prior_alpha=1, prior_beta=1)
    variant_b = BayesianUpdater(prior_alpha=1, prior_beta=1)
    
    # Variant A: 120 conversions out of 1000 visitors
    variant_a.update(successes=120, failures=880)
    
    # Variant B: 145 conversions out of 1000 visitors
    variant_b.update(successes=145, failures=855)
    
    print(f"Variant A: {variant_a}")
    print(f"  Conversion rate estimate: {variant_a.mean():.2%}")
    print(f"  95% credible interval: {variant_a.credible_interval()}")
    print(f"  Prob > 10%: {variant_a.probability_better_than(0.10):.2%}\n")
    
    print(f"Variant B: {variant_b}")
    print(f"  Conversion rate estimate: {variant_b.mean():.2%}")
    print(f"  95% credible interval: {variant_b.credible_interval()}")
    print(f"  Prob > 10%: {variant_b.probability_better_than(0.10):.2%}\n")
    
    prob_b_better = compare_variants(variant_a, variant_b)
    print(f"Probability that B beats A: {prob_b_better:.2%}")
    
    if prob_b_better > 0.95:
        print("✓ Strong evidence that B is better — ship it!")
    elif prob_b_better > 0.80:
        print("→ Moderate evidence for B — maybe collect more data")
    else:
        print("✗ Not enough evidence — keep testing or stick with A")