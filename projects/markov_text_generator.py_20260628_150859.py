"""
Date: 2026-06-28
Implemented a Markov chain text generator that builds n-gram probability models from input text and generates new sentences that sound similar to the training data.
"""

#!/usr/bin/env python3
"""
Markov Chain Text Generator

Builds a probabilistic model from input text and generates new sentences.
I wanted something that could mimic writing styles without being too complicated.
"""

import random
import re
from collections import defaultdict, Counter
from typing import List, Tuple, Optional


class MarkovChain:
    """
    N-gram based Markov chain for text generation.
    
    The state is a tuple of (order) words, and we track which words
    can follow each state. This lets us generate text that follows
    similar patterns to the training data.
    """
    
    def __init__(self, order: int = 2):
        """
        Initialize the Markov chain.
        
        Args:
            order: Number of words to use as context (higher = more coherent but less creative)
        """
        self.order = order
        # Maps state tuples to possible next words with counts
        self.transitions = defaultdict(Counter)
        # Track starting states for sentence generation
        self.start_states = []
    
    def tokenize(self, text: str) -> List[str]:
        """
        Break text into tokens (words and punctuation).
        
        I'm using a simple regex that keeps contractions together
        but splits on whitespace and most punctuation.
        """
        # Split on whitespace and capture punctuation as separate tokens
        tokens = re.findall(r"\w+(?:'\w+)?|[.,!?;:]", text)
        return tokens
    
    def train(self, text: str) -> None:
        """
        Build the Markov model from training text.
        
        We slide a window across the tokens, using each window as a state
        and recording what word comes next.
        """
        tokens = self.tokenize(text)
        
        if len(tokens) < self.order + 1:
            raise ValueError(f"Text too short for order {self.order}")
        
        # Build transitions by sliding a window
        for i in range(len(tokens) - self.order):
            # Current state is a tuple of 'order' words
            state = tuple(tokens[i:i + self.order])
            next_word = tokens[i + self.order]
            
            # Track this transition
            self.transitions[state][next_word] += 1
            
            # If this state starts with a capital letter, it could start a sentence
            if state[0][0].isupper():
                self.start_states.append(state)
    
    def generate(self, max_length: int = 50, seed_state: Optional[Tuple[str, ...]] = None) -> str:
        """
        Generate new text using the trained model.
        
        Args:
            max_length: Maximum number of words to generate
            seed_state: Optional starting state (randomly chosen if None)
        
        Returns:
            Generated text string
        """
        if not self.transitions:
            raise ValueError("Model not trained yet - call train() first")
        
        # Pick a random starting state if none provided
        if seed_state is None:
            if not self.start_states:
                # Fallback to any state if we don't have sentence starters
                current_state = random.choice(list(self.transitions.keys()))
            else:
                current_state = random.choice(self.start_states)
        else:
            current_state = seed_state
        
        # Start with the words from the initial state
        result = list(current_state)
        
        # Generate words one at a time
        for _ in range(max_length - self.order):
            if current_state not in self.transitions:
                # Dead end - stop generating
                break
            
            # Get possible next words and their counts
            next_words = self.transitions[current_state]
            
            # Choose weighted random next word
            # (words that appeared more often are more likely)
            words = list(next_words.keys())
            weights = list(next_words.values())
            next_word = random.choices(words, weights=weights)[0]
            
            result.append(next_word)
            
            # Shift the state window forward
            current_state = tuple(result[-self.order:])
            
            # Stop at sentence-ending punctuation sometimes
            if next_word in '.!?' and random.random() < 0.3:
                break
        
        # Join tokens with appropriate spacing
        # (punctuation shouldn't have a space before it)
        text = ""
        for i, token in enumerate(result):
            if i == 0:
                text = token
            elif token in '.,!?;:':
                text += token
            else:
                text += " " + token
        
        return text


if __name__ == "__main__":
    # Demo with some sample text about programming
    # (I'm using something I might actually write in a README)
    sample_text = """
    Python is a great language for quick prototypes. I love using Python
    because the syntax is clean and readable. When I write Python code,
    I try to keep things simple. Simple is better than complex, as the
    Zen of Python says. Python makes it easy to build tools quickly.
    The standard library has so much useful stuff. I find myself reaching
    for Python whenever I need to automate something. Python scripts are
    perfect for automation tasks. Writing clean code matters more than
    clever tricks. I prefer readable code over short code. Python lets
    me focus on solving problems instead of fighting the language.
    """
    
    print("=== Markov Chain Text Generator ===\n")
    
    # Train with order 2 (bigram context)
    print("Training model with order=2...")
    markov = MarkovChain(order=2)
    markov.train(sample_text)
    
    print(f"Learned {len(markov.transitions)} state transitions\n")
    
    # Generate a few examples
    print("Generated text samples:\n")
    for i in range(5):
        generated = markov.generate(max_length=20)
        print(f"{i+1}. {generated}\n")
    
    # Show what happens with higher order
    print("\n--- With order=3 (more context, closer to original) ---\n")
    markov3 = MarkovChain(order=3)
    markov3.train(sample_text)
    
    for i in range(3):
        generated = markov3.generate(max_length=25)
        print(f"{i+1}. {generated}\n")