"""
Date: 2026-06-28
Created a Markov chain generator that learns from input text and generates new sentences — I added punctuation-aware tokenization so it doesn't sound completely insane.
"""

#!/usr/bin/env python3
"""
Markov Chain Text Generator
Builds a statistical model from input text and generates new text that mimics the style.
I made this to experiment with natural language generation without any ML libraries.
"""

import random
import re
from collections import defaultdict
from typing import List, Tuple, Dict


class MarkovChain:
    """
    A Markov chain text generator that uses n-grams to predict next words.
    
    The chain_order determines how many previous words we look at when
    predicting the next one. Higher = more coherent but less creative.
    """
    
    def __init__(self, chain_order: int = 2):
        """
        Initialize the Markov chain.
        
        Args:
            chain_order: Number of words to use as state (context window)
        """
        self.chain_order = chain_order
        # Using defaultdict to avoid key checks everywhere
        self.chain: Dict[Tuple[str, ...], List[str]] = defaultdict(list)
        self.start_states: List[Tuple[str, ...]] = []
    
    def tokenize(self, text: str) -> List[str]:
        """
        Split text into words while preserving punctuation as separate tokens.
        
        I initially tried just split() but it mangled punctuation badly.
        This regex approach keeps periods/commas/etc as their own tokens.
        """
        # Split on whitespace but keep punctuation separate
        tokens = re.findall(r'\w+|[.,!?;:]', text)
        return tokens
    
    def train(self, text: str) -> None:
        """
        Build the Markov chain from training text.
        
        Args:
            text: Input text to learn from
        """
        tokens = self.tokenize(text)
        
        if len(tokens) < self.chain_order + 1:
            # Not enough data to build a chain
            return
        
        # Build n-grams: sliding window over the tokens
        for i in range(len(tokens) - self.chain_order):
            # Current state is a tuple of chain_order words
            state = tuple(tokens[i:i + self.chain_order])
            next_word = tokens[i + self.chain_order]
            
            self.chain[state].append(next_word)
            
            # Track states that start sentences (after punctuation or at beginning)
            if i == 0 or tokens[i - 1] in '.!?':
                if state not in self.start_states:
                    self.start_states.append(state)
    
    def generate(self, max_words: int = 50, seed_state: Tuple[str, ...] = None) -> str:
        """
        Generate new text using the trained Markov chain.
        
        Args:
            max_words: Maximum number of words to generate
            seed_state: Optional starting state (must match chain_order length)
        
        Returns:
            Generated text as a string
        """
        if not self.chain:
            return "Error: Chain not trained yet!"
        
        # Pick a starting state
        if seed_state and seed_state in self.chain:
            current_state = seed_state
        elif self.start_states:
            # Prefer states that start sentences
            current_state = random.choice(self.start_states)
        else:
            # Fallback to any state
            current_state = random.choice(list(self.chain.keys()))
        
        output = list(current_state)
        
        # Generate words until we hit max_words or run out of options
        for _ in range(max_words - self.chain_order):
            if current_state not in self.chain:
                # Dead end, can't continue
                break
            
            # Pick next word randomly from possibilities
            next_word = random.choice(self.chain[current_state])
            output.append(next_word)
            
            # Slide the window forward
            current_state = tuple(output[-self.chain_order:])
            
            # Stop at sentence boundaries sometimes for more natural output
            if next_word in '.!?' and random.random() < 0.3:
                break
        
        # Reconstruct text with proper spacing
        # Don't put spaces before punctuation
        result = []
        for i, token in enumerate(output):
            if token in '.,!?;:' and result:
                result[-1] += token
            else:
                result.append(token)
        
        return ' '.join(result)


if __name__ == "__main__":
    # Demo with some classic text snippets
    training_text = """
    To be or not to be, that is the question. Whether it is nobler in the mind to suffer
    the slings and arrows of outrageous fortune, or to take arms against a sea of troubles.
    All the world's a stage, and all the men and women merely players. They have their exits
    and their entrances, and one man in his time plays many parts. The quality of mercy is
    not strained. It droppeth as the gentle rain from heaven upon the place beneath.
    Some are born great, some achieve greatness, and some have greatness thrust upon them.
    The course of true love never did run smooth. What's in a name? A rose by any other name
    would smell as sweet. Brevity is the soul of wit. To thine own self be true.
    """
    
    print("=== Markov Chain Text Generator ===\n")
    print("Training on Shakespeare excerpts...\n")
    
    # Train with different chain orders to show the difference
    for order in [1, 2, 3]:
        markov = MarkovChain(chain_order=order)
        markov.train(training_text)
        
        print(f"--- Chain Order {order} ---")
        for i in range(3):
            generated = markov.generate(max_words=30)
            print(f"{i+1}. {generated}")
        print()
    
    # Show how it works with custom seed
    print("--- Using seed state 'to be' ---")
    markov = MarkovChain(chain_order=2)
    markov.train(training_text)
    seeded = markov.generate(max_words=25, seed_state=('to', 'be'))
    print(seeded)