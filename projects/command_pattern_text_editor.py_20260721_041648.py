"""
Date: 2026-07-21
Implemented the command pattern for a simple text editor that supports undo/redo operations, because I wanted something more practical than the usual light switch examples.
"""

"""
Text editor using the Command pattern for undo/redo functionality.

I've always wanted to build something with proper undo/redo support,
and the Command pattern is perfect for this. Each edit operation is
encapsulated as a command object that knows how to execute and reverse itself.
"""

from abc import ABC, abstractmethod
from typing import List


class Command(ABC):
    """
    Abstract base class for all commands.
    
    Each command must know how to execute itself and how to undo itself.
    This is the core of the Command pattern — turning operations into objects.
    """
    
    @abstractmethod
    def execute(self) -> None:
        """Perform the command's action."""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Reverse the command's action."""
        pass


class TextEditor:
    """
    Simple text editor that stores content as a string.
    
    This is the receiver in the Command pattern — it's what actually
    gets modified by the commands.
    """
    
    def __init__(self):
        self.content = ""
    
    def insert_text(self, position: int, text: str) -> None:
        """Insert text at a specific position."""
        self.content = self.content[:position] + text + self.content[position:]
    
    def delete_text(self, position: int, length: int) -> str:
        """Delete text at position and return what was deleted (for undo)."""
        deleted = self.content[position:position + length]
        self.content = self.content[:position] + self.content[position + length:]
        return deleted
    
    def get_content(self) -> str:
        """Return current content."""
        return self.content


class InsertCommand(Command):
    """
    Command to insert text at a position.
    
    Stores everything needed to both execute and undo the insertion.
    """
    
    def __init__(self, editor: TextEditor, position: int, text: str):
        self.editor = editor
        self.position = position
        self.text = text
    
    def execute(self) -> None:
        """Insert the text."""
        self.editor.insert_text(self.position, self.text)
    
    def undo(self) -> None:
        """Remove the text we inserted."""
        self.editor.delete_text(self.position, len(self.text))


class DeleteCommand(Command):
    """
    Command to delete text at a position.
    
    Has to remember what was deleted so we can restore it on undo.
    """
    
    def __init__(self, editor: TextEditor, position: int, length: int):
        self.editor = editor
        self.position = position
        self.length = length
        self.deleted_text = ""  # We'll store this when we execute
    
    def execute(self) -> None:
        """Delete the text and remember what we deleted."""
        self.deleted_text = self.editor.delete_text(self.position, self.length)
    
    def undo(self) -> None:
        """Restore the deleted text."""
        self.editor.insert_text(self.position, self.deleted_text)


class EditorInvoker:
    """
    Manages command history and handles undo/redo.
    
    This is the invoker in the Command pattern. It doesn't know what
    commands do, it just executes them and keeps track of history.
    """
    
    def __init__(self, editor: TextEditor):
        self.editor = editor
        self.history: List[Command] = []
        self.redo_stack: List[Command] = []
    
    def execute_command(self, command: Command) -> None:
        """
        Execute a command and add it to history.
        
        When we execute a new command, we clear the redo stack because
        we've branched off into a new timeline.
        """
        command.execute()
        self.history.append(command)
        self.redo_stack.clear()  # New action clears redo history
    
    def undo(self) -> bool:
        """
        Undo the last command.
        
        Returns True if we undid something, False if history is empty.
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
        
        Returns True if we redid something, False if redo stack is empty.
        """
        if not self.redo_stack:
            return False
        
        command = self.redo_stack.pop()
        command.execute()
        self.history.append(command)
        return True


if __name__ == "__main__":
    # Create our text editor and invoker
    editor = TextEditor()
    invoker = EditorInvoker(editor)
    
    print("=== Text Editor with Undo/Redo ===\n")
    
    # Start typing some text
    print("Inserting 'Hello '...")
    invoker.execute_command(InsertCommand(editor, 0, "Hello "))
    print(f"Content: '{editor.get_content()}'")
    
    print("\nInserting 'World'...")
    invoker.execute_command(InsertCommand(editor, 6, "World"))
    print(f"Content: '{editor.get_content()}'")
    
    print("\nInserting '!' at the end...")
    invoker.execute_command(InsertCommand(editor, 11, "!"))
    print(f"Content: '{editor.get_content()}'")
    
    # Delete something
    print("\nDeleting 5 characters starting at position 6...")
    invoker.execute_command(DeleteCommand(editor, 6, 5))
    print(f"Content: '{editor.get_content()}'")
    
    # Undo the delete
    print("\n--- Undoing delete ---")
    invoker.undo()
    print(f"Content: '{editor.get_content()}'")
    
    # Undo more
    print("\n--- Undoing insert '!' ---")
    invoker.undo()
    print(f"Content: '{editor.get_content()}'")
    
    # Redo
    print("\n--- Redoing insert '!' ---")
    invoker.redo()
    print(f"Content: '{editor.get_content()}'")
    
    # Make a new edit (this should clear redo stack)
    print("\n--- Adding ' Python' (clears redo history) ---")
    invoker.execute_command(InsertCommand(editor, 11, " Python"))
    print(f"Content: '{editor.get_content()}'")
    
    # Try to redo (should fail because we branched)
    print("\n--- Trying to redo (should fail) ---")
    if not invoker.redo():
        print("Cannot redo — new edits cleared the redo stack")
    
    print(f"\nFinal content: '{editor.get_content()}'")