"""
Date: 2026-06-16
Implemented bootstrap resampling and permutation testing from scratch because I wanted to understand the mechanics behind statistical significance without reaching for scipy.
"""

#!/usr/bin/env python3
"""
Bootstrap and permutation testing module.

I built this to really understand how resampling methods work under the hood.
It's wild how powerful shuffling data around can be for hypothesis testing.
"""

import random
from typing import List, Tuple, Callable
from collections import Counter


class BootstrapTester:
    """
    Handles bootstrap resampling for confidence intervals and hypothesis testing.
    
    Bootstrap is crazy useful when you don't want to assume normality or
    when your sample size is small. Just resample with replacement!
    """
    
    def __init__(self, data: List[float], n_iterations: int = 10000, seed: int = None):
        """
        Initialize the bootstrap tester.
        
        Args:
            data: Original sample data
            n_iterations: Number of bootstrap samples to generate
            seed: Random seed for reproducibility (I always set this in tests)
        """
        self.data = data
        self.n_iterations = n_iterations
        if seed is not None:
            random.seed(seed)
    
    def bootstrap_statistic(self, statistic_func: Callable) -> List[float]:
        """
        Generate bootstrap distribution of a statistic.
        
        This is the core: sample with replacement, compute statistic, repeat.
        Works for any statistic you can dream up - mean, median, variance, whatever.
        
        Args:
            statistic_func: Function that takes a list and returns a single number
            
        Returns:
            List of bootstrap statistics
        """
        bootstrap_stats = []
        n = len(self.data)
        
        for _ in range(self.n_iterations):
            # Sample with replacement - this is the magic
            resample = [random.choice(self.data) for _ in range(n)]
            stat = statistic_func(resample)
            bootstrap_stats.append(stat)
        
        return bootstrap_stats
    
    def confidence_interval(self, statistic_func: Callable, 
                          confidence_level: float = 0.95) -> Tuple[float, float]:
        """
        Calculate bootstrap confidence interval.
        
        Using percentile method here - there are fancier bias-corrected versions
        but this works well enough for most cases I've encountered.
        
        Args:
            statistic_func: Function to compute statistic
            confidence_level: e.g., 0.95 for 95% CI
            
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        bootstrap_stats = self.bootstrap_statistic(statistic_func)
        bootstrap_stats.sort()
        
        # Calculate percentile indices
        alpha = 1 - confidence_level
        lower_idx = int(alpha / 2 * self.n_iterations)
        upper_idx = int((1 - alpha / 2) * self.n_iterations)
        
        return (bootstrap_stats[lower_idx], bootstrap_stats[upper_idx])


class PermutationTest:
    """
    Permutation test for comparing two groups.
    
    This is my favorite non-parametric test. No assumptions about distributions,
    just shuffle the labels and see if the observed difference is unusual.
    """
    
    def __init__(self, group1: List[float], group2: List[float], 
                 n_permutations: int = 10000, seed: int = None):
        """
        Initialize permutation test.
        
        Args:
            group1: First sample
            group2: Second sample
            n_permutations: Number of random permutations to try
            seed: Random seed
        """
        self.group1 = group1
        self.group2 = group2
        self.n_permutations = n_permutations
        if seed is not None:
            random.seed(seed)
    
    def test_difference_in_means(self) -> Tuple[float, float]:
        """
        Test if means are significantly different.
        
        The null hypothesis is that both groups come from the same distribution.
        We permute labels randomly and see how often we get a difference as
        extreme as what we actually observed.
        
        Returns:
            Tuple of (observed_difference, p_value)
        """
        # Calculate observed difference
        observed_diff = sum(self.group1) / len(self.group1) - sum(self.group2) / len(self.group2)
        
        # Combine all data
        combined = self.group1 + self.group2
        n1 = len(self.group1)
        n_total = len(combined)
        
        # Count how many permutations give us a difference as extreme
        extreme_count = 0
        
        for _ in range(self.n_permutations):
            # Shuffle and split
            shuffled = combined.copy()
            random.shuffle(shuffled)
            perm_group1 = shuffled[:n1]
            perm_group2 = shuffled[n1:]
            
            # Calculate difference for this permutation
            perm_diff = sum(perm_group1) / len(perm_group1) - sum(perm_group2) / len(perm_group2)
            
            # Two-tailed test: check if absolute difference is as extreme
            if abs(perm_diff) >= abs(observed_diff):
                extreme_count += 1
        
        p_value = extreme_count / self.n_permutations
        return (observed_diff, p_value)


def mean(data: List[float]) -> float:
    """Calculate mean. Yeah I could use statistics.mean but I like being explicit."""
    return sum(data) / len(data)


def median(data: List[float]) -> float:
    """Calculate median."""
    sorted_data = sorted(data)
    n = len(sorted_data)
    if n % 2 == 0:
        return (sorted_data[n//2 - 1] + sorted_data[n//2]) / 2
    return sorted_data[n//2]


if __name__ == "__main__":
    print("=== Bootstrap Confidence Intervals Demo ===\n")
    
    # Simulate some reaction time data (in milliseconds)
    # Let's say I'm testing my typing speed or something
    reaction_times = [245, 267, 289, 312, 298, 275, 301, 288, 256, 294,
                     310, 278, 265, 290, 305, 282, 271, 296, 287, 299]
    
    print(f"Sample data (n={len(reaction_times)}): {reaction_times[:5]}... (showing first 5)")
    print(f"Sample mean: {mean(reaction_times):.2f} ms")
    print(f"Sample median: {median(reaction_times):.2f} ms\n")
    
    # Bootstrap the mean
    bootstrap = BootstrapTester(reaction_times, n_iterations=10000, seed=42)
    
    mean_ci = bootstrap.confidence_interval(mean, confidence_level=0.95)
    print(f"95% CI for mean: ({mean_ci[0]:.2f}, {mean_ci[1]:.2f}) ms")
    
    median_ci = bootstrap.confidence_interval(median, confidence_level=0.95)
    print(f"95% CI for median: ({median_ci[0]:.2f}, {median_ci[1]:.2f}) ms")
    
    print("\n=== Permutation Test Demo ===\n")
    
    # Compare two groups - maybe I'm testing if caffeine affects reaction time
    no_caffeine = [289, 312, 298, 275, 301, 288, 294, 310, 278, 265]
    with_caffeine = [245, 267, 256, 282, 271, 260, 253, 268, 249, 258]
    
    print(f"No caffeine group mean: {mean(no_caffeine):.2f} ms")
    print(f"With caffeine group mean: {mean(with_caffeine):.2f} ms")
    
    perm_test = PermutationTest(no_caffeine, with_caffeine, 
                               n_permutations=10000, seed=42)
    
    diff, p_value = perm_test.test_difference_in_means()
    
    print(f"\nObserved difference: {diff:.2f} ms")
    print(f"P-value: {p_value:.4f}")
    
    if p_value < 0.05:
        print("Result: Statistically significant at α=0.05")
        print("(Looks like caffeine might actually help!)")
    else:
        print("Result: Not statistically significant at α=0.05")
        print("(Can't conclude caffeine makes a difference)")