"""
Date: 2026-06-13
Built a command pattern implementation for a simple text editor with plugin-style operations that can be undone, redone, and logged — wanted something practical to show how the pattern actually helps.
"""

#!/usr/bin/env python3
"""
Command pattern implementation for a text editor with plugin-style operations.
Each operation (insert, delete, replace) is encapsulated as a command object
that can be executed, undone, and tracked in history.
"""

from abc import ABC, abstractmethod
from typing import List, Optional


class Command(ABC):
    """Abstract base class for all commands."""
    
    @abstractmethod
    def execute(self) -> None:
        """Execute the command."""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Undo the command."""
        pass
    
    @abstractmethod
    def description(self) -> str:
        """Return a human-readable description of the command."""
        pass


class TextBuffer:
    """
    The receiver in the command pattern — holds the actual text content.
    Commands operate on this buffer.
    """
    
    def __init__(self):
        self.content = ""
    
    def insert(self, position: int, text: str) -> None:
        """Insert text at the specified position."""
        self.content = self.content[:position] + text + self.content[position:]
    
    def delete(self, position: int, length: int) -> str:
        """Delete text at position and return the deleted text."""
        deleted = self.content[position:position + length]
        self.content = self.content[:position] + self.content[position + length:]
        return deleted
    
    def replace(self, position: int, length: int, new_text: str) -> str:
        """Replace text at position and return the old text."""
        old_text = self.content[position:position + length]
        self.content = self.content[:position] + new_text + self.content[position + length:]
        return old_text
    
    def __str__(self) -> str:
        return self.content


class InsertCommand(Command):
    """Command to insert text at a specific position."""
    
    def __init__(self, buffer: TextBuffer, position: int, text: str):
        self.buffer = buffer
        self.position = position
        self.text = text
    
    def execute(self) -> None:
        self.buffer.insert(self.position, self.text)
    
    def undo(self) -> None:
        # To undo an insert, we delete what we inserted
        self.buffer.delete(self.position, len(self.text))
    
    def description(self) -> str:
        return f"Insert '{self.text}' at position {self.position}"


class DeleteCommand(Command):
    """Command to delete text at a specific position."""
    
    def __init__(self, buffer: TextBuffer, position: int, length: int):
        self.buffer = buffer
        self.position = position
        self.length = length
        self.deleted_text: Optional[str] = None
    
    def execute(self) -> None:
        # Store what we deleted so we can undo it
        self.deleted_text = self.buffer.delete(self.position, self.length)
    
    def undo(self) -> None:
        if self.deleted_text is not None:
            self.buffer.insert(self.position, self.deleted_text)
    
    def description(self) -> str:
        return f"Delete {self.length} chars at position {self.position}"


class ReplaceCommand(Command):
    """Command to replace text at a specific position."""
    
    def __init__(self, buffer: TextBuffer, position: int, length: int, new_text: str):
        self.buffer = buffer
        self.position = position
        self.length = length
        self.new_text = new_text
        self.old_text: Optional[str] = None
    
    def execute(self) -> None:
        self.old_text = self.buffer.replace(self.position, self.length, self.new_text)
    
    def undo(self) -> None:
        if self.old_text is not None:
            self.buffer.replace(self.position, len(self.new_text), self.old_text)
    
    def description(self) -> str:
        return f"Replace {self.length} chars at position {self.position} with '{self.new_text}'"


class CommandManager:
    """
    The invoker in the command pattern — manages command execution and history.
    Supports undo/redo functionality.
    """
    
    def __init__(self):
        self.history: List[Command] = []
        self.redo_stack: List[Command] = []
    
    def execute(self, command: Command) -> None:
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
    
    def show_history(self) -> None:
        """Print the command history."""
        print("\n📜 Command History:")
        for i, cmd in enumerate(self.history, 1):
            print(f"  {i}. {cmd.description()}")


if __name__ == "__main__":
    # Create our text buffer and command manager
    buffer = TextBuffer()
    manager = CommandManager()
    
    print("=== Text Editor Command Pattern Demo ===\n")
    print(f"Initial buffer: '{buffer}'")
    
    # Execute a series of commands
    print("\n--- Executing commands ---")
    manager.execute(InsertCommand(buffer, 0, "Hello"))
    print(f"After insert: '{buffer}'")
    
    manager.execute(InsertCommand(buffer, 5, " World"))
    print(f"After insert: '{buffer}'")
    
    manager.execute(ReplaceCommand(buffer, 0, 5, "Hey"))
    print(f"After replace: '{buffer}'")
    
    manager.execute(InsertCommand(buffer, 3, " there"))
    print(f"After insert: '{buffer}'")
    
    manager.show_history()
    
    # Demonstrate undo
    print("\n--- Undoing last 2 commands ---")
    manager.undo()
    print(f"After undo: '{buffer}'")
    manager.undo()
    print(f"After undo: '{buffer}'")
    
    # Demonstrate redo
    print("\n--- Redoing 1 command ---")
    manager.redo()
    print(f"After redo: '{buffer}'")
    
    manager.show_history()
    
    # One more operation to show redo stack gets cleared
    print("\n--- Executing new command (clears redo stack) ---")
    manager.execute(DeleteCommand(buffer, 0, 3))
    print(f"After delete: '{buffer}'")
    
    manager.show_history()