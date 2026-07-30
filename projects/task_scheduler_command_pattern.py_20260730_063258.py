"""
Date: 2026-07-30
Built a task scheduler using the command pattern so I can queue up file operations and system tasks with full undo/redo support — super useful for my backup scripts.
"""

#!/usr/bin/env python3
"""
Task scheduler implementing the Command pattern.
Lets me queue up operations, execute them in order, and undo/redo as needed.
"""

import os
import shutil
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path


class Command(ABC):
    """
    Base command interface. Every concrete command needs to implement
    execute() and undo() so we can roll back if something goes wrong.
    """
    
    @abstractmethod
    def execute(self):
        """Run the command and return success status."""
        pass
    
    @abstractmethod
    def undo(self):
        """Reverse the command's effects."""
        pass
    
    @abstractmethod
    def description(self):
        """Return a human-readable description of what this command does."""
        pass


class CreateFileCommand(Command):
    """
    Creates a file with optional content.
    Undo removes the file if it was created successfully.
    """
    
    def __init__(self, filepath, content=""):
        self.filepath = Path(filepath)
        self.content = content
        self.was_created = False
    
    def execute(self):
        try:
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            self.filepath.write_text(self.content)
            self.was_created = True
            return True
        except Exception as e:
            print(f"Failed to create {self.filepath}: {e}")
            return False
    
    def undo(self):
        if self.was_created and self.filepath.exists():
            self.filepath.unlink()
            print(f"Removed {self.filepath}")
    
    def description(self):
        return f"Create file: {self.filepath}"


class DeleteFileCommand(Command):
    """
    Deletes a file, but keeps a backup so we can restore it on undo.
    """
    
    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.backup_content = None
        self.was_deleted = False
    
    def execute(self):
        try:
            if self.filepath.exists():
                # Back up the content before deleting
                self.backup_content = self.filepath.read_text()
                self.filepath.unlink()
                self.was_deleted = True
            return True
        except Exception as e:
            print(f"Failed to delete {self.filepath}: {e}")
            return False
    
    def undo(self):
        if self.was_deleted and self.backup_content is not None:
            self.filepath.write_text(self.backup_content)
            print(f"Restored {self.filepath}")
    
    def description(self):
        return f"Delete file: {self.filepath}"


class LogMessageCommand(Command):
    """
    Simple logging command that appends to a log file.
    Undo removes the last line we added (hacky but works for demo purposes).
    """
    
    def __init__(self, logfile, message):
        self.logfile = Path(logfile)
        self.message = message
        self.logged = False
    
    def execute(self):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] {self.message}\n"
            with open(self.logfile, 'a') as f:
                f.write(log_entry)
            self.logged = True
            return True
        except Exception as e:
            print(f"Failed to log message: {e}")
            return False
    
    def undo(self):
        # This is a simplified undo - just removes the last line
        # In production I'd use a better approach with line tracking
        if self.logged and self.logfile.exists():
            lines = self.logfile.read_text().splitlines()
            if lines:
                self.logfile.write_text('\n'.join(lines[:-1]) + '\n' if lines[:-1] else '')
                print(f"Removed log entry from {self.logfile}")
    
    def description(self):
        return f"Log message: {self.message}"


class TaskScheduler:
    """
    The invoker in command pattern terms. Manages a queue of commands
    and keeps history so we can undo/redo operations.
    """
    
    def __init__(self):
        self.history = []
        self.redo_stack = []
    
    def add_task(self, command):
        """Add a command to execute later."""
        self.history.append(command)
    
    def execute_all(self):
        """
        Run all queued commands in order. If one fails, we stop there
        to avoid cascading failures.
        """
        print("\n=== Executing tasks ===")
        for cmd in self.history:
            print(f"Running: {cmd.description()}")
            if not cmd.execute():
                print("Execution stopped due to error")
                return False
        print("All tasks completed successfully")
        return True
    
    def undo_last(self):
        """Undo the most recent command and add it to redo stack."""
        if not self.history:
            print("Nothing to undo")
            return
        
        cmd = self.history.pop()
        print(f"\nUndoing: {cmd.description()}")
        cmd.undo()
        self.redo_stack.append(cmd)
    
    def redo_last(self):
        """Re-execute the most recently undone command."""
        if not self.redo_stack:
            print("Nothing to redo")
            return
        
        cmd = self.redo_stack.pop()
        print(f"\nRedoing: {cmd.description()}")
        cmd.execute()
        self.history.append(cmd)


if __name__ == "__main__":
    # Demo: set up a task scheduler for organizing some temp files
    scheduler = TaskScheduler()
    
    # Create a temp directory for testing
    test_dir = Path("temp_scheduler_test")
    test_dir.mkdir(exist_ok=True)
    
    # Queue up some tasks
    scheduler.add_task(CreateFileCommand(test_dir / "config.txt", "debug=true\nport=8080\n"))
    scheduler.add_task(CreateFileCommand(test_dir / "data.txt", "sample data here"))
    scheduler.add_task(LogMessageCommand(test_dir / "activity.log", "System initialized"))
    scheduler.add_task(LogMessageCommand(test_dir / "activity.log", "Files created successfully"))
    
    # Execute everything
    scheduler.execute_all()
    
    # Demonstrate undo
    print("\n--- Testing undo ---")
    scheduler.undo_last()  # Undo the last log entry
    scheduler.undo_last()  # Undo the first log entry
    
    # Demonstrate redo
    print("\n--- Testing redo ---")
    scheduler.redo_last()  # Redo first log entry
    
    # Clean up the test directory
    print("\n--- Cleanup ---")
    cleanup = DeleteFileCommand(test_dir / "config.txt")
    cleanup.execute()
    
    shutil.rmtree(test_dir)
    print(f"\nRemoved test directory: {test_dir}")