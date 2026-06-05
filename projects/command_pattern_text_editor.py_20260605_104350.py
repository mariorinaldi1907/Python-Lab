"""
Date: 2026-06-05
Built a command pattern demo using a basic text editor that tracks operations so you can undo and redo changes — helps me remember why this pattern exists.
"""

"""
Simple text editor demonstrating the Command pattern.

I built this to understand how undo/redo actually works under the hood.
Each operation (insert, delete, replace) is wrapped in a command object
that knows how to execute itself and reverse itself. The editor maintains
two stacks: one for undo history and one for redo history.
"""

from abc import ABC, abstractmethod
from typing import List


class Command(ABC):
    """
    Abstract base class for all editor commands.
    
    Each command must know how to execute itself and undo itself.
    This is the core of the pattern — operations become objects.
    """
    
    @abstractmethod
    def execute(self) -> None:
        """Execute the command and modify the editor state."""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Reverse the command's effect on the editor."""
        pass


class InsertCommand(Command):
    """Insert text at a specific position."""
    
    def __init__(self, editor: 'TextEditor', position: int, text: str):
        """
        Initialize insert command.
        
        Args:
            editor: The text editor to operate on
            position: Where to insert the text
            text: What text to insert
        """
        self.editor = editor
        self.position = position
        self.text = text
    
    def execute(self) -> None:
        """Insert the text into the editor's content."""
        content = self.editor.get_content()
        new_content = content[:self.position] + self.text + content[self.position:]
        self.editor.set_content(new_content)
    
    def undo(self) -> None:
        """Remove the inserted text."""
        content = self.editor.get_content()
        text_len = len(self.text)
        new_content = content[:self.position] + content[self.position + text_len:]
        self.editor.set_content(new_content)


class DeleteCommand(Command):
    """Delete text from a specific position."""
    
    def __init__(self, editor: 'TextEditor', position: int, length: int):
        """
        Initialize delete command.
        
        Args:
            editor: The text editor to operate on
            position: Where to start deleting
            length: How many characters to delete
        """
        self.editor = editor
        self.position = position
        self.length = length
        self.deleted_text = ""  # We'll store what we deleted so we can undo
    
    def execute(self) -> None:
        """Delete text and remember what was deleted."""
        content = self.editor.get_content()
        self.deleted_text = content[self.position:self.position + self.length]
        new_content = content[:self.position] + content[self.position + self.length:]
        self.editor.set_content(new_content)
    
    def undo(self) -> None:
        """Restore the deleted text."""
        content = self.editor.get_content()
        new_content = content[:self.position] + self.deleted_text + content[self.position:]
        self.editor.set_content(new_content)


class ReplaceCommand(Command):
    """Replace text at a specific position with new text."""
    
    def __init__(self, editor: 'TextEditor', position: int, length: int, new_text: str):
        """
        Initialize replace command.
        
        Args:
            editor: The text editor to operate on
            position: Where to start replacing
            length: How many characters to replace
            new_text: What to replace them with
        """
        self.editor = editor
        self.position = position
        self.length = length
        self.new_text = new_text
        self.old_text = ""  # Store original text for undo
    
    def execute(self) -> None:
        """Replace text and remember what was replaced."""
        content = self.editor.get_content()
        self.old_text = content[self.position:self.position + self.length]
        new_content = content[:self.position] + self.new_text + content[self.position + self.length:]
        self.editor.set_content(new_content)
    
    def undo(self) -> None:
        """Restore the original text."""
        content = self.editor.get_content()
        new_len = len(self.new_text)
        new_content = content[:self.position] + self.old_text + content[self.position + new_len:]
        self.editor.set_content(new_content)


class TextEditor:
    """
    A simple text editor that supports undo/redo through the Command pattern.
    
    This is the receiver in the Command pattern terminology.
    It maintains the actual document state and two stacks for history.
    """
    
    def __init__(self):
        """Initialize an empty editor with empty undo/redo stacks."""
        self._content = ""
        self._undo_stack: List[Command] = []
        self._redo_stack: List[Command] = []
    
    def get_content(self) -> str:
        """Get the current document content."""
        return self._content
    
    def set_content(self, content: str) -> None:
        """Set the document content directly (used by commands)."""
        self._content = content
    
    def execute_command(self, command: Command) -> None:
        """
        Execute a command and add it to the undo stack.
        
        This clears the redo stack because once you make a new change,
        you can't redo the old future anymore.
        """
        command.execute()
        self._undo_stack.append(command)
        self._redo_stack.clear()  # New action invalidates redo history
    
    def undo(self) -> bool:
        """
        Undo the last command.
        
        Returns:
            True if there was something to undo, False otherwise
        """
        if not self._undo_stack:
            return False
        
        command = self._undo_stack.pop()
        command.undo()
        self._redo_stack.append(command)
        return True
    
    def redo(self) -> bool:
        """
        Redo the last undone command.
        
        Returns:
            True if there was something to redo, False otherwise
        """
        if not self._redo_stack:
            return False
        
        command = self._redo_stack.pop()
        command.execute()
        self._undo_stack.append(command)
        return True


if __name__ == "__main__":
    # Demo showing how the command pattern enables undo/redo
    print("=== Text Editor with Command Pattern Demo ===\n")
    
    editor = TextEditor()
    
    print("Starting with empty document")
    print(f"Content: '{editor.get_content()}'\n")
    
    # Insert some text
    print("Inserting 'Hello World'")
    editor.execute_command(InsertCommand(editor, 0, "Hello World"))
    print(f"Content: '{editor.get_content()}'\n")
    
    # Insert more text
    print("Inserting '!' at the end")
    editor.execute_command(InsertCommand(editor, 11, "!"))
    print(f"Content: '{editor.get_content()}'\n")
    
    # Replace text
    print("Replacing 'World' with 'Python'")
    editor.execute_command(ReplaceCommand(editor, 6, 5, "Python"))
    print(f"Content: '{editor.get_content()}'\n")
    
    # Delete text
    print("Deleting the '!'")
    editor.execute_command(DeleteCommand(editor, 12, 1))
    print(f"Content: '{editor.get_content()}'\n")
    
    # Now let's undo everything step by step
    print("--- Undo Operations ---\n")
    
    print("Undo #1")
    editor.undo()
    print(f"Content: '{editor.get_content()}'\n")
    
    print("Undo #2")
    editor.undo()
    print(f"Content: '{editor.get_content()}'\n")
    
    print("Undo #3")
    editor.undo()
    print(f"Content: '{editor.get_content()}'\n")
    
    # Redo some changes
    print("--- Redo Operations ---\n")
    
    print("Redo #1")
    editor.redo()
    print(f"Content: '{editor.get_content()}'\n")
    
    print("Redo #2")
    editor.redo()
    print(f"Content: '{editor.get_content()}'\n")
    
    print("Done! The Command pattern makes undo/redo straightforward.")