"""
Date: 2026-06-11
Created a Markov chain generator that learns from input text and produces semi-coherent random output — useful for prototyping chatbots or just having fun with language models.
"""

#!/usr/bin/env python3
"""
Markov Chain Text Generator
Reads text, builds transition probabilities, generates new text.
I wanted something lightweight to experiment with text generation before diving into neural nets.
"""

import random
import re
from collections import defaultdict, deque


class MarkovChain:
    """
    Markov chain text generator with configurable order (n-gram size).
    
    Higher order = more coherent but less creative output.
    I usually use order=2 for a good balance.
    """
    
    def __init__(self, order=2):
        """
        Initialize the Markov chain.
        
        Args:
            order: Number of previous tokens to consider (default 2 for trigrams)
        """
        self.order = order
        # Maps a tuple of N tokens -> list of possible next tokens
        self.transitions = defaultdict(list)
        # Store sentence starters separately for better generation
        self.starters = []
    
    def tokenize(self, text):
        """
        Split text into tokens, preserving sentence boundaries.
        
        I'm keeping punctuation attached to words because it helps maintain
        sentence structure in the generated text.
        """
        # Split on whitespace but keep punctuation
        tokens = text.split()
        return tokens
    
    def train(self, text):
        """
        Learn transition probabilities from training text.
        
        Args:
            text: Input string to learn from
        """
        tokens = self.tokenize(text)
        
        if len(tokens) < self.order + 1:
            # Not enough data to build meaningful chains
            return
        
        # Build the transition table
        # Using a sliding window approach
        for i in range(len(tokens) - self.order):
            # Current state is a tuple of 'order' tokens
            state = tuple(tokens[i:i + self.order])
            next_token = tokens[i + self.order]
            
            self.transitions[state].append(next_token)
            
            # Track potential sentence starters
            # Looking for capitalized words or tokens after sentence-ending punctuation
            if i == 0 or any(tokens[i-1].endswith(p) for p in '.!?'):
                self.starters.append(state)
    
    def generate(self, max_length=50, seed=None):
        """
        Generate new text using the learned model.
        
        Args:
            max_length: Maximum number of tokens to generate
            seed: Optional starting state (tuple of tokens), uses random starter if None
            
        Returns:
            Generated text as a string
        """
        if not self.transitions:
            return ""
        
        # Pick a starting state
        if seed and seed in self.transitions:
            current_state = seed
        elif self.starters:
            # Prefer sentence starters for more natural output
            current_state = random.choice(self.starters)
        else:
            current_state = random.choice(list(self.transitions.keys()))
        
        result = list(current_state)
        
        # Generate tokens until we hit max_length or run out of transitions
        for _ in range(max_length - self.order):
            if current_state not in self.transitions:
                # Dead end, stop generating
                break
            
            # Pick next token based on current state
            next_token = random.choice(self.transitions[current_state])
            result.append(next_token)
            
            # Update state by sliding the window forward
            current_state = tuple(result[-self.order:])
            
            # Stop at sentence boundaries sometimes for more natural breaks
            if next_token.endswith(('.', '!', '?')) and random.random() < 0.3:
                break
        
        return ' '.join(result)


def demo():
    """
    Demo the Markov chain with some sample text.
    Using Shakespeare because it's classic and generates funny results.
    """
    sample_text = """
    To be or not to be, that is the question. Whether tis nobler in the mind to suffer
    the slings and arrows of outrageous fortune, or to take arms against a sea of troubles
    and by opposing end them. To die, to sleep, no more, and by a sleep to say we end
    the heartache and the thousand natural shocks that flesh is heir to. Tis a consummation
    devoutly to be wished. To die, to sleep, to sleep perchance to dream, aye there's the rub.
    For in that sleep of death what dreams may come when we have shuffled off this mortal coil
    must give us pause. There's the respect that makes calamity of so long life.
    """
    
    print("=== Markov Chain Text Generator Demo ===\n")
    print("Training on Shakespeare's Hamlet soliloquy...\n")
    
    # Try different orders to show the effect
    for order in [1, 2, 3]:
        print(f"--- Order {order} (looking back {order} token{'s' if order > 1 else ''}) ---")
        
        chain = MarkovChain(order=order)
        chain.train(sample_text)
        
        # Generate a few samples
        for i in range(3):
            generated = chain.generate(max_length=30)
            print(f"  Sample {i+1}: {generated}")
        
        print()
    
    print("Notice how higher order = more coherent but less creative!")
    print("Order 1 is chaotic, order 3 basically quotes the original.")


if __name__ == "__main__":
    demo()