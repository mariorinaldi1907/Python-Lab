"""
Date: 2026-06-02
Built a text editor using the command pattern to handle operations like insert, delete, and replace with full undo/redo functionality — helps me understand reversible actions better.
"""

"""
Simple text editor using the Command pattern.
Supports insert, delete, and replace operations with undo/redo.
"""

from abc import ABC, abstractmethod
from typing import List


class Command(ABC):
    """
    Abstract base class for all commands.
    Each command must implement execute and undo methods.
    """
    
    @abstractmethod
    def execute(self) -> None:
        """Execute the command and modify the editor state."""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Reverse the command and restore previous state."""
        pass


class TextEditor:
    """
    Simple text editor that maintains content as a string.
    The actual operations are delegated to command objects.
    """
    
    def __init__(self):
        self.content = ""
    
    def get_content(self) -> str:
        """Return the current text content."""
        return self.content
    
    def set_content(self, content: str) -> None:
        """Set the text content directly."""
        self.content = content


class InsertCommand(Command):
    """
    Command to insert text at a specific position.
    Stores the position and text for undo capability.
    """
    
    def __init__(self, editor: TextEditor, position: int, text: str):
        self.editor = editor
        self.position = position
        self.text = text
    
    def execute(self) -> None:
        """Insert text at the specified position."""
        current = self.editor.get_content()
        new_content = current[:self.position] + self.text + current[self.position:]
        self.editor.set_content(new_content)
    
    def undo(self) -> None:
        """Remove the inserted text to restore previous state."""
        current = self.editor.get_content()
        new_content = current[:self.position] + current[self.position + len(self.text):]
        self.editor.set_content(new_content)


class DeleteCommand(Command):
    """
    Command to delete text from start to end position.
    Remembers deleted text so it can be restored on undo.
    """
    
    def __init__(self, editor: TextEditor, start: int, end: int):
        self.editor = editor
        self.start = start
        self.end = end
        self.deleted_text = ""  # Will be set during execute
    
    def execute(self) -> None:
        """Delete text between start and end positions."""
        current = self.editor.get_content()
        self.deleted_text = current[self.start:self.end]
        new_content = current[:self.start] + current[self.end:]
        self.editor.set_content(new_content)
    
    def undo(self) -> None:
        """Restore the deleted text."""
        current = self.editor.get_content()
        new_content = current[:self.start] + self.deleted_text + current[self.start:]
        self.editor.set_content(new_content)


class ReplaceCommand(Command):
    """
    Command to replace text in a range with new text.
    Internally uses delete and insert, but acts as a single atomic operation.
    """
    
    def __init__(self, editor: TextEditor, start: int, end: int, new_text: str):
        self.editor = editor
        self.start = start
        self.end = end
        self.new_text = new_text
        self.old_text = ""
    
    def execute(self) -> None:
        """Replace text in the specified range."""
        current = self.editor.get_content()
        self.old_text = current[self.start:self.end]
        new_content = current[:self.start] + self.new_text + current[self.end:]
        self.editor.set_content(new_content)
    
    def undo(self) -> None:
        """Restore the original text."""
        current = self.editor.get_content()
        new_content = current[:self.start] + self.old_text + current[self.start + len(self.new_text):]
        self.editor.set_content(new_content)


class EditorInvoker:
    """
    Invoker that manages command execution and maintains undo/redo history.
    This is the brain of the command pattern — it tracks what happened.
    """
    
    def __init__(self, editor: TextEditor):
        self.editor = editor
        self.history: List[Command] = []
        self.redo_stack: List[Command] = []
    
    def execute_command(self, command: Command) -> None:
        """Execute a command and add it to history."""
        command.execute()
        self.history.append(command)
        # When we execute a new command, we lose the redo history
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
    # Create the editor and invoker
    editor = TextEditor()
    invoker = EditorInvoker(editor)
    
    print("=== Text Editor with Command Pattern ===\n")
    
    # Start with some initial text
    print("1. Inserting 'Hello World'")
    invoker.execute_command(InsertCommand(editor, 0, "Hello World"))
    print(f"   Content: '{editor.get_content()}'\n")
    
    # Insert more text
    print("2. Inserting ' from Python' at the end")
    invoker.execute_command(InsertCommand(editor, len(editor.get_content()), " from Python"))
    print(f"   Content: '{editor.get_content()}'\n")
    
    # Delete some text
    print("3. Deleting ' from Python' (characters 11-23)")
    invoker.execute_command(DeleteCommand(editor, 11, 23))
    print(f"   Content: '{editor.get_content()}'\n")
    
    # Replace text
    print("4. Replacing 'World' with 'Universe' (characters 6-11)")
    invoker.execute_command(ReplaceCommand(editor, 6, 11, "Universe"))
    print(f"   Content: '{editor.get_content()}'\n")
    
    # Undo operations
    print("5. Undoing last operation")
    invoker.undo()
    print(f"   Content: '{editor.get_content()}'\n")
    
    print("6. Undoing again")
    invoker.undo()
    print(f"   Content: '{editor.get_content()}'\n")
    
    # Redo operations
    print("7. Redoing last undo")
    invoker.redo()
    print(f"   Content: '{editor.get_content()}'\n")
    
    print("8. Redoing again")
    invoker.redo()
    print(f"   Content: '{editor.get_content()}'\n")
    
    # Show that new commands clear redo stack
    print("9. Inserting '!' at the end")
    invoker.execute_command(InsertCommand(editor, len(editor.get_content()), "!"))
    print(f"   Content: '{editor.get_content()}'")
    print("   (Note: redo stack is now cleared)")