"""
Date: 2026-06-09
Created a Markov chain generator that learns from input text and generates semi-coherent sentences while respecting word boundaries and basic punctuation.
"""

#!/usr/bin/env python3
"""
Markov Chain Text Generator
Builds a probabilistic model from input text and generates new sentences.
I wanted something that could learn writing style without being too random.
"""

import random
import re
from collections import defaultdict, Counter
from typing import List, Tuple


class MarkovChainGenerator:
    """
    A Markov chain text generator that learns patterns from input text.
    Uses configurable n-gram order to control coherence vs creativity tradeoff.
    """
    
    def __init__(self, order: int = 2):
        """
        Initialize the generator with specified chain order.
        
        Args:
            order: Number of words to use as state (higher = more coherent but less creative)
        """
        self.order = order
        # Using defaultdict of Counters makes probability calculation cleaner
        self.chain = defaultdict(Counter)
        self.start_states = []  # Track valid sentence beginnings
        
    def tokenize(self, text: str) -> List[str]:
        """
        Split text into words while preserving sentence-ending punctuation.
        I'm treating punctuation as separate tokens so generated text has structure.
        """
        # Split on whitespace but keep punctuation attached or separate
        tokens = re.findall(r'\w+|[.,!?;]', text)
        return tokens
    
    def train(self, text: str) -> None:
        """
        Build the Markov chain from training text.
        Learns which words typically follow given sequences.
        """
        tokens = self.tokenize(text)
        
        if len(tokens) < self.order + 1:
            raise ValueError(f"Text too short for order {self.order}")
        
        # Build the chain by sliding a window through the text
        for i in range(len(tokens) - self.order):
            # Current state is a tuple of 'order' words
            state = tuple(tokens[i:i + self.order])
            next_word = tokens[i + self.order]
            
            # Track this transition
            self.chain[state][next_word] += 1
            
            # Remember states that start sentences (begin with capital letter)
            if i == 0 or tokens[i - 1] in '.!?':
                if state not in self.start_states and state[0][0].isupper():
                    self.start_states.append(state)
    
    def _choose_next_word(self, state: Tuple[str, ...]) -> str:
        """
        Randomly select next word based on learned probabilities.
        Uses weighted random choice to respect frequency patterns.
        """
        if state not in self.chain:
            # Fallback if we hit an unknown state
            return random.choice(['.', '!', '?'])
        
        # Get all possible next words and their counts
        possibilities = self.chain[state]
        words = list(possibilities.keys())
        weights = list(possibilities.values())
        
        # Weighted random choice based on how often each word appeared
        return random.choices(words, weights=weights)[0]
    
    def generate(self, max_length: int = 50, sentences: int = 3) -> str:
        """
        Generate new text based on learned patterns.
        
        Args:
            max_length: Maximum words per sentence
            sentences: Number of sentences to generate
        
        Returns:
            Generated text string
        """
        if not self.start_states:
            raise RuntimeError("Must train the model before generating text")
        
        result = []
        
        for _ in range(sentences):
            # Start with a random valid beginning
            current_state = list(random.choice(self.start_states))
            sentence = list(current_state)
            
            # Generate until we hit punctuation or max length
            for _ in range(max_length):
                next_word = self._choose_next_word(tuple(current_state))
                sentence.append(next_word)
                
                # Stop at sentence-ending punctuation
                if next_word in '.!?':
                    break
                
                # Slide the window: drop first word, add new one
                current_state = current_state[1:] + [next_word]
            
            # Join tokens, fixing spacing around punctuation
            sentence_text = ' '.join(sentence)
            sentence_text = re.sub(r'\s+([.,!?;])', r'\1', sentence_text)
            result.append(sentence_text)
        
        return ' '.join(result)


if __name__ == "__main__":
    # Demo with some sample text about programming (very meta)
    training_text = """
    Programming is the art of telling a computer what to do. Computers are very good at 
    following instructions. However, computers are also very literal. They will do exactly 
    what you tell them to do. If you make a mistake, the computer will make the same mistake.
    Writing good code is difficult. Good code is readable and maintainable. Bad code is a 
    nightmare to work with. Always write comments to explain your thinking. Future you will 
    thank present you. Testing is important because bugs are inevitable. Every programmer 
    makes mistakes. The best programmers test their code thoroughly. Debugging is twice as 
    hard as writing code. If you write clever code, you won't be able to debug it.
    Simplicity is the ultimate sophistication. Make it work, then make it better. Premature 
    optimization is the root of all evil. But optimization is still important when it matters.
    """
    
    print("=== Markov Chain Text Generator Demo ===\n")
    print("Training on sample text about programming...\n")
    
    # Create and train the generator
    generator = MarkovChainGenerator(order=2)
    generator.train(training_text)
    
    print("Generated text (order=2):")
    print("-" * 60)
    generated = generator.generate(max_length=40, sentences=5)
    print(generated)
    print("-" * 60)
    
    # Show how order affects output
    print("\n\nComparing different orders:\n")
    
    for order in [1, 2, 3]:
        gen = MarkovChainGenerator(order=order)
        gen.train(training_text)
        text = gen.generate(max_length=30, sentences=2)
        print(f"Order {order}: {text}\n")
    
    print("\nNote: Lower order = more random, higher order = more coherent but repetitive")