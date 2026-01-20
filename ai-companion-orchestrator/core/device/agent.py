"""
Device Agent Module - Virtual and Physical Device Abstraction
"""

import logging
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


class LEDState(str, Enum):
    """LED states for device"""
    IDLE = "Idle"
    LISTENING = "Listening"
    SPEAKING = "Speaking"
    THINKING = "Thinking"
    ERROR = "Error"
    CONNECTING = "Connecting"


class PersonaType(str, Enum):
    """Available persona types"""
    COMPANION = "companion"
    ACTIVITY = "activity"
    EMERGENCY = "emergency"
    ENTERTAINER = "entertainer"
    STORYTELLER = "storyteller"
    MEDICATION_NURSE = "medication_nurse"


class DeviceEvent:
    """Device event with timestamp and metadata"""
    def __init__(self, source: str, event_type: str, message: str, metadata: Optional[Dict[str, Any]] = None):
        self.timestamp = datetime.now()
        self.source = source
        self.event_type = event_type
        self.message = message
        self.metadata = metadata or {}
    
    def __str__(self):
        ts = self.timestamp.strftime("%H:%M:%S")
        return f"[{ts}] [{self.source}] {self.message}"
    
    def to_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "event_type": self.event_type,
            "message": self.message,
            "metadata": self.metadata
        }


class DeviceAgent:
    """
    Abstract Device Agent - Base class for physical and virtual devices
    """
    
    def __init__(
        self,
        device_id: str,
        device_name: str,
        device_type: str = "virtual",
        location: str = "Unknown"
    ):
        self.device_id = device_id
        self.device_name = device_name
        self.device_type = device_type
        self.location = location
        self.led_state = LEDState.IDLE
        self.current_persona = PersonaType.COMPANION
        self.is_connected = True
        self.latency_ms = 0
        self.event_log: List[DeviceEvent] = []
        self.event_listeners: List[Callable] = []
        
        logger.info(f"Device agent initialized: {device_id} ({device_name})")
    
    def log_event(self, source: str, event_type: str, message: str, metadata: Optional[Dict] = None):
        """Log a device event"""
        event = DeviceEvent(source, event_type, message, metadata)
        self.event_log.append(event)
        
        # Notify listeners
        for listener in self.event_listeners:
            try:
                listener(event)
            except Exception as e:
                logger.error(f"Error notifying event listener: {e}")
        
        logger.debug(f"Device event: {event}")
        return event
    
    def add_event_listener(self, callback: Callable):
        """Add event listener callback"""
        self.event_listeners.append(callback)
    
    def get_recent_events(self, limit: int = 10) -> List[DeviceEvent]:
        """Get recent events"""
        return self.event_log[-limit:]
    
    def set_led(self, state: LEDState):
        """Set LED state"""
        self.led_state = state
        self.log_event("DEVICE", "led_change", f"LED state → {state.value}")
    
    def switch_persona(self, persona: PersonaType):
        """Switch device persona"""
        old_persona = self.current_persona
        self.current_persona = persona
        self.log_event(
            "DEVICE",
            "persona_switch",
            f"Persona switched: {old_persona.value} → {persona.value}",
            {"from": old_persona.value, "to": persona.value}
        )
    
    def listen(self, audio_data: Any = None) -> str:
        """
        Listen for audio input (abstract - to be implemented by subclasses)
        Returns transcribed text
        """
        raise NotImplementedError("Subclass must implement listen()")
    
    def speak(self, text: str):
        """
        Speak text through device speaker (abstract - to be implemented by subclasses)
        """
        raise NotImplementedError("Subclass must implement speak()")
    
    def get_status(self) -> Dict[str, Any]:
        """Get device status"""
        return {
            "device_id": self.device_id,
            "device_name": self.device_name,
            "device_type": self.device_type,
            "location": self.location,
            "is_connected": self.is_connected,
            "led_state": self.led_state.value,
            "current_persona": self.current_persona.value,
            "latency_ms": self.latency_ms,
            "event_count": len(self.event_log)
        }


class VirtualDeviceAgent(DeviceAgent):
    """
    Virtual Device Agent - Simulated device for testing and UI
    """
    
    def __init__(
        self,
        device_id: str = "virtual-001",
        device_name: str = "Virtual Device",
        location: str = "Dashboard"
    ):
        super().__init__(device_id, device_name, "virtual", location)
        self.simulated_audio_buffer = ""
        self.assistant_response = ""
    
    def listen(self, text_input: str = None) -> str:
        """Simulate listening to audio input"""
        self.set_led(LEDState.LISTENING)
        self.log_event("EDGE", "wake_word_detected", "Wake word detected")
        
        if text_input:
            self.simulated_audio_buffer = text_input
            self.log_event("EDGE", "audio_buffer_ready", f"Audio transcribed: {text_input[:50]}...")
        
        return self.simulated_audio_buffer
    
    def speak(self, text: str):
        """Simulate speaking text"""
        self.set_led(LEDState.SPEAKING)
        self.log_event("EDGE", "tts_playback_start", f"Speaking: {text[:50]}...")
        self.assistant_response = text
        
        # Simulate speaking duration
        import time
        time.sleep(0.3)
        
        self.log_event("EDGE", "tts_playback_end", "Speech playback complete")
        self.set_led(LEDState.IDLE)
    
    def simulate_button_press(self, button_type: str):
        """Simulate physical button press"""
        self.log_event("EDGE", "button_press", f"Button pressed: {button_type}")
        
        if button_type in ["companion", "activity", "emergency"]:
            self.switch_persona(PersonaType(button_type))


class PhysicalDeviceAgent(DeviceAgent):
    """
    Physical Device Agent - Real Raspberry Pi device
    (Stub implementation - would interface with actual hardware)
    """
    
    def __init__(
        self,
        device_id: str,
        device_name: str,
        location: str = "Unknown",
        mic_device: str = "default",
        speaker_device: str = "default",
        gpio_config: Optional[Dict] = None
    ):
        super().__init__(device_id, device_name, "physical", location)
        self.mic_device = mic_device
        self.speaker_device = speaker_device
        self.gpio_config = gpio_config or {}
        
        # Hardware initialization would happen here
        logger.info(f"Physical device configured: mic={mic_device}, speaker={speaker_device}")
    
    def listen(self, audio_data: Any = None) -> str:
        """
        Listen for audio input from physical microphone
        (Stub - would use actual STT pipeline)
        """
        self.set_led(LEDState.LISTENING)
        self.log_event("EDGE", "mic_activated", "Microphone activated")
        
        # TODO: Implement actual audio capture and STT
        # - Capture audio from mic_device
        # - Send to STT service (Whisper, etc.)
        # - Return transcribed text
        
        raise NotImplementedError("Physical device STT not yet implemented")
    
    def speak(self, text: str):
        """
        Speak text through physical speaker
        (Stub - would use actual TTS pipeline)
        """
        self.set_led(LEDState.SPEAKING)
        self.log_event("EDGE", "tts_start", f"Starting TTS: {text[:50]}...")
        
        # TODO: Implement actual TTS and audio playback
        # - Generate audio with TTS service (ElevenLabs, etc.)
        # - Play audio through speaker_device
        # - Monitor playback completion
        
        raise NotImplementedError("Physical device TTS not yet implemented")
    
    def setup_gpio_buttons(self):
        """Setup GPIO buttons for persona switching"""
        # TODO: Implement GPIO setup
        # - Initialize GPIO library (RPi.GPIO, gpiozero)
        # - Configure button pins from gpio_config
        # - Setup interrupt handlers
        pass


class DeviceRegistry:
    """Registry to manage multiple devices"""
    
    def __init__(self):
        self.devices: Dict[str, DeviceAgent] = {}
    
    def register_device(self, device: DeviceAgent):
        """Register a device"""
        self.devices[device.device_id] = device
        logger.info(f"Device registered: {device.device_id}")
    
    def unregister_device(self, device_id: str):
        """Unregister a device"""
        if device_id in self.devices:
            del self.devices[device_id]
            logger.info(f"Device unregistered: {device_id}")
    
    def get_device(self, device_id: str) -> Optional[DeviceAgent]:
        """Get device by ID"""
        return self.devices.get(device_id)
    
    def list_devices(self) -> List[Dict[str, Any]]:
        """List all registered devices"""
        return [device.get_status() for device in self.devices.values()]
    
    def get_device_count(self) -> int:
        """Get total device count"""
        return len(self.devices)


# Global registry instance
_device_registry = DeviceRegistry()


def get_device_registry() -> DeviceRegistry:
    """Get global device registry"""
    return _device_registry
