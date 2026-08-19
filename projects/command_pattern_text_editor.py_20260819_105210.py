"""
Date: 2026-08-19
Built a text editor using the command pattern to handle operations like insert, delete, and replace with full undo/redo functionality — actually pretty satisfying to see it work.
"""

"""
Text Editor using Command Pattern

A simple demonstration of the Command pattern with undo/redo capabilities.
I wanted to explore how editors like vim implement their undo stacks, so I built
this minimal version that tracks text operations and allows you to rewind them.
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


class TextBuffer:
    """
    The receiver in the command pattern.
    Holds the actual text content and provides low-level operations.
    """
    
    def __init__(self):
        self.content = ""
    
    def insert(self, position: int, text: str) -> None:
        """Insert text at the specified position."""
        self.content = self.content[:position] + text + self.content[position:]
    
    def delete(self, position: int, length: int) -> str:
        """Delete text at position and return what was deleted."""
        deleted = self.content[position:position + length]
        self.content = self.content[:position] + self.content[position + length:]
        return deleted
    
    def replace(self, position: int, length: int, text: str) -> str:
        """Replace text at position and return what was replaced."""
        replaced = self.content[position:position + length]
        self.content = self.content[:position] + text + self.content[position + length:]
        return replaced
    
    def get_content(self) -> str:
        """Return the current content."""
        return self.content


class InsertCommand(Command):
    """
    Command to insert text at a specific position.
    Stores enough info to undo the insertion.
    """
    
    def __init__(self, buffer: TextBuffer, position: int, text: str):
        self.buffer = buffer
        self.position = position
        self.text = text
    
    def execute(self) -> None:
        """Insert the text."""
        self.buffer.insert(self.position, self.text)
    
    def undo(self) -> None:
        """Remove what we inserted."""
        self.buffer.delete(self.position, len(self.text))


class DeleteCommand(Command):
    """
    Command to delete text at a specific position.
    Saves the deleted text so we can restore it on undo.
    """
    
    def __init__(self, buffer: TextBuffer, position: int, length: int):
        self.buffer = buffer
        self.position = position
        self.length = length
        self.deleted_text = ""  # We'll capture this on execute
    
    def execute(self) -> None:
        """Delete the text and save what was deleted."""
        self.deleted_text = self.buffer.delete(self.position, self.length)
    
    def undo(self) -> None:
        """Re-insert the deleted text."""
        self.buffer.insert(self.position, self.deleted_text)


class ReplaceCommand(Command):
    """
    Command to replace text at a position.
    Essentially a delete + insert, but as a single atomic operation.
    """
    
    def __init__(self, buffer: TextBuffer, position: int, length: int, new_text: str):
        self.buffer = buffer
        self.position = position
        self.length = length
        self.new_text = new_text
        self.old_text = ""  # Captured on execute
    
    def execute(self) -> None:
        """Replace text and save the old version."""
        self.old_text = self.buffer.replace(self.position, self.length, self.new_text)
    
    def undo(self) -> None:
        """Restore the old text."""
        self.buffer.replace(self.position, len(self.new_text), self.old_text)


class TextEditor:
    """
    The invoker in the command pattern.
    Manages command history and provides undo/redo functionality.
    """
    
    def __init__(self):
        self.buffer = TextBuffer()
        self.history: List[Command] = []
        self.redo_stack: List[Command] = []
    
    def execute_command(self, command: Command) -> None:
        """Execute a command and add it to history."""
        command.execute()
        self.history.append(command)
        # Clear redo stack when new command is executed
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
    
    def get_text(self) -> str:
        """Get the current text content."""
        return self.buffer.get_content()


if __name__ == "__main__":
    print("=== Text Editor with Command Pattern Demo ===\n")
    
    editor = TextEditor()
    
    # Build up some text with various operations
    print("1. Inserting 'Hello'")
    editor.execute_command(InsertCommand(editor.buffer, 0, "Hello"))
    print(f"   Content: '{editor.get_text()}'")
    
    print("\n2. Inserting ' World' at the end")
    editor.execute_command(InsertCommand(editor.buffer, 5, " World"))
    print(f"   Content: '{editor.get_text()}'")
    
    print("\n3. Inserting ' Beautiful' in the middle")
    editor.execute_command(InsertCommand(editor.buffer, 5, " Beautiful"))
    print(f"   Content: '{editor.get_text()}'")
    
    print("\n4. Replacing 'Beautiful' with 'Awesome'")
    editor.execute_command(ReplaceCommand(editor.buffer, 6, 9, "Awesome"))
    print(f"   Content: '{editor.get_text()}'")
    
    print("\n5. Deleting 'Awesome ' (8 chars)")
    editor.execute_command(DeleteCommand(editor.buffer, 6, 8))
    print(f"   Content: '{editor.get_text()}'")
    
    # Demonstrate undo
    print("\n--- Undo Operations ---")
    for i in range(3):
        print(f"\nUndo #{i+1}")
        editor.undo()
        print(f"   Content: '{editor.get_text()}'")
    
    # Demonstrate redo
    print("\n--- Redo Operations ---")
    for i in range(2):
        print(f"\nRedo #{i+1}")
        editor.redo()
        print(f"   Content: '{editor.get_text()}'")
    
    print("\n--- Final State ---")
    print(f"Content: '{editor.get_text()}'")