"""
Date: 2026-07-16
Created a Markov chain text generator that learns from input text and produces semi-coherent output — useful for experimenting with probabilistic language models.
"""

#!/usr/bin/env python3
"""
Markov Chain Text Generator
Builds n-gram models from input text and generates new sequences.
"""

import random
from collections import defaultdict, deque
from typing import List, Tuple, Dict


class MarkovChain:
    """
    A Markov chain text generator using n-grams.
    
    The chain learns transition probabilities from input text and can generate
    new sequences that statistically resemble the training data.
    """
    
    def __init__(self, order: int = 2):
        """
        Initialize the Markov chain.
        
        Args:
            order: The number of previous tokens to consider (n-gram size - 1).
                   order=1 is bigrams, order=2 is trigrams, etc.
        """
        self.order = order
        # Maps a state (tuple of tokens) to a list of possible next tokens
        self.transitions: Dict[Tuple[str, ...], List[str]] = defaultdict(list)
        # Store starting states (for beginning generation)
        self.start_states: List[Tuple[str, ...]] = []
    
    def train(self, text: str) -> None:
        """
        Train the model on input text.
        
        Args:
            text: The training text. Will be tokenized by whitespace.
        """
        # Simple tokenization - split on whitespace
        tokens = text.split()
        
        if len(tokens) < self.order + 1:
            raise ValueError(f"Text too short for order {self.order}")
        
        # Use a deque as a sliding window for efficiency
        window = deque(maxlen=self.order)
        
        # Initialize the window with the first 'order' tokens
        for i in range(self.order):
            window.append(tokens[i])
        
        # Remember this as a valid starting state
        self.start_states.append(tuple(window))
        
        # Slide through the text, recording transitions
        for token in tokens[self.order:]:
            state = tuple(window)
            self.transitions[state].append(token)
            window.append(token)
            
            # If this looks like a sentence start (previous token ends with punctuation),
            # remember it as a potential start state
            if len(window) == self.order and any(state[-1].endswith(p) for p in '.!?'):
                self.start_states.append(tuple(window))
    
    def generate(self, max_length: int = 50, seed_state: Tuple[str, ...] = None) -> str:
        """
        Generate text using the trained model.
        
        Args:
            max_length: Maximum number of tokens to generate
            seed_state: Optional starting state. If None, picks randomly.
        
        Returns:
            Generated text as a string
        """
        if not self.transitions:
            raise ValueError("Model hasn't been trained yet")
        
        # Pick a starting state
        if seed_state is None:
            current_state = random.choice(self.start_states if self.start_states else list(self.transitions.keys()))
        else:
            current_state = seed_state
        
        # Start with the seed state
        result = list(current_state)
        
        # Generate tokens
        for _ in range(max_length - self.order):
            if current_state not in self.transitions:
                # Dead end - no transitions from this state
                break
            
            # Pick the next token based on what we've seen follow this state
            next_token = random.choice(self.transitions[current_state])
            result.append(next_token)
            
            # Update the current state (slide the window)
            current_state = tuple(list(current_state[1:]) + [next_token])
        
        return ' '.join(result)
    
    def get_stats(self) -> Dict[str, int]:
        """Return statistics about the trained model."""
        return {
            'unique_states': len(self.transitions),
            'total_transitions': sum(len(v) for v in self.transitions.values()),
            'start_states': len(self.start_states),
        }


if __name__ == "__main__":
    # Demo with some sample text - using a classic opening
    sample_text = """
    It was the best of times it was the worst of times it was the age of wisdom
    it was the age of foolishness it was the epoch of belief it was the epoch of
    incredulity it was the season of Light it was the season of Darkness it was
    the spring of hope it was the winter of despair we had everything before us
    we had nothing before us we were all going direct to Heaven we were all going
    direct the other way in short the period was so far like the present period
    that some of its noisiest authorities insisted on its being received for good
    or for evil in the superlative degree of comparison only.
    """
    
    print("=== Markov Chain Text Generator Demo ===\n")
    
    # Train with different orders to show the difference
    for order in [1, 2, 3]:
        print(f"--- Order {order} (using {order+1}-grams) ---")
        chain = MarkovChain(order=order)
        chain.train(sample_text)
        
        stats = chain.get_stats()
        print(f"Stats: {stats['unique_states']} unique states, "
              f"{stats['total_transitions']} total transitions")
        
        # Generate a few samples
        print("\nGenerated text:")
        for i in range(2):
            generated = chain.generate(max_length=30)
            print(f"  {i+1}. {generated}")
        print()
    
    # Show what happens with custom seed
    print("--- Using custom seed state ---")
    chain = MarkovChain(order=2)
    chain.train(sample_text)
    seed = ("it", "was")
    generated = chain.generate(max_length=25, seed_state=seed)
    print(f"Starting with '{' '.join(seed)}': {generated}")