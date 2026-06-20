"""
Date: 2026-06-20
Built a text editor using the command pattern to handle undo/redo operations — wanted to see how robust I could make history management with just standard lib.
"""

#!/usr/bin/env python3
"""
Text editor using the Command pattern for undo/redo functionality.
Each operation (insert, delete, replace) is encapsulated as a command object.
"""

from abc import ABC, abstractmethod
from typing import List


class Command(ABC):
    """
    Abstract base class for all text editing commands.
    Each command knows how to execute itself and undo itself.
    """
    
    @abstractmethod
    def execute(self) -> None:
        """Execute the command."""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Undo the command, reverting to previous state."""
        pass


class TextDocument:
    """
    The receiver in the command pattern.
    Stores the actual text content and provides primitive operations.
    """
    
    def __init__(self, initial_text: str = ""):
        self.content = initial_text
    
    def insert(self, position: int, text: str) -> None:
        """Insert text at the specified position."""
        self.content = self.content[:position] + text + self.content[position:]
    
    def delete(self, position: int, length: int) -> str:
        """Delete text from position for given length. Returns deleted text."""
        deleted = self.content[position:position + length]
        self.content = self.content[:position] + self.content[position + length:]
        return deleted
    
    def replace(self, position: int, length: int, new_text: str) -> str:
        """Replace text at position with new text. Returns old text."""
        old_text = self.content[position:position + length]
        self.content = self.content[:position] + new_text + self.content[position + length:]
        return old_text
    
    def __str__(self) -> str:
        return self.content


class InsertCommand(Command):
    """Command for inserting text into the document."""
    
    def __init__(self, document: TextDocument, position: int, text: str):
        self.document = document
        self.position = position
        self.text = text
    
    def execute(self) -> None:
        """Insert the text at the stored position."""
        self.document.insert(self.position, self.text)
    
    def undo(self) -> None:
        """Remove the text that was inserted."""
        self.document.delete(self.position, len(self.text))


class DeleteCommand(Command):
    """Command for deleting text from the document."""
    
    def __init__(self, document: TextDocument, position: int, length: int):
        self.document = document
        self.position = position
        self.length = length
        self.deleted_text = ""  # Will store what we delete for undo
    
    def execute(self) -> None:
        """Delete text and save it for potential undo."""
        self.deleted_text = self.document.delete(self.position, self.length)
    
    def undo(self) -> None:
        """Re-insert the text that was deleted."""
        self.document.insert(self.position, self.deleted_text)


class ReplaceCommand(Command):
    """Command for replacing text in the document."""
    
    def __init__(self, document: TextDocument, position: int, length: int, new_text: str):
        self.document = document
        self.position = position
        self.length = length
        self.new_text = new_text
        self.old_text = ""  # Will store replaced text for undo
    
    def execute(self) -> None:
        """Replace text and save the old text for undo."""
        self.old_text = self.document.replace(self.position, self.length, self.new_text)
    
    def undo(self) -> None:
        """Restore the original text."""
        self.document.replace(self.position, len(self.new_text), self.old_text)


class TextEditor:
    """
    The invoker in the command pattern.
    Manages command history and provides undo/redo functionality.
    """
    
    def __init__(self, document: TextDocument):
        self.document = document
        self.history: List[Command] = []
        self.current_position = -1  # Points to the last executed command
    
    def execute_command(self, command: Command) -> None:
        """
        Execute a command and add it to history.
        Any commands after current position are discarded (can't redo after new edits).
        """
        command.execute()
        # Discard any "future" commands if we're in the middle of history
        self.history = self.history[:self.current_position + 1]
        self.history.append(command)
        self.current_position += 1
    
    def undo(self) -> bool:
        """Undo the last command. Returns True if successful, False if nothing to undo."""
        if self.current_position < 0:
            return False
        
        self.history[self.current_position].undo()
        self.current_position -= 1
        return True
    
    def redo(self) -> bool:
        """Redo a previously undone command. Returns True if successful."""
        if self.current_position >= len(self.history) - 1:
            return False
        
        self.current_position += 1
        self.history[self.current_position].execute()
        return True
    
    def get_content(self) -> str:
        """Get the current document content."""
        return str(self.document)


if __name__ == "__main__":
    # Create a new document and editor
    doc = TextDocument("Hello world")
    editor = TextEditor(doc)
    
    print("Initial text:", editor.get_content())
    print()
    
    # Insert some text
    print("Inserting ' beautiful' at position 5...")
    editor.execute_command(InsertCommand(doc, 5, " beautiful"))
    print("After insert:", editor.get_content())
    print()
    
    # Delete some text
    print("Deleting 6 characters from position 5...")
    editor.execute_command(DeleteCommand(doc, 5, 6))
    print("After delete:", editor.get_content())
    print()
    
    # Replace some text
    print("Replacing 'world' with 'Python'...")
    editor.execute_command(ReplaceCommand(doc, 6, 5, "Python"))
    print("After replace:", editor.get_content())
    print()
    
    # Undo operations
    print("Undoing last operation...")
    editor.undo()
    print("After undo:", editor.get_content())
    print()
    
    print("Undoing again...")
    editor.undo()
    print("After undo:", editor.get_content())
    print()
    
    # Redo operations
    print("Redoing operation...")
    editor.redo()
    print("After redo:", editor.get_content())
    print()
    
    # New operation after undo - this clears redo history
    print("Inserting ' amazing' at position 5 (clears redo stack)...")
    editor.execute_command(InsertCommand(doc, 5, " amazing"))
    print("After insert:", editor.get_content())
    print()
    
    print("Trying to redo (should fail since we made new changes)...")
    if not editor.redo():
        print("Cannot redo - new edits cleared redo history")
    print("Final text:", editor.get_content())