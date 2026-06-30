"""
Date: 2026-06-30
Built an event-driven task scheduler using the observer pattern so I can monitor long-running tasks with different types of listeners without coupling everything together.
"""

#!/usr/bin/env python3
"""
Task scheduler with observer pattern implementation.
Useful for running background jobs and tracking their progress through multiple channels
(logging, notifications, analytics) without the scheduler caring about those details.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any
import time


class TaskStatus(Enum):
    """Enum representing the lifecycle states of a task."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskEvent:
    """
    Represents an event that occurred during task execution.
    Carries all the context observers might need.
    """
    
    def __init__(self, task_id: str, status: TaskStatus, message: str, metadata: Dict[str, Any] = None):
        self.task_id = task_id
        self.status = status
        self.message = message
        self.timestamp = datetime.now()
        self.metadata = metadata or {}


class Observer(ABC):
    """
    Abstract base class for observers.
    Any class wanting to listen to task events should inherit from this.
    """
    
    @abstractmethod
    def update(self, event: TaskEvent) -> None:
        """Called when a task event occurs."""
        pass


class ConsoleLogger(Observer):
    """Prints task events to console with timestamps."""
    
    def update(self, event: TaskEvent) -> None:
        timestamp = event.timestamp.strftime("%H:%M:%S")
        print(f"[{timestamp}] [{event.status.value.upper()}] Task {event.task_id}: {event.message}")


class StatisticsTracker(Observer):
    """
    Tracks task statistics across all executions.
    Useful for monitoring system health and performance.
    """
    
    def __init__(self):
        self.stats = {
            "total_tasks": 0,
            "completed": 0,
            "failed": 0,
            "total_runtime": 0.0
        }
        self._start_times = {}  # Track when tasks start
    
    def update(self, event: TaskEvent) -> None:
        if event.status == TaskStatus.PENDING:
            self.stats["total_tasks"] += 1
        elif event.status == TaskStatus.RUNNING:
            self._start_times[event.task_id] = event.timestamp
        elif event.status == TaskStatus.COMPLETED:
            self.stats["completed"] += 1
            if event.task_id in self._start_times:
                runtime = (event.timestamp - self._start_times[event.task_id]).total_seconds()
                self.stats["total_runtime"] += runtime
        elif event.status == TaskStatus.FAILED:
            self.stats["failed"] += 1
    
    def get_summary(self) -> str:
        """Returns a formatted summary of all tracked statistics."""
        avg_runtime = (self.stats["total_runtime"] / self.stats["completed"] 
                      if self.stats["completed"] > 0 else 0)
        return (f"\n--- Statistics Summary ---\n"
                f"Total tasks: {self.stats['total_tasks']}\n"
                f"Completed: {self.stats['completed']}\n"
                f"Failed: {self.stats['failed']}\n"
                f"Average runtime: {avg_runtime:.2f}s")


class AlertSystem(Observer):
    """
    Monitors for failures and sends alerts.
    In a real system, this would integrate with email/Slack/PagerDuty.
    """
    
    def __init__(self):
        self.failure_count = 0
    
    def update(self, event: TaskEvent) -> None:
        if event.status == TaskStatus.FAILED:
            self.failure_count += 1
            print(f"\n🚨 ALERT: Task {event.task_id} failed! ({event.message})")
            print(f"   Total failures today: {self.failure_count}\n")


class TaskScheduler:
    """
    The subject in the observer pattern.
    Manages tasks and notifies all registered observers about state changes.
    """
    
    def __init__(self):
        self._observers: List[Observer] = []
    
    def attach(self, observer: Observer) -> None:
        """Register an observer to receive task events."""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        """Unregister an observer."""
        self._observers.remove(observer)
    
    def notify(self, event: TaskEvent) -> None:
        """Send an event to all registered observers."""
        for observer in self._observers:
            observer.update(event)
    
    def execute_task(self, task_id: str, task_func, should_fail: bool = False) -> None:
        """
        Execute a task and emit events at each stage.
        The should_fail parameter is for demo purposes to show failure handling.
        """
        self.notify(TaskEvent(task_id, TaskStatus.PENDING, "Task queued"))
        
        time.sleep(0.1)  # Simulate queue time
        
        self.notify(TaskEvent(task_id, TaskStatus.RUNNING, "Task started"))
        
        try:
            if should_fail:
                raise Exception("Simulated task failure")
            
            result = task_func()
            time.sleep(0.2)  # Simulate work
            
            self.notify(TaskEvent(
                task_id, 
                TaskStatus.COMPLETED, 
                f"Task finished successfully",
                metadata={"result": result}
            ))
        except Exception as e:
            self.notify(TaskEvent(
                task_id,
                TaskStatus.FAILED,
                str(e),
                metadata={"error_type": type(e).__name__}
            ))


def sample_data_processing_task():
    """Simulates a data processing workload."""
    return {"processed_records": 1000, "errors": 0}


def sample_backup_task():
    """Simulates a backup operation."""
    return {"backup_size_mb": 250, "duration_sec": 45}


if __name__ == "__main__":
    print("=== Task Scheduler with Observer Pattern Demo ===\n")
    
    # Create the scheduler (subject)
    scheduler = TaskScheduler()
    
    # Create and attach observers
    console = ConsoleLogger()
    stats = StatisticsTracker()
    alerts = AlertSystem()
    
    scheduler.attach(console)
    scheduler.attach(stats)
    scheduler.attach(alerts)
    
    # Run some tasks
    print("Running data processing task...")
    scheduler.execute_task("task_001", sample_data_processing_task)
    
    print("\nRunning backup task...")
    scheduler.execute_task("task_002", sample_backup_task)
    
    print("\nSimulating a failing task...")
    scheduler.execute_task("task_003", lambda: None, should_fail=True)
    
    print("\nRunning one more successful task...")
    scheduler.execute_task("task_004", sample_data_processing_task)
    
    # Print statistics summary
    print(stats.get_summary())
    
    print("\n✅ Demo complete! The observer pattern lets me add new monitoring")
    print("   capabilities without modifying the scheduler core logic.")