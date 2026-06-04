"""
Date: 2026-06-04
Implemented a Gaussian Naive Bayes classifier to understand how probabilistic classification works under the hood — no sklearn needed.
"""

#!/usr/bin/env python3
"""
Gaussian Naive Bayes Classifier from Scratch

This implements the classic probabilistic classifier that assumes features
are independent given the class label. I'm using the Gaussian (normal)
distribution for continuous features, which is common for real-valued data.
"""

import math
import random
from collections import defaultdict


class GaussianNaiveBayes:
    """
    A Naive Bayes classifier that models each feature as a Gaussian distribution.
    
    The "naive" part comes from assuming features are independent given the class,
    which rarely holds in practice but works surprisingly well anyway.
    """
    
    def __init__(self):
        self.classes = []
        self.class_priors = {}  # P(class)
        self.feature_stats = {}  # mean and stddev for each feature per class
        
    def fit(self, X, y):
        """
        Train the classifier by computing class priors and feature statistics.
        
        Args:
            X: List of feature vectors (each vector is a list of numbers)
            y: List of class labels corresponding to X
        """
        # Group samples by class
        class_samples = defaultdict(list)
        for features, label in zip(X, y):
            class_samples[label].append(features)
        
        self.classes = list(class_samples.keys())
        n_samples = len(y)
        n_features = len(X[0])
        
        # Calculate prior probabilities for each class
        for cls in self.classes:
            self.class_priors[cls] = len(class_samples[cls]) / n_samples
        
        # Calculate mean and standard deviation for each feature in each class
        # This is where we're modeling features as Gaussian distributions
        self.feature_stats = {}
        for cls in self.classes:
            samples = class_samples[cls]
            self.feature_stats[cls] = []
            
            for feature_idx in range(n_features):
                feature_values = [sample[feature_idx] for sample in samples]
                mean = sum(feature_values) / len(feature_values)
                
                # Calculate standard deviation
                variance = sum((x - mean) ** 2 for x in feature_values) / len(feature_values)
                stddev = math.sqrt(variance) if variance > 0 else 1e-6  # avoid division by zero
                
                self.feature_stats[cls].append((mean, stddev))
    
    def _gaussian_probability(self, x, mean, stddev):
        """
        Calculate the probability density of x given a Gaussian distribution.
        
        This is the classic bell curve formula from statistics.
        """
        exponent = math.exp(-((x - mean) ** 2) / (2 * stddev ** 2))
        return (1 / (math.sqrt(2 * math.pi) * stddev)) * exponent
    
    def _calculate_class_probability(self, features, cls):
        """
        Calculate P(class | features) using Bayes' theorem.
        
        We actually calculate the log probability to avoid numerical underflow,
        since multiplying many small probabilities can lead to precision issues.
        """
        # Start with log of prior probability
        log_prob = math.log(self.class_priors[cls])
        
        # Add log probabilities for each feature (multiplication becomes addition in log space)
        for idx, feature_value in enumerate(features):
            mean, stddev = self.feature_stats[cls][idx]
            prob = self._gaussian_probability(feature_value, mean, stddev)
            # Add small epsilon to avoid log(0)
            log_prob += math.log(prob + 1e-10)
        
        return log_prob
    
    def predict(self, X):
        """
        Predict class labels for a list of feature vectors.
        
        Returns:
            List of predicted class labels
        """
        predictions = []
        for features in X:
            # Calculate probability for each class and pick the highest
            class_probs = {
                cls: self._calculate_class_probability(features, cls)
                for cls in self.classes
            }
            predicted_class = max(class_probs, key=class_probs.get)
            predictions.append(predicted_class)
        
        return predictions
    
    def predict_proba(self, features):
        """
        Return probability estimates for a single sample.
        
        This normalizes the probabilities so they sum to 1.
        """
        log_probs = {
            cls: self._calculate_class_probability(features, cls)
            for cls in self.classes
        }
        
        # Convert back from log space and normalize
        # Subtract max for numerical stability
        max_log_prob = max(log_probs.values())
        probs = {cls: math.exp(lp - max_log_prob) for cls, lp in log_probs.items()}
        total = sum(probs.values())
        
        return {cls: p / total for cls, p in probs.items()}


def generate_synthetic_data(n_samples=150):
    """
    Generate a synthetic dataset similar to the iris dataset.
    
    Three classes with different mean feature values — simulates flower measurements.
    """
    random.seed(42)
    X, y = [], []
    
    # Class 0: smaller flowers
    for _ in range(n_samples // 3):
        X.append([
            random.gauss(5.0, 0.5),  # sepal length
            random.gauss(3.4, 0.4),  # sepal width
            random.gauss(1.5, 0.3),  # petal length
            random.gauss(0.2, 0.1),  # petal width
        ])
        y.append(0)
    
    # Class 1: medium flowers
    for _ in range(n_samples // 3):
        X.append([
            random.gauss(6.0, 0.5),
            random.gauss(2.8, 0.4),
            random.gauss(4.5, 0.5),
            random.gauss(1.3, 0.3),
        ])
        y.append(1)
    
    # Class 2: larger flowers
    for _ in range(n_samples // 3):
        X.append([
            random.gauss(6.5, 0.6),
            random.gauss(3.0, 0.4),
            random.gauss(5.5, 0.5),
            random.gauss(2.0, 0.3),
        ])
        y.append(2)
    
    return X, y


if __name__ == "__main__":
    print("=== Gaussian Naive Bayes Classifier Demo ===\n")
    
    # Generate synthetic data
    X, y = generate_synthetic_data(n_samples=150)
    
    # Split into train/test (80/20 split, simple manual split)
    split_idx = int(0.8 * len(X))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    # Train the classifier
    nb = GaussianNaiveBayes()
    nb.fit(X_train, y_train)
    
    print(f"Trained on {len(X_train)} samples")
    print(f"Class priors: {nb.class_priors}\n")
    
    # Make predictions
    predictions = nb.predict(X_test)
    
    # Calculate accuracy
    correct = sum(1 for pred, true in zip(predictions, y_test) if pred == true)
    accuracy = correct / len(y_test)
    
    print(f"Test set accuracy: {accuracy:.2%} ({correct}/{len(y_test)})")
    
    # Show a few example predictions with probabilities
    print("\nSample predictions with probabilities:")
    for i in range(min(5, len(X_test))):
        probs = nb.predict_proba(X_test[i])
        print(f"  Sample {i+1}: True={y_test[i]}, Predicted={predictions[i]}")
        print(f"    Probabilities: {probs}")