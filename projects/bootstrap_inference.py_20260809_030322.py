"""
Date: 2026-08-09
Implemented a statistical bootstrapping library for resampling-based inference, because I got tired of using heavyweight stats packages for simple CI calculations.
"""

#!/usr/bin/env python3
"""
Bootstrap resampling module for statistical inference.
Supports confidence intervals, hypothesis testing, and comparison of distributions.
"""

import random
from typing import List, Callable, Tuple, Optional


class BootstrapSampler:
    """
    Performs bootstrap resampling to estimate sampling distributions and confidence intervals.
    
    Bootstrap is a resampling technique where we draw samples with replacement
    from our observed data to approximate the sampling distribution of a statistic.
    """
    
    def __init__(self, data: List[float], n_iterations: int = 10000, seed: Optional[int] = None):
        """
        Initialize the bootstrap sampler.
        
        Args:
            data: Original sample data
            n_iterations: Number of bootstrap resamples to generate
            seed: Random seed for reproducibility
        """
        self.data = data
        self.n_iterations = n_iterations
        self.n = len(data)
        
        if seed is not None:
            random.seed(seed)
    
    def resample(self) -> List[float]:
        """Generate one bootstrap resample by sampling with replacement."""
        return random.choices(self.data, k=self.n)
    
    def bootstrap_statistic(self, statistic: Callable[[List[float]], float]) -> List[float]:
        """
        Compute a statistic on many bootstrap resamples.
        
        Args:
            statistic: Function that takes a list and returns a single number
            
        Returns:
            List of statistic values, one per bootstrap iteration
        """
        results = []
        for _ in range(self.n_iterations):
            resample = self.resample()
            results.append(statistic(resample))
        return results
    
    def confidence_interval(
        self, 
        statistic: Callable[[List[float]], float], 
        confidence_level: float = 0.95
    ) -> Tuple[float, float, float]:
        """
        Calculate bootstrap confidence interval for a statistic.
        
        Uses the percentile method: the CI is just the middle percentage
        of the bootstrap distribution. Simple but effective.
        
        Args:
            statistic: Function to compute on resamples
            confidence_level: Desired confidence level (e.g., 0.95 for 95% CI)
            
        Returns:
            Tuple of (point_estimate, lower_bound, upper_bound)
        """
        bootstrap_stats = self.bootstrap_statistic(statistic)
        bootstrap_stats.sort()
        
        # Calculate percentiles for the CI
        alpha = 1 - confidence_level
        lower_percentile = alpha / 2
        upper_percentile = 1 - (alpha / 2)
        
        lower_idx = int(lower_percentile * self.n_iterations)
        upper_idx = int(upper_percentile * self.n_iterations)
        
        point_estimate = statistic(self.data)
        lower_bound = bootstrap_stats[lower_idx]
        upper_bound = bootstrap_stats[upper_idx]
        
        return point_estimate, lower_bound, upper_bound


def mean(data: List[float]) -> float:
    """Calculate arithmetic mean."""
    return sum(data) / len(data)


def median(data: List[float]) -> float:
    """Calculate median value."""
    sorted_data = sorted(data)
    n = len(sorted_data)
    mid = n // 2
    if n % 2 == 0:
        return (sorted_data[mid - 1] + sorted_data[mid]) / 2
    return sorted_data[mid]


def variance(data: List[float]) -> float:
    """Calculate sample variance."""
    m = mean(data)
    return sum((x - m) ** 2 for x in data) / (len(data) - 1)


def std_dev(data: List[float]) -> float:
    """Calculate sample standard deviation."""
    return variance(data) ** 0.5


def permutation_test(
    group_a: List[float], 
    group_b: List[float], 
    n_permutations: int = 10000,
    seed: Optional[int] = None
) -> float:
    """
    Two-sample permutation test to check if groups have different means.
    
    The null hypothesis is that the groups come from the same distribution.
    We shuffle the group labels randomly and see how extreme our observed
    difference is compared to random shuffling.
    
    Args:
        group_a: First sample
        group_b: Second sample
        n_permutations: Number of random permutations to test
        seed: Random seed for reproducibility
        
    Returns:
        p-value: proportion of permutations with difference >= observed difference
    """
    if seed is not None:
        random.seed(seed)
    
    # Observed difference in means
    observed_diff = abs(mean(group_a) - mean(group_b))
    
    # Combine all data and create labels
    combined = group_a + group_b
    n_a = len(group_a)
    n_total = len(combined)
    
    # Count how many permutations have a difference as extreme as observed
    extreme_count = 0
    
    for _ in range(n_permutations):
        # Randomly shuffle and split
        shuffled = combined.copy()
        random.shuffle(shuffled)
        
        perm_a = shuffled[:n_a]
        perm_b = shuffled[n_a:]
        
        perm_diff = abs(mean(perm_a) - mean(perm_b))
        
        if perm_diff >= observed_diff:
            extreme_count += 1
    
    # p-value is the proportion of permutations as extreme as observed
    return extreme_count / n_permutations


if __name__ == "__main__":
    print("=== Bootstrap Confidence Intervals ===\n")
    
    # Simulating some experimental data (e.g., response times in milliseconds)
    response_times = [
        23.1, 25.4, 22.8, 24.9, 26.2, 23.7, 25.1, 24.3, 
        22.9, 25.8, 24.1, 23.5, 26.0, 24.7, 23.3, 25.5,
        24.8, 23.9, 25.2, 24.4
    ]
    
    sampler = BootstrapSampler(response_times, n_iterations=10000, seed=42)
    
    # Confidence interval for mean
    mean_est, mean_lower, mean_upper = sampler.confidence_interval(mean)
    print(f"Mean response time: {mean_est:.2f} ms")
    print(f"95% CI: [{mean_lower:.2f}, {mean_upper:.2f}] ms\n")
    
    # Confidence interval for median (more robust to outliers)
    median_est, median_lower, median_upper = sampler.confidence_interval(median)
    print(f"Median response time: {median_est:.2f} ms")
    print(f"95% CI: [{median_lower:.2f}, {median_upper:.2f}] ms\n")
    
    # Confidence interval for standard deviation
    std_est, std_lower, std_upper = sampler.confidence_interval(std_dev)
    print(f"Std dev: {std_est:.2f} ms")
    print(f"95% CI: [{std_lower:.2f}, {std_upper:.2f}] ms\n")
    
    print("=== Permutation Test (Two-Sample Comparison) ===\n")
    
    # Comparing two different conditions (e.g., before and after optimization)
    before_optimization = [23.1, 25.4, 22.8, 24.9, 26.2, 23.7, 25.1, 24.3]
    after_optimization = [21.2, 22.1, 20.8, 21.9, 22.5, 21.4, 22.3, 21.7]
    
    p_value = permutation_test(before_optimization, after_optimization, n_permutations=10000, seed=42)
    
    print(f"Before optimization: mean = {mean(before_optimization):.2f} ms")
    print(f"After optimization: mean = {mean(after_optimization):.2f} ms")
    print(f"Difference: {mean(before_optimization) - mean(after_optimization):.2f} ms")
    print(f"Permutation test p-value: {p_value:.4f}")
    
    if p_value < 0.05:
        print("Result: Statistically significant difference (p < 0.05)")
    else:
        print("Result: No significant difference detected (p >= 0.05)")