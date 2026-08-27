"""
Date: 2026-08-27
Implemented a k-NN classifier without any ML libraries to really understand the distance calculations and voting mechanism under the hood.
"""

#!/usr/bin/env python3
"""
K-Nearest Neighbors Classifier from scratch.

I wanted to understand k-NN at a fundamental level, so I implemented it
using only the standard library. The core idea is simple: for a new point,
find the k closest training examples and let them vote on the class.
"""

import math
import random
from collections import Counter


class KNNClassifier:
    """
    A k-nearest neighbors classifier that uses Euclidean distance.
    
    I'm storing the raw training data because k-NN is a lazy learner — 
    there's no actual "training" phase, just memorization.
    """
    
    def __init__(self, k=3):
        """
        Initialize the classifier.
        
        Args:
            k: Number of neighbors to consider for voting
        """
        self.k = k
        self.X_train = []
        self.y_train = []
    
    def fit(self, X, y):
        """
        Store the training data.
        
        Args:
            X: List of feature vectors (each vector is a list of numbers)
            y: List of labels corresponding to each feature vector
        """
        self.X_train = X
        self.y_train = y
    
    def _euclidean_distance(self, point1, point2):
        """
        Calculate Euclidean distance between two points.
        
        I'm using the classic sqrt(sum of squared differences) formula.
        Could optimize by skipping the sqrt when only comparing distances,
        but keeping it simple for now.
        """
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(point1, point2)))
    
    def _get_neighbors(self, test_point):
        """
        Find the k nearest neighbors to a test point.
        
        Returns a list of (distance, label) tuples for the k closest points.
        """
        # Calculate distances to all training points
        distances = []
        for train_point, label in zip(self.X_train, self.y_train):
            dist = self._euclidean_distance(test_point, train_point)
            distances.append((dist, label))
        
        # Sort by distance and take the k closest
        distances.sort(key=lambda x: x[0])
        return distances[:self.k]
    
    def predict(self, X):
        """
        Predict labels for test data.
        
        Args:
            X: List of feature vectors to classify
            
        Returns:
            List of predicted labels
        """
        predictions = []
        for test_point in X:
            neighbors = self._get_neighbors(test_point)
            # Extract just the labels from the (distance, label) tuples
            neighbor_labels = [label for _, label in neighbors]
            # Vote: most common label wins
            most_common = Counter(neighbor_labels).most_common(1)[0][0]
            predictions.append(most_common)
        return predictions
    
    def score(self, X, y):
        """
        Calculate accuracy on test data.
        
        Args:
            X: Test feature vectors
            y: True labels
            
        Returns:
            Accuracy as a float between 0 and 1
        """
        predictions = self.predict(X)
        correct = sum(1 for pred, true in zip(predictions, y) if pred == true)
        return correct / len(y)


def generate_synthetic_data(n_samples=150, n_features=4, n_classes=3):
    """
    Generate synthetic data similar to the iris dataset.
    
    I'm creating clusters by picking random centers for each class,
    then generating points around those centers with some noise.
    This mimics real-world classification problems where classes
    have different characteristic features.
    """
    random.seed(42)  # For reproducibility
    
    X = []
    y = []
    
    # Generate a random center for each class
    class_centers = []
    for _ in range(n_classes):
        center = [random.uniform(0, 10) for _ in range(n_features)]
        class_centers.append(center)
    
    # Generate points around each center
    samples_per_class = n_samples // n_classes
    for class_idx, center in enumerate(class_centers):
        for _ in range(samples_per_class):
            # Add Gaussian noise around the center
            point = [c + random.gauss(0, 1.5) for c in center]
            X.append(point)
            y.append(class_idx)
    
    # Shuffle the data
    combined = list(zip(X, y))
    random.shuffle(combined)
    X, y = zip(*combined)
    
    return list(X), list(y)


def train_test_split(X, y, test_size=0.3):
    """
    Split data into training and test sets.
    
    Args:
        X: Feature vectors
        y: Labels
        test_size: Proportion of data to use for testing
        
    Returns:
        X_train, X_test, y_train, y_test
    """
    n_test = int(len(X) * test_size)
    n_train = len(X) - n_test
    
    X_train = X[:n_train]
    X_test = X[n_train:]
    y_train = y[:n_train]
    y_test = y[n_train:]
    
    return X_train, X_test, y_train, y_test


if __name__ == "__main__":
    print("K-Nearest Neighbors Classifier Demo")
    print("=" * 50)
    
    # Generate synthetic dataset
    print("\nGenerating synthetic 3-class dataset...")
    X, y = generate_synthetic_data(n_samples=150, n_features=4, n_classes=3)
    print(f"Total samples: {len(X)}")
    print(f"Features per sample: {len(X[0])}")
    print(f"Classes: {set(y)}")
    
    # Split into train and test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
    print(f"\nTraining samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")
    
    # Test different values of k
    print("\nTesting different values of k:")
    print("-" * 50)
    
    for k in [1, 3, 5, 7, 9]:
        knn = KNNClassifier(k=k)
        knn.fit(X_train, y_train)
        accuracy = knn.score(X_test, y_test)
        print(f"k={k}: Accuracy = {accuracy:.3f} ({int(accuracy * len(y_test))}/{len(y_test)} correct)")
    
    # Show some example predictions
    print("\nExample predictions (k=5):")
    print("-" * 50)
    knn = KNNClassifier(k=5)
    knn.fit(X_train, y_train)
    
    for i in range(5):
        test_point = X_test[i]
        true_label = y_test[i]
        predicted_label = knn.predict([test_point])[0]
        match = "✓" if predicted_label == true_label else "✗"
        print(f"Sample {i+1}: Predicted={predicted_label}, Actual={true_label} {match}")