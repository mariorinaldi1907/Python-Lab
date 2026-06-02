"""
Date: 2026-06-02
Implemented bootstrap resampling with configurable CIs and percentile methods — helpful for when I need quick statistical inference without assumptions about distributions.
"""

#!/usr/bin/env python3
"""
Bootstrap resampling module for statistical inference.

I kept running into situations where I needed confidence intervals but didn't
want to assume normality or deal with parametric tests. Bootstrap is perfect
for this — just resample with replacement and let the data speak for itself.
"""

import random
import statistics
from typing import List, Callable, Tuple, Optional


class BootstrapSampler:
    """
    Performs bootstrap resampling to estimate confidence intervals.
    
    The basic idea: treat your sample as the population, resample from it
    with replacement many times, and compute your statistic on each resample.
    The distribution of those statistics gives you the CI.
    """
    
    def __init__(self, data: List[float], n_iterations: int = 10000, seed: Optional[int] = None):
        """
        Initialize the bootstrap sampler.
        
        Args:
            data: Original sample data
            n_iterations: Number of bootstrap resamples to generate
            seed: Random seed for reproducibility (useful for debugging)
        """
        self.data = data
        self.n_iterations = n_iterations
        self.n = len(data)
        
        if seed is not None:
            random.seed(seed)
    
    def resample(self) -> List[float]:
        """Generate one bootstrap sample by sampling with replacement."""
        return random.choices(self.data, k=self.n)
    
    def bootstrap_statistic(self, statistic: Callable[[List[float]], float]) -> List[float]:
        """
        Compute a statistic on many bootstrap resamples.
        
        Args:
            statistic: Function that takes a list of floats and returns a single float
                      (e.g., statistics.mean, statistics.median, max, etc.)
        
        Returns:
            List of the statistic computed on each bootstrap sample
        """
        bootstrap_stats = []
        for _ in range(self.n_iterations):
            sample = self.resample()
            bootstrap_stats.append(statistic(sample))
        return bootstrap_stats
    
    def confidence_interval(
        self, 
        statistic: Callable[[List[float]], float], 
        confidence_level: float = 0.95
    ) -> Tuple[float, float, float]:
        """
        Calculate confidence interval using the percentile method.
        
        The percentile method is straightforward: if you want a 95% CI,
        just take the 2.5th and 97.5th percentiles of your bootstrap distribution.
        
        Args:
            statistic: Function to compute on each bootstrap sample
            confidence_level: Confidence level (e.g., 0.95 for 95% CI)
        
        Returns:
            Tuple of (point_estimate, lower_bound, upper_bound)
        """
        bootstrap_stats = self.bootstrap_statistic(statistic)
        
        # Point estimate from original data
        point_estimate = statistic(self.data)
        
        # Percentile bounds
        alpha = 1 - confidence_level
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100
        
        bootstrap_stats.sort()
        lower_bound = self._percentile(bootstrap_stats, lower_percentile)
        upper_bound = self._percentile(bootstrap_stats, upper_percentile)
        
        return point_estimate, lower_bound, upper_bound
    
    @staticmethod
    def _percentile(sorted_data: List[float], percentile: float) -> float:
        """
        Calculate percentile from sorted data.
        
        Using linear interpolation between closest ranks, which is what
        most stats packages do under the hood.
        """
        if not sorted_data:
            raise ValueError("Cannot compute percentile of empty data")
        
        k = (len(sorted_data) - 1) * (percentile / 100)
        f = int(k)
        c = f + 1
        
        if c >= len(sorted_data):
            return sorted_data[-1]
        
        # Linear interpolation
        d0 = sorted_data[f] * (c - k)
        d1 = sorted_data[c] * (k - f)
        return d0 + d1


def compare_groups_bootstrap(
    group_a: List[float], 
    group_b: List[float], 
    n_iterations: int = 10000,
    confidence_level: float = 0.95
) -> dict:
    """
    Compare two groups using bootstrap to test if their means differ.
    
    This is my go-to for A/B testing when I can't assume normality.
    Instead of a t-test, I bootstrap the difference in means and see
    if zero falls outside the confidence interval.
    
    Args:
        group_a: First group's data
        group_b: Second group's data
        n_iterations: Number of bootstrap iterations
        confidence_level: Confidence level for intervals
    
    Returns:
        Dictionary with comparison results
    """
    combined = group_a + group_b
    n_a = len(group_a)
    
    differences = []
    
    for _ in range(n_iterations):
        # Resample from combined pool (null hypothesis: no difference)
        resampled = random.choices(combined, k=len(combined))
        boot_a = resampled[:n_a]
        boot_b = resampled[n_a:]
        
        diff = statistics.mean(boot_a) - statistics.mean(boot_b)
        differences.append(diff)
    
    differences.sort()
    
    # Observed difference
    observed_diff = statistics.mean(group_a) - statistics.mean(group_b)
    
    # CI for the difference
    alpha = 1 - confidence_level
    lower_percentile = (alpha / 2) * 100
    upper_percentile = (1 - alpha / 2) * 100
    
    lower = BootstrapSampler._percentile(differences, lower_percentile)
    upper = BootstrapSampler._percentile(differences, upper_percentile)
    
    # P-value approximation: proportion of bootstrap diffs as extreme as observed
    more_extreme = sum(1 for d in differences if abs(d) >= abs(observed_diff))
    p_value = more_extreme / n_iterations
    
    return {
        'observed_difference': observed_diff,
        'ci_lower': lower,
        'ci_upper': upper,
        'p_value': p_value,
        'significant': 0 < lower or 0 > upper  # Zero not in CI means significant
    }


if __name__ == "__main__":
    print("=== Bootstrap Resampling Demo ===\n")
    
    # Example 1: Confidence interval for mean of a single sample
    print("Example 1: CI for mean of sample data")
    data = [23.1, 24.5, 22.8, 25.3, 23.7, 24.1, 23.9, 24.8, 23.5, 24.2]
    print(f"Original data (n={len(data)}): {data}")
    
    sampler = BootstrapSampler(data, n_iterations=5000, seed=42)
    mean_estimate, lower, upper = sampler.confidence_interval(statistics.mean, confidence_level=0.95)
    
    print(f"Mean estimate: {mean_estimate:.2f}")
    print(f"95% CI: [{lower:.2f}, {upper:.2f}]\n")
    
    # Example 2: CI for median (useful when data might be skewed)
    print("Example 2: CI for median")
    median_estimate, med_lower, med_upper = sampler.confidence_interval(statistics.median, confidence_level=0.95)
    print(f"Median estimate: {median_estimate:.2f}")
    print(f"95% CI: [{med_lower:.2f}, {med_upper:.2f}]\n")
    
    # Example 3: A/B test comparison
    print("Example 3: Comparing two groups (simulated A/B test)")
    control = [20.1, 21.3, 19.8, 20.5, 21.0, 20.3, 19.9, 20.7]
    treatment = [22.3, 23.1, 21.9, 22.8, 23.5, 22.0, 23.2, 22.6]
    
    print(f"Control group mean: {statistics.mean(control):.2f}")
    print(f"Treatment group mean: {statistics.mean(treatment):.2f}")
    
    result = compare_groups_bootstrap(control, treatment, n_iterations=5000, confidence_level=0.95)
    
    print(f"\nObserved difference: {result['observed_difference']:.2f}")
    print(f"95% CI for difference: [{result['ci_lower']:.2f}, {result['ci_upper']:.2f}]")
    print(f"Approximate p-value: {result['p_value']:.4f}")
    print(f"Statistically significant: {result['significant']}")