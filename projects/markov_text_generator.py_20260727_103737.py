"""
Date: 2026-07-27
Implemented a configurable-order Markov chain text generator because I wanted to play with statistical text generation without pulling in heavy NLP libraries.
"""

#!/usr/bin/env python3
"""
Markov Chain Text Generator
Generates semi-coherent text based on statistical patterns from input text.
Supports configurable chain order for better/worse coherence.
"""

import random
import re
from collections import defaultdict, deque


class MarkovChain:
    """
    A Markov chain text generator with configurable order.
    
    Order determines how many previous words influence the next word choice.
    Higher order = more coherent but less creative, needs more training data.
    """
    
    def __init__(self, order=2):
        """
        Initialize the Markov chain.
        
        Args:
            order: Number of previous words to consider (default: 2)
        """
        self.order = order
        # Using defaultdict to auto-create lists for new states
        self.chain = defaultdict(list)
        self.start_states = []
    
    def _tokenize(self, text):
        """
        Break text into words, preserving punctuation as separate tokens.
        This gives better results than just splitting on whitespace.
        """
        # Split on word boundaries but keep punctuation
        tokens = re.findall(r'\w+|[^\w\s]', text)
        return tokens
    
    def train(self, text):
        """
        Build the Markov chain from input text.
        
        Args:
            text: Training corpus as a string
        """
        tokens = self._tokenize(text)
        
        if len(tokens) < self.order + 1:
            raise ValueError(f"Text too short for order-{self.order} chain")
        
        # Use a deque for efficient sliding window over tokens
        window = deque(maxlen=self.order)
        
        # Collect initial states (sentence starts)
        for i in range(len(tokens)):
            if i == 0 or tokens[i-1] in '.!?':
                # Found a sentence start
                if i + self.order < len(tokens):
                    start_state = tuple(tokens[i:i+self.order])
                    self.start_states.append(start_state)
        
        # Build the chain by sliding through tokens
        for token in tokens[:self.order]:
            window.append(token)
        
        for token in tokens[self.order:]:
            # Current state is the window, next token is what follows
            state = tuple(window)
            self.chain[state].append(token)
            window.append(token)
    
    def generate(self, length=50, seed_state=None):
        """
        Generate text using the trained Markov chain.
        
        Args:
            length: Approximate number of words to generate
            seed_state: Starting state (tuple of words), or None for random start
        
        Returns:
            Generated text as a string
        """
        if not self.chain:
            raise RuntimeError("Train the chain first with train() method")
        
        # Pick a random starting state if none provided
        if seed_state is None:
            if self.start_states:
                current_state = random.choice(self.start_states)
            else:
                current_state = random.choice(list(self.chain.keys()))
        else:
            current_state = seed_state
        
        result = list(current_state)
        
        # Generate tokens one by one
        for _ in range(length - self.order):
            if current_state not in self.chain:
                # Dead end - pick a new random state
                current_state = random.choice(list(self.chain.keys()))
            
            # Pick next word randomly from possibilities
            next_word = random.choice(self.chain[current_state])
            result.append(next_word)
            
            # Slide the window forward
            current_state = tuple(list(current_state[1:]) + [next_word])
        
        # Join tokens, but handle punctuation spacing properly
        text = ""
        for i, token in enumerate(result):
            if token in '.,!?;:' or (i > 0 and result[i-1] in '"('):
                text += token
            else:
                if text:
                    text += " " + token
                else:
                    text = token
        
        return text


if __name__ == "__main__":
    # Sample text - a few paragraphs about Python (meta!)
    sample_text = """
    Python is a high-level programming language. It emphasizes code readability.
    The language provides constructs that enable clear programming. Python supports
    multiple programming paradigms. It includes object-oriented and functional programming.
    Python has a comprehensive standard library. The library provides many useful modules.
    Developers love Python for its simplicity. The syntax is clean and expressive.
    Many companies use Python in production. It powers web applications and data science.
    Machine learning libraries are popular. Scientists use Python for research too.
    The community is vibrant and helpful. Documentation is thorough and accessible.
    """
    
    print("=== Markov Chain Text Generator Demo ===\n")
    
    # Demo with order-1 chain (less coherent, more random)
    print("Training Order-1 Chain (looking at 1 previous word)...")
    markov1 = MarkovChain(order=1)
    markov1.train(sample_text)
    print("Generated text:")
    print(markov1.generate(30))
    print()
    
    # Demo with order-2 chain (more coherent)
    print("Training Order-2 Chain (looking at 2 previous words)...")
    markov2 = MarkovChain(order=2)
    markov2.train(sample_text)
    print("Generated text:")
    print(markov2.generate(30))
    print()
    
    # Show the difference with a longer generation
    print("Longer generation with Order-2 chain:")
    print(markov2.generate(50))
    print()
    
    print("Note: Higher order = more coherent but needs more training data.")
    print("With this small sample, even order-2 mostly just recombines original sentences.")