"""
Date: 2026-06-25
Created a text transformation pipeline where each operation is a command object that can be undone — lets me chain transforms like uppercase, reverse, and ROT13 with full history tracking.
"""

"""
Text processing pipeline using the Command pattern.
Each transformation is a reversible command that can be undone/redone.
I wanted a clean way to chain text operations and still roll back mistakes.
"""

from abc import ABC, abstractmethod
from typing import List, Optional


class Command(ABC):
    """
    Abstract base for all text transformation commands.
    Every command must know how to execute and undo itself.
    """
    
    @abstractmethod
    def execute(self, text: str) -> str:
        """Apply the transformation to the text."""
        pass
    
    @abstractmethod
    def undo(self, text: str) -> str:
        """Reverse the transformation."""
        pass
    
    @abstractmethod
    def name(self) -> str:
        """Return a human-readable name for this command."""
        pass


class UppercaseCommand(Command):
    """Converts text to uppercase, tracks original case for undo."""
    
    def __init__(self):
        self._original_chars = []
    
    def execute(self, text: str) -> str:
        # Store which chars were actually lowercase so we can restore them
        self._original_chars = [c.islower() for c in text]
        return text.upper()
    
    def undo(self, text: str) -> str:
        # Restore original casing using our tracking
        result = []
        for i, char in enumerate(text):
            if i < len(self._original_chars) and self._original_chars[i]:
                result.append(char.lower())
            else:
                result.append(char)
        return ''.join(result)
    
    def name(self) -> str:
        return "uppercase"


class ReverseCommand(Command):
    """Reverses the text — undo just reverses it again."""
    
    def execute(self, text: str) -> str:
        return text[::-1]
    
    def undo(self, text: str) -> str:
        # Reversing twice gets you back to the original
        return text[::-1]
    
    def name(self) -> str:
        return "reverse"


class ROT13Command(Command):
    """
    ROT13 cipher — shifts letters by 13 positions.
    Fun fact: ROT13 is its own inverse, so execute and undo are identical.
    """
    
    def execute(self, text: str) -> str:
        result = []
        for char in text:
            if 'a' <= char <= 'z':
                result.append(chr((ord(char) - ord('a') + 13) % 26 + ord('a')))
            elif 'A' <= char <= 'Z':
                result.append(chr((ord(char) - ord('A') + 13) % 26 + ord('A')))
            else:
                result.append(char)
        return ''.join(result)
    
    def undo(self, text: str) -> str:
        # ROT13 applied twice cancels itself out
        return self.execute(text)
    
    def name(self) -> str:
        return "rot13"


class RemoveSpacesCommand(Command):
    """Removes all whitespace, tracks original positions for undo."""
    
    def __init__(self):
        self._space_positions = []
    
    def execute(self, text: str) -> str:
        # Remember where the spaces were
        self._space_positions = [i for i, c in enumerate(text) if c.isspace()]
        return ''.join(c for c in text if not c.isspace())
    
    def undo(self, text: str) -> str:
        # Re-insert spaces at their original positions
        chars = list(text)
        for pos in self._space_positions:
            chars.insert(pos, ' ')
        return ''.join(chars)
    
    def name(self) -> str:
        return "remove_spaces"


class TextProcessor:
    """
    Main processor that executes commands and maintains undo/redo history.
    This is the invoker in the Command pattern terminology.
    """
    
    def __init__(self, initial_text: str = ""):
        self._text = initial_text
        self._history: List[Command] = []
        self._redo_stack: List[Command] = []
    
    def execute_command(self, command: Command) -> None:
        """Execute a command and add it to history."""
        self._text = command.execute(self._text)
        self._history.append(command)
        # Executing a new command clears the redo stack
        self._redo_stack.clear()
        print(f"  → Applied '{command.name()}': {self._text}")
    
    def undo(self) -> bool:
        """Undo the last command if possible."""
        if not self._history:
            print("  ✗ Nothing to undo")
            return False
        
        command = self._history.pop()
        self._text = command.undo(self._text)
        self._redo_stack.append(command)
        print(f"  ← Undid '{command.name()}': {self._text}")
        return True
    
    def redo(self) -> bool:
        """Redo the last undone command if possible."""
        if not self._redo_stack:
            print("  ✗ Nothing to redo")
            return False
        
        command = self._redo_stack.pop()
        self._text = command.execute(self._text)
        self._history.append(command)
        print(f"  → Redid '{command.name()}': {self._text}")
        return True
    
    def get_text(self) -> str:
        """Get the current processed text."""
        return self._text
    
    def get_history(self) -> List[str]:
        """Get a list of command names that have been executed."""
        return [cmd.name() for cmd in self._history]


if __name__ == "__main__":
    print("=== Text Processor with Command Pattern ===\n")
    
    # Start with some sample text
    processor = TextProcessor("Hello World! This is a test.")
    print(f"Initial text: {processor.get_text()}\n")
    
    # Apply a series of transformations
    print("Applying transformations:")
    processor.execute_command(UppercaseCommand())
    processor.execute_command(ROT13Command())
    processor.execute_command(RemoveSpacesCommand())
    processor.execute_command(ReverseCommand())
    
    print(f"\nCommand history: {processor.get_history()}")
    
    # Demonstrate undo
    print("\nUndoing transformations:")
    processor.undo()
    processor.undo()
    
    # Demonstrate redo
    print("\nRedoing transformations:")
    processor.redo()
    
    # Try more operations after redo
    print("\nApplying new command (clears redo stack):")
    processor.execute_command(UppercaseCommand())
    
    print("\nTrying to redo (should fail):")
    processor.redo()
    
    print(f"\nFinal text: {processor.get_text()}")
    print(f"Final history: {processor.get_history()}")