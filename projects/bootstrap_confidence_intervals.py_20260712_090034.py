"""
Date: 2026-07-12
Built a bootstrapping module to estimate confidence intervals from small datasets without assuming normal distributions — useful for when I'm analyzing experiment results.
"""

"""
Bootstrap resampling for confidence interval estimation.

I kept running into situations where I had small sample sizes and couldn't
assume normality, so I wrote this to do non-parametric bootstrap resampling.
Works surprisingly well for getting CI estimates on means, medians, whatever.
"""

import random
from typing import List, Callable, Tuple
from collections import Counter


def bootstrap_resample(data: List[float], n_iterations: int = 10000, 
                       statistic: Callable = None, seed: int = None) -> List[float]:
    """
    Generate bootstrap resamples and compute a statistic on each.
    
    The idea is simple: randomly sample with replacement from your data,
    compute your statistic (mean, median, etc.), repeat a bunch of times.
    This gives you a distribution of the statistic under resampling.
    
    Args:
        data: Original dataset
        n_iterations: Number of bootstrap samples to generate
        statistic: Function to apply to each resample (defaults to mean)
        seed: Random seed for reproducibility
        
    Returns:
        List of statistic values from each bootstrap sample
    """
    if statistic is None:
        statistic = lambda x: sum(x) / len(x)  # default to mean
    
    if seed is not None:
        random.seed(seed)
    
    n = len(data)
    bootstrap_statistics = []
    
    for _ in range(n_iterations):
        # Sample with replacement - this is the core of bootstrapping
        resample = [random.choice(data) for _ in range(n)]
        bootstrap_statistics.append(statistic(resample))
    
    return bootstrap_statistics


def confidence_interval(bootstrap_dist: List[float], alpha: float = 0.05) -> Tuple[float, float]:
    """
    Calculate confidence interval from bootstrap distribution.
    
    Uses the percentile method - just grabs the appropriate quantiles.
    For a 95% CI (alpha=0.05), we take the 2.5th and 97.5th percentiles.
    
    Args:
        bootstrap_dist: Distribution of bootstrap statistics
        alpha: Significance level (e.g., 0.05 for 95% CI)
        
    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    sorted_dist = sorted(bootstrap_dist)
    n = len(sorted_dist)
    
    lower_idx = int(n * (alpha / 2))
    upper_idx = int(n * (1 - alpha / 2))
    
    return (sorted_dist[lower_idx], sorted_dist[upper_idx])


def median(data: List[float]) -> float:
    """Calculate median of a dataset."""
    sorted_data = sorted(data)
    n = len(sorted_data)
    mid = n // 2
    
    if n % 2 == 0:
        return (sorted_data[mid - 1] + sorted_data[mid]) / 2
    else:
        return sorted_data[mid]


def std_dev(data: List[float]) -> float:
    """Calculate sample standard deviation."""
    n = len(data)
    mean = sum(data) / n
    variance = sum((x - mean) ** 2 for x in data) / (n - 1)
    return variance ** 0.5


def bootstrap_hypothesis_test(data1: List[float], data2: List[float], 
                              n_iterations: int = 10000, seed: int = None) -> float:
    """
    Two-sample bootstrap hypothesis test for difference in means.
    
    Tests null hypothesis that two samples come from the same distribution.
    We pool the data, then bootstrap resample to see how often we'd get
    a difference as extreme as observed just by chance.
    
    Args:
        data1: First sample
        data2: Second sample
        n_iterations: Number of bootstrap iterations
        seed: Random seed
        
    Returns:
        p-value (proportion of bootstrap samples with difference >= observed)
    """
    if seed is not None:
        random.seed(seed)
    
    mean1 = sum(data1) / len(data1)
    mean2 = sum(data2) / len(data2)
    observed_diff = abs(mean1 - mean2)
    
    # Pool the data under null hypothesis
    pooled = data1 + data2
    n1, n2 = len(data1), len(data2)
    
    extreme_count = 0
    
    for _ in range(n_iterations):
        # Resample two groups from pooled data
        sample1 = [random.choice(pooled) for _ in range(n1)]
        sample2 = [random.choice(pooled) for _ in range(n2)]
        
        boot_mean1 = sum(sample1) / n1
        boot_mean2 = sum(sample2) / n2
        boot_diff = abs(boot_mean1 - boot_mean2)
        
        if boot_diff >= observed_diff:
            extreme_count += 1
    
    return extreme_count / n_iterations


def print_summary_stats(data: List[float], label: str = "Data"):
    """Pretty print summary statistics for a dataset."""
    print(f"\n{label} Summary:")
    print(f"  n = {len(data)}")
    print(f"  Mean = {sum(data) / len(data):.3f}")
    print(f"  Median = {median(data):.3f}")
    print(f"  Std Dev = {std_dev(data):.3f}")
    print(f"  Range = [{min(data):.3f}, {max(data):.3f}]")


if __name__ == "__main__":
    # Demo with some made-up experimental data
    # Let's say I ran an A/B test and want to know if group B really performs better
    
    print("=" * 60)
    print("Bootstrap Confidence Interval Demo")
    print("=" * 60)
    
    # Simulated response times (in ms) for two groups
    group_a = [245, 289, 301, 267, 278, 255, 312, 298, 271, 285, 
               264, 295, 281, 308, 273, 287, 269, 291, 303, 276]
    
    group_b = [198, 215, 234, 207, 223, 189, 241, 219, 202, 228,
               211, 237, 205, 226, 214, 231, 196, 221, 209, 218]
    
    print_summary_stats(group_a, "Group A")
    print_summary_stats(group_b, "Group B")
    
    # Bootstrap CI for Group A mean
    print("\n" + "=" * 60)
    print("Bootstrap Analysis (10,000 iterations)")
    print("=" * 60)
    
    boot_means_a = bootstrap_resample(group_a, n_iterations=10000, seed=42)
    ci_a = confidence_interval(boot_means_a, alpha=0.05)
    
    print(f"\nGroup A - 95% CI for mean: [{ci_a[0]:.2f}, {ci_a[1]:.2f}]")
    
    boot_means_b = bootstrap_resample(group_b, n_iterations=10000, seed=42)
    ci_b = confidence_interval(boot_means_b, alpha=0.05)
    
    print(f"Group B - 95% CI for mean: [{ci_b[0]:.2f}, {ci_b[1]:.2f}]")
    
    # Hypothesis test
    p_value = bootstrap_hypothesis_test(group_a, group_b, n_iterations=10000, seed=42)
    
    print(f"\nTwo-sample bootstrap test:")
    print(f"  H0: Groups come from same distribution")
    print(f"  p-value = {p_value:.4f}")
    
    if p_value < 0.05:
        print(f"  Result: Reject H0 at α=0.05 — groups differ significantly")
    else:
        print(f"  Result: Fail to reject H0 at α=0.05")
    
    # Also demo median CI since that's where bootstrap really shines
    print("\n" + "-" * 60)
    print("Bonus: Bootstrap CI for median (harder to get analytically)")
    print("-" * 60)
    
    boot_medians_b = bootstrap_resample(group_b, n_iterations=10000, 
                                        statistic=median, seed=42)
    ci_median_b = confidence_interval(boot_medians_b, alpha=0.05)
    
    print(f"\nGroup B - 95% CI for median: [{ci_median_b[0]:.2f}, {ci_median_b[1]:.2f}]")
    print(f"Observed median: {median(group_b):.2f}")
    
    print("\n" + "=" * 60)