"""
Date: 2026-05-27
Implemented a Markov chain text generator with variable order n-grams — feeds on sample text and spits out statistically plausible gibberish.
"""

#!/usr/bin/env python3
"""
Markov Chain Text Generator
Builds transition tables from source text and generates new text based on probability distributions.
"""

import random
from collections import defaultdict, deque
from typing import List, Tuple, Optional


class MarkovChain:
    """
    A Markov chain text generator using n-gram based state transitions.
    
    The order parameter controls how many previous tokens determine the next token.
    Higher order = more coherent but less creative output.
    """
    
    def __init__(self, order: int = 2):
        """
        Initialize the Markov chain.
        
        Args:
            order: Number of previous tokens to consider (default 2 for bigrams)
        """
        self.order = order
        # Maps state (tuple of tokens) to list of possible next tokens
        self.transitions = defaultdict(list)
        self.start_states = []  # States that can begin a sentence
        
    def train(self, text: str) -> None:
        """
        Build the transition table from input text.
        
        Args:
            text: Training text to learn patterns from
        """
        # Simple tokenization - split on whitespace and keep punctuation attached
        tokens = text.split()
        
        if len(tokens) < self.order + 1:
            raise ValueError(f"Text too short for order {self.order}")
        
        # Build transitions using a sliding window
        for i in range(len(tokens) - self.order):
            # Current state is a tuple of 'order' tokens
            state = tuple(tokens[i:i + self.order])
            next_token = tokens[i + self.order]
            
            self.transitions[state].append(next_token)
            
            # Track states that start with capital letters as potential sentence starters
            if state[0][0].isupper():
                if state not in self.start_states:
                    self.start_states.append(state)
        
        # If no capital-start states found, use any state
        if not self.start_states:
            self.start_states = list(self.transitions.keys())
    
    def generate(self, max_length: int = 50, seed_state: Optional[Tuple[str, ...]] = None) -> str:
        """
        Generate text using the learned transitions.
        
        Args:
            max_length: Maximum number of tokens to generate
            seed_state: Starting state (tuple of tokens), or None for random
            
        Returns:
            Generated text as a string
        """
        if not self.transitions:
            raise RuntimeError("Model not trained - call train() first")
        
        # Pick starting state
        if seed_state is None:
            current_state = random.choice(self.start_states)
        else:
            current_state = seed_state
            if current_state not in self.transitions:
                raise ValueError(f"Seed state {seed_state} not found in model")
        
        # Start with the initial state tokens
        output = list(current_state)
        
        # Generate tokens one at a time
        for _ in range(max_length - self.order):
            # Get possible next tokens for current state
            if current_state not in self.transitions:
                # Dead end - we've reached a state with no transitions
                break
            
            possible_next = self.transitions[current_state]
            next_token = random.choice(possible_next)
            output.append(next_token)
            
            # Slide the window forward - drop first token, add new one
            current_state = tuple(list(current_state[1:]) + [next_token])
        
        return ' '.join(output)
    
    def stats(self) -> dict:
        """Return statistics about the trained model."""
        return {
            'order': self.order,
            'unique_states': len(self.transitions),
            'total_transitions': sum(len(v) for v in self.transitions.values()),
            'start_states': len(self.start_states)
        }


if __name__ == "__main__":
    # Sample training text - mix of tech and philosophy
    sample_text = """
    Python is a high-level programming language. Programming requires logic and creativity.
    Creativity flows from understanding the problem deeply. The problem space defines the solution.
    Solutions are elegant when they are simple. Simple code is maintainable code.
    Maintainable systems scale better over time. Time is the ultimate test of quality.
    Quality emerges from careful thought and iteration. Iteration reveals hidden complexity.
    Complexity should be managed not eliminated. Eliminated features often come back later.
    Later optimizations are easier with clean code. Clean architecture pays dividends forever.
    Forever is a long time in software years. Years of experience teach humility and patience.
    Patience with debugging leads to understanding. Understanding breeds better solutions.
    Python emphasizes readability and simplicity. Simplicity is the ultimate sophistication.
    """
    
    print("=" * 70)
    print("Markov Chain Text Generator Demo")
    print("=" * 70)
    
    # Train with different orders and show results
    for order in [1, 2, 3]:
        print(f"\n--- Order {order} (uses {order} previous token(s)) ---")
        
        markov = MarkovChain(order=order)
        markov.train(sample_text)
        
        # Show model stats
        stats = markov.stats()
        print(f"Model stats: {stats['unique_states']} unique states, "
              f"{stats['total_transitions']} total transitions")
        
        # Generate a couple examples
        print("\nGenerated text samples:")
        for i in range(2):
            generated = markov.generate(max_length=30)
            print(f"  {i+1}. {generated}")
    
    print("\n" + "=" * 70)
    print("Notice: Higher order = more coherent but less creative")
    print("=" * 70)