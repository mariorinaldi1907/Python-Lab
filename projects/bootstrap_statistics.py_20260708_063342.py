"""
Date: 2026-07-08
Built a bootstrap statistics module to estimate sampling distributions and confidence intervals without assuming normality — useful for my data analysis experiments.
"""

#!/usr/bin/env python3
"""
Bootstrap statistics module with resampling and hypothesis testing.

I wanted a simple way to calculate confidence intervals without relying on
parametric assumptions, so I built this bootstrap implementation from scratch.
Also added a basic t-test since I use it all the time.
"""

import random
import math
from typing import List, Callable, Tuple


def bootstrap_resample(data: List[float], num_samples: int = 10000,
                       statistic: Callable = None) -> List[float]:
    """
    Generate bootstrap samples by resampling with replacement.
    
    Args:
        data: Original dataset to resample from
        num_samples: Number of bootstrap samples to generate
        statistic: Function to apply to each sample (default: mean)
    
    Returns:
        List of statistics computed on each bootstrap sample
    
    The key idea here is sampling WITH replacement - each bootstrap sample
    has the same size as the original data, but some elements appear multiple
    times while others might not appear at all.
    """
    if statistic is None:
        statistic = lambda x: sum(x) / len(x)  # default to mean
    
    n = len(data)
    bootstrap_stats = []
    
    for _ in range(num_samples):
        # Sample with replacement - this is the core of bootstrapping
        sample = [random.choice(data) for _ in range(n)]
        bootstrap_stats.append(statistic(sample))
    
    return bootstrap_stats


def confidence_interval(bootstrap_stats: List[float], 
                       confidence_level: float = 0.95) -> Tuple[float, float]:
    """
    Calculate confidence interval from bootstrap distribution.
    
    Args:
        bootstrap_stats: List of bootstrap statistics
        confidence_level: Desired confidence level (e.g., 0.95 for 95%)
    
    Returns:
        Tuple of (lower_bound, upper_bound)
    
    Using the percentile method here - just grab the appropriate quantiles
    from the bootstrap distribution. Simple but effective.
    """
    sorted_stats = sorted(bootstrap_stats)
    n = len(sorted_stats)
    
    alpha = 1 - confidence_level
    lower_idx = int(n * (alpha / 2))
    upper_idx = int(n * (1 - alpha / 2))
    
    return (sorted_stats[lower_idx], sorted_stats[upper_idx])


def mean_and_std(data: List[float]) -> Tuple[float, float]:
    """Calculate mean and standard deviation."""
    n = len(data)
    mean = sum(data) / n
    variance = sum((x - mean) ** 2 for x in data) / (n - 1)
    std = math.sqrt(variance)
    return mean, std


def two_sample_t_test(sample1: List[float], sample2: List[float]) -> Tuple[float, bool]:
    """
    Welch's t-test for two independent samples (unequal variances).
    
    Args:
        sample1: First sample
        sample2: Second sample
    
    Returns:
        Tuple of (t_statistic, is_significant_at_5_percent)
    
    I went with Welch's t-test instead of Student's because it doesn't assume
    equal variances, which is more realistic for most real-world data.
    """
    mean1, std1 = mean_and_std(sample1)
    mean2, std2 = mean_and_std(sample2)
    
    n1, n2 = len(sample1), len(sample2)
    
    # Welch's t-statistic
    se = math.sqrt((std1 ** 2 / n1) + (std2 ** 2 / n2))
    t_stat = (mean1 - mean2) / se
    
    # Welch-Satterthwaite degrees of freedom (approximation)
    numerator = ((std1 ** 2 / n1) + (std2 ** 2 / n2)) ** 2
    denominator = ((std1 ** 2 / n1) ** 2 / (n1 - 1) + 
                   (std2 ** 2 / n2) ** 2 / (n2 - 1))
    df = numerator / denominator
    
    # Rough critical value check for p < 0.05 (two-tailed)
    # For most practical df > 30, critical value ≈ 2.0
    critical_value = 2.0 if df > 30 else 2.5
    is_significant = abs(t_stat) > critical_value
    
    return t_stat, is_significant


def median(data: List[float]) -> float:
    """Calculate the median of a dataset."""
    sorted_data = sorted(data)
    n = len(sorted_data)
    mid = n // 2
    
    if n % 2 == 0:
        return (sorted_data[mid - 1] + sorted_data[mid]) / 2
    else:
        return sorted_data[mid]


def bootstrap_hypothesis_test(sample1: List[float], sample2: List[float],
                             num_samples: int = 10000) -> float:
    """
    Non-parametric hypothesis test using bootstrap.
    
    Tests whether two samples come from populations with different means.
    Returns the p-value (proportion of bootstrap samples with difference
    as extreme as observed).
    
    This is cool because it doesn't require any distributional assumptions.
    """
    observed_diff = abs(sum(sample1) / len(sample1) - sum(sample2) / len(sample2))
    
    # Pool the data under null hypothesis (no difference)
    pooled = sample1 + sample2
    n1, n2 = len(sample1), len(sample2)
    
    extreme_count = 0
    for _ in range(num_samples):
        # Shuffle and split
        shuffled = pooled.copy()
        random.shuffle(shuffled)
        boot1 = shuffled[:n1]
        boot2 = shuffled[n1:n1 + n2]
        
        boot_diff = abs(sum(boot1) / len(boot1) - sum(boot2) / len(boot2))
        if boot_diff >= observed_diff:
            extreme_count += 1
    
    return extreme_count / num_samples


if __name__ == "__main__":
    print("=== Bootstrap Statistics Demo ===\n")
    
    # Simulate some experimental data
    random.seed(42)  # for reproducibility in demo
    
    control_group = [random.gauss(100, 15) for _ in range(30)]
    treatment_group = [random.gauss(110, 15) for _ in range(30)]
    
    print("Control group (n=30):")
    print(f"  Mean: {sum(control_group) / len(control_group):.2f}")
    print(f"  Median: {median(control_group):.2f}")
    
    print("\nTreatment group (n=30):")
    print(f"  Mean: {sum(treatment_group) / len(treatment_group):.2f}")
    print(f"  Median: {median(treatment_group):.2f}")
    
    # Bootstrap confidence interval for control group mean
    print("\n--- Bootstrap Analysis (10,000 samples) ---")
    boot_means = bootstrap_resample(control_group, num_samples=10000)
    ci_lower, ci_upper = confidence_interval(boot_means, confidence_level=0.95)
    print(f"Control group 95% CI for mean: [{ci_lower:.2f}, {ci_upper:.2f}]")
    
    # Bootstrap CI for median (custom statistic)
    boot_medians = bootstrap_resample(treatment_group, num_samples=10000, 
                                     statistic=median)
    ci_lower, ci_upper = confidence_interval(boot_medians)
    print(f"Treatment group 95% CI for median: [{ci_lower:.2f}, {ci_upper:.2f}]")
    
    # Traditional t-test
    print("\n--- Welch's t-test ---")
    t_stat, is_sig = two_sample_t_test(control_group, treatment_group)
    print(f"t-statistic: {t_stat:.3f}")
    print(f"Significant at α=0.05? {is_sig}")
    
    # Bootstrap hypothesis test
    print("\n--- Bootstrap Hypothesis Test ---")
    p_value = bootstrap_hypothesis_test(control_group, treatment_group, 
                                       num_samples=10000)
    print(f"Bootstrap p-value: {p_value:.4f}")
    print(f"Reject null hypothesis at α=0.05? {p_value < 0.05}")
    
    print("\nDone! The bootstrap method rocks for non-normal data.")