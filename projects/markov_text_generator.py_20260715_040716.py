"""
Date: 2026-07-15
Implemented a Markov chain text generator that can learn from input text and generate new plausible sentences — useful for understanding probabilistic text models.
"""

#!/usr/bin/env python3
"""
Markov Chain Text Generator

A simple implementation of a Markov chain for text generation.
The generator learns from input text and produces new sentences
that follow similar patterns. The 'order' parameter controls how
many previous words influence the next word choice.
"""

import random
import re
from collections import defaultdict, deque


class MarkovChain:
    """
    A Markov chain text generator that learns word sequences from input text.
    
    The chain stores transitions between n-grams (sequences of words) and uses
    them to generate new text that statistically resembles the input.
    """
    
    def __init__(self, order=2):
        """
        Initialize the Markov chain.
        
        Args:
            order: Number of words to consider for context (default: 2)
                   Higher order = more coherent but less creative output
        """
        self.order = order
        self.chain = defaultdict(list)
        self.start_words = []  # Store sentence starters separately
        
    def _tokenize(self, text):
        """
        Split text into sentences and words.
        
        Returns:
            List of sentences, where each sentence is a list of words
        """
        # Split on sentence boundaries (., !, ?)
        sentences = re.split(r'[.!?]+', text)
        
        tokenized = []
        for sentence in sentences:
            # Clean and split into words
            words = sentence.strip().split()
            if words:  # Only keep non-empty sentences
                tokenized.append(words)
        
        return tokenized
    
    def train(self, text):
        """
        Learn patterns from the input text.
        
        This builds the internal state transition table by analyzing
        which words follow which n-grams in the training text.
        """
        sentences = self._tokenize(text)
        
        for sentence in sentences:
            if len(sentence) < self.order:
                continue  # Skip sentences too short for our order
            
            # Store the first n words as potential sentence starters
            starter = tuple(sentence[:self.order])
            self.start_words.append(starter)
            
            # Build the chain by creating (state -> next_word) mappings
            for i in range(len(sentence) - self.order):
                # The "state" is a tuple of 'order' consecutive words
                state = tuple(sentence[i:i + self.order])
                next_word = sentence[i + self.order]
                
                # Store this transition
                self.chain[state].append(next_word)
    
    def generate(self, length=20, seed=None):
        """
        Generate new text based on learned patterns.
        
        Args:
            length: Approximate number of words to generate
            seed: Optional starting words (tuple). If None, pick randomly.
        
        Returns:
            Generated text as a string
        """
        if not self.chain:
            return "Error: Train the model first!"
        
        # Pick a starting state
        if seed and seed in self.chain:
            current_state = seed
        elif self.start_words:
            current_state = random.choice(self.start_words)
        else:
            current_state = random.choice(list(self.chain.keys()))
        
        # Build the output starting with our initial state
        result = list(current_state)
        
        # Generate words until we reach desired length
        for _ in range(length - self.order):
            if current_state not in self.chain:
                # Dead end — try to recover by picking a new starting point
                if self.start_words:
                    current_state = random.choice(self.start_words)
                else:
                    break
            
            # Pick next word based on what followed this state in training
            next_word = random.choice(self.chain[current_state])
            result.append(next_word)
            
            # Slide the window: drop first word, add the new word
            current_state = tuple(list(current_state[1:]) + [next_word])
        
        return ' '.join(result)
    
    def stats(self):
        """Return some statistics about the trained model."""
        num_states = len(self.chain)
        total_transitions = sum(len(v) for v in self.chain.values())
        avg_transitions = total_transitions / num_states if num_states > 0 else 0
        
        return {
            'order': self.order,
            'unique_states': num_states,
            'total_transitions': total_transitions,
            'avg_transitions_per_state': avg_transitions
        }


if __name__ == "__main__":
    # Demo with some classic literature text
    sample_text = """
    It was the best of times, it was the worst of times. It was the age of wisdom,
    it was the age of foolishness. It was the epoch of belief, it was the epoch of
    incredulity. It was the season of Light, it was the season of Darkness. It was
    the spring of hope, it was the winter of despair. We had everything before us,
    we had nothing before us. We were all going direct to Heaven, we were all going
    direct the other way. In short, the period was so far like the present period,
    that some of its noisiest authorities insisted on its being received, for good
    or for evil, in the superlative degree of comparison only.
    """
    
    print("=" * 60)
    print("MARKOV CHAIN TEXT GENERATOR")
    print("=" * 60)
    
    # Train with different orders to show the difference
    for order in [1, 2, 3]:
        print(f"\n--- Order {order} ---")
        markov = MarkovChain(order=order)
        markov.train(sample_text)
        
        stats = markov.stats()
        print(f"Trained on {stats['unique_states']} unique states")
        print(f"Average transitions per state: {stats['avg_transitions_per_state']:.2f}")
        print("\nGenerated text:")
        print(markov.generate(length=25))
        print()
    
    print("=" * 60)
    print("Try training on your own text for better results!")