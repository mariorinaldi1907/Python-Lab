"""
Date: 2026-06-09
Built a multinomial Naive Bayes classifier to finally understand how probabilistic text classification actually works under the hood.
"""

#!/usr/bin/env python3
"""
Naive Bayes classifier implementation from scratch.
Uses multinomial model with Laplace smoothing for text classification.
"""

import math
from collections import defaultdict, Counter


class NaiveBayesClassifier:
    """
    Multinomial Naive Bayes classifier for text classification.
    
    Uses Laplace (add-one) smoothing to handle unseen words gracefully.
    Stores log probabilities internally to avoid numerical underflow.
    """
    
    def __init__(self, alpha=1.0):
        """
        Initialize the classifier.
        
        Args:
            alpha: Smoothing parameter (default 1.0 for Laplace smoothing)
        """
        self.alpha = alpha
        self.class_counts = Counter()  # How many docs per class
        self.class_word_counts = defaultdict(Counter)  # Word frequencies per class
        self.vocabulary = set()  # All unique words seen during training
        self.class_log_priors = {}  # Log P(class)
        self.total_docs = 0
        
    def _tokenize(self, text):
        """
        Simple whitespace tokenization with lowercasing.
        
        In a real system I'd use better tokenization, but keeping it simple here.
        """
        return text.lower().split()
    
    def fit(self, documents, labels):
        """
        Train the classifier on labeled documents.
        
        Args:
            documents: List of text strings
            labels: List of corresponding class labels
        """
        if len(documents) != len(labels):
            raise ValueError("Documents and labels must have the same length")
        
        self.total_docs = len(documents)
        
        # Count everything we need for probability calculations
        for doc, label in zip(documents, labels):
            self.class_counts[label] += 1
            tokens = self._tokenize(doc)
            
            for token in tokens:
                self.vocabulary.add(token)
                self.class_word_counts[label][token] += 1
        
        # Pre-compute log priors for each class
        # P(class) = count(class) / total_docs
        for label in self.class_counts:
            self.class_log_priors[label] = math.log(
                self.class_counts[label] / self.total_docs
            )
    
    def _calculate_log_likelihood(self, word, label):
        """
        Calculate log P(word | class) with Laplace smoothing.
        
        This is where the "naive" assumption comes in — we assume
        words are independent given the class, which isn't true but works well.
        """
        word_count = self.class_word_counts[label][word]
        total_words_in_class = sum(self.class_word_counts[label].values())
        vocab_size = len(self.vocabulary)
        
        # Laplace smoothing: add alpha to numerator, alpha * vocab_size to denominator
        probability = (word_count + self.alpha) / (
            total_words_in_class + self.alpha * vocab_size
        )
        
        return math.log(probability)
    
    def predict(self, document):
        """
        Predict the most likely class for a document.
        
        Returns the class with the highest posterior probability.
        """
        tokens = self._tokenize(document)
        class_scores = {}
        
        for label in self.class_counts:
            # Start with log prior
            log_prob = self.class_log_priors[label]
            
            # Add log likelihood for each word
            # We only consider words we've seen during training
            for token in tokens:
                if token in self.vocabulary:
                    log_prob += self._calculate_log_likelihood(token, label)
            
            class_scores[label] = log_prob
        
        # Return class with highest log probability
        return max(class_scores, key=class_scores.get)
    
    def predict_proba(self, document):
        """
        Get probability distribution over all classes.
        
        Returns a dict mapping each class to its probability.
        """
        tokens = self._tokenize(document)
        log_probs = {}
        
        for label in self.class_counts:
            log_prob = self.class_log_priors[label]
            for token in tokens:
                if token in self.vocabulary:
                    log_prob += self._calculate_log_likelihood(token, label)
            log_probs[label] = log_prob
        
        # Convert log probs back to probabilities using exp
        # Subtract max for numerical stability
        max_log_prob = max(log_probs.values())
        probs = {
            label: math.exp(log_prob - max_log_prob)
            for label, log_prob in log_probs.items()
        }
        
        # Normalize to sum to 1
        total = sum(probs.values())
        return {label: prob / total for label, prob in probs.items()}


if __name__ == "__main__":
    # Simple sentiment analysis demo
    # Training data: movie reviews
    train_docs = [
        "this movie is great amazing wonderful",
        "loved this film fantastic acting",
        "best movie ever brilliant performance",
        "terrible movie worst film ever",
        "awful acting horrible plot",
        "hated it boring and bad",
        "not good disappointing waste of time",
    ]
    
    train_labels = [
        "positive",
        "positive", 
        "positive",
        "negative",
        "negative",
        "negative",
        "negative",
    ]
    
    # Train the classifier
    print("Training Naive Bayes classifier...")
    classifier = NaiveBayesClassifier(alpha=1.0)
    classifier.fit(train_docs, train_labels)
    
    print(f"Vocabulary size: {len(classifier.vocabulary)}")
    print(f"Classes: {list(classifier.class_counts.keys())}\n")
    
    # Test on new reviews
    test_docs = [
        "this film is amazing and wonderful",
        "terrible waste of time",
        "brilliant and fantastic",
        "boring and awful movie",
    ]
    
    print("Predictions on test documents:\n")
    for doc in test_docs:
        prediction = classifier.predict(doc)
        probas = classifier.predict_proba(doc)
        
        print(f"Document: '{doc}'")
        print(f"Predicted: {prediction}")
        print(f"Probabilities: {probas}")
        print()