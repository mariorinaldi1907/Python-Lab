"""
Date: 2026-06-08
Built a Gaussian Naive Bayes classifier to understand probabilistic ML — handles continuous features and computes class probabilities properly.
"""

#!/usr/bin/env python3
"""
Naive Bayes Classifier from scratch using only the standard library.
Implements Gaussian Naive Bayes for continuous features.
"""

import math
import random
from collections import defaultdict


class GaussianNaiveBayes:
    """
    A Naive Bayes classifier that assumes features follow a Gaussian distribution.
    
    The "naive" part comes from assuming features are independent given the class,
    which is rarely true but works surprisingly well in practice.
    """
    
    def __init__(self):
        self.classes = []
        self.class_priors = {}  # P(class)
        self.feature_stats = {}  # mean and std dev for each feature per class
        
    def fit(self, X, y):
        """
        Train the classifier by computing statistics from the training data.
        
        Args:
            X: List of feature vectors (each a list of numbers)
            y: List of class labels
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
        self.feature_stats = {}
        for cls in self.classes:
            samples = class_samples[cls]
            self.feature_stats[cls] = []
            
            for feature_idx in range(n_features):
                # Extract all values for this feature in this class
                values = [sample[feature_idx] for sample in samples]
                mean = sum(values) / len(values)
                
                # Calculate standard deviation
                # Using population std dev here (dividing by N, not N-1)
                variance = sum((x - mean) ** 2 for x in values) / len(values)
                std_dev = math.sqrt(variance + 1e-6)  # small epsilon to avoid division by zero
                
                self.feature_stats[cls].append((mean, std_dev))
    
    def _gaussian_probability(self, x, mean, std_dev):
        """
        Calculate probability density using the Gaussian distribution formula.
        
        This is the probability of observing value x given the distribution
        defined by mean and std_dev.
        """
        exponent = math.exp(-((x - mean) ** 2) / (2 * std_dev ** 2))
        return (1 / (math.sqrt(2 * math.pi) * std_dev)) * exponent
    
    def _calculate_class_probability(self, features, cls):
        """
        Calculate P(class | features) using Bayes' theorem.
        
        We compute log probabilities to avoid numerical underflow when
        multiplying many small probabilities together.
        """
        # Start with the log of the prior probability
        log_prob = math.log(self.class_priors[cls])
        
        # Multiply by the likelihood of each feature (in log space, this is addition)
        for idx, value in enumerate(features):
            mean, std_dev = self.feature_stats[cls][idx]
            prob = self._gaussian_probability(value, mean, std_dev)
            # Add a small epsilon to avoid log(0)
            log_prob += math.log(prob + 1e-10)
        
        return log_prob
    
    def predict(self, X):
        """
        Predict class labels for samples in X.
        
        Args:
            X: List of feature vectors
            
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
        Return the probability distribution over classes for a single sample.
        
        This is useful when you want to see how confident the model is.
        """
        log_probs = {
            cls: self._calculate_class_probability(features, cls)
            for cls in self.classes
        }
        
        # Convert log probabilities back to regular probabilities and normalize
        # Using the log-sum-exp trick for numerical stability
        max_log_prob = max(log_probs.values())
        probs = {
            cls: math.exp(log_prob - max_log_prob)
            for cls, log_prob in log_probs.items()
        }
        total = sum(probs.values())
        return {cls: prob / total for cls, prob in probs.items()}


def generate_synthetic_data(n_samples=100, seed=42):
    """
    Generate synthetic data for demonstration.
    
    Creates two classes with different distributions:
    - Class 0: centered around (2, 2)
    - Class 1: centered around (6, 6)
    """
    random.seed(seed)
    X, y = [], []
    
    for _ in range(n_samples // 2):
        # Class 0: lower-left cluster
        X.append([random.gauss(2, 1), random.gauss(2, 1)])
        y.append(0)
        
        # Class 1: upper-right cluster
        X.append([random.gauss(6, 1), random.gauss(6, 1)])
        y.append(1)
    
    return X, y


if __name__ == "__main__":
    print("=== Gaussian Naive Bayes Classifier Demo ===\n")
    
    # Generate training and test data
    print("Generating synthetic 2D data...")
    X_train, y_train = generate_synthetic_data(n_samples=80, seed=42)
    X_test, y_test = generate_synthetic_data(n_samples=20, seed=123)
    
    # Train the classifier
    print("Training classifier...\n")
    nb = GaussianNaiveBayes()
    nb.fit(X_train, y_train)
    
    # Make predictions
    predictions = nb.predict(X_test)
    
    # Calculate accuracy
    correct = sum(1 for pred, true in zip(predictions, y_test) if pred == true)
    accuracy = correct / len(y_test) * 100
    
    print(f"Test Accuracy: {accuracy:.1f}% ({correct}/{len(y_test)} correct)\n")
    
    # Show some example predictions with probabilities
    print("Sample predictions with confidence:")
    for i in range(min(5, len(X_test))):
        features = X_test[i]
        true_label = y_test[i]
        probs = nb.predict_proba(features)
        predicted = max(probs, key=probs.get)
        
        print(f"  Sample {i+1}: features={[f'{x:.2f}' for x in features]}")
        print(f"    True label: {true_label}, Predicted: {predicted}")
        print(f"    P(class=0)={probs[0]:.3f}, P(class=1)={probs[1]:.3f}")
        print()