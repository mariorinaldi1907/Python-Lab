"""
Date: 2026-06-16
Built a minimal text editor using the command pattern to handle undo/redo operations cleanly — makes it super easy to add new editing commands.
"""

"""
Text editor implementing the Command pattern for undo/redo functionality.

I wanted to build something that actually demonstrates why the command pattern
is useful in practice. Text editors are the perfect use case since every edit
needs to be undoable/redoable.
"""

from abc import ABC, abstractmethod
from typing import List


class Command(ABC):
    """
    Abstract base class for all commands.
    
    Each command knows how to execute itself and undo itself.
    """
    
    @abstractmethod
    def execute(self) -> None:
        """Execute the command."""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Undo the command."""
        pass


class TextDocument:
    """
    The receiver in the command pattern.
    
    This is what actually stores the text and performs operations on it.
    Commands delegate to this object.
    """
    
    def __init__(self):
        self.content = ""
    
    def insert(self, position: int, text: str) -> None:
        """Insert text at a specific position."""
        self.content = self.content[:position] + text + self.content[position:]
    
    def delete(self, position: int, length: int) -> str:
        """Delete text and return what was deleted (so we can undo)."""
        deleted = self.content[position:position + length]
        self.content = self.content[:position] + self.content[position + length:]
        return deleted
    
    def get_content(self) -> str:
        """Get the current document content."""
        return self.content


class InsertCommand(Command):
    """
    Command to insert text into the document.
    
    Stores the position and text so it can be undone by deleting
    the same amount of text at the same position.
    """
    
    def __init__(self, document: TextDocument, position: int, text: str):
        self.document = document
        self.position = position
        self.text = text
    
    def execute(self) -> None:
        """Insert the text."""
        self.document.insert(self.position, self.text)
    
    def undo(self) -> None:
        """Remove the text we inserted."""
        self.document.delete(self.position, len(self.text))


class DeleteCommand(Command):
    """
    Command to delete text from the document.
    
    Saves what was deleted so we can re-insert it on undo.
    """
    
    def __init__(self, document: TextDocument, position: int, length: int):
        self.document = document
        self.position = position
        self.length = length
        self.deleted_text = ""  # Will store what we delete
    
    def execute(self) -> None:
        """Delete text and remember what we deleted."""
        self.deleted_text = self.document.delete(self.position, self.length)
    
    def undo(self) -> None:
        """Re-insert the text we deleted."""
        self.document.insert(self.position, self.deleted_text)


class TextEditor:
    """
    The invoker in the command pattern.
    
    This maintains the command history and handles undo/redo.
    Users interact with this class, not directly with commands.
    """
    
    def __init__(self):
        self.document = TextDocument()
        self.history: List[Command] = []
        self.redo_stack: List[Command] = []
    
    def execute_command(self, command: Command) -> None:
        """
        Execute a command and add it to history.
        
        Clears the redo stack because once you make a new edit,
        you can't redo the old future anymore.
        """
        command.execute()
        self.history.append(command)
        self.redo_stack.clear()  # New action invalidates redo history
    
    def undo(self) -> bool:
        """
        Undo the last command.
        
        Returns True if there was something to undo, False otherwise.
        """
        if not self.history:
            return False
        
        command = self.history.pop()
        command.undo()
        self.redo_stack.append(command)
        return True
    
    def redo(self) -> bool:
        """
        Redo the last undone command.
        
        Returns True if there was something to redo, False otherwise.
        """
        if not self.redo_stack:
            return False
        
        command = self.redo_stack.pop()
        command.execute()
        self.history.append(command)
        return True
    
    def get_content(self) -> str:
        """Get current document content."""
        return self.document.get_content()


if __name__ == "__main__":
    # Create an editor instance
    editor = TextEditor()
    
    print("=== Text Editor Command Pattern Demo ===\n")
    
    # Type "Hello"
    print("Action: Insert 'Hello' at position 0")
    cmd1 = InsertCommand(editor.document, 0, "Hello")
    editor.execute_command(cmd1)
    print(f"Content: '{editor.get_content()}'\n")
    
    # Type " World"
    print("Action: Insert ' World' at position 5")
    cmd2 = InsertCommand(editor.document, 5, " World")
    editor.execute_command(cmd2)
    print(f"Content: '{editor.get_content()}'\n")
    
    # Delete "World"
    print("Action: Delete 6 characters starting at position 5")
    cmd3 = DeleteCommand(editor.document, 5, 6)
    editor.execute_command(cmd3)
    print(f"Content: '{editor.get_content()}'\n")
    
    # Undo the delete
    print("Action: Undo (restore ' World')")
    editor.undo()
    print(f"Content: '{editor.get_content()}'\n")
    
    # Undo again
    print("Action: Undo (remove ' World')")
    editor.undo()
    print(f"Content: '{editor.get_content()}'\n")
    
    # Redo
    print("Action: Redo (re-add ' World')")
    editor.redo()
    print(f"Content: '{editor.get_content()}'\n")
    
    # Add more text
    print("Action: Insert '!' at position 11")
    cmd4 = InsertCommand(editor.document, 11, "!")
    editor.execute_command(cmd4)
    print(f"Content: '{editor.get_content()}'\n")
    
    print("=== Final content ===")
    print(f"'{editor.get_content()}'")