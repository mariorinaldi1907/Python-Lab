"""
Date: 2026-06-24
Built a bootstrap resampling module to test hypotheses without assuming normal distributions — handles mean differences, correlation tests, and generates confidence intervals from empirical distributions.
"""

#!/usr/bin/env python3
"""
Bootstrap hypothesis testing module.
Implements resampling methods for statistical inference when you can't
rely on parametric assumptions. I built this because I kept needing
to test differences between groups in my side projects without assuming normality.
"""

import random
import statistics
from typing import List, Callable, Tuple


class BootstrapTester:
    """
    Performs bootstrap resampling for hypothesis testing and confidence intervals.
    
    The core idea: resample your data with replacement many times, calculate
    your test statistic each time, and build an empirical distribution.
    """
    
    def __init__(self, n_resamples: int = 10000, seed: int = None):
        """
        Initialize the bootstrap tester.
        
        Args:
            n_resamples: Number of bootstrap samples to draw
            seed: Random seed for reproducibility (None for random)
        """
        self.n_resamples = n_resamples
        if seed is not None:
            random.seed(seed)
    
    def resample(self, data: List[float]) -> List[float]:
        """
        Create a single bootstrap sample by sampling with replacement.
        
        Args:
            data: Original dataset
            
        Returns:
            A bootstrap sample of the same size as the original data
        """
        return random.choices(data, k=len(data))
    
    def bootstrap_statistic(self, data: List[float], 
                           statistic_func: Callable[[List[float]], float]) -> List[float]:
        """
        Generate bootstrap distribution of a statistic.
        
        Args:
            data: Original dataset
            statistic_func: Function that computes the statistic (e.g., mean, median)
            
        Returns:
            List of statistic values from bootstrap samples
        """
        bootstrap_stats = []
        for _ in range(self.n_resamples):
            sample = self.resample(data)
            bootstrap_stats.append(statistic_func(sample))
        return bootstrap_stats
    
    def confidence_interval(self, data: List[float], 
                           statistic_func: Callable[[List[float]], float],
                           confidence_level: float = 0.95) -> Tuple[float, float]:
        """
        Calculate bootstrap confidence interval for a statistic.
        
        Args:
            data: Original dataset
            statistic_func: Function to compute the statistic
            confidence_level: Confidence level (default 0.95 for 95% CI)
            
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        bootstrap_stats = self.bootstrap_statistic(data, statistic_func)
        bootstrap_stats.sort()
        
        # Calculate percentile indices for the CI
        alpha = 1 - confidence_level
        lower_idx = int(alpha / 2 * self.n_resamples)
        upper_idx = int((1 - alpha / 2) * self.n_resamples)
        
        return (bootstrap_stats[lower_idx], bootstrap_stats[upper_idx])
    
    def permutation_test(self, group1: List[float], group2: List[float],
                        statistic_func: Callable[[List[float], List[float]], float]) -> float:
        """
        Perform a permutation test to compare two groups.
        
        The null hypothesis is that the groups come from the same distribution.
        We shuffle labels randomly and see how extreme our observed statistic is.
        
        Args:
            group1: First group data
            group2: Second group data
            statistic_func: Function that takes two groups and returns a test statistic
            
        Returns:
            p-value (proportion of permutations with statistic >= observed)
        """
        observed_stat = statistic_func(group1, group2)
        
        # Combine all data for permutation
        combined = group1 + group2
        n1 = len(group1)
        
        # Count how many permutations give a statistic as extreme as observed
        extreme_count = 0
        for _ in range(self.n_resamples):
            random.shuffle(combined)
            perm_group1 = combined[:n1]
            perm_group2 = combined[n1:]
            perm_stat = statistic_func(perm_group1, perm_group2)
            
            # Two-tailed test: count both directions
            if abs(perm_stat) >= abs(observed_stat):
                extreme_count += 1
        
        return extreme_count / self.n_resamples


def mean_difference(group1: List[float], group2: List[float]) -> float:
    """Calculate the difference in means between two groups."""
    return statistics.mean(group1) - statistics.mean(group2)


def correlation(x: List[float], y: List[float]) -> float:
    """
    Calculate Pearson correlation coefficient.
    
    I implemented this from scratch instead of using a library
    because I wanted to understand what's actually happening.
    """
    n = len(x)
    mean_x = statistics.mean(x)
    mean_y = statistics.mean(y)
    
    numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    denom_x = sum((x[i] - mean_x) ** 2 for i in range(n))
    denom_y = sum((y[i] - mean_y) ** 2 for i in range(n))
    
    if denom_x == 0 or denom_y == 0:
        return 0.0
    
    return numerator / (denom_x * denom_y) ** 0.5


if __name__ == "__main__":
    print("=== Bootstrap Hypothesis Testing Demo ===\n")
    
    # Demo 1: Confidence interval for a mean
    print("Demo 1: Bootstrap confidence interval for mean")
    treatment_group = [23, 25, 28, 22, 27, 24, 26, 29, 21, 25, 28, 30]
    
    tester = BootstrapTester(n_resamples=10000, seed=42)
    ci_lower, ci_upper = tester.confidence_interval(treatment_group, statistics.mean)
    observed_mean = statistics.mean(treatment_group)
    
    print(f"Treatment group data: {treatment_group}")
    print(f"Observed mean: {observed_mean:.2f}")
    print(f"95% Bootstrap CI: [{ci_lower:.2f}, {ci_upper:.2f}]")
    print()
    
    # Demo 2: Permutation test comparing two groups
    print("Demo 2: Permutation test for difference in means")
    control_group = [18, 20, 19, 21, 17, 22, 20, 19, 18, 21]
    treatment_group_2 = [24, 26, 25, 27, 23, 28, 26, 25, 29, 24]
    
    control_mean = statistics.mean(control_group)
    treatment_mean = statistics.mean(treatment_group_2)
    observed_diff = treatment_mean - control_mean
    
    p_value = tester.permutation_test(control_group, treatment_group_2, mean_difference)
    
    print(f"Control group mean: {control_mean:.2f}")
    print(f"Treatment group mean: {treatment_mean:.2f}")
    print(f"Observed difference: {observed_diff:.2f}")
    print(f"P-value: {p_value:.4f}")
    
    if p_value < 0.05:
        print("Result: Statistically significant at α=0.05")
    else:
        print("Result: Not statistically significant at α=0.05")
    print()
    
    # Demo 3: Bootstrap correlation coefficient
    print("Demo 3: Bootstrap CI for correlation coefficient")
    x_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    y_data = [2.1, 3.9, 6.2, 8.1, 9.8, 12.3, 14.1, 15.9, 18.2, 20.1]
    
    def correlation_from_pairs(paired_data):
        """Helper to compute correlation from paired bootstrap samples."""
        x_vals = [pair[0] for pair in paired_data]
        y_vals = [pair[1] for pair in paired_data]
        return correlation(x_vals, y_vals)
    
    # Need to keep pairs together when bootstrapping
    paired_data = list(zip(x_data, y_data))
    bootstrap_correlations = []
    
    for _ in range(10000):
        sample = random.choices(paired_data, k=len(paired_data))
        bootstrap_correlations.append(correlation_from_pairs(sample))
    
    bootstrap_correlations.sort()
    corr_lower = bootstrap_correlations[int(0.025 * len(bootstrap_correlations))]
    corr_upper = bootstrap_correlations[int(0.975 * len(bootstrap_correlations))]
    observed_corr = correlation(x_data, y_data)
    
    print(f"Observed correlation: {observed_corr:.3f}")
    print(f"95% Bootstrap CI: [{corr_lower:.3f}, {corr_upper:.3f}]")
    print("\n=== All tests completed successfully! ===")