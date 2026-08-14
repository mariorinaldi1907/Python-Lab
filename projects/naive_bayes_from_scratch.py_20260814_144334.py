"""
Date: 2026-08-14
Implemented a Gaussian Naive Bayes classifier without any ML libraries to really understand how probability-based classification works under the hood.
"""

#!/usr/bin/env python3
"""
Gaussian Naive Bayes Classifier from Scratch
Mario's implementation - no sklearn, just math and Python stdlib
"""

import math
import random
from collections import defaultdict


class GaussianNaiveBayes:
    """
    A Naive Bayes classifier that assumes features follow a Gaussian (normal) distribution.
    
    The "naive" part comes from assuming features are independent given the class label.
    This is rarely true in practice, but it works surprisingly well anyway.
    """
    
    def __init__(self):
        self.class_priors = {}  # P(class)
        self.feature_stats = {}  # mean and std dev for each feature per class
        self.classes = []
        
    def _calculate_mean(self, numbers):
        """Calculate the arithmetic mean of a list of numbers."""
        return sum(numbers) / len(numbers) if numbers else 0
    
    def _calculate_stdev(self, numbers, mean):
        """
        Calculate standard deviation using the sample formula.
        Adding a small epsilon to avoid division by zero in edge cases.
        """
        if len(numbers) < 2:
            return 1e-6
        variance = sum((x - mean) ** 2 for x in numbers) / (len(numbers) - 1)
        return math.sqrt(variance) + 1e-6
    
    def fit(self, X, y):
        """
        Train the classifier by calculating statistics for each class.
        
        X: list of feature vectors (each vector is a list of numbers)
        y: list of class labels
        """
        # Group samples by class
        class_samples = defaultdict(list)
        for features, label in zip(X, y):
            class_samples[label].append(features)
        
        self.classes = sorted(class_samples.keys())
        total_samples = len(y)
        
        # Calculate prior probability for each class
        for cls in self.classes:
            self.class_priors[cls] = len(class_samples[cls]) / total_samples
        
        # Calculate mean and stdev for each feature in each class
        # This is where we assume Gaussian distribution
        for cls in self.classes:
            samples = class_samples[cls]
            num_features = len(samples[0])
            self.feature_stats[cls] = []
            
            for feature_idx in range(num_features):
                feature_values = [sample[feature_idx] for sample in samples]
                mean = self._calculate_mean(feature_values)
                stdev = self._calculate_stdev(feature_values, mean)
                self.feature_stats[cls].append((mean, stdev))
    
    def _gaussian_probability(self, x, mean, stdev):
        """
        Calculate the probability density function for a Gaussian distribution.
        This is the classic bell curve formula.
        """
        exponent = math.exp(-((x - mean) ** 2) / (2 * stdev ** 2))
        return (1 / (math.sqrt(2 * math.pi) * stdev)) * exponent
    
    def _calculate_class_probability(self, features, cls):
        """
        Calculate P(class|features) using Bayes' theorem.
        We work in log space to avoid numerical underflow with tiny probabilities.
        """
        # Start with log of prior probability
        log_prob = math.log(self.class_priors[cls])
        
        # Add log probabilities of each feature given the class
        # This is where the "naive" independence assumption comes in
        for idx, feature_value in enumerate(features):
            mean, stdev = self.feature_stats[cls][idx]
            probability = self._gaussian_probability(feature_value, mean, stdev)
            log_prob += math.log(probability + 1e-10)  # avoid log(0)
        
        return log_prob
    
    def predict(self, X):
        """
        Predict class labels for a list of feature vectors.
        Returns the class with the highest posterior probability for each sample.
        """
        predictions = []
        for features in X:
            class_probs = {}
            for cls in self.classes:
                class_probs[cls] = self._calculate_class_probability(features, cls)
            # Return class with highest log probability
            predictions.append(max(class_probs, key=class_probs.get))
        return predictions
    
    def predict_proba(self, features):
        """
        Return probability distribution over classes for a single sample.
        Useful for understanding model confidence.
        """
        log_probs = {cls: self._calculate_class_probability(features, cls) 
                     for cls in self.classes}
        
        # Convert from log space and normalize to get real probabilities
        max_log = max(log_probs.values())
        probs = {cls: math.exp(log_prob - max_log) 
                 for cls, log_prob in log_probs.items()}
        total = sum(probs.values())
        return {cls: prob / total for cls, prob in probs.items()}


def generate_synthetic_data(n_samples=150):
    """
    Generate synthetic data similar to the iris dataset.
    Three classes with slightly different feature distributions.
    """
    random.seed(42)
    X, y = [], []
    
    # Class 0: smaller values
    for _ in range(n_samples // 3):
        X.append([
            random.gauss(5.0, 0.5),
            random.gauss(3.0, 0.4),
            random.gauss(1.5, 0.3),
            random.gauss(0.3, 0.1)
        ])
        y.append(0)
    
    # Class 1: medium values
    for _ in range(n_samples // 3):
        X.append([
            random.gauss(6.0, 0.5),
            random.gauss(2.8, 0.4),
            random.gauss(4.5, 0.5),
            random.gauss(1.4, 0.3)
        ])
        y.append(1)
    
    # Class 2: larger values
    for _ in range(n_samples // 3):
        X.append([
            random.gauss(6.5, 0.6),
            random.gauss(3.0, 0.4),
            random.gauss(5.5, 0.5),
            random.gauss(2.0, 0.4)
        ])
        y.append(2)
    
    return X, y


if __name__ == "__main__":
    print("=== Gaussian Naive Bayes Classifier Demo ===\n")
    
    # Generate synthetic dataset
    X, y = generate_synthetic_data(150)
    
    # Split into train/test (simple 80/20 split)
    split_idx = int(0.8 * len(X))
    X_train, y_train = X[:split_idx], y[:split_idx]
    X_test, y_test = X[split_idx:], y[split_idx:]
    
    # Train the classifier
    print(f"Training on {len(X_train)} samples...")
    nb = GaussianNaiveBayes()
    nb.fit(X_train, y_train)
    
    # Make predictions
    predictions = nb.predict(X_test)
    
    # Calculate accuracy
    correct = sum(1 for pred, actual in zip(predictions, y_test) if pred == actual)
    accuracy = correct / len(y_test)
    
    print(f"Test accuracy: {accuracy:.2%} ({correct}/{len(y_test)} correct)\n")
    
    # Show some example predictions with probabilities
    print("Sample predictions with confidence:")
    for i in range(min(5, len(X_test))):
        probs = nb.predict_proba(X_test[i])
        pred = predictions[i]
        actual = y_test[i]
        match = "✓" if pred == actual else "✗"
        print(f"{match} Predicted: Class {pred} | Actual: Class {actual}")
        print(f"  Probabilities: {', '.join(f'Class {c}: {p:.3f}' for c, p in sorted(probs.items()))}")
    
    print("\nClass prior probabilities:")
    for cls, prior in sorted(nb.class_priors.items()):
        print(f"  Class {cls}: {prior:.3f}")