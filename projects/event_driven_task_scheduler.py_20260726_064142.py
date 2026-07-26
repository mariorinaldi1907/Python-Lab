"""
Date: 2026-07-26
Built an event-driven task scheduler using the observer pattern so different parts of my scripts can react to events without tight coupling.
"""

#!/usr/bin/env python3
"""
Event-driven task scheduler using the Observer pattern.

I wanted a way to trigger different actions when certain events happen
in my scripts (like file changes, API responses, etc.) without hardcoding
all the dependencies. This pattern makes it super flexible to add new
subscribers without touching existing code.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List
import time


class Event:
    """
    Represents an event that occurred in the system.
    Stores metadata about what happened and when.
    """
    
    def __init__(self, event_type: str, data: Dict[str, Any]):
        self.event_type = event_type
        self.data = data
        self.timestamp = datetime.now()
    
    def __repr__(self):
        return f"Event(type={self.event_type}, data={self.data}, time={self.timestamp.strftime('%H:%M:%S')})"


class Observer(ABC):
    """
    Abstract base class for all observers.
    Any class that wants to listen to events must implement handle_event.
    """
    
    @abstractmethod
    def handle_event(self, event: Event) -> None:
        """Process the event - each observer decides what to do with it."""
        pass


class Subject:
    """
    The main event dispatcher - maintains a list of observers and notifies them.
    This is the core of the observer pattern implementation.
    """
    
    def __init__(self):
        # Using a dict to allow filtering by event type if needed later
        self._observers: List[Observer] = []
    
    def attach(self, observer: Observer) -> None:
        """Register a new observer to receive event notifications."""
        if observer not in self._observers:
            self._observers.append(observer)
            print(f"[EventDispatcher] Attached {observer.__class__.__name__}")
    
    def detach(self, observer: Observer) -> None:
        """Unregister an observer - they won't get future notifications."""
        if observer in self._observers:
            self._observers.remove(observer)
            print(f"[EventDispatcher] Detached {observer.__class__.__name__}")
    
    def notify(self, event: Event) -> None:
        """
        Send the event to all registered observers.
        In production, I'd probably add error handling so one bad observer
        doesn't crash the whole notification chain.
        """
        print(f"\n[EventDispatcher] Broadcasting: {event}")
        for observer in self._observers:
            observer.handle_event(event)


class LoggerObserver(Observer):
    """
    Simple logging observer - writes events to console.
    In real usage, this would write to a file or external logging service.
    """
    
    def handle_event(self, event: Event) -> None:
        log_message = f"[LOG {event.timestamp.strftime('%H:%M:%S')}] {event.event_type}: {event.data}"
        print(f"  → {log_message}")


class EmailNotifierObserver(Observer):
    """
    Simulates sending email notifications for critical events.
    Only reacts to events marked as 'critical' priority.
    """
    
    def __init__(self, email_address: str):
        self.email_address = email_address
    
    def handle_event(self, event: Event) -> None:
        # Only send emails for critical events - don't spam myself
        if event.data.get('priority') == 'critical':
            print(f"  → [EMAIL to {self.email_address}] ALERT: {event.event_type}")
            print(f"     Details: {event.data.get('message', 'No details provided')}")


class TaskExecutorObserver(Observer):
    """
    Automatically runs tasks when specific events occur.
    This is useful for chaining actions - like 'when file uploads, run processing'.
    """
    
    def __init__(self):
        # Map event types to callable tasks
        self.task_handlers = {
            'file_uploaded': self._process_file,
            'api_response': self._handle_api_data,
            'user_action': self._log_analytics
        }
    
    def handle_event(self, event: Event) -> None:
        handler = self.task_handlers.get(event.event_type)
        if handler:
            handler(event.data)
    
    def _process_file(self, data: Dict[str, Any]) -> None:
        filename = data.get('filename', 'unknown')
        print(f"  → [TASK] Processing uploaded file: {filename}")
        print(f"     Simulating work...")
    
    def _handle_api_data(self, data: Dict[str, Any]) -> None:
        status = data.get('status', 'unknown')
        print(f"  → [TASK] Handling API response with status: {status}")
    
    def _log_analytics(self, data: Dict[str, Any]) -> None:
        action = data.get('action', 'unknown')
        print(f"  → [TASK] Logging user action to analytics: {action}")


class EventScheduler:
    """
    Main scheduler that ties everything together.
    In my actual scripts, this would integrate with file watchers,
    API polling, or other event sources.
    """
    
    def __init__(self):
        self.dispatcher = Subject()
    
    def register_observer(self, observer: Observer) -> None:
        """Convenience method to attach observers."""
        self.dispatcher.attach(observer)
    
    def trigger_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Create and dispatch a new event."""
        event = Event(event_type, data)
        self.dispatcher.notify(event)


if __name__ == "__main__":
    print("=== Event-Driven Task Scheduler Demo ===\n")
    
    # Set up the scheduler and observers
    scheduler = EventScheduler()
    
    logger = LoggerObserver()
    email_notifier = EmailNotifierObserver("mario@example.com")
    task_executor = TaskExecutorObserver()
    
    # Register all observers
    scheduler.register_observer(logger)
    scheduler.register_observer(email_notifier)
    scheduler.register_observer(task_executor)
    
    print("\n--- Simulating various events ---")
    
    # Normal file upload - logger and task executor will react
    scheduler.trigger_event('file_uploaded', {
        'filename': 'data_export.csv',
        'size': '2.4MB',
        'priority': 'normal'
    })
    
    time.sleep(0.5)
    
    # Critical API failure - all observers should react
    scheduler.trigger_event('api_response', {
        'status': 'error',
        'message': 'Service timeout after 30s',
        'priority': 'critical'
    })
    
    time.sleep(0.5)
    
    # User action - task executor logs to analytics
    scheduler.trigger_event('user_action', {
        'action': 'clicked_export_button',
        'user_id': '12345',
        'priority': 'low'
    })
    
    time.sleep(0.5)
    
    # Unknown event type - logger still records it
    scheduler.trigger_event('system_startup', {
        'version': '1.2.3',
        'priority': 'normal'
    })
    
    print("\n=== Demo Complete ===")