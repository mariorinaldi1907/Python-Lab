"""
Date: 2026-08-19
Built a command pattern implementation for a simple text editor that supports full undo/redo functionality using a stack-based history.
"""

#!/usr/bin/env python3
"""
Text editor with undo/redo using the Command Pattern.

I wanted to build something practical that shows how the command pattern
really shines when you need reversible operations. This simulates a
basic text editor where every action can be undone and redone.
"""

from abc import ABC, abstractmethod
from typing import List


class Command(ABC):
    """
    Abstract base class for all commands.
    
    Each command knows how to execute itself and undo itself.
    This is the core of the command pattern.
    """
    
    @abstractmethod
    def execute(self) -> None:
        """Execute the command."""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Reverse the command's effect."""
        pass


class TextDocument:
    """
    The receiver in the command pattern.
    
    This is what actually holds the text and performs operations.
    Commands will delegate to this object.
    """
    
    def __init__(self):
        self.content = ""
    
    def insert(self, position: int, text: str) -> None:
        """Insert text at a specific position."""
        self.content = self.content[:position] + text + self.content[position:]
    
    def delete(self, position: int, length: int) -> str:
        """Delete text and return what was deleted (for undo purposes)."""
        deleted = self.content[position:position + length]
        self.content = self.content[:position] + self.content[position + length:]
        return deleted
    
    def replace(self, position: int, length: int, new_text: str) -> str:
        """Replace text and return the old text."""
        old_text = self.content[position:position + length]
        self.content = self.content[:position] + new_text + self.content[position + length:]
        return old_text
    
    def get_content(self) -> str:
        """Return the current document content."""
        return self.content


class InsertCommand(Command):
    """Command to insert text into the document."""
    
    def __init__(self, document: TextDocument, position: int, text: str):
        self.document = document
        self.position = position
        self.text = text
    
    def execute(self) -> None:
        """Insert the text at the stored position."""
        self.document.insert(self.position, self.text)
    
    def undo(self) -> None:
        """Remove the text we inserted."""
        self.document.delete(self.position, len(self.text))


class DeleteCommand(Command):
    """Command to delete text from the document."""
    
    def __init__(self, document: TextDocument, position: int, length: int):
        self.document = document
        self.position = position
        self.length = length
        self.deleted_text = ""  # Store what we delete so we can restore it
    
    def execute(self) -> None:
        """Delete text and remember what was deleted."""
        self.deleted_text = self.document.delete(self.position, self.length)
    
    def undo(self) -> None:
        """Re-insert the deleted text."""
        self.document.insert(self.position, self.deleted_text)


class ReplaceCommand(Command):
    """Command to replace text in the document."""
    
    def __init__(self, document: TextDocument, position: int, length: int, new_text: str):
        self.document = document
        self.position = position
        self.length = length
        self.new_text = new_text
        self.old_text = ""  # Store original text for undo
    
    def execute(self) -> None:
        """Replace text and save the old text."""
        self.old_text = self.document.replace(self.position, self.length, self.new_text)
    
    def undo(self) -> None:
        """Restore the original text."""
        self.document.replace(self.position, len(self.new_text), self.old_text)


class TextEditor:
    """
    The invoker in the command pattern.
    
    This manages command history and provides undo/redo functionality.
    I'm using two stacks here — one for undo history and one for redo.
    """
    
    def __init__(self):
        self.document = TextDocument()
        self.history: List[Command] = []
        self.redo_stack: List[Command] = []
    
    def execute_command(self, command: Command) -> None:
        """Execute a command and add it to history."""
        command.execute()
        self.history.append(command)
        # Clear redo stack when a new command is executed
        # (can't redo after making new changes)
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
    
    def get_content(self) -> str:
        """Get the current document content."""
        return self.document.get_content()


if __name__ == "__main__":
    # Demo showing the command pattern in action
    print("=== Text Editor with Undo/Redo ===\n")
    
    editor = TextEditor()
    
    # Start typing
    print("1. Insert 'Hello'")
    editor.execute_command(InsertCommand(editor.document, 0, "Hello"))
    print(f"   Content: '{editor.get_content()}'\n")
    
    print("2. Insert ' World' at position 5")
    editor.execute_command(InsertCommand(editor.document, 5, " World"))
    print(f"   Content: '{editor.get_content()}'\n")
    
    print("3. Insert '!' at the end")
    editor.execute_command(InsertCommand(editor.document, 11, "!"))
    print(f"   Content: '{editor.get_content()}'\n")
    
    print("4. Replace 'World' with 'Python' (position 6, length 5)")
    editor.execute_command(ReplaceCommand(editor.document, 6, 5, "Python"))
    print(f"   Content: '{editor.get_content()}'\n")
    
    print("5. Undo last command (replace)")
    editor.undo()
    print(f"   Content: '{editor.get_content()}'\n")
    
    print("6. Undo again (remove '!')")
    editor.undo()
    print(f"   Content: '{editor.get_content()}'\n")
    
    print("7. Redo (add '!' back)")
    editor.redo()
    print(f"   Content: '{editor.get_content()}'\n")
    
    print("8. Delete ' World' (position 5, length 6)")
    editor.execute_command(DeleteCommand(editor.document, 5, 6))
    print(f"   Content: '{editor.get_content()}'\n")
    
    print("9. Undo delete")
    editor.undo()
    print(f"   Content: '{editor.get_content()}'\n")
    
    print("Demo complete! The command pattern makes undo/redo elegant.")