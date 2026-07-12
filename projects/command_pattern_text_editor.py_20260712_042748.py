"""
Date: 2026-07-12
Built a text editor simulator using the command pattern to handle undo/redo operations, which I've always wanted to implement properly.
"""

#!/usr/bin/env python3
"""
Text editor with undo/redo using the Command pattern.

I wanted to explore the Command pattern in a realistic scenario, so I built
this mini text editor that tracks every action (insert, delete, replace) and
lets you undo/redo them. It's surprisingly satisfying to see the state roll
back and forward cleanly.
"""

from abc import ABC, abstractmethod
from typing import List


class Command(ABC):
    """
    Abstract base class for all editor commands.
    
    Each command knows how to execute itself and undo itself. This is the
    core of the pattern — actions become first-class objects.
    """
    
    @abstractmethod
    def execute(self) -> None:
        """Execute the command and modify the editor state."""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Reverse the command's effect on the editor state."""
        pass


class InsertCommand(Command):
    """Insert text at a specific position in the document."""
    
    def __init__(self, editor: 'TextEditor', position: int, text: str):
        """
        Args:
            editor: The editor instance to operate on
            position: Where to insert the text (0-indexed)
            text: The text to insert
        """
        self.editor = editor
        self.position = position
        self.text = text
    
    def execute(self) -> None:
        """Insert the text at the specified position."""
        self.editor.content = (
            self.editor.content[:self.position] + 
            self.text + 
            self.editor.content[self.position:]
        )
    
    def undo(self) -> None:
        """Remove the text that was inserted."""
        self.editor.content = (
            self.editor.content[:self.position] + 
            self.editor.content[self.position + len(self.text):]
        )


class DeleteCommand(Command):
    """Delete a range of text from the document."""
    
    def __init__(self, editor: 'TextEditor', start: int, end: int):
        """
        Args:
            editor: The editor instance to operate on
            start: Starting position of deletion (inclusive)
            end: Ending position of deletion (exclusive)
        """
        self.editor = editor
        self.start = start
        self.end = end
        self.deleted_text = ""  # We'll store this when executing
    
    def execute(self) -> None:
        """Delete the text and remember it for undo."""
        self.deleted_text = self.editor.content[self.start:self.end]
        self.editor.content = (
            self.editor.content[:self.start] + 
            self.editor.content[self.end:]
        )
    
    def undo(self) -> None:
        """Restore the deleted text."""
        self.editor.content = (
            self.editor.content[:self.start] + 
            self.deleted_text + 
            self.editor.content[self.start:]
        )


class ReplaceCommand(Command):
    """Replace a range of text with new text."""
    
    def __init__(self, editor: 'TextEditor', start: int, end: int, new_text: str):
        """
        Args:
            editor: The editor instance to operate on
            start: Starting position of replacement (inclusive)
            end: Ending position of replacement (exclusive)
            new_text: The text to insert in place of the old text
        """
        self.editor = editor
        self.start = start
        self.end = end
        self.new_text = new_text
        self.old_text = ""  # Store the original text for undo
    
    def execute(self) -> None:
        """Replace the text range with new text."""
        self.old_text = self.editor.content[self.start:self.end]
        self.editor.content = (
            self.editor.content[:self.start] + 
            self.new_text + 
            self.editor.content[self.end:]
        )
    
    def undo(self) -> None:
        """Restore the original text."""
        # Calculate where the new text ends
        new_end = self.start + len(self.new_text)
        self.editor.content = (
            self.editor.content[:self.start] + 
            self.old_text + 
            self.editor.content[new_end:]
        )


class TextEditor:
    """
    A simple text editor that supports undo/redo operations.
    
    This uses the Command pattern to keep a history of all operations.
    I keep two stacks: one for undo (past commands) and one for redo
    (undone commands that can be reapplied).
    """
    
    def __init__(self):
        """Initialize an empty editor with empty history."""
        self.content = ""
        self.history: List[Command] = []
        self.redo_stack: List[Command] = []
    
    def execute_command(self, command: Command) -> None:
        """
        Execute a command and add it to history.
        
        When a new command is executed, we clear the redo stack because
        the old "future" is no longer valid.
        """
        command.execute()
        self.history.append(command)
        self.redo_stack.clear()  # New action invalidates redo history
    
    def undo(self) -> bool:
        """
        Undo the last command.
        
        Returns:
            True if undo was successful, False if nothing to undo
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
        
        Returns:
            True if redo was successful, False if nothing to redo
        """
        if not self.redo_stack:
            return False
        
        command = self.redo_stack.pop()
        command.execute()
        self.history.append(command)
        return True
    
    def get_content(self) -> str:
        """Return the current document content."""
        return self.content


if __name__ == "__main__":
    # Demo: simulate a realistic editing session
    editor = TextEditor()
    
    print("=== Text Editor with Undo/Redo ===\n")
    
    # Start typing
    print("Action: Insert 'Hello, world!'")
    editor.execute_command(InsertCommand(editor, 0, "Hello, world!"))
    print(f"Content: '{editor.get_content()}'\n")
    
    # Add more text
    print("Action: Insert ' How are you?' at end")
    editor.execute_command(InsertCommand(editor, len(editor.get_content()), " How are you?"))
    print(f"Content: '{editor.get_content()}'\n")
    
    # Fix a mistake
    print("Action: Replace 'world' with 'Python'")
    editor.execute_command(ReplaceCommand(editor, 7, 12, "Python"))
    print(f"Content: '{editor.get_content()}'\n")
    
    # Delete something
    print("Action: Delete ' How are you?'")
    editor.execute_command(DeleteCommand(editor, 14, len(editor.get_content())))
    print(f"Content: '{editor.get_content()}'\n")
    
    # Oops, undo that deletion
    print("Action: Undo (restore ' How are you?')")
    editor.undo()
    print(f"Content: '{editor.get_content()}'\n")
    
    # Actually, let's undo the replacement too
    print("Action: Undo (restore 'world')")
    editor.undo()
    print(f"Content: '{editor.get_content()}'\n")
    
    # Change our mind and redo
    print("Action: Redo (back to 'Python')")
    editor.redo()
    print(f"Content: '{editor.get_content()}'\n")
    
    print("=== Demo complete! ===")