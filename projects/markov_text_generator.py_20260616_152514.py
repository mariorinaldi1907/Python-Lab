"""
Date: 2026-06-16
Implemented a Markov chain generator that creates surprisingly coherent text from any input corpus — been wanting to play with this since reading about it in college.
"""

#!/usr/bin/env python3
"""
Markov Chain Text Generator
Generates semi-random text based on n-gram probabilities from input text.
I've always found Markov chains fascinating for how simple they are yet how
surprisingly coherent the output can be. This implementation lets you tune
the n-gram size (chain order) to balance between randomness and structure.
"""

import random
import re
from collections import defaultdict, Counter
from typing import List, Tuple, Dict


class MarkovChain:
    """
    A simple Markov chain text generator.
    
    The chain order determines how many previous words influence the next word.
    Higher orders = more coherent but less creative. Lower orders = more random.
    """
    
    def __init__(self, order: int = 2):
        """
        Initialize the Markov chain.
        
        Args:
            order: Number of words to use as context (default 2 = trigrams)
        """
        self.order = order
        # Maps tuple of words -> Counter of possible next words
        self.chain: Dict[Tuple[str, ...], Counter] = defaultdict(Counter)
        # Track all possible starting n-grams for sentence generation
        self.starts: List[Tuple[str, ...]] = []
    
    def tokenize(self, text: str) -> List[str]:
        """
        Split text into words, preserving sentence-ending punctuation.
        
        I'm keeping periods/question marks/exclamation marks as separate tokens
        so the generated text has some concept of sentence boundaries.
        """
        # Split on whitespace but keep sentence-ending punctuation separate
        text = re.sub(r'([.!?])', r' \1', text)
        tokens = text.split()
        return [t for t in tokens if t]  # Filter empty strings
    
    def train(self, text: str) -> None:
        """
        Build the Markov chain from training text.
        
        Args:
            text: Input text to learn from
        """
        tokens = self.tokenize(text)
        
        if len(tokens) < self.order + 1:
            raise ValueError(f"Text too short for order {self.order}")
        
        # Build n-grams and record transitions
        for i in range(len(tokens) - self.order):
            # Current state is a tuple of `order` words
            state = tuple(tokens[i:i + self.order])
            next_word = tokens[i + self.order]
            
            # Record this transition
            self.chain[state][next_word] += 1
            
            # If this state starts with a capital letter, it could start a sentence
            if state[0][0].isupper():
                self.starts.append(state)
    
    def generate(self, length: int = 50, seed: str = None) -> str:
        """
        Generate text using the trained Markov chain.
        
        Args:
            length: Maximum number of words to generate
            seed: Optional starting text (must match chain order)
        
        Returns:
            Generated text as a string
        """
        if not self.chain:
            raise ValueError("Chain not trained yet - call train() first")
        
        # Choose starting state
        if seed:
            seed_tokens = self.tokenize(seed)
            if len(seed_tokens) < self.order:
                raise ValueError(f"Seed must have at least {self.order} words")
            state = tuple(seed_tokens[-self.order:])
            if state not in self.chain:
                raise ValueError("Seed not found in training data")
        else:
            # Pick a random sentence start
            state = random.choice(self.starts) if self.starts else random.choice(list(self.chain.keys()))
        
        result = list(state)
        
        # Generate until we hit length or run out of options
        for _ in range(length - self.order):
            if state not in self.chain:
                break
            
            # Get possible next words and their frequencies
            possible_next = self.chain[state]
            # Weighted random choice based on frequency
            words = list(possible_next.keys())
            weights = list(possible_next.values())
            next_word = random.choices(words, weights=weights)[0]
            
            result.append(next_word)
            
            # Slide the window: drop first word, add new word
            state = tuple(list(state[1:]) + [next_word])
            
            # Stop at sentence boundaries sometimes for more natural output
            if next_word in '.!?' and random.random() < 0.3:
                break
        
        # Join tokens, but handle punctuation spacing properly
        text = ' '.join(result)
        text = re.sub(r'\s+([.!?,;:])', r'\1', text)  # Remove space before punctuation
        return text


if __name__ == "__main__":
    # Demo with some classic literature (public domain)
    sample_text = """
    It was the best of times, it was the worst of times, it was the age of wisdom,
    it was the age of foolishness, it was the epoch of belief, it was the epoch of
    incredulity, it was the season of Light, it was the season of Darkness, it was
    the spring of hope, it was the winter of despair. We had everything before us,
    we had nothing before us. We were all going direct to Heaven, we were all going
    direct the other way. In short, the period was so far like the present period,
    that some of its noisiest authorities insisted on its being received, for good
    or for evil, in the superlative degree of comparison only.
    """
    
    print("=== Markov Chain Text Generator Demo ===\n")
    
    # Try different chain orders
    for order in [1, 2, 3]:
        print(f"--- Order {order} (using {order}-word context) ---")
        chain = MarkovChain(order=order)
        chain.train(sample_text)
        
        generated = chain.generate(length=40)
        print(f"{generated}\n")
    
    # Show that we can seed the generation
    print("--- Seeded generation (order=2, seed='it was') ---")
    chain = MarkovChain(order=2)
    chain.train(sample_text)
    seeded = chain.generate(length=30, seed="it was")
    print(f"{seeded}\n")