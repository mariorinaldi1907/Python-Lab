"""
Date: 2026-07-23
Built a notification dispatcher using the observer pattern to handle multi-channel alerts with priority levels — felt like a clean way to decouple event sources from handlers.
"""

"""
Notification system using the Observer pattern.
Supports multiple notification channels (email, SMS, push) with priority filtering.
Each observer can subscribe to specific priority levels.
"""

from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
from typing import List, Set


class Priority(Enum):
    """Notification priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class Observer(ABC):
    """
    Abstract base for notification observers.
    Each observer processes notifications in their own way.
    """
    
    def __init__(self, name: str, min_priority: Priority = Priority.LOW):
        self.name = name
        self.min_priority = min_priority
    
    @abstractmethod
    def update(self, message: str, priority: Priority, timestamp: datetime):
        """
        Called when a notification is dispatched.
        Subclasses implement their specific delivery logic here.
        """
        pass
    
    def should_notify(self, priority: Priority) -> bool:
        """Check if this observer cares about the given priority level."""
        return priority.value >= self.min_priority.value


class EmailObserver(Observer):
    """Sends notifications via email (simulated)."""
    
    def update(self, message: str, priority: Priority, timestamp: datetime):
        if self.should_notify(priority):
            print(f"[EMAIL] {self.name}")
            print(f"  To: admin@example.com")
            print(f"  Subject: [{priority.name}] System Notification")
            print(f"  Body: {message}")
            print(f"  Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")


class SMSObserver(Observer):
    """Sends notifications via SMS (simulated)."""
    
    def update(self, message: str, priority: Priority, timestamp: datetime):
        if self.should_notify(priority):
            # SMS messages are typically shorter, so I truncate them
            short_msg = message[:100] + "..." if len(message) > 100 else message
            print(f"[SMS] {self.name}")
            print(f"  To: +1-555-0100")
            print(f"  Message: [{priority.name}] {short_msg}")
            print(f"  Time: {timestamp.strftime('%H:%M:%S')}\n")


class PushNotificationObserver(Observer):
    """Sends push notifications (simulated)."""
    
    def update(self, message: str, priority: Priority, timestamp: datetime):
        if self.should_notify(priority):
            print(f"[PUSH] {self.name}")
            print(f"  Device: iPhone 12 Pro")
            print(f"  Alert: {message}")
            print(f"  Badge: {priority.value}")
            print(f"  Time: {timestamp.strftime('%H:%M')}\n")


class NotificationSubject:
    """
    The subject (observable) that dispatches notifications to all registered observers.
    This is the core of the observer pattern — it maintains the list of observers
    and notifies them when something happens.
    """
    
    def __init__(self):
        self._observers: List[Observer] = []
    
    def attach(self, observer: Observer):
        """Register a new observer to receive notifications."""
        if observer not in self._observers:
            self._observers.append(observer)
            print(f"✓ Attached observer: {observer.name} (min priority: {observer.min_priority.name})")
    
    def detach(self, observer: Observer):
        """Unregister an observer from receiving notifications."""
        if observer in self._observers:
            self._observers.remove(observer)
            print(f"✗ Detached observer: {observer.name}")
    
    def notify(self, message: str, priority: Priority):
        """
        Send a notification to all observers.
        Each observer decides whether to act based on their priority threshold.
        """
        timestamp = datetime.now()
        print(f"\n{'='*70}")
        print(f"📢 Dispatching {priority.name} notification...")
        print(f"{'='*70}\n")
        
        for observer in self._observers:
            observer.update(message, priority, timestamp)


def main():
    """
    Demo of the observer pattern with a realistic notification scenario.
    We set up different channels with different priority thresholds.
    """
    print("Setting up notification system...\n")
    
    # Create the subject (notification dispatcher)
    notifier = NotificationSubject()
    
    # Create observers with different priority thresholds
    # Email gets everything (LOW and above)
    email_channel = EmailObserver("Primary Email Channel", Priority.LOW)
    
    # SMS only for important stuff (HIGH and above)
    sms_channel = SMSObserver("Emergency SMS", Priority.HIGH)
    
    # Push notifications for medium priority and above
    push_channel = PushNotificationObserver("Mobile App", Priority.MEDIUM)
    
    # Register all observers
    notifier.attach(email_channel)
    notifier.attach(sms_channel)
    notifier.attach(push_channel)
    
    print("\n" + "="*70)
    print("Running notification scenarios...")
    print("="*70)
    
    # Scenario 1: Low priority - only email should trigger
    notifier.notify(
        "Scheduled backup completed successfully. 1.2 GB backed up to cloud storage.",
        Priority.LOW
    )
    
    # Scenario 2: Medium priority - email and push should trigger
    notifier.notify(
        "Database connection pool reaching capacity. Current usage: 85%",
        Priority.MEDIUM
    )
    
    # Scenario 3: Critical priority - all channels should trigger
    notifier.notify(
        "CRITICAL: Production server CPU usage at 98%. Immediate attention required!",
        Priority.CRITICAL
    )
    
    print("\n" + "="*70)
    print("Demo complete!")
    print("="*70)


if __name__ == "__main__":
    main()