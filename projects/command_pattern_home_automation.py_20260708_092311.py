"""
Date: 2026-07-08
Built a home automation controller using the command pattern to handle device controls with full undo/redo support — feels like building a mini smart home.
"""

"""
Home Automation System using Command Pattern

This demonstrates the Command pattern with a practical use case: controlling
smart home devices with the ability to undo/redo operations. Each command
encapsulates a specific action (turn on light, set thermostat, etc.) and
knows how to reverse itself.
"""

from abc import ABC, abstractmethod
from typing import List


class Command(ABC):
    """
    Abstract base class for all commands.
    Each command must know how to execute and undo itself.
    """
    
    @abstractmethod
    def execute(self):
        """Execute the command."""
        pass
    
    @abstractmethod
    def undo(self):
        """Undo the command, reverting to previous state."""
        pass


class Light:
    """A simple smart light that can be turned on/off and dimmed."""
    
    def __init__(self, location: str):
        self.location = location
        self.is_on = False
        self.brightness = 0  # 0-100
    
    def turn_on(self):
        """Turn the light on."""
        self.is_on = True
        self.brightness = 100
        print(f"[{self.location}] Light is ON at {self.brightness}% brightness")
    
    def turn_off(self):
        """Turn the light off."""
        self.is_on = False
        self.brightness = 0
        print(f"[{self.location}] Light is OFF")
    
    def set_brightness(self, level: int):
        """Set brightness level (0-100)."""
        self.brightness = max(0, min(100, level))
        self.is_on = self.brightness > 0
        print(f"[{self.location}] Light brightness set to {self.brightness}%")


class Thermostat:
    """A smart thermostat for temperature control."""
    
    def __init__(self, location: str):
        self.location = location
        self.temperature = 70  # Default temp in Fahrenheit
    
    def set_temperature(self, temp: int):
        """Set the target temperature."""
        self.temperature = temp
        print(f"[{self.location}] Thermostat set to {self.temperature}°F")


class LightOnCommand(Command):
    """Command to turn a light on."""
    
    def __init__(self, light: Light):
        self.light = light
        self.previous_state = None
    
    def execute(self):
        """Turn the light on, saving previous state for undo."""
        self.previous_state = (self.light.is_on, self.light.brightness)
        self.light.turn_on()
    
    def undo(self):
        """Restore previous light state."""
        if self.previous_state:
            was_on, brightness = self.previous_state
            if was_on:
                self.light.set_brightness(brightness)
            else:
                self.light.turn_off()


class LightOffCommand(Command):
    """Command to turn a light off."""
    
    def __init__(self, light: Light):
        self.light = light
        self.previous_state = None
    
    def execute(self):
        """Turn the light off, saving previous state for undo."""
        self.previous_state = (self.light.is_on, self.light.brightness)
        self.light.turn_off()
    
    def undo(self):
        """Restore previous light state."""
        if self.previous_state:
            was_on, brightness = self.previous_state
            if was_on:
                self.light.set_brightness(brightness)


class DimLightCommand(Command):
    """Command to dim a light to a specific brightness."""
    
    def __init__(self, light: Light, brightness: int):
        self.light = light
        self.brightness = brightness
        self.previous_brightness = None
    
    def execute(self):
        """Set light brightness, saving previous value."""
        self.previous_brightness = self.light.brightness
        self.light.set_brightness(self.brightness)
    
    def undo(self):
        """Restore previous brightness level."""
        if self.previous_brightness is not None:
            self.light.set_brightness(self.previous_brightness)


class SetThermostatCommand(Command):
    """Command to set thermostat temperature."""
    
    def __init__(self, thermostat: Thermostat, temperature: int):
        self.thermostat = thermostat
        self.temperature = temperature
        self.previous_temperature = None
    
    def execute(self):
        """Set new temperature, saving previous value."""
        self.previous_temperature = self.thermostat.temperature
        self.thermostat.set_temperature(self.temperature)
    
    def undo(self):
        """Restore previous temperature."""
        if self.previous_temperature is not None:
            self.thermostat.set_temperature(self.previous_temperature)


class HomeAutomationController:
    """
    The invoker in the Command pattern.
    Manages command execution and maintains history for undo/redo.
    """
    
    def __init__(self):
        self.history: List[Command] = []
        self.redo_stack: List[Command] = []
    
    def execute_command(self, command: Command):
        """Execute a command and add it to history."""
        command.execute()
        self.history.append(command)
        # Clear redo stack since we're executing a new command
        self.redo_stack.clear()
    
    def undo(self):
        """Undo the last command."""
        if not self.history:
            print("Nothing to undo!")
            return
        
        command = self.history.pop()
        command.undo()
        self.redo_stack.append(command)
        print("↩ Undo performed")
    
    def redo(self):
        """Redo the last undone command."""
        if not self.redo_stack:
            print("Nothing to redo!")
            return
        
        command = self.redo_stack.pop()
        command.execute()
        self.history.append(command)
        print("↪ Redo performed")


if __name__ == "__main__":
    # Create devices
    living_room_light = Light("Living Room")
    bedroom_light = Light("Bedroom")
    living_room_thermostat = Thermostat("Living Room")
    
    # Create controller
    controller = HomeAutomationController()
    
    print("=== Home Automation Demo ===\n")
    
    # Turn on living room light
    controller.execute_command(LightOnCommand(living_room_light))
    print()
    
    # Dim it
    controller.execute_command(DimLightCommand(living_room_light, 50))
    print()
    
    # Turn on bedroom light
    controller.execute_command(LightOnCommand(bedroom_light))
    print()
    
    # Set thermostat
    controller.execute_command(SetThermostatCommand(living_room_thermostat, 72))
    print()
    
    # Undo last command (thermostat change)
    print("--- Undoing operations ---")
    controller.undo()
    print()
    
    # Undo bedroom light
    controller.undo()
    print()
    
    # Redo bedroom light
    print("--- Redoing operations ---")
    controller.redo()
    print()
    
    # Turn off all lights
    print("--- Turning off lights ---")
    controller.execute_command(LightOffCommand(living_room_light))
    controller.execute_command(LightOffCommand(bedroom_light))
    print()
    
    # Undo both
    print("--- Undo twice ---")
    controller.undo()
    controller.undo()