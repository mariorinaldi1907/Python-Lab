"""
Date: 2026-08-23
Built a Gaussian Naive Bayes classifier to understand probabilistic ML — calculates class probabilities using Bayes' theorem with normal distributions for continuous features.
"""

import math
import random
from collections import defaultdict


class GaussianNaiveBayes:
    """
    A Naive Bayes classifier for continuous features using Gaussian distribution.
    
    This implementation stores class priors and feature statistics (mean, variance)
    for each class, then uses Bayes' theorem for prediction.
    """
    
    def __init__(self):
        self.classes = []
        self.class_priors = {}  # P(class)
        self.feature_stats = {}  # {class: {feature_idx: {'mean': x, 'var': y}}}
        
    def fit(self, X, y):
        """
        Train the classifier by calculating priors and feature distributions.
        
        Args:
            X: List of feature vectors (list of lists)
            y: List of class labels
        """
        # Count samples per class to calculate priors
        class_counts = defaultdict(int)
        for label in y:
            class_counts[label] += 1
        
        self.classes = list(class_counts.keys())
        total_samples = len(y)
        
        # Calculate prior probabilities P(class)
        for cls in self.classes:
            self.class_priors[cls] = class_counts[cls] / total_samples
        
        # Group features by class
        class_features = defaultdict(list)
        for features, label in zip(X, y):
            class_features[label].append(features)
        
        # Calculate mean and variance for each feature in each class
        # This is where the "Gaussian" part comes in — we assume normal distribution
        self.feature_stats = {}
        for cls in self.classes:
            samples = class_features[cls]
            n_features = len(samples[0])
            
            self.feature_stats[cls] = {}
            for feature_idx in range(n_features):
                # Extract this feature across all samples for this class
                feature_values = [sample[feature_idx] for sample in samples]
                
                mean = sum(feature_values) / len(feature_values)
                variance = sum((x - mean) ** 2 for x in feature_values) / len(feature_values)
                
                # Avoid zero variance (would cause division by zero in pdf)
                variance = max(variance, 1e-6)
                
                self.feature_stats[cls][feature_idx] = {
                    'mean': mean,
                    'var': variance
                }
    
    def _gaussian_pdf(self, x, mean, variance):
        """
        Calculate probability density function of Gaussian distribution.
        
        This tells us how likely a value is given a normal distribution.
        """
        exponent = math.exp(-((x - mean) ** 2) / (2 * variance))
        return (1 / math.sqrt(2 * math.pi * variance)) * exponent
    
    def _calculate_class_probability(self, features, cls):
        """
        Calculate P(class | features) using Bayes' theorem.
        
        We calculate log probabilities to avoid numerical underflow when
        multiplying many small probabilities together.
        """
        # Start with log of prior probability
        log_prob = math.log(self.class_priors[cls])
        
        # Multiply by likelihood of each feature (add in log space)
        for feature_idx, value in enumerate(features):
            mean = self.feature_stats[cls][feature_idx]['mean']
            var = self.feature_stats[cls][feature_idx]['var']
            
            # Get probability density and add log to running total
            pdf = self._gaussian_pdf(value, mean, var)
            # Avoid log(0) by setting a floor
            log_prob += math.log(max(pdf, 1e-10))
        
        return log_prob
    
    def predict(self, X):
        """
        Predict class labels for samples in X.
        
        For each sample, calculate probability for each class and pick the max.
        """
        predictions = []
        
        for features in X:
            # Calculate probability for each class
            class_probabilities = {}
            for cls in self.classes:
                class_probabilities[cls] = self._calculate_class_probability(features, cls)
            
            # Pick class with highest probability
            predicted_class = max(class_probabilities, key=class_probabilities.get)
            predictions.append(predicted_class)
        
        return predictions


def generate_sample_data():
    """
    Generate synthetic 2D data with two classes.
    
    Class 0: centered around (2, 2)
    Class 1: centered around (6, 6)
    """
    random.seed(42)
    
    X = []
    y = []
    
    # Generate class 0 samples
    for _ in range(40):
        x1 = random.gauss(2, 1)
        x2 = random.gauss(2, 1)
        X.append([x1, x2])
        y.append(0)
    
    # Generate class 1 samples
    for _ in range(40):
        x1 = random.gauss(6, 1)
        x2 = random.gauss(6, 1)
        X.append([x1, x2])
        y.append(1)
    
    return X, y


if __name__ == "__main__":
    print("=== Gaussian Naive Bayes Classifier Demo ===\n")
    
    # Generate training data
    X_train, y_train = generate_sample_data()
    
    print(f"Generated {len(X_train)} training samples")
    print(f"Class distribution: {y_train.count(0)} class 0, {y_train.count(1)} class 1\n")
    
    # Train classifier
    nb = GaussianNaiveBayes()
    nb.fit(X_train, y_train)
    
    print("Training complete!")
    print(f"Class priors: {nb.class_priors}\n")
    
    # Show learned parameters for first feature
    print("Learned parameters (feature 0):")
    for cls in nb.classes:
        stats = nb.feature_stats[cls][0]
        print(f"  Class {cls}: mean={stats['mean']:.2f}, var={stats['var']:.2f}")
    print()
    
    # Test on new data points
    test_samples = [
        [2.5, 2.5],  # Should be class 0
        [5.5, 5.5],  # Should be class 1
        [1.0, 1.0],  # Should be class 0
        [7.0, 7.0],  # Should be class 1
    ]
    
    predictions = nb.predict(test_samples)
    
    print("Test predictions:")
    for sample, pred in zip(test_samples, predictions):
        print(f"  {sample} -> class {pred}")
    
    # Calculate training accuracy
    train_predictions = nb.predict(X_train)
    accuracy = sum(1 for true, pred in zip(y_train, train_predictions) if true == pred) / len(y_train)
    print(f"\nTraining accuracy: {accuracy:.2%}")