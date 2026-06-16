"""
Date: 2026-06-16
Wrote a Markov chain generator that learns from input text and produces semi-coherent output — tracks sentence starts separately so it doesn't start mid-thought.
"""

#!/usr/bin/env python3
"""
Markov Chain Text Generator

Learns patterns from input text and generates new sentences that sound similar.
I wanted to make sure it actually starts sentences properly instead of just
spitting out random mid-sentence fragments like most simple implementations do.
"""

import random
import re
from collections import defaultdict
from typing import List, Dict, Tuple


class MarkovGenerator:
    """
    A Markov chain text generator that learns from input text.
    
    Uses bigrams (pairs of words) to predict the next word. Keeps track of
    sentence-starting words separately so generated text starts naturally.
    """
    
    def __init__(self, order: int = 2):
        """
        Initialize the generator.
        
        Args:
            order: Number of words to use as context (chain order).
                   Default is 2 which gives decent results without being too rigid.
        """
        self.order = order
        # Maps tuples of words to possible next words
        self.chain: Dict[Tuple[str, ...], List[str]] = defaultdict(list)
        # Track words that can start sentences
        self.sentence_starters: List[Tuple[str, ...]] = []
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Break text into words, preserving punctuation as separate tokens.
        
        This way punctuation influences the chain and we can detect sentence ends.
        """
        # Split on whitespace but keep punctuation separate
        tokens = re.findall(r'\w+|[.,!?;:]', text)
        return tokens
    
    def train(self, text: str) -> None:
        """
        Learn patterns from the input text.
        
        Builds the Markov chain by sliding a window through the text and
        recording what words follow each sequence.
        """
        tokens = self._tokenize(text)
        
        if len(tokens) < self.order + 1:
            # Not enough data to train
            return
        
        # Slide through the text with a window
        for i in range(len(tokens) - self.order):
            # Current state is a tuple of 'order' words
            state = tuple(tokens[i:i + self.order])
            next_word = tokens[i + self.order]
            
            self.chain[state].append(next_word)
            
            # Track if this state can start a sentence
            # (either at the beginning or after sentence-ending punctuation)
            if i == 0:
                self.sentence_starters.append(state)
            elif tokens[i - 1] in '.!?':
                self.sentence_starters.append(state)
    
    def generate(self, max_words: int = 50, seed: Tuple[str, ...] = None) -> str:
        """
        Generate new text based on learned patterns.
        
        Args:
            max_words: Maximum number of words to generate
            seed: Optional starting state. If None, picks a random sentence starter.
        
        Returns:
            Generated text as a string
        """
        if not self.chain:
            return ""
        
        # Start with a sentence-starting sequence if possible
        if seed is None:
            if self.sentence_starters:
                current_state = random.choice(self.sentence_starters)
            else:
                current_state = random.choice(list(self.chain.keys()))
        else:
            current_state = seed
        
        result = list(current_state)
        
        # Generate words one at a time
        for _ in range(max_words - self.order):
            if current_state not in self.chain:
                # Dead end — no data for this state
                break
            
            # Pick a random next word based on what we've seen follow this state
            next_word = random.choice(self.chain[current_state])
            result.append(next_word)
            
            # Slide the window forward
            current_state = tuple(result[-self.order:])
            
            # Stop at sentence-ending punctuation sometimes (makes output less rambling)
            if next_word in '.!?' and random.random() < 0.3:
                break
        
        # Join tokens, handling punctuation spacing
        text = ""
        for i, token in enumerate(result):
            if token in '.,!?;:' or i == 0:
                text += token
            else:
                text += " " + token
        
        return text.strip()


def main():
    """Demo the Markov generator with some sample text."""
    
    # Sample training text - using public domain text
    training_text = """
    The quick brown fox jumps over the lazy dog. The dog was not amused.
    Meanwhile, the fox was very pleased with itself. It had been practicing
    that jump for weeks. The lazy dog finally decided to take a nap.
    Every fox knows that practice makes perfect. The brown fox jumped again
    and again. Perfect jumps require perfect timing. The dog slept through
    all the noise. Peace and quiet at last, thought the dog.
    """
    
    print("=== Markov Chain Text Generator ===\n")
    print("Training text sample:")
    print(training_text[:150] + "...\n")
    
    # Create and train the generator
    gen = MarkovGenerator(order=2)
    gen.train(training_text)
    
    print(f"Learned {len(gen.chain)} unique states")
    print(f"Found {len(gen.sentence_starters)} sentence starters\n")
    
    # Generate some new sentences
    print("Generated text samples:\n")
    for i in range(5):
        text = gen.generate(max_words=20)
        print(f"{i+1}. {text}")
    
    print("\n--- Generating longer passage ---")
    longer = gen.generate(max_words=40)
    print(longer)


if __name__ == "__main__":
    main()