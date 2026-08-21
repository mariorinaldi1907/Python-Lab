"""
Date: 2026-08-21
Implemented a Gaussian Naive Bayes classifier to finally understand how probabilistic classification actually works under the hood.
"""

#!/usr/bin/env python3
"""
Naive Bayes classifier implementation from scratch.
Uses Gaussian distribution for continuous features.
"""

import math
from collections import defaultdict


class NaiveBayesClassifier:
    """
    A Gaussian Naive Bayes classifier.
    
    Assumes features follow a normal distribution within each class.
    This is the 'naive' part — we assume features are independent given the class.
    """
    
    def __init__(self):
        self.classes = []
        self.class_priors = {}  # P(class)
        self.feature_stats = {}  # {class: {feature_idx: {'mean': x, 'std': y}}}
        
    def fit(self, X, y):
        """
        Train the classifier on feature matrix X and labels y.
        
        Args:
            X: List of samples, where each sample is a list of feature values
            y: List of class labels corresponding to each sample
        """
        n_samples = len(X)
        n_features = len(X[0])
        
        # Group samples by class
        class_samples = defaultdict(list)
        for features, label in zip(X, y):
            class_samples[label].append(features)
        
        self.classes = list(class_samples.keys())
        
        # Calculate prior probabilities P(class)
        for cls in self.classes:
            self.class_priors[cls] = len(class_samples[cls]) / n_samples
        
        # Calculate mean and std dev for each feature in each class
        self.feature_stats = {}
        for cls in self.classes:
            self.feature_stats[cls] = {}
            samples = class_samples[cls]
            
            for feature_idx in range(n_features):
                feature_values = [sample[feature_idx] for sample in samples]
                mean = sum(feature_values) / len(feature_values)
                
                # Calculate standard deviation
                variance = sum((x - mean) ** 2 for x in feature_values) / len(feature_values)
                std = math.sqrt(variance) if variance > 0 else 1e-6  # avoid division by zero
                
                self.feature_stats[cls][feature_idx] = {'mean': mean, 'std': std}
    
    def _gaussian_probability(self, x, mean, std):
        """
        Calculate probability density using Gaussian distribution.
        
        This is the likelihood P(feature|class) assuming normal distribution.
        """
        exponent = math.exp(-((x - mean) ** 2) / (2 * std ** 2))
        return (1 / (math.sqrt(2 * math.pi) * std)) * exponent
    
    def _calculate_class_probability(self, sample, cls):
        """
        Calculate P(class|sample) using Bayes theorem.
        
        Actually calculates log probability to avoid numerical underflow
        when multiplying many small probabilities.
        """
        # Start with log of prior probability
        log_prob = math.log(self.class_priors[cls])
        
        # Multiply (add logs) likelihoods for each feature
        for feature_idx, feature_value in enumerate(sample):
            mean = self.feature_stats[cls][feature_idx]['mean']
            std = self.feature_stats[cls][feature_idx]['std']
            
            # Add log of likelihood P(feature|class)
            likelihood = self._gaussian_probability(feature_value, mean, std)
            log_prob += math.log(likelihood + 1e-10)  # add small value to avoid log(0)
        
        return log_prob
    
    def predict(self, X):
        """
        Predict class labels for samples in X.
        
        Args:
            X: List of samples to classify
            
        Returns:
            List of predicted class labels
        """
        predictions = []
        
        for sample in X:
            # Calculate probability for each class and pick the max
            class_probabilities = {}
            for cls in self.classes:
                class_probabilities[cls] = self._calculate_class_probability(sample, cls)
            
            # Return class with highest probability
            predicted_class = max(class_probabilities, key=class_probabilities.get)
            predictions.append(predicted_class)
        
        return predictions
    
    def predict_proba(self, X):
        """
        Predict class probabilities for samples in X.
        
        Returns normalized probabilities (not log probabilities).
        """
        all_probabilities = []
        
        for sample in X:
            log_probs = {}
            for cls in self.classes:
                log_probs[cls] = self._calculate_class_probability(sample, cls)
            
            # Convert log probabilities back to regular probabilities
            # Subtract max for numerical stability
            max_log_prob = max(log_probs.values())
            probs = {cls: math.exp(log_prob - max_log_prob) 
                    for cls, log_prob in log_probs.items()}
            
            # Normalize to sum to 1
            total = sum(probs.values())
            normalized_probs = {cls: prob / total for cls, prob in probs.items()}
            
            all_probabilities.append(normalized_probs)
        
        return all_probabilities


if __name__ == "__main__":
    # Demo with the classic Iris dataset (simplified, manual entry)
    # Features: sepal_length, sepal_width, petal_length, petal_width
    
    print("Naive Bayes Classifier Demo")
    print("=" * 50)
    
    # Training data - simplified iris dataset
    # Format: [sepal_length, sepal_width, petal_length, petal_width]
    X_train = [
        [5.1, 3.5, 1.4, 0.2],
        [4.9, 3.0, 1.4, 0.2],
        [4.7, 3.2, 1.3, 0.2],
        [7.0, 3.2, 4.7, 1.4],
        [6.4, 3.2, 4.5, 1.5],
        [6.9, 3.1, 4.9, 1.5],
        [6.3, 3.3, 6.0, 2.5],
        [5.8, 2.7, 5.1, 1.9],
        [7.1, 3.0, 5.9, 2.1],
    ]
    
    y_train = ['setosa', 'setosa', 'setosa', 
               'versicolor', 'versicolor', 'versicolor',
               'virginica', 'virginica', 'virginica']
    
    # Train the classifier
    nb = NaiveBayesClassifier()
    nb.fit(X_train, y_train)
    
    print("\nTraining complete!")
    print(f"Classes found: {nb.classes}")
    print(f"Prior probabilities: {nb.class_priors}")
    
    # Test samples
    X_test = [
        [5.0, 3.6, 1.4, 0.2],   # Should be setosa
        [6.5, 3.0, 4.8, 1.5],   # Should be versicolor
        [6.2, 2.8, 5.8, 2.0],   # Should be virginica
    ]
    
    print("\n" + "=" * 50)
    print("Making predictions on test samples:")
    print("=" * 50)
    
    predictions = nb.predict(X_test)
    probabilities = nb.predict_proba(X_test)
    
    for i, (sample, pred, probs) in enumerate(zip(X_test, predictions, probabilities)):
        print(f"\nSample {i+1}: {sample}")
        print(f"Predicted class: {pred}")
        print(f"Class probabilities:")
        for cls in sorted(probs.keys()):
            print(f"  {cls}: {probs[cls]:.4f}")