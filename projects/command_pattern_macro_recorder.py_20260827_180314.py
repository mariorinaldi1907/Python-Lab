"""
Date: 2026-08-27
Built a command pattern implementation that records user actions as reversible commands — useful for building undo/redo functionality in apps.
"""

"""
Macro recorder using the Command pattern.
Records user actions (text edits, cursor moves) and lets you undo/redo them.
Also supports saving/loading macro sequences to replay later.
"""

from abc import ABC, abstractmethod
from typing import List
import json


class Command(ABC):
    """
    Abstract base for all commands.
    Each command knows how to execute and undo itself.
    """
    
    @abstractmethod
    def execute(self) -> None:
        """Execute the command's action."""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Reverse the command's action."""
        pass
    
    @abstractmethod
    def to_dict(self) -> dict:
        """Serialize command to dict for saving."""
        pass


class TextDocument:
    """
    Simple text document that commands operate on.
    In a real app, this would be your actual document/model.
    """
    
    def __init__(self):
        self.content = ""
        self.cursor_position = 0
    
    def insert_text(self, text: str, position: int) -> None:
        """Insert text at a specific position."""
        self.content = self.content[:position] + text + self.content[position:]
        self.cursor_position = position + len(text)
    
    def delete_text(self, start: int, length: int) -> str:
        """Delete text and return what was deleted (for undo)."""
        deleted = self.content[start:start + length]
        self.content = self.content[:start] + self.content[start + length:]
        self.cursor_position = start
        return deleted
    
    def __str__(self) -> str:
        """Show document content with cursor position marked."""
        if not self.content:
            return "[empty] cursor at 0"
        return f"{self.content[:self.cursor_position]}|{self.content[self.cursor_position:]}"


class InsertTextCommand(Command):
    """Command to insert text into the document."""
    
    def __init__(self, document: TextDocument, text: str, position: int):
        self.document = document
        self.text = text
        self.position = position
    
    def execute(self) -> None:
        self.document.insert_text(self.text, self.position)
    
    def undo(self) -> None:
        # Remove what we just inserted
        self.document.delete_text(self.position, len(self.text))
    
    def to_dict(self) -> dict:
        return {
            "type": "insert",
            "text": self.text,
            "position": self.position
        }


class DeleteTextCommand(Command):
    """Command to delete text from the document."""
    
    def __init__(self, document: TextDocument, start: int, length: int):
        self.document = document
        self.start = start
        self.length = length
        self.deleted_text = ""  # Store what was deleted for undo
    
    def execute(self) -> None:
        self.deleted_text = self.document.delete_text(self.start, self.length)
    
    def undo(self) -> None:
        # Put back what we deleted
        self.document.insert_text(self.deleted_text, self.start)
    
    def to_dict(self) -> dict:
        return {
            "type": "delete",
            "start": self.start,
            "length": self.length
        }


class MacroRecorder:
    """
    Manages command history and provides undo/redo functionality.
    This is the invoker in the Command pattern.
    """
    
    def __init__(self, document: TextDocument):
        self.document = document
        self.history: List[Command] = []
        self.current_index = -1  # Points to the last executed command
    
    def execute_command(self, command: Command) -> None:
        """Execute a command and add it to history."""
        command.execute()
        # Discard any "future" commands if we're in the middle of history
        self.history = self.history[:self.current_index + 1]
        self.history.append(command)
        self.current_index += 1
    
    def undo(self) -> bool:
        """Undo the last command. Returns True if successful."""
        if self.current_index < 0:
            return False
        
        self.history[self.current_index].undo()
        self.current_index -= 1
        return True
    
    def redo(self) -> bool:
        """Redo a previously undone command. Returns True if successful."""
        if self.current_index >= len(self.history) - 1:
            return False
        
        self.current_index += 1
        self.history[self.current_index].execute()
        return True
    
    def save_macro(self, filename: str) -> None:
        """Save the current command history to a file."""
        macro_data = [cmd.to_dict() for cmd in self.history]
        with open(filename, 'w') as f:
            json.dump(macro_data, f, indent=2)
    
    def replay_macro(self, filename: str) -> None:
        """Load and replay commands from a saved macro file."""
        with open(filename, 'r') as f:
            macro_data = json.load(f)
        
        for cmd_dict in macro_data:
            if cmd_dict["type"] == "insert":
                cmd = InsertTextCommand(
                    self.document,
                    cmd_dict["text"],
                    cmd_dict["position"]
                )
            elif cmd_dict["type"] == "delete":
                cmd = DeleteTextCommand(
                    self.document,
                    cmd_dict["start"],
                    cmd_dict["length"]
                )
            else:
                continue
            
            self.execute_command(cmd)


if __name__ == "__main__":
    # Create a document and recorder
    doc = TextDocument()
    recorder = MacroRecorder(doc)
    
    print("=== Command Pattern Macro Recorder Demo ===\n")
    
    # Execute some commands
    print("1. Inserting 'Hello'...")
    recorder.execute_command(InsertTextCommand(doc, "Hello", 0))
    print(f"   Document: {doc}\n")
    
    print("2. Inserting ' World'...")
    recorder.execute_command(InsertTextCommand(doc, " World", 5))
    print(f"   Document: {doc}\n")
    
    print("3. Inserting '!' at the end...")
    recorder.execute_command(InsertTextCommand(doc, "!", 11))
    print(f"   Document: {doc}\n")
    
    # Undo a couple times
    print("4. Undo...")
    recorder.undo()
    print(f"   Document: {doc}\n")
    
    print("5. Undo again...")
    recorder.undo()
    print(f"   Document: {doc}\n")
    
    # Redo
    print("6. Redo...")
    recorder.redo()
    print(f"   Document: {doc}\n")
    
    # Delete some text
    print("7. Deleting 6 characters starting at position 5...")
    recorder.execute_command(DeleteTextCommand(doc, 5, 6))
    print(f"   Document: {doc}\n")
    
    print("8. Undo the deletion...")
    recorder.undo()
    print(f"   Document: {doc}\n")
    
    # Save the macro
    print("9. Saving macro to 'test_macro.json'...")
    recorder.save_macro("test_macro.json")
    print("   Macro saved!\n")
    
    # Reset document and replay
    print("10. Resetting document and replaying macro...")
    doc.content = ""
    doc.cursor_position = 0
    recorder = MacroRecorder(doc)
    recorder.replay_macro("test_macro.json")
    print(f"    Final document: {doc}")