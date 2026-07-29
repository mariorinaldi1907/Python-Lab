"""
Date: 2026-07-29
Built a Gaussian Naive Bayes classifier to see how probabilities combine for predictions — handles continuous features and multiple classes.
"""

#!/usr/bin/env python3
"""
Naive Bayes Classifier - Gaussian variant for continuous features.

I wanted to understand how Naive Bayes actually works under the hood, so I built
this from scratch. It assumes features are normally distributed (Gaussian), which
works surprisingly well for a lot of real-world data.

The "naive" part means we assume features are independent given the class label,
which is rarely true but still gives good results in practice.
"""

import math
from collections import defaultdict


class GaussianNaiveBayes:
    """
    A Gaussian Naive Bayes classifier that works with continuous features.
    
    Uses Maximum Likelihood Estimation to learn mean and variance for each
    feature per class, then applies Bayes' theorem for predictions.
    """
    
    def __init__(self):
        """Initialize empty model parameters."""
        self.classes = []
        self.class_priors = {}  # P(class)
        self.feature_params = {}  # mean and std dev for each feature per class
        
    def fit(self, X, y):
        """
        Train the model on feature matrix X and labels y.
        
        Args:
            X: List of feature vectors (each a list of numbers)
            y: List of class labels (corresponding to each row in X)
        
        For each class, we calculate:
        - Prior probability (how often this class appears)
        - Mean and standard deviation for each feature
        """
        # Group samples by class
        class_samples = defaultdict(list)
        for features, label in zip(X, y):
            class_samples[label].append(features)
        
        self.classes = sorted(class_samples.keys())
        n_total = len(y)
        n_features = len(X[0])
        
        # Calculate priors and feature statistics for each class
        for cls in self.classes:
            samples = class_samples[cls]
            n_samples = len(samples)
            
            # Prior: P(class) = count(class) / total_count
            self.class_priors[cls] = n_samples / n_total
            
            # For each feature, calculate mean and std dev
            self.feature_params[cls] = []
            for feature_idx in range(n_features):
                values = [sample[feature_idx] for sample in samples]
                mean = sum(values) / len(values)
                
                # Calculate standard deviation
                # Using n-1 for Bessel's correction (unbiased estimator)
                variance = sum((x - mean) ** 2 for x in values) / max(len(values) - 1, 1)
                std_dev = math.sqrt(variance)
                
                # Prevent zero std dev (would cause division by zero)
                std_dev = max(std_dev, 1e-6)
                
                self.feature_params[cls].append({'mean': mean, 'std': std_dev})
    
    def _calculate_probability(self, x, mean, std):
        """
        Calculate Gaussian probability density for value x.
        
        This is the formula for a normal distribution's PDF.
        We use this to estimate P(feature_value | class).
        """
        exponent = math.exp(-((x - mean) ** 2) / (2 * std ** 2))
        return (1 / (math.sqrt(2 * math.pi) * std)) * exponent
    
    def predict_proba(self, features):
        """
        Calculate posterior probabilities for each class given features.
        
        Returns a dict mapping each class to its probability.
        
        We're calculating P(class | features) using Bayes' theorem:
        P(class | features) ∝ P(class) * P(features | class)
        
        The "naive" assumption lets us decompose:
        P(features | class) = P(f1 | class) * P(f2 | class) * ...
        """
        posteriors = {}
        
        for cls in self.classes:
            # Start with the prior probability
            log_prob = math.log(self.class_priors[cls])
            
            # Multiply by likelihood of each feature
            # Using log probabilities to avoid numerical underflow
            for idx, value in enumerate(features):
                params = self.feature_params[cls][idx]
                likelihood = self._calculate_probability(
                    value, params['mean'], params['std']
                )
                # Add log instead of multiplying (log(a*b) = log(a) + log(b))
                log_prob += math.log(likelihood + 1e-10)  # tiny epsilon to avoid log(0)
            
            posteriors[cls] = log_prob
        
        # Convert back from log space and normalize
        # Find max for numerical stability
        max_log = max(posteriors.values())
        for cls in posteriors:
            posteriors[cls] = math.exp(posteriors[cls] - max_log)
        
        # Normalize to get proper probabilities
        total = sum(posteriors.values())
        for cls in posteriors:
            posteriors[cls] /= total
        
        return posteriors
    
    def predict(self, X):
        """
        Predict class labels for feature matrix X.
        
        Returns the class with highest posterior probability for each sample.
        """
        predictions = []
        for features in X:
            proba = self.predict_proba(features)
            predicted_class = max(proba, key=proba.get)
            predictions.append(predicted_class)
        return predictions


if __name__ == "__main__":
    # Demo with a simple 2D dataset (like height and weight predicting gender)
    print("=== Gaussian Naive Bayes Classifier Demo ===\n")
    
    # Training data: [height_cm, weight_kg] -> gender
    # Made up data, but roughly based on realistic distributions
    X_train = [
        [180, 75], [175, 70], [185, 80], [178, 73], [182, 77],  # male
        [165, 55], [160, 52], [170, 60], [162, 54], [168, 58],  # female
        [183, 78], [176, 72], [181, 76],                        # male
        [163, 53], [166, 56], [169, 59]                         # female
    ]
    
    y_train = ['M', 'M', 'M', 'M', 'M', 
               'F', 'F', 'F', 'F', 'F',
               'M', 'M', 'M',
               'F', 'F', 'F']
    
    # Train the model
    model = GaussianNaiveBayes()
    model.fit(X_train, y_train)
    
    print("Model trained on {} samples".format(len(y_train)))
    print("Classes: {}".format(model.classes))
    print("\nClass priors:")
    for cls, prior in model.class_priors.items():
        print(f"  P({cls}) = {prior:.3f}")
    
    # Test predictions
    print("\n--- Predictions ---")
    X_test = [
        [179, 74],  # Should predict M
        [164, 54],  # Should predict F
        [172, 65],  # Borderline case
    ]
    
    for features in X_test:
        proba = model.predict_proba(features)
        prediction = max(proba, key=proba.get)
        print(f"\nFeatures: height={features[0]}cm, weight={features[1]}kg")
        print(f"Predicted: {prediction}")
        print(f"Probabilities: M={proba['M']:.3f}, F={proba['F']:.3f}")
    
    # Calculate training accuracy
    predictions = model.predict(X_train)
    correct = sum(1 for pred, true in zip(predictions, y_train) if pred == true)
    accuracy = correct / len(y_train)
    print(f"\nTraining accuracy: {accuracy:.1%}")
```