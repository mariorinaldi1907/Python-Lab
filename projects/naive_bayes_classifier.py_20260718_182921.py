"""
Date: 2026-07-18
Built a Gaussian Naive Bayes classifier to understand probabilistic classification — handles continuous features and multiple classes.
"""

"""
Naive Bayes classifier implementation from scratch.
Uses Gaussian distribution for continuous features.
"""

import math
import random
from collections import defaultdict


class GaussianNaiveBayes:
    """
    Naive Bayes classifier assuming Gaussian distribution for features.
    
    The key insight: we calculate P(class|features) using Bayes' theorem.
    We assume features are independent (the "naive" part) which makes
    computation way simpler even though it's rarely true in practice.
    """
    
    def __init__(self):
        self.classes = []
        self.class_priors = {}  # P(class)
        self.feature_stats = {}  # mean and std dev for each feature per class
        
    def fit(self, X, y):
        """
        Train the classifier by calculating statistics for each class.
        
        Args:
            X: list of feature vectors (each vector is a list of numbers)
            y: list of class labels
        """
        # Group samples by class
        class_samples = defaultdict(list)
        for features, label in zip(X, y):
            class_samples[label].append(features)
        
        self.classes = list(class_samples.keys())
        n_samples = len(y)
        n_features = len(X[0])
        
        # Calculate priors: P(class) = count(class) / total_samples
        for label in self.classes:
            self.class_priors[label] = len(class_samples[label]) / n_samples
        
        # Calculate mean and std for each feature in each class
        # This is where we assume Gaussian distribution
        self.feature_stats = {}
        for label in self.classes:
            samples = class_samples[label]
            self.feature_stats[label] = []
            
            for feature_idx in range(n_features):
                values = [sample[feature_idx] for sample in samples]
                mean = sum(values) / len(values)
                
                # Calculate standard deviation
                variance = sum((x - mean) ** 2 for x in values) / len(values)
                std = math.sqrt(variance) if variance > 0 else 1e-6  # avoid division by zero
                
                self.feature_stats[label].append({'mean': mean, 'std': std})
    
    def _calculate_gaussian_probability(self, x, mean, std):
        """
        Calculate probability using Gaussian PDF.
        
        This is the probability density function for normal distribution.
        Returns how likely a value x is given the mean and std of a class.
        """
        exponent = math.exp(-((x - mean) ** 2) / (2 * std ** 2))
        return (1 / (math.sqrt(2 * math.pi) * std)) * exponent
    
    def _predict_single(self, features):
        """
        Predict class for a single sample.
        
        We calculate P(class|features) for each class and pick the max.
        Using log probabilities to avoid numerical underflow.
        """
        class_scores = {}
        
        for label in self.classes:
            # Start with log of prior probability
            log_prob = math.log(self.class_priors[label])
            
            # Multiply (add in log space) probabilities for each feature
            for feature_idx, value in enumerate(features):
                stats = self.feature_stats[label][feature_idx]
                prob = self._calculate_gaussian_probability(
                    value, stats['mean'], stats['std']
                )
                # Add log to avoid underflow with tiny probabilities
                log_prob += math.log(prob + 1e-10)  # small epsilon to avoid log(0)
            
            class_scores[label] = log_prob
        
        # Return class with highest probability
        return max(class_scores, key=class_scores.get)
    
    def predict(self, X):
        """Predict classes for multiple samples."""
        return [self._predict_single(features) for features in X]
    
    def score(self, X, y):
        """Calculate accuracy on test data."""
        predictions = self.predict(X)
        correct = sum(1 for pred, true in zip(predictions, y) if pred == true)
        return correct / len(y)


def generate_synthetic_data():
    """
    Create some fake data for testing.
    
    Two classes with different feature distributions:
    - Class 0: features centered around (2, 2)
    - Class 1: features centered around (8, 8)
    """
    random.seed(42)
    data = []
    labels = []
    
    # Generate class 0 samples
    for _ in range(50):
        x1 = random.gauss(2, 1.5)
        x2 = random.gauss(2, 1.5)
        data.append([x1, x2])
        labels.append(0)
    
    # Generate class 1 samples
    for _ in range(50):
        x1 = random.gauss(8, 1.5)
        x2 = random.gauss(8, 1.5)
        data.append([x1, x2])
        labels.append(1)
    
    return data, labels


if __name__ == "__main__":
    print("Naive Bayes Classifier Demo")
    print("=" * 40)
    
    # Generate data
    X, y = generate_synthetic_data()
    
    # Split into train/test (80/20 split)
    split_idx = int(0.8 * len(X))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    print(f"\nTraining samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")
    
    # Train the model
    nb = GaussianNaiveBayes()
    nb.fit(X_train, y_train)
    
    print("\nLearned parameters:")
    for label in nb.classes:
        print(f"\nClass {label}:")
        print(f"  Prior probability: {nb.class_priors[label]:.3f}")
        for idx, stats in enumerate(nb.feature_stats[label]):
            print(f"  Feature {idx}: mean={stats['mean']:.2f}, std={stats['std']:.2f}")
    
    # Make predictions
    train_accuracy = nb.score(X_train, y_train)
    test_accuracy = nb.score(X_test, y_test)
    
    print(f"\nTraining accuracy: {train_accuracy:.2%}")
    print(f"Test accuracy: {test_accuracy:.2%}")
    
    # Show some example predictions
    print("\nExample predictions:")
    for i in range(min(5, len(X_test))):
        features = X_test[i]
        true_label = y_test[i]
        pred_label = nb.predict([features])[0]
        status = "✓" if pred_label == true_label else "✗"
        print(f"  {status} Features: [{features[0]:.2f}, {features[1]:.2f}] "
              f"→ Predicted: {pred_label}, Actual: {true_label}")