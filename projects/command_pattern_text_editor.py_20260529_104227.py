"""
Date: 2026-05-29
Built a simple text editor using the command pattern to handle operations like insert, delete, and replace with full undo/redo functionality.
"""

"""
A simple text editor implementation using the Command pattern.
Supports undo/redo for insert, delete, and replace operations.
I wanted to explore the command pattern with something practical — 
this felt more real than the usual lamp on/off examples.
"""

from abc import ABC, abstractmethod
from typing import List


class Command(ABC):
    """
    Abstract base class for all editor commands.
    Each command knows how to execute itself and undo its changes.
    """
    
    @abstractmethod
    def execute(self) -> None:
        """Execute the command and modify the editor state."""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Revert the changes made by this command."""
        pass


class TextEditor:
    """
    The receiver class that actually holds and manipulates the text.
    Commands will call methods on this class to perform operations.
    """
    
    def __init__(self):
        self.content = ""
    
    def insert_text(self, position: int, text: str) -> None:
        """Insert text at the specified position."""
        self.content = self.content[:position] + text + self.content[position:]
    
    def delete_text(self, position: int, length: int) -> str:
        """Delete text starting at position for the given length. Returns deleted text."""
        deleted = self.content[position:position + length]
        self.content = self.content[:position] + self.content[position + length:]
        return deleted
    
    def replace_text(self, position: int, length: int, new_text: str) -> str:
        """Replace text at position with new text. Returns old text."""
        old_text = self.content[position:position + length]
        self.content = self.content[:position] + new_text + self.content[position + length:]
        return old_text
    
    def get_content(self) -> str:
        """Return the current content."""
        return self.content


class InsertCommand(Command):
    """Command to insert text at a specific position."""
    
    def __init__(self, editor: TextEditor, position: int, text: str):
        self.editor = editor
        self.position = position
        self.text = text
    
    def execute(self) -> None:
        """Insert the text."""
        self.editor.insert_text(self.position, self.text)
    
    def undo(self) -> None:
        """Remove the inserted text."""
        self.editor.delete_text(self.position, len(self.text))


class DeleteCommand(Command):
    """Command to delete text from a specific position."""
    
    def __init__(self, editor: TextEditor, position: int, length: int):
        self.editor = editor
        self.position = position
        self.length = length
        self.deleted_text = ""  # Store what we deleted for undo
    
    def execute(self) -> None:
        """Delete the text and store it for potential undo."""
        self.deleted_text = self.editor.delete_text(self.position, self.length)
    
    def undo(self) -> None:
        """Reinsert the deleted text."""
        self.editor.insert_text(self.position, self.deleted_text)


class ReplaceCommand(Command):
    """Command to replace text at a specific position."""
    
    def __init__(self, editor: TextEditor, position: int, length: int, new_text: str):
        self.editor = editor
        self.position = position
        self.length = length
        self.new_text = new_text
        self.old_text = ""  # Store the old text for undo
    
    def execute(self) -> None:
        """Replace the text and store the old text."""
        self.old_text = self.editor.replace_text(self.position, self.length, self.new_text)
    
    def undo(self) -> None:
        """Restore the old text."""
        self.editor.replace_text(self.position, len(self.new_text), self.old_text)


class EditorInvoker:
    """
    The invoker that manages command execution and history.
    This is where the undo/redo magic happens — we maintain two stacks.
    """
    
    def __init__(self, editor: TextEditor):
        self.editor = editor
        self.history: List[Command] = []  # Commands we've executed
        self.redo_stack: List[Command] = []  # Commands we've undone
    
    def execute_command(self, command: Command) -> None:
        """Execute a command and add it to history."""
        command.execute()
        self.history.append(command)
        # Clear redo stack since we're on a new timeline now
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


if __name__ == "__main__":
    # Demo showing the command pattern in action
    editor = TextEditor()
    invoker = EditorInvoker(editor)
    
    print("=== Text Editor Command Pattern Demo ===\n")
    
    # Insert some text
    print("1. Inserting 'Hello World'")
    invoker.execute_command(InsertCommand(editor, 0, "Hello World"))
    print(f"   Content: '{editor.get_content()}'\n")
    
    # Insert more text
    print("2. Inserting ' from Python' at end")
    invoker.execute_command(InsertCommand(editor, len(editor.get_content()), " from Python"))
    print(f"   Content: '{editor.get_content()}'\n")
    
    # Replace some text
    print("3. Replacing 'World' with 'Mario'")
    invoker.execute_command(ReplaceCommand(editor, 6, 5, "Mario"))
    print(f"   Content: '{editor.get_content()}'\n")
    
    # Delete some text
    print("4. Deleting ' from Python'")
    invoker.execute_command(DeleteCommand(editor, 11, 12))
    print(f"   Content: '{editor.get_content()}'\n")
    
    # Undo last operation
    print("5. Undo (restore ' from Python')")
    invoker.undo()
    print(f"   Content: '{editor.get_content()}'\n")
    
    # Undo again
    print("6. Undo (restore 'World')")
    invoker.undo()
    print(f"   Content: '{editor.get_content()}'\n")
    
    # Redo
    print("7. Redo (back to 'Mario')")
    invoker.redo()
    print(f"   Content: '{editor.get_content()}'\n")
    
    # Try to redo when there's nothing left
    print("8. Redo again (should work)")
    if invoker.redo():
        print(f"   Content: '{editor.get_content()}'\n")
    
    print("9. Another redo (nothing to redo)")
    if not invoker.redo():
        print("   No more commands to redo")
    print(f"   Final content: '{editor.get_content()}'")