"""
Date: 2026-07-24
Implemented a Markov chain text generator that learns from input text and produces new sentences — useful for generating plausible but random text from any corpus.
"""

#!/usr/bin/env python3
"""
Markov Chain Text Generator
Builds a statistical model from input text and generates new sentences
that sound similar to the original corpus.
"""

import random
import re
from collections import defaultdict, deque
from typing import List, Dict, Tuple


class MarkovChain:
    """
    A Markov chain text generator that builds n-gram transition probabilities
    from sample text and generates new text based on those patterns.
    """
    
    def __init__(self, order: int = 2):
        """
        Initialize the Markov chain generator.
        
        Args:
            order: The number of previous words to consider when predicting the next word.
                   Higher order = more coherent but less creative output.
        """
        self.order = order
        # Using defaultdict of lists to store possible next words for each state
        self.chain: Dict[Tuple[str, ...], List[str]] = defaultdict(list)
        self.start_states: List[Tuple[str, ...]] = []
    
    def tokenize(self, text: str) -> List[str]:
        """
        Split text into words while preserving sentence-ending punctuation.
        
        Args:
            text: Input text to tokenize
            
        Returns:
            List of tokens (words and punctuation)
        """
        # Keep sentence-ending punctuation separate so we can identify sentence boundaries
        text = re.sub(r'([.!?])', r' \1', text)
        # Clean up extra whitespace
        tokens = text.split()
        return [token for token in tokens if token]
    
    def train(self, text: str) -> None:
        """
        Build the Markov chain model from the provided text.
        
        Args:
            text: Training corpus
        """
        tokens = self.tokenize(text)
        
        if len(tokens) < self.order + 1:
            raise ValueError(f"Text too short for order {self.order} Markov chain")
        
        # Use a deque as a sliding window for efficiency
        window = deque(maxlen=self.order)
        
        for i, token in enumerate(tokens):
            if i < self.order:
                window.append(token)
                continue
            
            # Current state is the last `order` words
            state = tuple(window)
            
            # Track states that start sentences (after punctuation)
            if i == self.order or tokens[i - self.order - 1] in '.!?':
                self.start_states.append(state)
            
            # Map state -> possible next words
            self.chain[state].append(token)
            window.append(token)
    
    def generate(self, length: int = 50, start_state: Tuple[str, ...] = None) -> str:
        """
        Generate new text using the trained Markov chain.
        
        Args:
            length: Maximum number of words to generate
            start_state: Optional starting state; if None, picks a random sentence start
            
        Returns:
            Generated text string
        """
        if not self.chain:
            raise RuntimeError("Model not trained yet. Call train() first.")
        
        if start_state is None:
            if not self.start_states:
                # Fallback to any random state
                current = random.choice(list(self.chain.keys()))
            else:
                current = random.choice(self.start_states)
        else:
            current = start_state
        
        result = list(current)
        
        for _ in range(length - self.order):
            if current not in self.chain:
                # Dead end - try to start a new sentence
                if self.start_states:
                    current = random.choice(self.start_states)
                    result.append("...")  # Indicate the jump
                    result.extend(current)
                else:
                    break
            
            # Pick a random next word based on the current state
            next_word = random.choice(self.chain[current])
            result.append(next_word)
            
            # Slide the window forward
            current = tuple(list(current)[1:] + [next_word])
            
            # Stop if we hit sentence-ending punctuation and we have enough words
            if next_word in '.!?' and len(result) > self.order * 2:
                break
        
        # Join tokens and clean up spacing around punctuation
        text = ' '.join(result)
        text = re.sub(r'\s+([.!?,;:])', r'\1', text)
        return text


if __name__ == "__main__":
    # Demo with a sample corpus - using some classic literature excerpts
    sample_text = """
    It was the best of times, it was the worst of times. It was the age of wisdom,
    it was the age of foolishness. It was the epoch of belief, it was the epoch of
    incredulity. It was the season of light, it was the season of darkness.
    
    Call me Ishmael. Some years ago, never mind how long precisely, having little or
    no money in my purse, and nothing particular to interest me on shore, I thought
    I would sail about a little and see the watery part of the world.
    
    All happy families are alike. Each unhappy family is unhappy in its own way.
    Everything was in confusion in the Oblonskys' house. The wife had discovered
    that the husband was carrying on an intrigue with a French girl.
    """
    
    print("=" * 60)
    print("Markov Chain Text Generator Demo")
    print("=" * 60)
    
    # Train with order 2 (bigram model)
    print("\n[Training order-2 model...]")
    markov_2 = MarkovChain(order=2)
    markov_2.train(sample_text)
    
    print("\nGenerated text (order=2):")
    for i in range(3):
        print(f"\n{i+1}. {markov_2.generate(length=30)}")
    
    # Train with order 1 for comparison (more random)
    print("\n" + "=" * 60)
    print("[Training order-1 model for comparison...]")
    markov_1 = MarkovChain(order=1)
    markov_1.train(sample_text)
    
    print("\nGenerated text (order=1, more random):")
    for i in range(3):
        print(f"\n{i+1}. {markov_1.generate(length=30)}")
    
    print("\n" + "=" * 60)
    print("Done! Higher order = more coherent, lower order = more creative chaos")