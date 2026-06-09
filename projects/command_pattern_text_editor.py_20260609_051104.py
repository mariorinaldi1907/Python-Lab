"""
Date: 2026-06-09
Built a simple text editor using the command pattern because I wanted to understand how undo/redo actually works under the hood in real applications.
"""

"""
A text editor demonstrating the Command pattern.

I built this to finally understand how undo/redo works in apps like vim or VSCode.
The Command pattern encapsulates each operation (insert, delete, etc.) as an object,
which makes implementing undo/redo stacks super straightforward.
"""

from abc import ABC, abstractmethod
from typing import List


class Command(ABC):
    """
    Abstract base class for all commands.
    
    Each command knows how to execute itself and undo itself.
    This is the core of the pattern — treating operations as first-class objects.
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
    The actual text buffer that stores our content.
    
    This is the "receiver" in command pattern terminology — it knows how to
    actually perform the operations, but doesn't know anything about undo/redo.
    """
    
    def __init__(self):
        self.content = ""
    
    def insert(self, position: int, text: str) -> None:
        """Insert text at a specific position."""
        self.content = self.content[:position] + text + self.content[position:]
    
    def delete(self, position: int, length: int) -> str:
        """Delete text and return what was deleted (needed for undo)."""
        deleted = self.content[position:position + length]
        self.content = self.content[:position] + self.content[position + length:]
        return deleted
    
    def get_text(self) -> str:
        """Get the full content."""
        return self.content


class InsertCommand(Command):
    """
    Command to insert text at a position.
    
    Stores everything needed to undo the operation later.
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
    Command to delete text at a position.
    
    We need to remember what was deleted so we can restore it during undo.
    """
    
    def __init__(self, buffer: TextBuffer, position: int, length: int):
        self.buffer = buffer
        self.position = position
        self.length = length
        self.deleted_text = ""  # Will be populated during execute
    
    def execute(self) -> None:
        """Delete the text and remember what we deleted."""
        self.deleted_text = self.buffer.delete(self.position, self.length)
    
    def undo(self) -> None:
        """Restore the deleted text."""
        self.buffer.insert(self.position, self.deleted_text)


class TextEditor:
    """
    The text editor that manages the command history.
    
    This is where the magic happens — we maintain two stacks for undo and redo.
    When you execute a command, it goes on the undo stack. When you undo,
    it moves to the redo stack. When you execute a new command, redo stack is cleared.
    """
    
    def __init__(self):
        self.buffer = TextBuffer()
        self.undo_stack: List[Command] = []
        self.redo_stack: List[Command] = []
    
    def execute_command(self, command: Command) -> None:
        """
        Execute a command and add it to history.
        
        Any new command clears the redo stack — this matches how real editors work.
        """
        command.execute()
        self.undo_stack.append(command)
        self.redo_stack.clear()  # Can't redo after a new operation
    
    def undo(self) -> bool:
        """
        Undo the last command.
        
        Returns True if something was undone, False if nothing to undo.
        """
        if not self.undo_stack:
            return False
        
        command = self.undo_stack.pop()
        command.undo()
        self.redo_stack.append(command)
        return True
    
    def redo(self) -> bool:
        """
        Redo the last undone command.
        
        Returns True if something was redone, False if nothing to redo.
        """
        if not self.redo_stack:
            return False
        
        command = self.redo_stack.pop()
        command.execute()
        self.undo_stack.append(command)
        return True
    
    def get_text(self) -> str:
        """Get the current buffer content."""
        return self.buffer.get_text()


if __name__ == "__main__":
    # Demo time! Let's simulate editing a simple text document
    editor = TextEditor()
    
    print("=== Text Editor Command Pattern Demo ===\n")
    
    # Start with some text
    print("1. Insert 'Hello '")
    editor.execute_command(InsertCommand(editor.buffer, 0, "Hello "))
    print(f"   Content: '{editor.get_text()}'\n")
    
    # Add more text
    print("2. Insert 'world'")
    editor.execute_command(InsertCommand(editor.buffer, 6, "world"))
    print(f"   Content: '{editor.get_text()}'\n")
    
    # Insert in the middle
    print("3. Insert 'beautiful ' at position 6")
    editor.execute_command(InsertCommand(editor.buffer, 6, "beautiful "))
    print(f"   Content: '{editor.get_text()}'\n")
    
    # Undo last operation
    print("4. Undo (remove 'beautiful ')")
    editor.undo()
    print(f"   Content: '{editor.get_text()}'\n")
    
    # Redo it
    print("5. Redo (add 'beautiful ' back)")
    editor.redo()
    print(f"   Content: '{editor.get_text()}'\n")
    
    # Delete some text
    print("6. Delete 10 characters starting at position 6")
    editor.execute_command(DeleteCommand(editor.buffer, 6, 10))
    print(f"   Content: '{editor.get_text()}'\n")
    
    # Undo the deletion
    print("7. Undo (restore 'beautiful ')")
    editor.undo()
    print(f"   Content: '{editor.get_text()}'\n")
    
    # Multiple undos
    print("8. Undo again")
    editor.undo()
    print(f"   Content: '{editor.get_text()}'\n")
    
    print("9. Undo again")
    editor.undo()
    print(f"   Content: '{editor.get_text()}'\n")
    
    # Try to undo when nothing left
    print("10. Try to undo (should fail gracefully)")
    if not editor.undo():
        print("    Nothing to undo!\n")
    
    # Redo a few times
    print("11. Redo twice")
    editor.redo()
    editor.redo()
    print(f"    Content: '{editor.get_text()}'\n")
    
    print("=== Demo complete! ===")