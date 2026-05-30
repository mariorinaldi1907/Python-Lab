"""
Date: 2026-05-30
Built a text editor using the command pattern to handle undo/redo functionality cleanly, something I've always wanted to explore after dealing with messy state management in other projects.
"""

#!/usr/bin/env python3
"""
A simple text editor implementation using the Command Pattern.
Each operation (insert, delete, replace) is encapsulated as a command object
that knows how to execute and undo itself. This makes undo/redo trivial.
"""

from abc import ABC, abstractmethod
from typing import List


class Command(ABC):
    """
    Abstract base class for all editor commands.
    Each command must know how to execute and undo itself.
    """
    
    @abstractmethod
    def execute(self) -> None:
        """Apply the command to the editor."""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Reverse the command's effect."""
        pass


class InsertCommand(Command):
    """
    Inserts text at a specific position.
    Stores position and text so it can undo by deleting what it inserted.
    """
    
    def __init__(self, editor: 'TextEditor', position: int, text: str):
        self.editor = editor
        self.position = position
        self.text = text
    
    def execute(self) -> None:
        """Insert text at the stored position."""
        current = self.editor.get_content()
        new_content = current[:self.position] + self.text + current[self.position:]
        self.editor.set_content(new_content)
    
    def undo(self) -> None:
        """Remove the text that was inserted."""
        current = self.editor.get_content()
        new_content = current[:self.position] + current[self.position + len(self.text):]
        self.editor.set_content(new_content)


class DeleteCommand(Command):
    """
    Deletes text from position to position+length.
    Stores the deleted text so it can be restored on undo.
    """
    
    def __init__(self, editor: 'TextEditor', position: int, length: int):
        self.editor = editor
        self.position = position
        self.length = length
        self.deleted_text = ""  # Will store what we delete
    
    def execute(self) -> None:
        """Delete text and remember what was deleted."""
        current = self.editor.get_content()
        self.deleted_text = current[self.position:self.position + self.length]
        new_content = current[:self.position] + current[self.position + self.length:]
        self.editor.set_content(new_content)
    
    def undo(self) -> None:
        """Re-insert the deleted text."""
        current = self.editor.get_content()
        new_content = current[:self.position] + self.deleted_text + current[self.position:]
        self.editor.set_content(new_content)


class ReplaceCommand(Command):
    """
    Replaces text from position to position+length with new text.
    Stores both old and new text for proper undo/redo.
    """
    
    def __init__(self, editor: 'TextEditor', position: int, length: int, new_text: str):
        self.editor = editor
        self.position = position
        self.length = length
        self.new_text = new_text
        self.old_text = ""  # Will store what we replace
    
    def execute(self) -> None:
        """Replace text and remember the original."""
        current = self.editor.get_content()
        self.old_text = current[self.position:self.position + self.length]
        new_content = current[:self.position] + self.new_text + current[self.position + self.length:]
        self.editor.set_content(new_content)
    
    def undo(self) -> None:
        """Restore the original text."""
        current = self.editor.get_content()
        new_content = current[:self.position] + self.old_text + current[self.position + len(self.new_text):]
        self.editor.set_content(new_content)


class TextEditor:
    """
    The actual editor that holds the text content.
    Uses a command pattern so undo/redo is just a matter of
    keeping track of command history.
    """
    
    def __init__(self):
        self._content = ""
        self._history: List[Command] = []  # Commands that have been executed
        self._redo_stack: List[Command] = []  # Commands that have been undone
    
    def get_content(self) -> str:
        """Return the current text content."""
        return self._content
    
    def set_content(self, content: str) -> None:
        """Directly set the content (used by commands)."""
        self._content = content
    
    def execute_command(self, command: Command) -> None:
        """
        Execute a command and add it to history.
        Clears redo stack since we're on a new timeline now.
        """
        command.execute()
        self._history.append(command)
        self._redo_stack.clear()  # Can't redo after new action
    
    def undo(self) -> bool:
        """
        Undo the last command if possible.
        Returns True if undo was performed, False if nothing to undo.
        """
        if not self._history:
            return False
        
        command = self._history.pop()
        command.undo()
        self._redo_stack.append(command)
        return True
    
    def redo(self) -> bool:
        """
        Redo the last undone command if possible.
        Returns True if redo was performed, False if nothing to redo.
        """
        if not self._redo_stack:
            return False
        
        command = self._redo_stack.pop()
        command.execute()
        self._history.append(command)
        return True
    
    def __str__(self) -> str:
        """String representation showing current content."""
        return f"Content: '{self._content}'"


if __name__ == "__main__":
    # Create a new editor
    editor = TextEditor()
    print("=== Text Editor with Command Pattern ===\n")
    
    # Start with some text
    print("1. Inserting 'Hello World'")
    cmd1 = InsertCommand(editor, 0, "Hello World")
    editor.execute_command(cmd1)
    print(editor)
    print()
    
    # Insert some more text in the middle
    print("2. Inserting ' Beautiful' after 'Hello'")
    cmd2 = InsertCommand(editor, 5, " Beautiful")
    editor.execute_command(cmd2)
    print(editor)
    print()
    
    # Delete part of the text
    print("3. Deleting ' Beautiful' (9 chars from position 5)")
    cmd3 = DeleteCommand(editor, 5, 10)
    editor.execute_command(cmd3)
    print(editor)
    print()
    
    # Replace text
    print("4. Replacing 'World' with 'Python'")
    cmd4 = ReplaceCommand(editor, 6, 5, "Python")
    editor.execute_command(cmd4)
    print(editor)
    print()
    
    # Undo last action
    print("5. Undo (restore 'World')")
    editor.undo()
    print(editor)
    print()
    
    # Undo again
    print("6. Undo (restore ' Beautiful')")
    editor.undo()
    print(editor)
    print()
    
    # Redo
    print("7. Redo (remove ' Beautiful' again)")
    editor.redo()
    print(editor)
    print()
    
    # Redo again
    print("8. Redo (replace with 'Python' again)")
    editor.redo()
    print(editor)
    print()
    
    # New action clears redo stack
    print("9. Insert '!' at the end (this clears redo stack)")
    cmd5 = InsertCommand(editor, len(editor.get_content()), "!")
    editor.execute_command(cmd5)
    print(editor)
    print()
    
    # Try to redo (should fail)
    print("10. Trying to redo (should fail since we made a new edit)")
    if not editor.redo():
        print("Nothing to redo!")
    print(editor)