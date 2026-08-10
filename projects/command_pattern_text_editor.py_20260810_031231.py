"""
Date: 2026-08-10
Built a simple text editor using the command pattern to handle operations like insert, delete, and replace with full undo/redo functionality.
"""

#!/usr/bin/env python3
"""
A simple text editor implementation using the Command pattern.

I wanted to explore how undo/redo actually works under the hood, and the
Command pattern is perfect for this. Each edit operation becomes a command
object that knows how to execute and undo itself.
"""

from abc import ABC, abstractmethod
from typing import List


class Command(ABC):
    """
    Abstract base class for all editor commands.
    
    Each command must know how to execute itself and how to undo itself.
    This is the core of the Command pattern.
    """
    
    @abstractmethod
    def execute(self) -> None:
        """Perform the command's action."""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Reverse the command's action."""
        pass


class TextBuffer:
    """
    The actual text storage that commands will modify.
    
    Keeping this separate from the command system makes it easier to test
    and reason about. The buffer doesn't know anything about undo/redo.
    """
    
    def __init__(self):
        self.content = ""
    
    def insert(self, position: int, text: str) -> None:
        """Insert text at the given position."""
        self.content = self.content[:position] + text + self.content[position:]
    
    def delete(self, position: int, length: int) -> str:
        """Delete text starting at position and return what was deleted."""
        deleted = self.content[position:position + length]
        self.content = self.content[:position] + self.content[position + length:]
        return deleted
    
    def get_content(self) -> str:
        """Return the current buffer content."""
        return self.content


class InsertCommand(Command):
    """Command to insert text at a specific position."""
    
    def __init__(self, buffer: TextBuffer, position: int, text: str):
        self.buffer = buffer
        self.position = position
        self.text = text
    
    def execute(self) -> None:
        """Insert the text."""
        self.buffer.insert(self.position, self.text)
    
    def undo(self) -> None:
        """Remove the text we just inserted."""
        self.buffer.delete(self.position, len(self.text))


class DeleteCommand(Command):
    """Command to delete text at a specific position."""
    
    def __init__(self, buffer: TextBuffer, position: int, length: int):
        self.buffer = buffer
        self.position = position
        self.length = length
        self.deleted_text = ""  # Store what we delete so we can restore it
    
    def execute(self) -> None:
        """Delete the text and remember what we deleted."""
        self.deleted_text = self.buffer.delete(self.position, self.length)
    
    def undo(self) -> None:
        """Put back the text we deleted."""
        self.buffer.insert(self.position, self.deleted_text)


class ReplaceCommand(Command):
    """
    Command to replace text at a specific position.
    
    This is basically a delete followed by an insert, but implementing it
    as a single command makes the undo/redo behavior cleaner.
    """
    
    def __init__(self, buffer: TextBuffer, position: int, length: int, new_text: str):
        self.buffer = buffer
        self.position = position
        self.length = length
        self.new_text = new_text
        self.old_text = ""
    
    def execute(self) -> None:
        """Replace old text with new text."""
        self.old_text = self.buffer.delete(self.position, self.length)
        self.buffer.insert(self.position, self.new_text)
    
    def undo(self) -> None:
        """Restore the original text."""
        self.buffer.delete(self.position, len(self.new_text))
        self.buffer.insert(self.position, self.old_text)


class TextEditor:
    """
    The editor that manages commands and handles undo/redo.
    
    This is where the Command pattern really shines. The editor doesn't need
    to know the details of each operation — it just executes commands and
    keeps track of history.
    """
    
    def __init__(self):
        self.buffer = TextBuffer()
        self.history: List[Command] = []
        self.redo_stack: List[Command] = []
    
    def execute(self, command: Command) -> None:
        """Execute a command and add it to history."""
        command.execute()
        self.history.append(command)
        # Any new command clears the redo stack
        self.redo_stack.clear()
    
    def undo(self) -> bool:
        """Undo the last command. Returns True if successful."""
        if not self.history:
            return False
        
        command = self.history.pop()
        command.undo()
        self.redo_stack.append(command)
        return True
    
    def redo(self) -> bool:
        """Redo the last undone command. Returns True if successful."""
        if not self.redo_stack:
            return False
        
        command = self.redo_stack.pop()
        command.execute()
        self.history.append(command)
        return True
    
    def get_content(self) -> str:
        """Get the current buffer content."""
        return self.buffer.get_content()


if __name__ == "__main__":
    print("=== Text Editor with Command Pattern ===\n")
    
    editor = TextEditor()
    
    # Start with some initial text
    print("1. Inserting 'Hello World'")
    editor.execute(InsertCommand(editor.buffer, 0, "Hello World"))
    print(f"   Content: '{editor.get_content()}'\n")
    
    # Insert more text
    print("2. Inserting ' from Python' at the end")
    editor.execute(InsertCommand(editor.buffer, 11, " from Python"))
    print(f"   Content: '{editor.get_content()}'\n")
    
    # Replace some text
    print("3. Replacing 'World' with 'there'")
    editor.execute(ReplaceCommand(editor.buffer, 6, 5, "there"))
    print(f"   Content: '{editor.get_content()}'\n")
    
    # Delete some text
    print("4. Deleting ' from Python'")
    editor.execute(DeleteCommand(editor.buffer, 11, 12))
    print(f"   Content: '{editor.get_content()}'\n")
    
    # Now undo everything step by step
    print("5. Undo (restore ' from Python')")
    editor.undo()
    print(f"   Content: '{editor.get_content()}'\n")
    
    print("6. Undo (restore 'World')")
    editor.undo()
    print(f"   Content: '{editor.get_content()}'\n")
    
    print("7. Undo (remove ' from Python')")
    editor.undo()
    print(f"   Content: '{editor.get_content()}'\n")
    
    # Redo some operations
    print("8. Redo (add ' from Python' back)")
    editor.redo()
    print(f"   Content: '{editor.get_content()}'\n")
    
    print("9. Redo (replace with 'there' again)")
    editor.redo()
    print(f"   Content: '{editor.get_content()}'\n")
    
    print("Demo complete! The Command pattern makes undo/redo pretty elegant.")