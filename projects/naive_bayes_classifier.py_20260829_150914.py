"""
Date: 2026-08-29
Built a Naive Bayes classifier to understand probabilistic ML better — handles categorical features and includes smoothing to avoid zero probabilities.
"""

"""
Naive Bayes Classifier from scratch.

I wanted to really understand how probabilistic classifiers work under the hood,
so I built this without any ML libraries. Uses Laplace smoothing to handle
unseen feature values, which was a fun problem to solve.
"""

from collections import defaultdict
import math


class NaiveBayesClassifier:
    """
    A simple Naive Bayes classifier for categorical features.
    
    Uses Laplace (add-one) smoothing to handle zero probabilities.
    Perfect for text classification or any categorical data.
    """
    
    def __init__(self, smoothing=1.0):
        """
        Initialize the classifier.
        
        Args:
            smoothing: Laplace smoothing parameter (default 1.0)
        """
        self.smoothing = smoothing
        # Store prior probabilities for each class
        self.class_probs = {}
        # Store conditional probabilities: P(feature=value | class)
        # Structure: {class: {feature_idx: {value: count}}}
        self.feature_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        # Track total counts per class for smoothing
        self.class_counts = defaultdict(int)
        # Track unique values per feature for smoothing denominator
        self.feature_values = defaultdict(set)
        self.classes = []
        
    def fit(self, X, y):
        """
        Train the classifier on the data.
        
        Args:
            X: List of feature lists (each sample is a list of feature values)
            y: List of class labels
        """
        n_samples = len(y)
        
        # Count class occurrences for prior probabilities
        class_counts_temp = defaultdict(int)
        for label in y:
            class_counts_temp[label] += 1
        
        self.classes = list(class_counts_temp.keys())
        
        # Calculate prior probabilities: P(class)
        for cls in self.classes:
            self.class_probs[cls] = class_counts_temp[cls] / n_samples
        
        # Count feature occurrences for each class
        for sample, label in zip(X, y):
            self.class_counts[label] += len(sample)
            for feature_idx, value in enumerate(sample):
                self.feature_counts[label][feature_idx][value] += 1
                self.feature_values[feature_idx].add(value)
        
    def _calculate_conditional_prob(self, cls, feature_idx, value):
        """
        Calculate P(feature=value | class) with Laplace smoothing.
        
        The smoothing is crucial here — without it, a single unseen word
        would make the entire probability zero, which seems harsh.
        """
        count = self.feature_counts[cls][feature_idx][value]
        # Number of unique values this feature can take
        n_unique_values = len(self.feature_values[feature_idx])
        # Total count for this class + smoothing for all possible values
        total = self.class_counts[cls] + self.smoothing * n_unique_values
        
        return (count + self.smoothing) / total
    
    def predict_proba(self, sample):
        """
        Calculate probability for each class given a sample.
        
        Returns a dict of {class: probability}.
        Using log probabilities to avoid underflow with many features.
        """
        log_probs = {}
        
        for cls in self.classes:
            # Start with log of prior probability
            log_prob = math.log(self.class_probs[cls])
            
            # Multiply (add in log space) conditional probabilities
            for feature_idx, value in enumerate(sample):
                cond_prob = self._calculate_conditional_prob(cls, feature_idx, value)
                log_prob += math.log(cond_prob)
            
            log_probs[cls] = log_prob
        
        # Convert back from log space for interpretability
        # Subtract max for numerical stability
        max_log_prob = max(log_probs.values())
        probs = {}
        for cls, log_prob in log_probs.items():
            probs[cls] = math.exp(log_prob - max_log_prob)
        
        # Normalize to sum to 1
        total = sum(probs.values())
        for cls in probs:
            probs[cls] /= total
            
        return probs
    
    def predict(self, X):
        """
        Predict class labels for samples.
        
        Args:
            X: List of samples (each sample is a list of features)
            
        Returns:
            List of predicted class labels
        """
        predictions = []
        for sample in X:
            probs = self.predict_proba(sample)
            # Pick class with highest probability
            predicted_class = max(probs, key=probs.get)
            predictions.append(predicted_class)
        
        return predictions


if __name__ == "__main__":
    # Demo with a simple text classification problem
    # Features are individual words (bag of words, basically)
    
    print("=== Naive Bayes Text Classifier Demo ===\n")
    
    # Training data: simple movie reviews (positive/negative)
    # Each review is tokenized into words
    train_reviews = [
        ["love", "great", "awesome", "best"],
        ["amazing", "wonderful", "love", "excellent"],
        ["best", "great", "fantastic", "love"],
        ["terrible", "bad", "worst", "hate"],
        ["awful", "horrible", "bad", "hate"],
        ["worst", "terrible", "horrible", "disappointing"],
    ]
    
    train_labels = ["positive", "positive", "positive", 
                    "negative", "negative", "negative"]
    
    # Train the classifier
    nb = NaiveBayesClassifier(smoothing=1.0)
    nb.fit(train_reviews, train_labels)
    
    print("Training completed!")
    print(f"Classes learned: {nb.classes}\n")
    
    # Test on new reviews
    test_reviews = [
        ["love", "best", "great"],
        ["terrible", "worst", "bad"],
        ["great", "awful"],  # Mixed sentiment
        ["amazing", "fantastic"],
    ]
    
    print("Testing on new reviews:\n")
    
    for review in test_reviews:
        probs = nb.predict_proba(review)
        prediction = max(probs, key=probs.get)
        
        print(f"Review: {' '.join(review)}")
        print(f"  Predicted: {prediction}")
        print(f"  Probabilities: ", end="")
        for cls, prob in sorted(probs.items()):
            print(f"{cls}={prob:.3f} ", end="")
        print("\n")
    
    # Batch prediction
    predictions = nb.predict(test_reviews)
    print(f"Batch predictions: {predictions}")