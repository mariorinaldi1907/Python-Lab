"""
Date: 2026-08-27
Built a Gaussian Naive Bayes classifier to understand probabilistic ML — handles continuous features and includes prior probability estimation.
"""

#!/usr/bin/env python3
"""
Gaussian Naive Bayes classifier implementation from scratch.
Uses maximum likelihood estimation with Laplace smoothing option.
"""

import math
from collections import defaultdict


class GaussianNaiveBayes:
    """
    Naive Bayes classifier assuming features follow a Gaussian distribution.
    
    This implementation calculates class priors and feature likelihoods
    during training, then uses Bayes' theorem for prediction.
    """
    
    def __init__(self, laplace_alpha=1.0):
        """
        Initialize the classifier.
        
        Args:
            laplace_alpha: Smoothing parameter for priors (default 1.0)
        """
        self.laplace_alpha = laplace_alpha
        self.class_priors = {}
        self.feature_stats = {}  # stores mean and std dev per class per feature
        self.classes = []
        
    def fit(self, X, y):
        """
        Train the classifier on the given data.
        
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
        n_classes = len(self.classes)
        
        # Calculate class priors with Laplace smoothing
        for cls in self.classes:
            count = len(class_samples[cls])
            # Add alpha to numerator, alpha * n_classes to denominator
            self.class_priors[cls] = (count + self.laplace_alpha) / (n_samples + self.laplace_alpha * n_classes)
        
        # Calculate mean and std dev for each feature in each class
        for cls in self.classes:
            samples = class_samples[cls]
            n_features = len(samples[0])
            self.feature_stats[cls] = []
            
            for feature_idx in range(n_features):
                # Extract all values for this feature in this class
                values = [sample[feature_idx] for sample in samples]
                mean = sum(values) / len(values)
                
                # Calculate standard deviation
                variance = sum((x - mean) ** 2 for x in values) / len(values)
                std_dev = math.sqrt(variance) if variance > 0 else 1e-6  # avoid division by zero
                
                self.feature_stats[cls].append({'mean': mean, 'std': std_dev})
    
    def _gaussian_probability(self, x, mean, std):
        """
        Calculate probability density function of Gaussian distribution.
        
        Args:
            x: Value to calculate probability for
            mean: Mean of the distribution
            std: Standard deviation of the distribution
            
        Returns:
            Probability density at x
        """
        exponent = math.exp(-((x - mean) ** 2) / (2 * std ** 2))
        return (1 / (math.sqrt(2 * math.pi) * std)) * exponent
    
    def _calculate_class_probability(self, features, cls):
        """
        Calculate the posterior probability for a given class.
        
        Uses log probabilities to avoid numerical underflow.
        
        Args:
            features: Feature vector to classify
            cls: Class label to calculate probability for
            
        Returns:
            Log probability of the class given the features
        """
        # Start with log of class prior
        log_prob = math.log(self.class_priors[cls])
        
        # Multiply by likelihood of each feature (add in log space)
        for idx, value in enumerate(features):
            stats = self.feature_stats[cls][idx]
            likelihood = self._gaussian_probability(value, stats['mean'], stats['std'])
            # Add small epsilon to avoid log(0)
            log_prob += math.log(likelihood + 1e-10)
        
        return log_prob
    
    def predict(self, X):
        """
        Predict class labels for samples in X.
        
        Args:
            X: List of feature vectors to classify
            
        Returns:
            List of predicted class labels
        """
        predictions = []
        
        for features in X:
            # Calculate probability for each class
            class_probs = {}
            for cls in self.classes:
                class_probs[cls] = self._calculate_class_probability(features, cls)
            
            # Predict the class with highest probability
            predicted_class = max(class_probs, key=class_probs.get)
            predictions.append(predicted_class)
        
        return predictions
    
    def predict_proba(self, X):
        """
        Predict class probabilities for samples in X.
        
        Args:
            X: List of feature vectors
            
        Returns:
            List of dictionaries mapping classes to probabilities
        """
        probabilities = []
        
        for features in X:
            class_log_probs = {}
            for cls in self.classes:
                class_log_probs[cls] = self._calculate_class_probability(features, cls)
            
            # Convert log probabilities to actual probabilities
            # Use exp and normalize to sum to 1
            max_log_prob = max(class_log_probs.values())
            exp_probs = {cls: math.exp(lp - max_log_prob) for cls, lp in class_log_probs.items()}
            total = sum(exp_probs.values())
            normalized_probs = {cls: prob / total for cls, prob in exp_probs.items()}
            
            probabilities.append(normalized_probs)
        
        return probabilities


if __name__ == "__main__":
    # Demo: Classify iris-like data (simplified version)
    # Features: [sepal_length, sepal_width, petal_length, petal_width]
    
    print("=== Gaussian Naive Bayes Classifier Demo ===\n")
    
    # Training data (simplified iris dataset)
    X_train = [
        [5.1, 3.5, 1.4, 0.2],  # setosa
        [4.9, 3.0, 1.4, 0.2],  # setosa
        [4.7, 3.2, 1.3, 0.2],  # setosa
        [7.0, 3.2, 4.7, 1.4],  # versicolor
        [6.4, 3.2, 4.5, 1.5],  # versicolor
        [6.9, 3.1, 4.9, 1.5],  # versicolor
        [6.3, 3.3, 6.0, 2.5],  # virginica
        [5.8, 2.7, 5.1, 1.9],  # virginica
        [7.1, 3.0, 5.9, 2.1],  # virginica
    ]
    
    y_train = ['setosa', 'setosa', 'setosa', 
               'versicolor', 'versicolor', 'versicolor',
               'virginica', 'virginica', 'virginica']
    
    # Initialize and train classifier
    nb = GaussianNaiveBayes(laplace_alpha=1.0)
    nb.fit(X_train, y_train)
    
    print("Training complete!")
    print(f"Classes detected: {nb.classes}")
    print(f"\nClass priors: {nb.class_priors}\n")
    
    # Test samples
    X_test = [
        [5.0, 3.6, 1.4, 0.2],  # should be setosa
        [6.5, 3.0, 4.6, 1.5],  # should be versicolor
        [6.7, 3.1, 5.6, 2.4],  # should be virginica
    ]
    
    predictions = nb.predict(X_test)
    probabilities = nb.predict_proba(X_test)
    
    print("=== Predictions ===")
    for i, (features, pred, probs) in enumerate(zip(X_test, predictions, probabilities)):
        print(f"\nSample {i+1}: {features}")
        print(f"  Predicted class: {pred}")
        print(f"  Probabilities:")
        for cls, prob in probs.items():
            print(f"    {cls}: {prob:.4f}")