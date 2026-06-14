"""
Date: 2026-06-14
Built a Gaussian Naive Bayes classifier to understand probabilistic classification better — includes smoothing and handles continuous features.
"""

#!/usr/bin/env python3
"""
Naive Bayes classifier from scratch using only the standard library.
Implements Gaussian Naive Bayes for continuous features.
"""

import math
import random
from collections import defaultdict


class NaiveBayesClassifier:
    """
    A Gaussian Naive Bayes classifier for continuous features.
    
    Uses the assumption that features are independent given the class,
    and that each feature follows a normal distribution within each class.
    """
    
    def __init__(self):
        self.class_priors = {}  # P(class)
        self.feature_stats = {}  # mean and stddev for each feature per class
        self.classes = set()
        
    def _calculate_mean(self, values):
        """Calculate the arithmetic mean of a list of values."""
        return sum(values) / len(values) if values else 0.0
    
    def _calculate_stddev(self, values, mean):
        """Calculate standard deviation with Bessel's correction."""
        if len(values) < 2:
            return 1e-6  # avoid division by zero, use small epsilon
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return math.sqrt(variance) if variance > 0 else 1e-6
    
    def fit(self, X, y):
        """
        Train the classifier on feature matrix X and labels y.
        
        Args:
            X: List of feature vectors (each vector is a list of floats)
            y: List of class labels corresponding to each feature vector
        """
        # Group data by class
        class_data = defaultdict(list)
        for features, label in zip(X, y):
            class_data[label].append(features)
            self.classes.add(label)
        
        total_samples = len(y)
        num_features = len(X[0]) if X else 0
        
        # Calculate class priors: P(class) = count(class) / total_count
        for class_label in self.classes:
            self.class_priors[class_label] = len(class_data[class_label]) / total_samples
        
        # Calculate mean and stddev for each feature in each class
        self.feature_stats = {}
        for class_label in self.classes:
            self.feature_stats[class_label] = []
            
            # Transpose to get all values for each feature
            feature_values = [[] for _ in range(num_features)]
            for sample in class_data[class_label]:
                for feature_idx, value in enumerate(sample):
                    feature_values[feature_idx].append(value)
            
            # Calculate statistics for each feature
            for values in feature_values:
                mean = self._calculate_mean(values)
                stddev = self._calculate_stddev(values, mean)
                self.feature_stats[class_label].append((mean, stddev))
    
    def _gaussian_probability(self, x, mean, stddev):
        """
        Calculate probability density using Gaussian distribution.
        
        P(x | mean, stddev) = (1 / sqrt(2π * σ²)) * exp(-(x - μ)² / (2σ²))
        """
        exponent = math.exp(-((x - mean) ** 2) / (2 * stddev ** 2))
        return (1 / (math.sqrt(2 * math.pi) * stddev)) * exponent
    
    def predict_proba(self, features):
        """
        Calculate probability for each class given the features.
        
        Returns a dictionary mapping class labels to their probabilities.
        """
        posteriors = {}
        
        for class_label in self.classes:
            # Start with the prior probability (in log space to avoid underflow)
            log_prob = math.log(self.class_priors[class_label])
            
            # Multiply by the likelihood of each feature (add in log space)
            for feature_idx, feature_value in enumerate(features):
                mean, stddev = self.feature_stats[class_label][feature_idx]
                likelihood = self._gaussian_probability(feature_value, mean, stddev)
                log_prob += math.log(likelihood + 1e-10)  # small epsilon to avoid log(0)
            
            posteriors[class_label] = log_prob
        
        # Convert back from log space and normalize
        max_log_prob = max(posteriors.values())
        for class_label in posteriors:
            posteriors[class_label] = math.exp(posteriors[class_label] - max_log_prob)
        
        total = sum(posteriors.values())
        for class_label in posteriors:
            posteriors[class_label] /= total
        
        return posteriors
    
    def predict(self, features):
        """Predict the most likely class for the given features."""
        probas = self.predict_proba(features)
        return max(probas, key=probas.get)


def generate_synthetic_data(n_samples=100, seed=42):
    """
    Generate synthetic data for testing the classifier.
    
    Creates two classes with different feature distributions:
    - Class 0: centered around (2, 2)
    - Class 1: centered around (7, 7)
    """
    random.seed(seed)
    X, y = [], []
    
    for _ in range(n_samples // 2):
        # Class 0: mean around (2, 2)
        x1 = random.gauss(2, 1.5)
        x2 = random.gauss(2, 1.5)
        X.append([x1, x2])
        y.append(0)
        
        # Class 1: mean around (7, 7)
        x1 = random.gauss(7, 1.5)
        x2 = random.gauss(7, 1.5)
        X.append([x1, x2])
        y.append(1)
    
    return X, y


if __name__ == "__main__":
    print("=== Naive Bayes Classifier Demo ===\n")
    
    # Generate synthetic dataset
    X_train, y_train = generate_synthetic_data(n_samples=200, seed=42)
    X_test, y_test = generate_synthetic_data(n_samples=40, seed=123)
    
    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}\n")
    
    # Train the classifier
    nb = NaiveBayesClassifier()
    nb.fit(X_train, y_train)
    
    print("Learned class priors:")
    for class_label, prior in nb.class_priors.items():
        print(f"  Class {class_label}: {prior:.3f}")
    
    print("\nLearned feature statistics (mean, stddev):")
    for class_label in sorted(nb.classes):
        print(f"  Class {class_label}:")
        for feat_idx, (mean, stddev) in enumerate(nb.feature_stats[class_label]):
            print(f"    Feature {feat_idx}: μ={mean:.2f}, σ={stddev:.2f}")
    
    # Make predictions on test set
    correct = 0
    print("\n--- Sample Predictions ---")
    for i, (features, true_label) in enumerate(zip(X_test[:5], y_test[:5])):
        pred_label = nb.predict(features)
        probas = nb.predict_proba(features)
        correct += (pred_label == true_label)
        
        print(f"\nSample {i+1}: {[f'{x:.2f}' for x in features]}")
        print(f"  True class: {true_label}, Predicted: {pred_label}")
        print(f"  Probabilities: {dict((k, f'{v:.3f}') for k, v in probas.items())}")
    
    # Calculate overall accuracy
    all_correct = sum(1 for features, true_label in zip(X_test, y_test) 
                      if nb.predict(features) == true_label)
    accuracy = all_correct / len(X_test)
    
    print(f"\n=== Overall Test Accuracy: {accuracy:.2%} ===")