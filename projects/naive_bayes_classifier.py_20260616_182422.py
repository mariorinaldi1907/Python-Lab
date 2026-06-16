"""
Date: 2026-06-16
Built a Gaussian and Multinomial Naive Bayes classifier to really understand how probabilistic classification works under the hood.
"""

#!/usr/bin/env python3
"""
Naive Bayes Classifier Implementation
Supports both Gaussian (continuous features) and Multinomial (discrete/count features).
I wanted to understand the math behind spam filters and sentiment analysis.
"""

import math
from collections import defaultdict


class GaussianNaiveBayes:
    """
    Naive Bayes classifier for continuous features.
    Assumes features follow a Gaussian (normal) distribution within each class.
    """
    
    def __init__(self):
        self.classes = []
        self.class_priors = {}  # P(class)
        self.feature_stats = {}  # mean and std dev per feature per class
        
    def fit(self, X, y):
        """
        Train the classifier by calculating priors and feature statistics.
        
        X: list of feature vectors (each vector is a list of floats)
        y: list of class labels
        """
        # Group samples by class
        class_samples = defaultdict(list)
        for features, label in zip(X, y):
            class_samples[label].append(features)
        
        self.classes = list(class_samples.keys())
        total_samples = len(y)
        n_features = len(X[0])
        
        # Calculate class priors: P(class) = count(class) / total
        for cls in self.classes:
            self.class_priors[cls] = len(class_samples[cls]) / total_samples
        
        # Calculate mean and std dev for each feature in each class
        self.feature_stats = {}
        for cls in self.classes:
            samples = class_samples[cls]
            self.feature_stats[cls] = []
            
            for feature_idx in range(n_features):
                values = [sample[feature_idx] for sample in samples]
                mean = sum(values) / len(values)
                # Using sample std dev (n-1) to avoid division by zero issues
                variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1 + 1e-6)
                std_dev = math.sqrt(variance)
                self.feature_stats[cls].append((mean, std_dev))
    
    def _gaussian_probability(self, x, mean, std_dev):
        """Calculate probability density using Gaussian distribution."""
        # Avoid division by zero
        if std_dev < 1e-6:
            std_dev = 1e-6
        exponent = math.exp(-((x - mean) ** 2) / (2 * std_dev ** 2))
        return (1 / (math.sqrt(2 * math.pi) * std_dev)) * exponent
    
    def predict(self, X):
        """Predict class labels for samples in X."""
        return [self._predict_single(x) for x in X]
    
    def _predict_single(self, x):
        """Predict class for a single sample using log probabilities to avoid underflow."""
        log_posteriors = {}
        
        for cls in self.classes:
            # Start with log of prior probability
            log_posterior = math.log(self.class_priors[cls])
            
            # Add log probabilities of each feature (multiplication becomes addition in log space)
            for feature_idx, feature_val in enumerate(x):
                mean, std_dev = self.feature_stats[cls][feature_idx]
                prob = self._gaussian_probability(feature_val, mean, std_dev)
                # Avoid log(0)
                log_posterior += math.log(prob + 1e-10)
            
            log_posteriors[cls] = log_posterior
        
        # Return class with highest posterior probability
        return max(log_posteriors, key=log_posteriors.get)


class MultinomialNaiveBayes:
    """
    Naive Bayes for discrete/count features (like word counts in text).
    Uses Laplace smoothing to handle unseen features.
    """
    
    def __init__(self, alpha=1.0):
        """alpha: Laplace smoothing parameter (1.0 is add-one smoothing)."""
        self.alpha = alpha
        self.classes = []
        self.class_priors = {}
        self.feature_probs = {}  # P(feature | class)
        
    def fit(self, X, y):
        """
        Train the classifier.
        X: list of feature vectors (counts or frequencies)
        y: list of class labels
        """
        class_counts = defaultdict(int)
        feature_counts = defaultdict(lambda: defaultdict(float))
        
        # Count everything
        for features, label in zip(X, y):
            class_counts[label] += 1
            for feature_idx, count in enumerate(features):
                feature_counts[label][feature_idx] += count
        
        self.classes = list(class_counts.keys())
        total_samples = len(y)
        n_features = len(X[0])
        
        # Calculate priors
        for cls in self.classes:
            self.class_priors[cls] = class_counts[cls] / total_samples
        
        # Calculate feature probabilities with Laplace smoothing
        self.feature_probs = {}
        for cls in self.classes:
            total_count = sum(feature_counts[cls].values())
            self.feature_probs[cls] = []
            
            for feature_idx in range(n_features):
                # Laplace smoothing: (count + alpha) / (total + alpha * n_features)
                count = feature_counts[cls].get(feature_idx, 0)
                prob = (count + self.alpha) / (total_count + self.alpha * n_features)
                self.feature_probs[cls].append(prob)
    
    def predict(self, X):
        """Predict class labels for samples in X."""
        predictions = []
        for x in X:
            log_posteriors = {}
            
            for cls in self.classes:
                log_posterior = math.log(self.class_priors[cls])
                
                for feature_idx, count in enumerate(x):
                    if count > 0:
                        prob = self.feature_probs[cls][feature_idx]
                        log_posterior += count * math.log(prob)
                
                log_posteriors[cls] = log_posterior
            
            predictions.append(max(log_posteriors, key=log_posteriors.get))
        
        return predictions


if __name__ == "__main__":
    print("=== Gaussian Naive Bayes Demo ===")
    print("Classifying iris-like flower measurements\n")
    
    # Synthetic data: [sepal_length, sepal_width, petal_length, petal_width]
    # Class 0: small flowers, Class 1: large flowers
    X_train = [
        [5.1, 3.5, 1.4, 0.2],
        [4.9, 3.0, 1.4, 0.2],
        [4.7, 3.2, 1.3, 0.2],
        [7.0, 3.2, 4.7, 1.4],
        [6.4, 3.2, 4.5, 1.5],
        [6.9, 3.1, 4.9, 1.5],
    ]
    y_train = [0, 0, 0, 1, 1, 1]
    
    X_test = [
        [5.0, 3.4, 1.5, 0.2],  # Should be class 0
        [6.7, 3.1, 4.4, 1.4],  # Should be class 1
    ]
    
    gnb = GaussianNaiveBayes()
    gnb.fit(X_train, y_train)
    predictions = gnb.predict(X_test)
    
    print(f"Test sample 1: {X_test[0]} -> Predicted class: {predictions[0]}")
    print(f"Test sample 2: {X_test[1]} -> Predicted class: {predictions[1]}")
    
    print("\n=== Multinomial Naive Bayes Demo ===")
    print("Simple text classification (word counts)\n")
    
    # Word counts for simple spam detection
    # Features: ["free", "money", "meeting", "schedule", "project"]
    X_train_text = [
        [2, 1, 0, 0, 0],  # spam
        [3, 2, 0, 0, 0],  # spam
        [0, 0, 2, 1, 1],  # not spam
        [0, 0, 1, 2, 2],  # not spam
    ]
    y_train_text = ["spam", "spam", "ham", "ham"]
    
    X_test_text = [
        [1, 1, 0, 0, 0],  # Should be spam
        [0, 0, 1, 1, 0],  # Should be ham
    ]
    
    mnb = MultinomialNaiveBayes(alpha=1.0)
    mnb.fit(X_train_text, y_train_text)
    predictions_text = mnb.predict(X_test_text)
    
    print(f"Test email 1 (free:1, money:1): {predictions_text[0]}")
    print(f"Test email 2 (meeting:1, schedule:1): {predictions_text[1]}")