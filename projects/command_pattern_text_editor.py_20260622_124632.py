"""
Date: 2026-06-22
Built a text editor simulator using the command pattern because I wanted to understand how undo/redo stacks actually work under the hood.
"""

"""
Simple text editor using the Command pattern.

I always wondered how text editors handle undo/redo so elegantly, so I built
this to explore the command pattern. Each operation (insert, delete, replace)
is a command object that knows how to execute and undo itself.
"""

from abc import ABC, abstractmethod
from typing import List


class Command(ABC):
    """
    Abstract base class for all editor commands.
    
    Each command must know how to execute itself and how to undo that execution.
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
    
    Stores the position and text so it can be removed during undo.
    """
    
    def __init__(self, editor: 'TextEditor', position: int, text: str):
        self.editor = editor
        self.position = position
        self.text = text
    
    def execute(self) -> None:
        """Insert text into the editor's content."""
        content = self.editor.content
        self.editor.content = content[:self.position] + self.text + content[self.position:]
    
    def undo(self) -> None:
        """Remove the inserted text."""
        content = self.editor.content
        self.editor.content = content[:self.position] + content[self.position + len(self.text):]


class DeleteCommand(Command):
    """
    Command to delete text from a specific position.
    
    We need to remember what was deleted so we can restore it on undo.
    """
    
    def __init__(self, editor: 'TextEditor', position: int, length: int):
        self.editor = editor
        self.position = position
        self.length = length
        self.deleted_text = ""  # Will be populated during execute
    
    def execute(self) -> None:
        """Delete text and remember what was deleted."""
        content = self.editor.content
        self.deleted_text = content[self.position:self.position + self.length]
        self.editor.content = content[:self.position] + content[self.position + self.length:]
    
    def undo(self) -> None:
        """Restore the deleted text."""
        content = self.editor.content
        self.editor.content = content[:self.position] + self.deleted_text + content[self.position:]


class ReplaceCommand(Command):
    """
    Command to replace text in a range with new text.
    
    This is essentially a delete + insert, but treating it as one atomic
    operation makes undo/redo cleaner.
    """
    
    def __init__(self, editor: 'TextEditor', position: int, length: int, new_text: str):
        self.editor = editor
        self.position = position
        self.length = length
        self.new_text = new_text
        self.old_text = ""  # Will store what we replaced
    
    def execute(self) -> None:
        """Replace text and remember the original."""
        content = self.editor.content
        self.old_text = content[self.position:self.position + self.length]
        self.editor.content = content[:self.position] + self.new_text + content[self.position + self.length:]
    
    def undo(self) -> None:
        """Restore the original text."""
        content = self.editor.content
        self.editor.content = content[:self.position] + self.old_text + content[self.position + len(self.new_text):]


class TextEditor:
    """
    A simple text editor that supports undo/redo via the command pattern.
    
    Uses two stacks: one for undo history and one for redo. When you execute
    a new command, the redo stack gets cleared (standard editor behavior).
    """
    
    def __init__(self):
        self.content = ""
        self.undo_stack: List[Command] = []
        self.redo_stack: List[Command] = []
    
    def execute_command(self, command: Command) -> None:
        """
        Execute a command and add it to the undo stack.
        
        Any new command clears the redo stack — you can't redo after
        making a new change.
        """
        command.execute()
        self.undo_stack.append(command)
        self.redo_stack.clear()  # New action invalidates redo history
    
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
    
    def get_content(self) -> str:
        """Return the current editor content."""
        return self.content


if __name__ == "__main__":
    # Create a new editor instance
    editor = TextEditor()
    
    print("=== Text Editor Command Pattern Demo ===\n")
    
    # Start with inserting some text
    print("1. Inserting 'Hello' at position 0")
    editor.execute_command(InsertCommand(editor, 0, "Hello"))
    print(f"   Content: '{editor.get_content()}'")
    
    # Insert more text
    print("\n2. Inserting ' World' at position 5")
    editor.execute_command(InsertCommand(editor, 5, " World"))
    print(f"   Content: '{editor.get_content()}'")
    
    # Delete some text
    print("\n3. Deleting 6 characters from position 5")
    editor.execute_command(DeleteCommand(editor, 5, 6))
    print(f"   Content: '{editor.get_content()}'")
    
    # Replace text
    print("\n4. Replacing 'Hello' with 'Hey there'")
    editor.execute_command(ReplaceCommand(editor, 0, 5, "Hey there"))
    print(f"   Content: '{editor.get_content()}'")
    
    # Undo operations
    print("\n5. Undoing last operation")
    editor.undo()
    print(f"   Content: '{editor.get_content()}'")
    
    print("\n6. Undoing again")
    editor.undo()
    print(f"   Content: '{editor.get_content()}'")
    
    # Redo operations
    print("\n7. Redoing last undo")
    editor.redo()
    print(f"   Content: '{editor.get_content()}'")
    
    # New command clears redo stack
    print("\n8. Inserting '!!!' at the end (this will clear redo stack)")
    editor.execute_command(InsertCommand(editor, len(editor.get_content()), "!!!"))
    print(f"   Content: '{editor.get_content()}'")
    
    print("\n9. Trying to redo (should fail - redo stack was cleared)")
    if not editor.redo():
        print("   Nothing to redo!")
    
    print("\n10. But we can still undo the '!!!' we just added")
    editor.undo()
    print(f"   Content: '{editor.get_content()}'")