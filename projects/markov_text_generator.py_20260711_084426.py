"""
Date: 2026-07-11
Created a Markov chain text generator that learns from input text and generates plausible-sounding sentences using n-grams of configurable order.
"""

#!/usr/bin/env python3
"""
Markov Chain Text Generator

Builds a probabilistic model from input text and generates new text
that mimics the style and patterns of the original.
"""

import random
import re
from collections import defaultdict, Counter
from typing import List, Tuple, Dict


class MarkovChain:
    """
    N-gram based Markov chain for text generation.
    
    The order determines how many previous tokens influence the next token.
    Higher order = more coherent but less creative output.
    """
    
    def __init__(self, order: int = 2):
        """
        Initialize the Markov chain.
        
        Args:
            order: Number of previous tokens to consider (n-gram size - 1)
        """
        self.order = order
        # Maps n-grams to possible next tokens with frequencies
        self.transitions: Dict[Tuple[str, ...], Counter] = defaultdict(Counter)
        # Store starting n-grams to seed generation
        self.start_states: List[Tuple[str, ...]] = []
    
    def tokenize(self, text: str) -> List[str]:
        """
        Split text into tokens (words and punctuation).
        
        I'm keeping punctuation separate so the generated text has
        better sentence structure.
        """
        # Split on whitespace but keep punctuation as separate tokens
        tokens = re.findall(r'\w+|[.,!?;:]', text.lower())
        return tokens
    
    def train(self, text: str) -> None:
        """
        Build the transition probability model from input text.
        
        Args:
            text: Training corpus
        """
        tokens = self.tokenize(text)
        
        if len(tokens) <= self.order:
            raise ValueError(f"Text too short for order {self.order}")
        
        # Build n-grams and their transitions
        for i in range(len(tokens) - self.order):
            # Current state is an n-gram of 'order' tokens
            current_state = tuple(tokens[i:i + self.order])
            next_token = tokens[i + self.order]
            
            # Track this transition
            self.transitions[current_state][next_token] += 1
            
            # Remember potential starting states (beginning of sentences)
            if i == 0 or tokens[i - 1] in '.!?':
                self.start_states.append(current_state)
    
    def _choose_next_token(self, state: Tuple[str, ...]) -> str:
        """
        Pick the next token based on weighted probabilities.
        
        Args:
            state: Current n-gram state
            
        Returns:
            Next token chosen probabilistically
        """
        if state not in self.transitions:
            # Fallback to random start if we hit an unknown state
            return random.choice(list(self.transitions.keys()))[0]
        
        # Get all possible next tokens with their frequencies
        choices = self.transitions[state]
        tokens = list(choices.keys())
        weights = list(choices.values())
        
        # Use weighted random selection
        return random.choices(tokens, weights=weights)[0]
    
    def generate(self, length: int = 50, seed_state: Tuple[str, ...] = None) -> str:
        """
        Generate new text using the trained model.
        
        Args:
            length: Approximate number of tokens to generate
            seed_state: Optional starting n-gram (chosen randomly if None)
            
        Returns:
            Generated text as a string
        """
        if not self.transitions:
            raise ValueError("Model not trained yet. Call train() first.")
        
        # Pick starting state
        if seed_state is None:
            current_state = random.choice(self.start_states if self.start_states 
                                         else list(self.transitions.keys()))
        else:
            current_state = seed_state
        
        # Start with the initial state
        result = list(current_state)
        
        # Generate tokens one at a time
        for _ in range(length):
            next_token = self._choose_next_token(current_state)
            result.append(next_token)
            
            # Slide the window forward
            current_state = tuple(result[-self.order:])
        
        # Format output - add spaces except before punctuation
        formatted = []
        for i, token in enumerate(result):
            if i == 0:
                formatted.append(token.capitalize())
            elif token in '.,!?;:':
                formatted.append(token)
            else:
                formatted.append(' ' + token)
        
        return ''.join(formatted)


if __name__ == "__main__":
    # Sample training text - using some classic literature
    training_text = """
    It was the best of times, it was the worst of times, it was the age of wisdom,
    it was the age of foolishness, it was the epoch of belief, it was the epoch of
    incredulity, it was the season of light, it was the season of darkness, it was
    the spring of hope, it was the winter of despair. We had everything before us,
    we had nothing before us. We were all going direct to heaven, we were all going
    direct the other way. In short, the period was so far like the present period,
    that some of its noisiest authorities insisted on its being received, for good
    or for evil, in the superlative degree of comparison only.
    """
    
    print("=== Markov Chain Text Generator ===\n")
    
    # Test with different orders to show the effect
    for order in [1, 2, 3]:
        print(f"--- Order {order} (considers previous {order} token(s)) ---")
        markov = MarkovChain(order=order)
        markov.train(training_text)
        
        # Generate a couple of samples
        for i in range(2):
            generated = markov.generate(length=30)
            print(f"Sample {i+1}: {generated}")
        print()