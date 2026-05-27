"""
Date: 2026-05-27
Built a task scheduler using the command pattern to handle executable tasks with full undo/redo capability and command macros.
"""

#!/usr/bin/env python3
"""
Task Scheduler using Command Pattern

I wanted to build something that actually demonstrates why the command pattern
is useful beyond textbook examples. This scheduler lets you queue up tasks,
execute them, undo/redo operations, and even create macros (composite commands).

Perfect for scenarios where you need an audit trail or want to replay operations.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any


class Command(ABC):
    """
    Abstract base for all commands. Each command must know how to execute
    and undo itself.
    """
    
    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """Execute the command and return result metadata."""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Reverse the command's effects."""
        pass
    
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what this command does."""
        pass


class WriteFileCommand(Command):
    """
    Simulates writing content to a file. Stores previous content for undo.
    In a real system, this would actually write to disk.
    """
    
    def __init__(self, filename: str, content: str, file_system: Dict[str, str]):
        self.filename = filename
        self.content = content
        self.file_system = file_system  # Shared mutable state (our "filesystem")
        self.previous_content = None
    
    def execute(self) -> Dict[str, Any]:
        self.previous_content = self.file_system.get(self.filename, None)
        self.file_system[self.filename] = self.content
        return {
            "action": "write",
            "filename": self.filename,
            "bytes": len(self.content)
        }
    
    def undo(self) -> None:
        if self.previous_content is None:
            # File didn't exist before, so delete it
            self.file_system.pop(self.filename, None)
        else:
            self.file_system[self.filename] = self.previous_content
    
    def description(self) -> str:
        return f"Write {len(self.content)} bytes to {self.filename}"


class DeleteFileCommand(Command):
    """
    Simulates deleting a file. Keeps backup for undo.
    """
    
    def __init__(self, filename: str, file_system: Dict[str, str]):
        self.filename = filename
        self.file_system = file_system
        self.backup_content = None
    
    def execute(self) -> Dict[str, Any]:
        if self.filename not in self.file_system:
            return {"action": "delete", "status": "file_not_found"}
        
        self.backup_content = self.file_system.pop(self.filename)
        return {"action": "delete", "filename": self.filename}
    
    def undo(self) -> None:
        if self.backup_content is not None:
            self.file_system[self.filename] = self.backup_content
    
    def description(self) -> str:
        return f"Delete {self.filename}"


class MacroCommand(Command):
    """
    Composite command that groups multiple commands together.
    Useful for transactions or batch operations.
    """
    
    def __init__(self, commands: List[Command], name: str = "Macro"):
        self.commands = commands
        self.name = name
        self.executed_commands = []  # Track which ones actually ran
    
    def execute(self) -> Dict[str, Any]:
        results = []
        for cmd in self.commands:
            result = cmd.execute()
            self.executed_commands.append(cmd)
            results.append(result)
        
        return {
            "action": "macro",
            "name": self.name,
            "commands_executed": len(results),
            "results": results
        }
    
    def undo(self) -> None:
        # Undo in reverse order — critical for maintaining consistency
        for cmd in reversed(self.executed_commands):
            cmd.undo()
        self.executed_commands.clear()
    
    def description(self) -> str:
        return f"Macro '{self.name}' with {len(self.commands)} commands"


class TaskScheduler:
    """
    Scheduler that executes commands and maintains history for undo/redo.
    This is the invoker in command pattern terminology.
    """
    
    def __init__(self):
        self.history: List[Command] = []
        self.redo_stack: List[Command] = []
    
    def execute(self, command: Command) -> Dict[str, Any]:
        """
        Execute a command and add it to history.
        Clears redo stack since we're on a new timeline now.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] Executing: {command.description()}")
        
        result = command.execute()
        self.history.append(command)
        self.redo_stack.clear()  # Can't redo after new command
        
        return result
    
    def undo(self) -> bool:
        """Undo the last command."""
        if not self.history:
            print("Nothing to undo!")
            return False
        
        command = self.history.pop()
        print(f"Undoing: {command.description()}")
        command.undo()
        self.redo_stack.append(command)
        return True
    
    def redo(self) -> bool:
        """Redo the last undone command."""
        if not self.redo_stack:
            print("Nothing to redo!")
            return False
        
        command = self.redo_stack.pop()
        print(f"Redoing: {command.description()}")
        command.execute()
        self.history.append(command)
        return True
    
    def show_history(self) -> None:
        """Print command history."""
        print("\n=== Command History ===")
        for i, cmd in enumerate(self.history, 1):
            print(f"{i}. {cmd.description()}")
        print()


if __name__ == "__main__":
    # Simulated filesystem — just a dict for demo purposes
    filesystem = {}
    
    scheduler = TaskScheduler()
    
    print("=== Task Scheduler with Command Pattern ===\n")
    
    # Execute some individual commands
    scheduler.execute(WriteFileCommand("readme.txt", "Hello World", filesystem))
    scheduler.execute(WriteFileCommand("config.json", '{"debug": true}', filesystem))
    
    print(f"\nFilesystem state: {list(filesystem.keys())}")
    
    # Create and execute a macro (batch operation)
    macro = MacroCommand([
        WriteFileCommand("log1.txt", "Log entry 1", filesystem),
        WriteFileCommand("log2.txt", "Log entry 2", filesystem),
        WriteFileCommand("log3.txt", "Log entry 3", filesystem)
    ], name="Create Logs")
    
    scheduler.execute(macro)
    print(f"Filesystem state: {list(filesystem.keys())}")
    
    # Demonstrate undo
    print("\n--- Testing Undo ---")
    scheduler.undo()  # Undo macro (removes all 3 logs)
    print(f"Filesystem state: {list(filesystem.keys())}")
    
    scheduler.undo()  # Undo config.json write
    print(f"Filesystem state: {list(filesystem.keys())}")
    
    # Demonstrate redo
    print("\n--- Testing Redo ---")
    scheduler.redo()  # Redo config.json
    print(f"Filesystem state: {list(filesystem.keys())}")
    
    # Show full history
    scheduler.show_history()
    
    # Test delete command
    scheduler.execute(DeleteFileCommand("readme.txt", filesystem))
    print(f"Filesystem state: {list(filesystem.keys())}")
    
    # Undo the delete
    scheduler.undo()
    print(f"After undoing delete: {list(filesystem.keys())}")
    
    print("\n✓ Command pattern demo complete!")