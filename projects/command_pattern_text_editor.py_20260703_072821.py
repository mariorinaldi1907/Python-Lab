"""
Date: 2026-07-03
Built a simple text editor using the command pattern to handle operations like insert, delete, and replace with full undo/redo support — wanted to explore how this pattern makes action history manageable.
"""

"""
A text editor implementation using the Command pattern.
Each operation (insert, delete, replace) is encapsulated as a command object
that knows how to execute and undo itself. This makes undo/redo trivial.
"""

from abc import ABC, abstractmethod
from typing import List


class Command(ABC):
    """
    Abstract base class for all editor commands.
    Each command must know how to execute and undo itself.
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
    Stores the position and text so it can be undone.
    """
    
    def __init__(self, document: 'Document', position: int, text: str):
        self.document = document
        self.position = position
        self.text = text
    
    def execute(self) -> None:
        """Insert text at the stored position."""
        self.document.insert(self.position, self.text)
    
    def undo(self) -> None:
        """Remove the inserted text to restore previous state."""
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
    Command to replace text in a range with new text.
    This is essentially a delete followed by an insert, but we treat it as atomic.
    """
    
    def __init__(self, document: 'Document', position: int, length: int, new_text: str):
        self.document = document
        self.position = position
        self.length = length
        self.new_text = new_text
        self.old_text = ""  # Store original text for undo
    
    def execute(self) -> None:
        """Replace the text and remember what was there."""
        self.old_text = self.document.get_text()[self.position:self.position + self.length]
        self.document.delete(self.position, self.length)
        self.document.insert(self.position, self.new_text)
    
    def undo(self) -> None:
        """Restore the original text."""
        self.document.delete(self.position, len(self.new_text))
        self.document.insert(self.position, self.old_text)


class Document:
    """
    The actual document that holds text.
    Provides low-level operations but doesn't handle undo/redo itself.
    """
    
    def __init__(self):
        self._content = ""
    
    def insert(self, position: int, text: str) -> None:
        """Insert text at the given position."""
        self._content = self._content[:position] + text + self._content[position:]
    
    def delete(self, position: int, length: int) -> None:
        """Delete length characters starting at position."""
        self._content = self._content[:position] + self._content[position + length:]
    
    def get_text(self) -> str:
        """Return the full document content."""
        return self._content
    
    def __str__(self) -> str:
        return self._content


class TextEditor:
    """
    The main editor class that manages commands and provides undo/redo.
    This is where the Command pattern really shines — we just maintain a history.
    """
    
    def __init__(self):
        self.document = Document()
        self.history: List[Command] = []  # Executed commands
        self.redo_stack: List[Command] = []  # Undone commands that can be redone
    
    def execute_command(self, command: Command) -> None:
        """
        Execute a command and add it to history.
        Clears the redo stack because we're starting a new timeline.
        """
        command.execute()
        self.history.append(command)
        self.redo_stack.clear()  # Can't redo after a new action
    
    def undo(self) -> bool:
        """
        Undo the last command if possible.
        Returns True if something was undone, False otherwise.
        """
        if not self.history:
            return False
        
        command = self.history.pop()
        command.undo()
        self.redo_stack.append(command)
        return True
    
    def redo(self) -> bool:
        """
        Redo the last undone command if possible.
        Returns True if something was redone, False otherwise.
        """
        if not self.redo_stack:
            return False
        
        command = self.redo_stack.pop()
        command.execute()
        self.history.append(command)
        return True
    
    def get_content(self) -> str:
        """Get the current document content."""
        return self.document.get_text()


if __name__ == "__main__":
    # Demo showing how the command pattern makes undo/redo clean
    editor = TextEditor()
    
    print("=== Text Editor Command Pattern Demo ===\n")
    
    # Start with a base text
    cmd1 = InsertCommand(editor.document, 0, "Hello world")
    editor.execute_command(cmd1)
    print(f"After insert: '{editor.get_content()}'")
    
    # Insert more text
    cmd2 = InsertCommand(editor.document, 5, " beautiful")
    editor.execute_command(cmd2)
    print(f"After second insert: '{editor.get_content()}'")
    
    # Delete some text
    cmd3 = DeleteCommand(editor.document, 6, 10)  # Remove "beautiful "
    editor.execute_command(cmd3)
    print(f"After delete: '{editor.get_content()}'")
    
    # Replace text
    cmd4 = ReplaceCommand(editor.document, 0, 5, "Hi")
    editor.execute_command(cmd4)
    print(f"After replace: '{editor.get_content()}'")
    
    print("\n--- Testing Undo ---")
    editor.undo()
    print(f"Undo replace: '{editor.get_content()}'")
    
    editor.undo()
    print(f"Undo delete: '{editor.get_content()}'")
    
    print("\n--- Testing Redo ---")
    editor.redo()
    print(f"Redo delete: '{editor.get_content()}'")
    
    editor.redo()
    print(f"Redo replace: '{editor.get_content()}'")
    
    print("\n--- New action clears redo stack ---")
    editor.undo()
    print(f"After undo: '{editor.get_content()}'")
    
    cmd5 = InsertCommand(editor.document, 0, "Hey, ")
    editor.execute_command(cmd5)
    print(f"New insert: '{editor.get_content()}'")
    
    can_redo = editor.redo()
    print(f"Can redo after new action? {can_redo}")