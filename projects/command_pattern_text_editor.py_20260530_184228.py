"""
Date: 2026-05-30
Built a mini text editor using the command pattern to handle undo/redo operations, because I always wanted to see how real editors implement this under the hood.
"""

#!/usr/bin/env python3
"""
A simple text editor implementation using the Command pattern.
Supports insert, delete, and replace operations with full undo/redo.
"""

from abc import ABC, abstractmethod
from typing import List


class Command(ABC):
    """
    Abstract base class for all commands.
    Each command knows how to execute and undo itself.
    """
    
    @abstractmethod
    def execute(self) -> None:
        """Execute the command."""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Undo the command."""
        pass


class InsertCommand(Command):
    """
    Command to insert text at a specific position.
    Keeps track of what was inserted so we can remove it on undo.
    """
    
    def __init__(self, document: 'Document', position: int, text: str):
        self.document = document
        self.position = position
        self.text = text
    
    def execute(self) -> None:
        """Insert text into the document."""
        self.document.insert(self.position, self.text)
    
    def undo(self) -> None:
        """Remove the inserted text."""
        self.document.delete(self.position, len(self.text))


class DeleteCommand(Command):
    """
    Command to delete text from a specific position.
    Stores the deleted text so we can restore it on undo.
    """
    
    def __init__(self, document: 'Document', position: int, length: int):
        self.document = document
        self.position = position
        self.length = length
        self.deleted_text = ""  # Will store what we delete
    
    def execute(self) -> None:
        """Delete text and remember what was deleted."""
        self.deleted_text = self.document.get_text()[self.position:self.position + self.length]
        self.document.delete(self.position, self.length)
    
    def undo(self) -> None:
        """Restore the deleted text."""
        self.document.insert(self.position, self.deleted_text)


class ReplaceCommand(Command):
    """
    Command to replace text at a specific position.
    Essentially a delete + insert, but as one atomic operation.
    """
    
    def __init__(self, document: 'Document', position: int, length: int, new_text: str):
        self.document = document
        self.position = position
        self.length = length
        self.new_text = new_text
        self.old_text = ""
    
    def execute(self) -> None:
        """Replace text and remember the old value."""
        self.old_text = self.document.get_text()[self.position:self.position + self.length]
        self.document.delete(self.position, self.length)
        self.document.insert(self.position, self.new_text)
    
    def undo(self) -> None:
        """Restore the original text."""
        self.document.delete(self.position, len(self.new_text))
        self.document.insert(self.position, self.old_text)


class Document:
    """
    The document being edited. Just wraps a string.
    We could optimize this with a gap buffer or rope, but keeping it simple.
    """
    
    def __init__(self, initial_text: str = ""):
        self._text = initial_text
    
    def insert(self, position: int, text: str) -> None:
        """Insert text at the given position."""
        self._text = self._text[:position] + text + self._text[position:]
    
    def delete(self, position: int, length: int) -> None:
        """Delete 'length' characters starting at position."""
        self._text = self._text[:position] + self._text[position + length:]
    
    def get_text(self) -> str:
        """Get the current document text."""
        return self._text


class TextEditor:
    """
    The main editor class that manages commands and undo/redo stacks.
    This is where the Command pattern really shines.
    """
    
    def __init__(self):
        self.document = Document()
        self.history: List[Command] = []  # Commands that have been executed
        self.redo_stack: List[Command] = []  # Commands that have been undone
    
    def execute_command(self, command: Command) -> None:
        """
        Execute a command and add it to history.
        Clears redo stack because we're creating a new timeline.
        """
        command.execute()
        self.history.append(command)
        self.redo_stack.clear()  # Can't redo after a new action
    
    def undo(self) -> bool:
        """Undo the last command if possible."""
        if not self.history:
            return False
        
        command = self.history.pop()
        command.undo()
        self.redo_stack.append(command)
        return True
    
    def redo(self) -> bool:
        """Redo the last undone command if possible."""
        if not self.redo_stack:
            return False
        
        command = self.redo_stack.pop()
        command.execute()
        self.history.append(command)
        return True
    
    def get_text(self) -> str:
        """Get the current document text."""
        return self.document.get_text()


if __name__ == "__main__":
    # Demo: simulating a real editing session
    print("=== Text Editor with Command Pattern ===\n")
    
    editor = TextEditor()
    
    # Start typing
    print("1. Inserting 'Hello'...")
    editor.execute_command(InsertCommand(editor.document, 0, "Hello"))
    print(f"   Text: '{editor.get_text()}'")
    
    # Add more text
    print("\n2. Inserting ' World'...")
    editor.execute_command(InsertCommand(editor.document, 5, " World"))
    print(f"   Text: '{editor.get_text()}'")
    
    # Make a typo and fix it
    print("\n3. Inserting '!!!' at the end...")
    editor.execute_command(InsertCommand(editor.document, 11, "!!!"))
    print(f"   Text: '{editor.get_text()}'")
    
    print("\n4. Oops, too many exclamation marks. Deleting 2...")
    editor.execute_command(DeleteCommand(editor.document, 12, 2))
    print(f"   Text: '{editor.get_text()}'")
    
    # Replace a word
    print("\n5. Replacing 'World' with 'Python'...")
    editor.execute_command(ReplaceCommand(editor.document, 6, 5, "Python"))
    print(f"   Text: '{editor.get_text()}'")
    
    # Now let's undo a few times
    print("\n6. Undoing last action...")
    editor.undo()
    print(f"   Text: '{editor.get_text()}'")
    
    print("\n7. Undoing again...")
    editor.undo()
    print(f"   Text: '{editor.get_text()}'")
    
    print("\n8. Undoing again...")
    editor.undo()
    print(f"   Text: '{editor.get_text()}'")
    
    # Redo them back
    print("\n9. Redoing...")
    editor.redo()
    print(f"   Text: '{editor.get_text()}'")
    
    print("\n10. Redoing again...")
    editor.redo()
    print(f"   Text: '{editor.get_text()}'")
    
    print("\n✓ Command pattern working perfectly!")