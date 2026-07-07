"""
Date: 2026-07-07
Built a Markov chain text generator that learns from input text and produces semi-coherent output — playing around with n-grams was fun.
"""

#!/usr/bin/env python3
"""
Markov Chain Text Generator

Builds a statistical model from input text and generates new text
that mimics the original style. Uses n-grams to predict what word
should come next based on the previous n-1 words.
"""

import random
from collections import defaultdict
from typing import List, Dict, Tuple


class MarkovChain:
    """
    A Markov chain text generator using n-grams.
    
    The model learns transition probabilities between sequences of words
    and uses them to generate new text that statistically resembles the input.
    """
    
    def __init__(self, order: int = 2):
        """
        Initialize the Markov chain.
        
        Args:
            order: The order of the Markov chain (n-1 in n-grams).
                   Higher order = more coherent but less creative.
        """
        self.order = order
        # Store what words can follow each n-gram
        # Using tuple keys because they're hashable (lists aren't)
        self.transitions: Dict[Tuple[str, ...], List[str]] = defaultdict(list)
        self.start_words: List[Tuple[str, ...]] = []
    
    def train(self, text: str) -> None:
        """
        Train the model on input text.
        
        Args:
            text: The training text to learn from.
        """
        # Tokenize by splitting on whitespace - simple but works
        words = text.split()
        
        if len(words) < self.order + 1:
            raise ValueError(f"Text too short for order {self.order} Markov chain")
        
        # Build n-grams and record transitions
        for i in range(len(words) - self.order):
            # Current state is a tuple of 'order' words
            state = tuple(words[i:i + self.order])
            next_word = words[i + self.order]
            
            self.transitions[state].append(next_word)
            
            # Track possible starting states (beginning of sentences ideally)
            # Here I'm just using the first n-grams, could be smarter
            if i == 0 or words[i - 1].endswith(('.', '!', '?')):
                self.start_words.append(state)
        
        # Fallback if we didn't find any sentence starts
        if not self.start_words:
            self.start_words.append(tuple(words[:self.order]))
    
    def generate(self, max_words: int = 50, seed: str = None) -> str:
        """
        Generate text using the trained model.
        
        Args:
            max_words: Maximum number of words to generate.
            seed: Optional starting phrase. If None, picks randomly.
        
        Returns:
            Generated text as a string.
        """
        if not self.transitions:
            raise RuntimeError("Model not trained yet - call train() first")
        
        # Pick starting state
        if seed:
            seed_words = seed.split()
            if len(seed_words) >= self.order:
                current_state = tuple(seed_words[-self.order:])
            else:
                # Seed too short, just use random start
                current_state = random.choice(self.start_words)
            result = list(current_state)
        else:
            current_state = random.choice(self.start_words)
            result = list(current_state)
        
        # Generate words one at a time
        for _ in range(max_words - self.order):
            if current_state not in self.transitions:
                # Dead end - no transitions available from this state
                break
            
            # Pick next word randomly from possible transitions
            next_word = random.choice(self.transitions[current_state])
            result.append(next_word)
            
            # Slide the window forward
            current_state = tuple(list(current_state[1:]) + [next_word])
        
        return ' '.join(result)


def demo_with_sample_text():
    """Run a demo showing the Markov chain in action."""
    
    # Using a chunk of public domain text for demonstration
    # This is from "The Time Machine" by H.G. Wells
    sample_text = """
    The Time Traveller for so it will be convenient to speak of him was
    expounding a recondite matter to us. His pale grey eyes shone and
    twinkled and his usually pale face was flushed and animated. The
    fire burnt brightly and the soft radiance of the incandescent lights
    in the lilies of silver caught the bubbles that flashed and passed in
    our glasses. Our chairs embracing us and caressing us rather than
    submitted to be sat upon and there was that luxurious after-dinner
    atmosphere when thought runs gracefully free of the trammels of
    precision. And he put it to us in this way marking the points with a
    lean forefinger as we sat and lazily admired his earnestness over
    this new paradox as we thought it and his fecundity.
    """
    
    print("=== Markov Chain Text Generator Demo ===\n")
    
    # Try different orders to show the difference
    for order in [1, 2, 3]:
        print(f"--- Order {order} Markov Chain ---")
        markov = MarkovChain(order=order)
        markov.train(sample_text)
        
        generated = markov.generate(max_words=40)
        print(f"Generated: {generated}\n")
    
    # Demo with seed text
    print("--- Using seed text 'The Time' ---")
    markov = MarkovChain(order=2)
    markov.train(sample_text)
    generated = markov.generate(max_words=30, seed="The Time")
    print(f"Generated: {generated}\n")


if __name__ == "__main__":
    demo_with_sample_text()