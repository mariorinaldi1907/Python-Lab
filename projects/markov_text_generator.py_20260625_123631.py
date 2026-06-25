"""
Date: 2026-06-25
Wrote a Markov chain text generator to experiment with probabilistic text generation — feeds on sample text and spits out surprisingly coherent nonsense.
"""

#!/usr/bin/env python3
"""
Markov Chain Text Generator

A simple but functional implementation that builds a statistical model from input text
and generates new text based on transition probabilities. I wanted something that could
produce actually readable output, not just random word soup.
"""

import random
import re
from collections import defaultdict, Counter


class MarkovChain:
    """
    Markov chain text generator using bigram transitions.
    
    The model learns which words tend to follow other words in the training text,
    then generates new sequences by randomly walking through these transitions.
    """
    
    def __init__(self, order=1):
        """
        Initialize the Markov chain.
        
        Args:
            order: The number of previous words to consider (1 = bigram, 2 = trigram, etc.)
                   Keeping it at 1 for simplicity but structure supports higher orders
        """
        self.order = order
        self.chain = defaultdict(Counter)  # state -> {next_word: count}
        self.start_words = []  # words that can begin sentences
        
    def _tokenize(self, text):
        """
        Split text into words, preserving sentence boundaries.
        
        I'm using a simple regex that splits on whitespace but keeps punctuation
        attached to words. Good enough for most cases.
        """
        # Split on whitespace while keeping punctuation
        words = re.findall(r'\S+', text)
        return words
    
    def _is_sentence_end(self, word):
        """Check if a word ends a sentence (has terminal punctuation)."""
        return word.endswith(('.', '!', '?'))
    
    def train(self, text):
        """
        Build the Markov chain from input text.
        
        This is where we count all the transitions. For each word, we record
        what words come after it and how often.
        """
        words = self._tokenize(text)
        
        if not words:
            return
        
        # First word can always start a sentence
        self.start_words.append(words[0])
        
        # Build the transition table
        for i in range(len(words) - 1):
            current_word = words[i]
            next_word = words[i + 1]
            
            # Record this transition
            self.chain[current_word][next_word] += 1
            
            # If current word ends a sentence, next word can start one
            if self._is_sentence_end(current_word):
                self.start_words.append(next_word)
    
    def _pick_next_word(self, current_word):
        """
        Choose the next word based on transition probabilities.
        
        Uses weighted random selection so more common transitions are more likely,
        but rare ones can still happen (makes output more interesting).
        """
        if current_word not in self.chain:
            return None
        
        # Get all possible next words and their counts
        possibilities = self.chain[current_word]
        words = list(possibilities.keys())
        weights = list(possibilities.values())
        
        # Pick one based on frequency (more common = more likely)
        return random.choices(words, weights=weights)[0]
    
    def generate(self, max_words=50, start_word=None):
        """
        Generate new text using the trained model.
        
        Args:
            max_words: Maximum number of words to generate
            start_word: Optional word to start with (random start word if None)
        
        Returns:
            Generated text string
        """
        if not self.start_words:
            return ""
        
        # Pick a starting word
        if start_word and start_word in self.chain:
            current_word = start_word
        else:
            current_word = random.choice(self.start_words)
        
        result = [current_word]
        
        # Keep generating until we hit max_words or run out of transitions
        for _ in range(max_words - 1):
            next_word = self._pick_next_word(current_word)
            
            if next_word is None:
                # Dead end, stop here
                break
            
            result.append(next_word)
            current_word = next_word
            
            # Stop if we've completed a sentence and hit at least half the max
            if self._is_sentence_end(current_word) and len(result) >= max_words // 2:
                break
        
        return ' '.join(result)


if __name__ == "__main__":
    # Demo with some sample text - using a mix of simple sentences
    # to show how the model picks up patterns
    sample_text = """
    The quick brown fox jumps over the lazy dog. The dog was sleeping under a tree.
    The tree was old and tall. A tall building stood nearby. The building had many windows.
    Windows let in the light. The light was bright and warm. Warm summer days are nice.
    Nice weather makes people happy. Happy people smile often. The fox ran through the forest.
    The forest was dark and mysterious. Mysterious sounds echoed at night.
    Night time is quiet. Quiet moments are peaceful. The dog liked to run.
    Running is good exercise. Exercise keeps you healthy. The brown fox was clever.
    Clever animals survive longer. The lazy dog finally woke up. Woke up feeling refreshed.
    """
    
    print("=== Markov Chain Text Generator ===\n")
    print("Training on sample text...\n")
    
    # Create and train the model
    markov = MarkovChain(order=1)
    markov.train(sample_text)
    
    # Generate a few examples
    print("Generated texts:\n")
    for i in range(5):
        generated = markov.generate(max_words=20)
        print(f"{i+1}. {generated}\n")
    
    # Show that we can start with a specific word
    print("\nStarting with 'The':")
    print(markov.generate(max_words=25, start_word="The"))