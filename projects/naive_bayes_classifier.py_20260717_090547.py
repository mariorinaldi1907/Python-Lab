"""
Date: 2026-07-17
Built a Gaussian Naive Bayes classifier to refresh my understanding of probabilistic ML — handles continuous features and includes smoothing.
"""

"""
Naive Bayes Classifier from scratch
Implements Gaussian Naive Bayes for continuous features.
I wanted to really understand the probability mechanics behind this algorithm.
"""

import math
from collections import defaultdict


class GaussianNaiveBayes:
    """
    A Naive Bayes classifier that assumes features follow a Gaussian distribution.
    
    This is a simple but surprisingly effective probabilistic classifier.
    The 'naive' part comes from assuming feature independence, which rarely holds
    in practice but works well anyway.
    """
    
    def __init__(self):
        self.classes = []
        self.class_priors = {}  # P(class)
        self.feature_stats = {}  # mean and std for each feature per class
        
    def fit(self, X, y):
        """
        Train the classifier by calculating class priors and feature statistics.
        
        Args:
            X: Training features (list of lists)
            y: Training labels (list)
        """
        # Get unique classes and their counts
        self.classes = list(set(y))
        n_samples = len(y)
        
        # Group samples by class
        class_samples = defaultdict(list)
        for features, label in zip(X, y):
            class_samples[label].append(features)
        
        # Calculate priors P(class) - just the frequency of each class
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
                # Added small epsilon to avoid division by zero
                variance = sum((x - mean) ** 2 for x in values) / len(values)
                std = math.sqrt(variance) + 1e-6
                
                self.feature_stats[cls].append({'mean': mean, 'std': std})
    
    def _gaussian_probability(self, x, mean, std):
        """
        Calculate probability using Gaussian PDF.
        
        This is the heart of Gaussian Naive Bayes - we assume each feature
        follows a normal distribution within each class.
        
        Args:
            x: Feature value
            mean: Mean of the distribution
            std: Standard deviation
            
        Returns:
            Probability density at x
        """
        exponent = math.exp(-((x - mean) ** 2) / (2 * std ** 2))
        return (1 / (math.sqrt(2 * math.pi) * std)) * exponent
    
    def _predict_single(self, features):
        """
        Predict class for a single sample.
        
        Uses Bayes theorem: P(class|features) ∝ P(class) * P(features|class)
        We calculate this for each class and pick the max.
        """
        posteriors = {}
        
        for cls in self.classes:
            # Start with the prior probability
            posterior = math.log(self.class_priors[cls])
            
            # Multiply by likelihood of each feature (using log to avoid underflow)
            for idx, feature_value in enumerate(features):
                stats = self.feature_stats[cls][idx]
                likelihood = self._gaussian_probability(
                    feature_value, 
                    stats['mean'], 
                    stats['std']
                )
                # Use log probabilities to avoid numerical underflow
                posterior += math.log(likelihood + 1e-10)
            
            posteriors[cls] = posterior
        
        # Return class with highest posterior probability
        return max(posteriors, key=posteriors.get)
    
    def predict(self, X):
        """
        Predict classes for multiple samples.
        
        Args:
            X: Features to predict (list of lists)
            
        Returns:
            List of predicted class labels
        """
        return [self._predict_single(features) for features in X]
    
    def score(self, X, y):
        """
        Calculate accuracy on test data.
        
        Args:
            X: Test features
            y: True labels
            
        Returns:
            Accuracy as a float between 0 and 1
        """
        predictions = self.predict(X)
        correct = sum(1 for pred, true in zip(predictions, y) if pred == true)
        return correct / len(y)


if __name__ == "__main__":
    # Simple demo with a toy dataset
    # Let's classify flowers based on petal/sepal measurements (inspired by iris)
    
    print("=== Gaussian Naive Bayes Classifier Demo ===\n")
    
    # Training data: [sepal_length, petal_length, petal_width]
    # Class 0: small flowers, Class 1: large flowers
    X_train = [
        [5.1, 1.4, 0.2],
        [4.9, 1.4, 0.2],
        [4.7, 1.3, 0.2],
        [5.0, 1.5, 0.2],
        [7.0, 4.7, 1.4],
        [6.4, 4.5, 1.5],
        [6.9, 4.9, 1.5],
        [6.5, 4.6, 1.3],
        [6.3, 4.4, 1.3],
        [5.8, 4.0, 1.2],
    ]
    
    y_train = [0, 0, 0, 0, 1, 1, 1, 1, 1, 1]
    
    # Test data
    X_test = [
        [5.2, 1.5, 0.3],  # Should be class 0
        [6.7, 4.8, 1.4],  # Should be class 1
        [4.8, 1.3, 0.1],  # Should be class 0
        [6.1, 4.3, 1.2],  # Should be class 1
    ]
    
    y_test = [0, 1, 0, 1]
    
    # Train the classifier
    print("Training Naive Bayes classifier...")
    nb = GaussianNaiveBayes()
    nb.fit(X_train, y_train)
    
    # Show learned statistics
    print("\nLearned class priors:")
    for cls, prior in nb.class_priors.items():
        print(f"  Class {cls}: {prior:.2f}")
    
    print("\nLearned feature statistics (mean ± std):")
    for cls in nb.classes:
        print(f"  Class {cls}:")
        for idx, stats in enumerate(nb.feature_stats[cls]):
            print(f"    Feature {idx}: {stats['mean']:.2f} ± {stats['std']:.2f}")
    
    # Make predictions
    print("\n--- Predictions ---")
    predictions = nb.predict(X_test)
    for i, (features, pred, true) in enumerate(zip(X_test, predictions, y_test)):
        status = "✓" if pred == true else "✗"
        print(f"{status} Sample {features} -> Predicted: {pred}, True: {true}")
    
    # Calculate accuracy
    accuracy = nb.score(X_test, y_test)
    print(f"\nTest Accuracy: {accuracy * 100:.1f}%")