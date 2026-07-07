"""
Date: 2026-07-07
Built a simple text editor using the command pattern to handle operations like insert, delete, and replace with full undo/redo functionality.
"""

"""
A simple text editor implementation using the Command design pattern.
This lets me experiment with undo/redo functionality in a clean way.
Each edit operation is encapsulated as a command object.
"""

from abc import ABC, abstractmethod
from typing import List


class Command(ABC):
    """
    Abstract base class for all commands.
    Every command needs to know how to execute and undo itself.
    """
    
    @abstractmethod
    def execute(self) -> None:
        """Execute the command."""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Undo the command."""
        pass


class TextEditor:
    """
    The receiver in the command pattern.
    Holds the actual text content and provides low-level operations.
    """
    
    def __init__(self):
        self._content = ""
    
    def insert(self, position: int, text: str) -> None:
        """Insert text at the specified position."""
        self._content = self._content[:position] + text + self._content[position:]
    
    def delete(self, position: int, length: int) -> str:
        """Delete text from position and return the deleted text."""
        deleted = self._content[position:position + length]
        self._content = self._content[:position] + self._content[position + length:]
        return deleted
    
    def get_content(self) -> str:
        """Return the current content."""
        return self._content
    
    def set_content(self, content: str) -> None:
        """Set the entire content (used for undo operations)."""
        self._content = content


class InsertCommand(Command):
    """
    Command to insert text at a specific position.
    Stores what was inserted and where, so we can undo it.
    """
    
    def __init__(self, editor: TextEditor, position: int, text: str):
        self.editor = editor
        self.position = position
        self.text = text
    
    def execute(self) -> None:
        self.editor.insert(self.position, self.text)
    
    def undo(self) -> None:
        # Remove what we inserted
        self.editor.delete(self.position, len(self.text))


class DeleteCommand(Command):
    """
    Command to delete text from a position.
    Remembers what was deleted so we can restore it on undo.
    """
    
    def __init__(self, editor: TextEditor, position: int, length: int):
        self.editor = editor
        self.position = position
        self.length = length
        self.deleted_text = ""  # Will be filled during execute
    
    def execute(self) -> None:
        self.deleted_text = self.editor.delete(self.position, self.length)
    
    def undo(self) -> None:
        # Restore what was deleted
        self.editor.insert(self.position, self.deleted_text)


class ReplaceCommand(Command):
    """
    Command to replace text in a range with new text.
    This is essentially a delete followed by an insert, but tracked as one operation.
    """
    
    def __init__(self, editor: TextEditor, position: int, length: int, new_text: str):
        self.editor = editor
        self.position = position
        self.length = length
        self.new_text = new_text
        self.old_text = ""  # Filled during execute
    
    def execute(self) -> None:
        self.old_text = self.editor.delete(self.position, self.length)
        self.editor.insert(self.position, self.new_text)
    
    def undo(self) -> None:
        # Remove new text and restore old text
        self.editor.delete(self.position, len(self.new_text))
        self.editor.insert(self.position, self.old_text)


class EditorInvoker:
    """
    The invoker manages command history for undo/redo.
    This is where the magic happens — keeping track of what's been done.
    """
    
    def __init__(self, editor: TextEditor):
        self.editor = editor
        self.history: List[Command] = []
        self.redo_stack: List[Command] = []
    
    def execute_command(self, command: Command) -> None:
        """Execute a command and add it to history."""
        command.execute()
        self.history.append(command)
        # Clear redo stack when a new command is executed
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
    # Demo of the text editor with command pattern
    print("=== Text Editor with Command Pattern ===\n")
    
    editor = TextEditor()
    invoker = EditorInvoker(editor)
    
    # Insert some text
    print("1. Insert 'Hello' at position 0")
    invoker.execute_command(InsertCommand(editor, 0, "Hello"))
    print(f"   Content: '{editor.get_content()}'")
    
    # Insert more text
    print("\n2. Insert ' World' at position 5")
    invoker.execute_command(InsertCommand(editor, 5, " World"))
    print(f"   Content: '{editor.get_content()}'")
    
    # Insert at the end
    print("\n3. Insert '!' at position 11")
    invoker.execute_command(InsertCommand(editor, 11, "!"))
    print(f"   Content: '{editor.get_content()}'")
    
    # Delete some text
    print("\n4. Delete 6 characters starting from position 5")
    invoker.execute_command(DeleteCommand(editor, 5, 6))
    print(f"   Content: '{editor.get_content()}'")
    
    # Undo the delete
    print("\n5. Undo last operation")
    invoker.undo()
    print(f"   Content: '{editor.get_content()}'")
    
    # Replace text
    print("\n6. Replace 'World' with 'Python' (position 6, length 5)")
    invoker.execute_command(ReplaceCommand(editor, 6, 5, "Python"))
    print(f"   Content: '{editor.get_content()}'")
    
    # Multiple undos
    print("\n7. Undo twice")
    invoker.undo()
    print(f"   After first undo: '{editor.get_content()}'")
    invoker.undo()
    print(f"   After second undo: '{editor.get_content()}'")
    
    # Redo
    print("\n8. Redo once")
    invoker.redo()
    print(f"   Content: '{editor.get_content()}'")
    
    print("\n=== Demo Complete ===")