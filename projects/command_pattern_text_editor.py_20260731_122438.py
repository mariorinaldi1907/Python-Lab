"""
Date: 2026-07-31
Built a text editor simulator using the command pattern because I wanted a clean way to handle undo/redo without spaghetti code.
"""

"""
Text Editor with Command Pattern
---------------------------------
I built this to practice the command pattern in a real scenario.
The idea is that every operation (insert, delete, etc.) is a command object
that knows how to execute itself AND undo itself. This makes undo/redo trivial.
"""

from abc import ABC, abstractmethod
from typing import List


class Command(ABC):
    """
    Abstract base class for all editor commands.
    Each command must implement execute() and undo().
    """
    
    @abstractmethod
    def execute(self) -> None:
        """Perform the command's action."""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Reverse the command's action."""
        pass


class InsertCommand(Command):
    """
    Command to insert text at a specific position.
    Stores the position and text so we can reverse it later.
    """
    
    def __init__(self, editor: 'TextEditor', position: int, text: str):
        self.editor = editor
        self.position = position
        self.text = text
    
    def execute(self) -> None:
        """Insert text at the stored position."""
        self.editor._content = (
            self.editor._content[:self.position] + 
            self.text + 
            self.editor._content[self.position:]
        )
    
    def undo(self) -> None:
        """Remove the text we just inserted."""
        end_pos = self.position + len(self.text)
        self.editor._content = (
            self.editor._content[:self.position] + 
            self.editor._content[end_pos:]
        )


class DeleteCommand(Command):
    """
    Command to delete text from a position.
    We store what was deleted so we can restore it on undo.
    """
    
    def __init__(self, editor: 'TextEditor', position: int, length: int):
        self.editor = editor
        self.position = position
        self.length = length
        self.deleted_text = ""  # Will store what we delete
    
    def execute(self) -> None:
        """Delete text and remember what we deleted."""
        end_pos = self.position + self.length
        self.deleted_text = self.editor._content[self.position:end_pos]
        self.editor._content = (
            self.editor._content[:self.position] + 
            self.editor._content[end_pos:]
        )
    
    def undo(self) -> None:
        """Put back the deleted text."""
        self.editor._content = (
            self.editor._content[:self.position] + 
            self.deleted_text + 
            self.editor._content[self.position:]
        )


class ReplaceCommand(Command):
    """
    Command to replace text at a position.
    This is basically delete + insert but as a single atomic operation.
    """
    
    def __init__(self, editor: 'TextEditor', position: int, length: int, new_text: str):
        self.editor = editor
        self.position = position
        self.length = length
        self.new_text = new_text
        self.old_text = ""
    
    def execute(self) -> None:
        """Replace old text with new text."""
        end_pos = self.position + self.length
        self.old_text = self.editor._content[self.position:end_pos]
        self.editor._content = (
            self.editor._content[:self.position] + 
            self.new_text + 
            self.editor._content[end_pos:]
        )
    
    def undo(self) -> None:
        """Restore the original text."""
        end_pos = self.position + len(self.new_text)
        self.editor._content = (
            self.editor._content[:self.position] + 
            self.old_text + 
            self.editor._content[end_pos:]
        )


class TextEditor:
    """
    Simple text editor that uses commands for all modifications.
    This keeps the editor logic clean and makes undo/redo super easy.
    """
    
    def __init__(self):
        self._content = ""
        self._history: List[Command] = []  # Commands we've executed
        self._redo_stack: List[Command] = []  # Commands we've undone
    
    def insert(self, position: int, text: str) -> None:
        """Insert text at a position."""
        command = InsertCommand(self, position, text)
        self._execute_command(command)
    
    def delete(self, position: int, length: int) -> None:
        """Delete text from a position."""
        command = DeleteCommand(self, position, length)
        self._execute_command(command)
    
    def replace(self, position: int, length: int, new_text: str) -> None:
        """Replace text at a position."""
        command = ReplaceCommand(self, position, length, new_text)
        self._execute_command(command)
    
    def _execute_command(self, command: Command) -> None:
        """Execute a command and add it to history."""
        command.execute()
        self._history.append(command)
        # Clear redo stack when we do a new action
        self._redo_stack.clear()
    
    def undo(self) -> bool:
        """Undo the last command. Returns True if successful."""
        if not self._history:
            return False
        
        command = self._history.pop()
        command.undo()
        self._redo_stack.append(command)
        return True
    
    def redo(self) -> bool:
        """Redo the last undone command. Returns True if successful."""
        if not self._redo_stack:
            return False
        
        command = self._redo_stack.pop()
        command.execute()
        self._history.append(command)
        return True
    
    def get_content(self) -> str:
        """Get the current editor content."""
        return self._content
    
    def __str__(self) -> str:
        """String representation shows the content."""
        return f'Editor content: "{self._content}"'


if __name__ == "__main__":
    # Demo: simulate editing a document with undo/redo
    print("=== Text Editor with Command Pattern ===\n")
    
    editor = TextEditor()
    
    print("Starting with empty editor")
    print(editor)
    print()
    
    print("Inserting 'Hello World'...")
    editor.insert(0, "Hello World")
    print(editor)
    print()
    
    print("Inserting '!' at the end...")
    editor.insert(11, "!")
    print(editor)
    print()
    
    print("Replacing 'World' with 'Python'...")
    editor.replace(6, 5, "Python")
    print(editor)
    print()
    
    print("Deleting '!' at the end...")
    editor.delete(12, 1)
    print(editor)
    print()
    
    print("Undo last operation (restore '!')...")
    editor.undo()
    print(editor)
    print()
    
    print("Undo again (restore 'World')...")
    editor.undo()
    print(editor)
    print()
    
    print("Redo (back to 'Python')...")
    editor.redo()
    print(editor)
    print()
    
    print("Inserting ' 3.11' at the end...")
    editor.insert(12, " 3.11")
    print(editor)
    print()
    
    print("Final content:", editor.get_content())