"""
Date: 2026-06-25
Built an event-driven task scheduler using the observer pattern because I wanted a clean way to handle multiple reactions to task completions without tight coupling.
"""

#!/usr/bin/env python3
"""
Event-driven task scheduler using the Observer pattern.

I built this because I kept writing messy callbacks in my automation scripts.
The observer pattern lets me register multiple handlers that react to task
events without the scheduler knowing anything about what they do.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any


class TaskStatus(Enum):
    """Possible states for a task."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskEvent:
    """
    Represents an event that occurred during task execution.
    
    I wrap events in a class so observers get all the context they need
    without having to pass a million arguments.
    """
    
    def __init__(self, task_id: str, status: TaskStatus, message: str = "", data: Dict[str, Any] = None):
        self.task_id = task_id
        self.status = status
        self.message = message
        self.timestamp = datetime.now()
        self.data = data or {}


class Observer(ABC):
    """
    Base class for all observers.
    
    Concrete observers implement update() to react to task events however they want.
    """
    
    @abstractmethod
    def update(self, event: TaskEvent) -> None:
        """Called when a task event occurs."""
        pass


class LoggingObserver(Observer):
    """Logs all task events to console with timestamps."""
    
    def update(self, event: TaskEvent) -> None:
        timestamp = event.timestamp.strftime("%H:%M:%S")
        print(f"[{timestamp}] LOG: Task '{event.task_id}' -> {event.status.value}")
        if event.message:
            print(f"         └─ {event.message}")


class MetricsObserver(Observer):
    """
    Tracks task metrics like success rate and execution count.
    
    In a real app, this would push to Prometheus or whatever, but for now
    it just keeps counts in memory.
    """
    
    def __init__(self):
        self.completed = 0
        self.failed = 0
        self.total_started = 0
    
    def update(self, event: TaskEvent) -> None:
        if event.status == TaskStatus.RUNNING:
            self.total_started += 1
        elif event.status == TaskStatus.COMPLETED:
            self.completed += 1
        elif event.status == TaskStatus.FAILED:
            self.failed += 1
    
    def print_summary(self) -> None:
        """Print a summary of tracked metrics."""
        success_rate = (self.completed / self.total_started * 100) if self.total_started > 0 else 0
        print(f"\n{'='*50}")
        print(f"METRICS SUMMARY")
        print(f"  Total started: {self.total_started}")
        print(f"  Completed: {self.completed}")
        print(f"  Failed: {self.failed}")
        print(f"  Success rate: {success_rate:.1f}%")
        print(f"{'='*50}")


class AlertObserver(Observer):
    """
    Sends alerts when tasks fail.
    
    In production I'd hook this up to Slack or PagerDuty, but here it just
    prints loud messages so I notice failures immediately.
    """
    
    def update(self, event: TaskEvent) -> None:
        if event.status == TaskStatus.FAILED:
            print(f"\n🚨 ALERT: Task '{event.task_id}' FAILED!")
            print(f"    Reason: {event.message}")
            print(f"    Time: {event.timestamp}\n")


class TaskScheduler:
    """
    The subject in the observer pattern.
    
    Tasks register here, and when they change state, all registered observers
    get notified. The scheduler doesn't care what observers do with events.
    """
    
    def __init__(self):
        self._observers: List[Observer] = []
    
    def attach(self, observer: Observer) -> None:
        """Register an observer to receive task events."""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        """Unregister an observer."""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def _notify(self, event: TaskEvent) -> None:
        """Send an event to all registered observers."""
        for observer in self._observers:
            observer.update(event)
    
    def run_task(self, task_id: str, should_fail: bool = False) -> None:
        """
        Simulate running a task.
        
        In a real scheduler, this would execute actual work. Here I just
        simulate success or failure to demonstrate the observer notifications.
        """
        # Task starts
        self._notify(TaskEvent(task_id, TaskStatus.RUNNING, "Task started"))
        
        # Simulate some work happening
        # In reality, this is where you'd call actual task logic
        
        if should_fail:
            # Task failed
            self._notify(TaskEvent(
                task_id, 
                TaskStatus.FAILED, 
                "Simulated failure for demo purposes"
            ))
        else:
            # Task succeeded
            self._notify(TaskEvent(
                task_id, 
                TaskStatus.COMPLETED, 
                "Task finished successfully",
                data={"result": "some output data"}
            ))


if __name__ == "__main__":
    print("Event-Driven Task Scheduler Demo")
    print("=" * 50)
    
    # Create the scheduler (subject)
    scheduler = TaskScheduler()
    
    # Create observers
    logger = LoggingObserver()
    metrics = MetricsObserver()
    alerts = AlertObserver()
    
    # Attach observers to scheduler
    # The cool thing here is I can add/remove observers at runtime
    # without touching the scheduler code at all
    scheduler.attach(logger)
    scheduler.attach(metrics)
    scheduler.attach(alerts)
    
    # Run some tasks
    print("\nRunning tasks...\n")
    scheduler.run_task("data_backup")
    scheduler.run_task("send_emails")
    scheduler.run_task("database_cleanup", should_fail=True)  # This one fails
    scheduler.run_task("generate_reports")
    scheduler.run_task("sync_files", should_fail=True)  # This one fails too
    
    # Print metrics summary
    metrics.print_summary()
    
    print("\nDemo complete! Each observer reacted independently to task events.")