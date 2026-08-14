"""
Date: 2026-08-14
Built a multinomial naive bayes classifier to understand probabilistic classification better — handles text data and includes smoothing to avoid zero probabilities.
"""

#!/usr/bin/env python3
"""
Naive Bayes classifier implementation from scratch.

I wanted to really understand how naive bayes works under the hood,
especially for text classification. This uses the multinomial variant
with Laplace smoothing to handle words we haven't seen before.
"""

import math
from collections import defaultdict, Counter


class NaiveBayesClassifier:
    """
    A multinomial Naive Bayes classifier for text classification.
    
    Uses Laplace (add-one) smoothing to handle unseen words gracefully.
    Works by calculating P(class|document) using Bayes' theorem and the
    naive assumption that features are independent given the class.
    """
    
    def __init__(self, alpha=1.0):
        """
        Initialize the classifier.
        
        Args:
            alpha: Smoothing parameter (default 1.0 for Laplace smoothing)
        """
        self.alpha = alpha
        self.class_counts = Counter()  # How many docs per class
        self.class_word_counts = defaultdict(Counter)  # Word counts per class
        self.class_total_words = defaultdict(int)  # Total words per class
        self.vocabulary = set()  # All unique words we've seen
        self.classes = set()
        
    def _tokenize(self, text):
        """
        Simple tokenization: lowercase and split on whitespace.
        
        In a real project I'd use something fancier, but keeping it simple.
        """
        return text.lower().split()
    
    def fit(self, documents, labels):
        """
        Train the classifier on documents and their labels.
        
        Args:
            documents: List of text documents (strings)
            labels: List of corresponding class labels
        """
        if len(documents) != len(labels):
            raise ValueError("documents and labels must have same length")
        
        # Reset everything in case fit() is called multiple times
        self.class_counts.clear()
        self.class_word_counts.clear()
        self.class_total_words.clear()
        self.vocabulary.clear()
        self.classes.clear()
        
        # Count everything we need for probability calculations
        for doc, label in zip(documents, labels):
            self.classes.add(label)
            self.class_counts[label] += 1
            
            words = self._tokenize(doc)
            for word in words:
                self.vocabulary.add(word)
                self.class_word_counts[label][word] += 1
                self.class_total_words[label] += 1
    
    def _calculate_log_probability(self, document, class_label):
        """
        Calculate log P(class|document) using Bayes' theorem.
        
        Using log probabilities to avoid numerical underflow since
        multiplying many small probabilities gets dicey.
        """
        words = self._tokenize(document)
        
        # Start with log prior probability: log P(class)
        total_docs = sum(self.class_counts.values())
        log_prob = math.log(self.class_counts[class_label] / total_docs)
        
        # Add log likelihood for each word: log P(word|class)
        vocab_size = len(self.vocabulary)
        for word in words:
            # Laplace smoothing: add alpha to numerator, alpha * vocab_size to denominator
            word_count = self.class_word_counts[class_label][word]
            total_words = self.class_total_words[class_label]
            
            # This is the smoothed probability of seeing this word in this class
            word_prob = (word_count + self.alpha) / (total_words + self.alpha * vocab_size)
            log_prob += math.log(word_prob)
        
        return log_prob
    
    def predict(self, document):
        """
        Predict the class for a single document.
        
        Returns the class with highest posterior probability.
        """
        if not self.classes:
            raise ValueError("Model not trained yet - call fit() first")
        
        # Calculate log probability for each class and pick the max
        class_log_probs = {
            cls: self._calculate_log_probability(document, cls)
            for cls in self.classes
        }
        
        return max(class_log_probs, key=class_log_probs.get)
    
    def predict_proba(self, document):
        """
        Get probability distribution over classes for a document.
        
        Returns a dict mapping class labels to probabilities.
        """
        if not self.classes:
            raise ValueError("Model not trained yet - call fit() first")
        
        # Get log probabilities
        log_probs = {
            cls: self._calculate_log_probability(document, cls)
            for cls in self.classes
        }
        
        # Convert back to probabilities using exp, then normalize
        # Subtract max for numerical stability
        max_log_prob = max(log_probs.values())
        probs = {cls: math.exp(lp - max_log_prob) for cls, lp in log_probs.items()}
        
        total = sum(probs.values())
        return {cls: p / total for cls, p in probs.items()}


if __name__ == "__main__":
    # Demo with a simple sentiment classification task
    print("=== Naive Bayes Sentiment Classifier Demo ===\n")
    
    # Training data: simple movie reviews
    train_docs = [
        "this movie was amazing and fantastic great acting",
        "loved it best film ever wonderful experience",
        "absolutely brilliant superb performances loved every minute",
        "terrible movie worst film ever seen",
        "awful acting horrible plot waste of time",
        "boring and disappointing terrible waste",
        "not great but not terrible just okay",
        "pretty good enjoyed it overall nice film",
    ]
    
    train_labels = [
        "positive", "positive", "positive",
        "negative", "negative", "negative",
        "neutral", "neutral"
    ]
    
    # Train the classifier
    clf = NaiveBayesClassifier(alpha=1.0)
    clf.fit(train_docs, train_labels)
    
    print(f"Trained on {len(train_docs)} documents")
    print(f"Vocabulary size: {len(clf.vocabulary)}")
    print(f"Classes: {sorted(clf.classes)}\n")
    
    # Test on new reviews
    test_docs = [
        "amazing film loved every second",
        "terrible and boring waste of time",
        "okay movie nothing special",
        "wonderful acting brilliant story"
    ]
    
    print("Test predictions:\n")
    for doc in test_docs:
        prediction = clf.predict(doc)
        probabilities = clf.predict_proba(doc)
        
        print(f'Review: "{doc}"')
        print(f'Predicted: {prediction}')
        print(f'Probabilities: {probabilities}')
        print()