"""
Date: 2026-06-23
Built a Gaussian Naive Bayes classifier to understand probabilistic ML from first principles — works on continuous data using probability density functions.
"""

#!/usr/bin/env python3
"""
Naive Bayes Classifier from Scratch
Implements Gaussian Naive Bayes for continuous features.
"""

import math
import random
from collections import defaultdict


class GaussianNaiveBayes:
    """
    Naive Bayes classifier assuming features follow Gaussian distributions.
    
    The "naive" part comes from assuming feature independence, which lets us
    multiply individual probabilities together. In practice this works surprisingly
    well even when the assumption doesn't hold perfectly.
    """
    
    def __init__(self):
        self.classes = []
        self.class_priors = {}  # P(class)
        self.feature_stats = {}  # mean and std dev for each feature per class
        
    def fit(self, X, y):
        """
        Learn the parameters (mean, std) for each feature in each class.
        
        Args:
            X: list of feature vectors (each vector is a list of numbers)
            y: list of class labels corresponding to X
        """
        self.classes = list(set(y))
        n_samples = len(y)
        
        # Group samples by class
        class_samples = defaultdict(list)
        for features, label in zip(X, y):
            class_samples[label].append(features)
        
        # Calculate prior probabilities P(class)
        for cls in self.classes:
            self.class_priors[cls] = len(class_samples[cls]) / n_samples
        
        # Calculate mean and std for each feature in each class
        # This is where we make the Gaussian assumption
        self.feature_stats = {}
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
                # Add small epsilon to avoid division by zero
                std = math.sqrt(variance + 1e-6)
                
                self.feature_stats[cls].append({'mean': mean, 'std': std})
    
    def _gaussian_pdf(self, x, mean, std):
        """
        Probability density function for Gaussian distribution.
        
        This gives us P(feature_value | class) under the assumption that
        features are normally distributed within each class.
        """
        exponent = math.exp(-((x - mean) ** 2) / (2 * std ** 2))
        return (1 / (math.sqrt(2 * math.pi) * std)) * exponent
    
    def _predict_single(self, features):
        """
        Predict class for a single sample using Bayes' theorem.
        
        We calculate P(class | features) for each class and pick the maximum.
        Using log probabilities to avoid numerical underflow from multiplying
        many small probabilities together.
        """
        log_posteriors = {}
        
        for cls in self.classes:
            # Start with log of prior probability
            log_posterior = math.log(self.class_priors[cls])
            
            # Multiply by likelihood of each feature (add logs)
            for feature_idx, feature_value in enumerate(features):
                stats = self.feature_stats[cls][feature_idx]
                likelihood = self._gaussian_pdf(
                    feature_value, 
                    stats['mean'], 
                    stats['std']
                )
                # Add log likelihood (equivalent to multiplying probabilities)
                log_posterior += math.log(likelihood + 1e-10)  # small epsilon for safety
            
            log_posteriors[cls] = log_posterior
        
        # Return class with highest posterior probability
        return max(log_posteriors, key=log_posteriors.get)
    
    def predict(self, X):
        """Predict classes for multiple samples."""
        return [self._predict_single(features) for features in X]
    
    def score(self, X, y):
        """Calculate accuracy on test data."""
        predictions = self.predict(X)
        correct = sum(pred == true for pred, true in zip(predictions, y))
        return correct / len(y)


def generate_synthetic_data(n_samples=200):
    """
    Generate synthetic 2D data for testing.
    
    Creates two classes with different centers but overlapping distributions.
    This simulates a real-world scenario where classes aren't perfectly separable.
    """
    data = []
    labels = []
    
    # Class 0: centered around (2, 3)
    for _ in range(n_samples // 2):
        x1 = random.gauss(2, 1)
        x2 = random.gauss(3, 1.5)
        data.append([x1, x2])
        labels.append(0)
    
    # Class 1: centered around (6, 7)
    for _ in range(n_samples // 2):
        x1 = random.gauss(6, 1.2)
        x2 = random.gauss(7, 1)
        data.append([x1, x2])
        labels.append(1)
    
    return data, labels


def train_test_split(X, y, test_size=0.3):
    """Simple train/test split without sklearn."""
    combined = list(zip(X, y))
    random.shuffle(combined)
    
    split_idx = int(len(combined) * (1 - test_size))
    train = combined[:split_idx]
    test = combined[split_idx:]
    
    X_train, y_train = zip(*train)
    X_test, y_test = zip(*test)
    
    return list(X_train), list(y_train), list(X_test), list(y_test)


if __name__ == "__main__":
    print("Gaussian Naive Bayes Classifier - From Scratch\n")
    print("=" * 50)
    
    # Set seed for reproducibility
    random.seed(42)
    
    # Generate synthetic dataset
    print("\n1. Generating synthetic 2D dataset...")
    X, y = generate_synthetic_data(n_samples=200)
    print(f"   Created {len(X)} samples with 2 features each")
    print(f"   Class distribution: {sum(1 for label in y if label == 0)} class-0, {sum(1 for label in y if label == 1)} class-1")
    
    # Split into train/test
    print("\n2. Splitting into train/test sets (70/30)...")
    X_train, y_train, X_test, y_test = train_test_split(X, y, test_size=0.3)
    print(f"   Training samples: {len(X_train)}")
    print(f"   Test samples: {len(X_test)}")
    
    # Train classifier
    print("\n3. Training Naive Bayes classifier...")
    nb = GaussianNaiveBayes()
    nb.fit(X_train, y_train)
    
    print("\n   Learned parameters:")
    for cls in nb.classes:
        print(f"\n   Class {cls}:")
        print(f"     Prior probability: {nb.class_priors[cls]:.3f}")
        for feat_idx, stats in enumerate(nb.feature_stats[cls]):
            print(f"     Feature {feat_idx}: mean={stats['mean']:.2f}, std={stats['std']:.2f}")
    
    # Evaluate
    print("\n4. Evaluating on test set...")
    train_accuracy = nb.score(X_train, y_train)
    test_accuracy = nb.score(X_test, y_test)
    
    print(f"   Training accuracy: {train_accuracy:.2%}")
    print(f"   Test accuracy: {test_accuracy:.2%}")
    
    # Demo predictions
    print("\n5. Sample predictions:")
    sample_indices = random.sample(range(len(X_test)), min(5, len(X_test)))
    for idx in sample_indices:
        features = X_test[idx]
        true_label = y_test[idx]
        predicted = nb._predict_single(features)
        print(f"   Features: [{features[0]:.2f}, {features[1]:.2f}] -> Predicted: {predicted}, True: {true_label}")
    
    print("\n" + "=" * 50)
    print("Done! The classifier learned Gaussian distributions for each class.")