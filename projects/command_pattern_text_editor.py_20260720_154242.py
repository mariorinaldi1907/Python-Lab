"""
Date: 2026-07-20
Built a text editor simulator using the command pattern to handle undo/redo operations cleanly, because I wanted to understand how editors actually track changes.
"""

"""
Text editor implementation using the Command pattern.
Each action (insert, delete, replace) is encapsulated as a command object
that knows how to execute and undo itself. This makes undo/redo trivial.
"""

from abc import ABC, abstractmethod
from typing import List


class Command(ABC):
    """
    Base command interface. Every concrete command must implement
    execute() and undo() methods.
    """
    
    @abstractmethod
    def execute(self) -> None:
        """Execute the command and modify the document."""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Reverse the command's effect on the document."""
        pass


class Document:
    """
    The receiver in the command pattern. This is what gets modified.
    Keeping it simple with a string buffer.
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
        self.delete(position, length)
        self.insert(position, text)
        return replaced
    
    def __str__(self) -> str:
        return self.content


class InsertCommand(Command):
    """Command to insert text at a specific position."""
    
    def __init__(self, document: Document, position: int, text: str):
        self.document = document
        self.position = position
        self.text = text
    
    def execute(self) -> None:
        self.document.insert(self.position, self.text)
    
    def undo(self) -> None:
        # To undo an insert, we delete what we just inserted
        self.document.delete(self.position, len(self.text))


class DeleteCommand(Command):
    """Command to delete text at a specific position."""
    
    def __init__(self, document: Document, position: int, length: int):
        self.document = document
        self.position = position
        self.length = length
        self.deleted_text = ""  # Store what we deleted for undo
    
    def execute(self) -> None:
        self.deleted_text = self.document.delete(self.position, self.length)
    
    def undo(self) -> None:
        # To undo a delete, we re-insert what was deleted
        self.document.insert(self.position, self.deleted_text)


class ReplaceCommand(Command):
    """Command to replace text at a specific position."""
    
    def __init__(self, document: Document, position: int, length: int, text: str):
        self.document = document
        self.position = position
        self.length = length
        self.text = text
        self.replaced_text = ""  # Store what we replaced for undo
    
    def execute(self) -> None:
        self.replaced_text = self.document.replace(self.position, self.length, self.text)
    
    def undo(self) -> None:
        # To undo a replace, we replace back with the original text
        self.document.replace(self.position, len(self.text), self.replaced_text)


class TextEditor:
    """
    The invoker in the command pattern. Manages command history
    and provides undo/redo functionality.
    """
    
    def __init__(self, document: Document):
        self.document = document
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
    
    def show_document(self) -> str:
        """Return current document content."""
        return str(self.document)


if __name__ == "__main__":
    # Create a document and editor
    doc = Document()
    editor = TextEditor(doc)
    
    print("=== Text Editor with Command Pattern ===\n")
    
    # Type some text
    print("1. Insert 'Hello '")
    editor.execute_command(InsertCommand(doc, 0, "Hello "))
    print(f"   Content: '{editor.show_document()}'\n")
    
    print("2. Insert 'World'")
    editor.execute_command(InsertCommand(doc, 6, "World"))
    print(f"   Content: '{editor.show_document()}'\n")
    
    print("3. Insert '!' at the end")
    editor.execute_command(InsertCommand(doc, 11, "!"))
    print(f"   Content: '{editor.show_document()}'\n")
    
    # Replace some text
    print("4. Replace 'World' with 'Python'")
    editor.execute_command(ReplaceCommand(doc, 6, 5, "Python"))
    print(f"   Content: '{editor.show_document()}'\n")
    
    # Undo operations
    print("5. Undo (reverse replace)")
    editor.undo()
    print(f"   Content: '{editor.show_document()}'\n")
    
    print("6. Undo (remove '!')")
    editor.undo()
    print(f"   Content: '{editor.show_document()}'\n")
    
    # Redo operations
    print("7. Redo (add '!' back)")
    editor.redo()
    print(f"   Content: '{editor.show_document()}'\n")
    
    print("8. Redo (replace with 'Python' again)")
    editor.redo()
    print(f"   Content: '{editor.show_document()}'\n")
    
    # Delete some text
    print("9. Delete 'Python' (6 chars starting at position 6)")
    editor.execute_command(DeleteCommand(doc, 6, 6))
    print(f"   Content: '{editor.show_document()}'\n")
    
    print("10. Undo (restore 'Python')")
    editor.undo()
    print(f"   Content: '{editor.show_document()}'\n")