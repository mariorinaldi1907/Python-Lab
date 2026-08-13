"""
Date: 2026-08-13
Created a Markov chain text generator that learns from input text and produces new sequences — wanted to experiment with n-gram modeling and see how different chain orders affect output quality.
"""

#!/usr/bin/env python3
"""
Markov Chain Text Generator

Builds n-gram models from input text and generates new text based on probability distributions.
I wanted to see how different chain orders affect coherence vs creativity.
"""

import random
import re
from collections import defaultdict, Counter
from typing import List, Tuple, Optional


class MarkovChain:
    """
    A Markov chain text generator using n-grams.
    
    The order determines how many previous tokens influence the next token.
    Higher order = more coherent but less creative output.
    """
    
    def __init__(self, order: int = 2):
        """
        Initialize the Markov chain.
        
        Args:
            order: Number of previous tokens to consider (chain order)
        """
        if order < 1:
            raise ValueError("Order must be at least 1")
        
        self.order = order
        # Using defaultdict of Counter for easy probability calculations
        self.chain = defaultdict(Counter)
        self.start_states = []  # Track valid starting n-grams
        
    def _tokenize(self, text: str) -> List[str]:
        """
        Split text into tokens (words + punctuation).
        
        I'm keeping punctuation as separate tokens because it affects rhythm.
        """
        # Split on whitespace but keep punctuation separate
        tokens = re.findall(r'\w+|[^\w\s]', text)
        return tokens
    
    def train(self, text: str) -> None:
        """
        Train the model on input text.
        
        Builds the transition probability table from n-grams.
        """
        tokens = self._tokenize(text)
        
        if len(tokens) < self.order + 1:
            raise ValueError(f"Text too short for order {self.order}")
        
        # Build n-grams and their successors
        for i in range(len(tokens) - self.order):
            # Current state is a tuple of 'order' tokens
            state = tuple(tokens[i:i + self.order])
            next_token = tokens[i + self.order]
            
            # Track this transition
            self.chain[state][next_token] += 1
            
            # First n-gram in text is a valid starting point
            if i == 0:
                self.start_states.append(state)
        
        # Also track states at sentence boundaries for better starts
        # (simplistic: after periods, exclamations, questions)
        for i in range(len(tokens) - self.order):
            if i > 0 and tokens[i - 1] in '.!?':
                state = tuple(tokens[i:i + self.order])
                if state in self.chain:  # Only if it has successors
                    self.start_states.append(state)
    
    def _choose_next_token(self, state: Tuple[str, ...]) -> Optional[str]:
        """
        Choose the next token based on the current state.
        
        Uses weighted random selection based on observed frequencies.
        """
        if state not in self.chain:
            return None
        
        # Get all possible next tokens and their counts
        possibilities = self.chain[state]
        tokens = list(possibilities.keys())
        weights = list(possibilities.values())
        
        # Weighted random choice
        return random.choices(tokens, weights=weights)[0]
    
    def generate(self, max_tokens: int = 100, start_state: Optional[Tuple[str, ...]] = None) -> str:
        """
        Generate new text using the trained model.
        
        Args:
            max_tokens: Maximum number of tokens to generate
            start_state: Optional starting state (must match order)
        
        Returns:
            Generated text as a string
        """
        if not self.chain:
            raise RuntimeError("Model not trained yet")
        
        # Pick a random starting state if none provided
        if start_state is None:
            if not self.start_states:
                start_state = random.choice(list(self.chain.keys()))
            else:
                start_state = random.choice(self.start_states)
        
        if len(start_state) != self.order:
            raise ValueError(f"Start state must have {self.order} tokens")
        
        # Begin generation
        current_state = start_state
        output = list(current_state)
        
        for _ in range(max_tokens - self.order):
            next_token = self._choose_next_token(current_state)
            
            if next_token is None:
                # Dead end, stop generation
                break
            
            output.append(next_token)
            
            # Slide the window: drop first token, add new one
            current_state = tuple(list(current_state[1:]) + [next_token])
        
        # Reconstruct text with basic spacing rules
        result = []
        for token in output:
            if token in ',.!?;:)]}':
                # No space before punctuation
                result.append(token)
            elif token in '([{':
                # Space before, but not after
                if result:
                    result.append(' ')
                result.append(token)
            else:
                # Regular token
                if result:
                    result.append(' ')
                result.append(token)
        
        return ''.join(result).strip()


if __name__ == "__main__":
    # Demo with some sample text (a mix of tech and philosophy for fun)
    sample_text = """
    The quick brown fox jumps over the lazy dog. But why does the fox jump?
    Perhaps the fox seeks adventure. Perhaps the dog seeks rest.
    In programming, we often seek elegant solutions. We build systems that scale.
    We write code that others will read. The best code is simple code.
    Simple code is maintainable code. Maintainable code makes teams happy.
    Happy teams build great products. Great products change the world.
    But the world is complex. Complexity requires careful thought.
    Careful thought takes time. Time is our most valuable resource.
    We must choose wisely what we build. We must build with purpose.
    Purpose drives innovation. Innovation creates the future.
    """
    
    print("=== Markov Chain Text Generator Demo ===\n")
    
    # Train models with different orders
    for order in [1, 2, 3]:
        print(f"--- Order {order} Model ---")
        model = MarkovChain(order=order)
        model.train(sample_text)
        
        # Generate a few samples
        for i in range(2):
            generated = model.generate(max_tokens=30)
            print(f"Sample {i+1}: {generated}")
        print()
    
    print("Notice how higher order = more coherent but less creative!")