## 11. Device Runtime - Full Implementation

### 11.1 Overview

The device runtime is a lightweight Python agent that runs on edge hardware (Raspberry Pi 4) and communicates with the cloud control plane.

### 11.2 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Device Agent Runtime                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Audio Handler   │  │ Network Client  │  │ Hardware I/O    │ │
│  │                 │  │                 │  │                 │ │
│  │ • Microphone    │  │ • WebSocket     │  │ • GPIO/Buttons  │ │
│  │ • Speaker       │  │ • HTTP fallback │  │ • LED control   │ │
│  │ • VAD           │  │ • Reconnection  │  │ • Display (opt) │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│                              │                                   │
│                    ┌─────────┴─────────┐                        │
│                    │   State Manager   │                        │
│                    │                   │                        │
│                    │ • Persona cache   │                        │
│                    │ • Offline queue   │                        │
│                    │ • Session state   │                        │
│                    └───────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
```

### 11.3 Main Entry Point

```python
# device_agent/main.py
"""
Device Agent - Main entry point for Raspberry Pi runtime.
"""

import asyncio
import signal
import logging
from pathlib import Path

from device_agent.hardware.audio import AudioHandler
from device_agent.hardware.gpio import GPIOController
from device_agent.network.websocket_client import WebSocketClient
from device_agent.cache.persona_cache import PersonaCache
from device_agent.config import DeviceConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeviceAgent:
    """Main device agent orchestrating all components."""
    
    def __init__(self, config: DeviceConfig):
        self.config = config
        self.running = False
        
        # Initialize components
        self.audio = AudioHandler(
            sample_rate=config.audio_sample_rate,
            channels=config.audio_channels
        )
        self.gpio = GPIOController(
            button_pins=config.button_pins,
            led_pins=config.led_pins
        )
        self.ws_client = WebSocketClient(
            url=config.control_plane_url,
            device_id=config.device_id,
            auth_token=config.auth_token
        )
        self.persona_cache = PersonaCache(
            cache_dir=Path(config.cache_dir)
        )
        
        # Current state
        self.active_persona_id = None
        self.session_id = None
        self.is_listening = False
        
    async def start(self):
        """Start the device agent."""
        logger.info(f"Starting device agent: {self.config.device_id}")
        self.running = True
        
        # Set initial LED state
        self.gpio.set_led_state("idle")
        
        # Connect to control plane
        await self.ws_client.connect()
        
        # Register event handlers
        self._register_handlers()
        
        # Start main loop
        await self._main_loop()
    
    async def stop(self):
        """Stop the device agent gracefully."""
        logger.info("Stopping device agent...")
        self.running = False
        self.gpio.set_led_state("off")
        await self.ws_client.disconnect()
        self.audio.cleanup()
        self.gpio.cleanup()
    
    def _register_handlers(self):
        """Register event handlers for buttons and network."""
        # Button handlers
        self.gpio.on_button_press("red", self._handle_emergency)
        self.gpio.on_button_press("green", self._handle_companion_mode)
        self.gpio.on_button_press("blue", self._handle_activity_mode)
        
        # WebSocket handlers
        self.ws_client.on_message("persona_switch", self._handle_persona_switch)
        self.ws_client.on_message("audio_response", self._handle_audio_response)
        self.ws_client.on_message("sync_event", self._handle_sync_event)
    
    async def _main_loop(self):
        """Main event loop."""
        while self.running:
            try:
                # Check for voice activity
                if self.audio.detect_voice_activity():
                    await self._handle_voice_input()
                
                # Process any pending WebSocket messages
                await self.ws_client.process_messages()
                
                # Heartbeat
                await self._send_heartbeat()
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                self.gpio.set_led_state("error")
                await asyncio.sleep(1)
    
    async def _handle_voice_input(self):
        """Handle voice input from user."""
        self.gpio.set_led_state("listening")
        self.is_listening = True
        
        # Record audio until silence
        audio_data = await self.audio.record_until_silence(
            max_duration=30,
            silence_threshold=0.5
        )
        
        if audio_data:
            self.gpio.set_led_state("processing")
            
            # Send to control plane
            await self.ws_client.send({
                "type": "audio_stream",
                "payload": {
                    "audio_b64": audio_data,
                    "persona_id": self.active_persona_id,
                    "session_id": self.session_id
                }
            })
        
        self.is_listening = False
    
    async def _handle_audio_response(self, message: dict):
        """Handle audio response from control plane."""
        self.gpio.set_led_state("speaking")
        
        audio_url = message["payload"].get("audio_url")
        audio_b64 = message["payload"].get("audio_b64")
        
        if audio_url:
            audio_data = await self._download_audio(audio_url)
        elif audio_b64:
            audio_data = audio_b64
        else:
            return
        
        await self.audio.play(audio_data)
        self.gpio.set_led_state("idle")
    
    async def _handle_persona_switch(self, message: dict):
        """Handle persona switch command."""
        new_persona_id = message["payload"]["persona_id"]
        logger.info(f"Switching persona: {self.active_persona_id} -> {new_persona_id}")
        
        self.gpio.set_led_state("processing")
        
        # Load persona from cache or request from control plane
        persona = await self.persona_cache.get_or_fetch(
            new_persona_id,
            self.ws_client
        )
        
        self.active_persona_id = new_persona_id
        
        # Play transition sound/message if configured
        if message["payload"].get("transition_message"):
            await self.audio.speak_text(message["payload"]["transition_message"])
        
        self.gpio.set_led_state("idle")
        
        # Acknowledge switch
        await self.ws_client.send({
            "type": "ack",
            "payload": {
                "switch_complete": True,
                "persona_id": new_persona_id
            }
        })
    
    async def _handle_emergency(self):
        """Handle emergency button press."""
        logger.warning("Emergency button pressed!")
        self.gpio.set_led_state("emergency")  # Red flashing
        
        await self.ws_client.send({
            "type": "button_press",
            "payload": {
                "button": "emergency",
                "request_persona": "emergency"
            }
        })
    
    async def _handle_companion_mode(self):
        """Handle companion mode button."""
        await self.ws_client.send({
            "type": "button_press",
            "payload": {
                "button": "companion",
                "request_persona": "companion"
            }
        })
    
    async def _handle_activity_mode(self):
        """Handle activity mode button."""
        await self.ws_client.send({
            "type": "button_press",
            "payload": {
                "button": "activity",
                "request_persona": "entertainer"
            }
        })
    
    async def _handle_sync_event(self, message: dict):
        """Handle multi-device sync events."""
        event_type = message["payload"]["event_type"]
        
        if event_type == "start_group_activity":
            # Join group activity
            pass
        elif event_type == "sync_playback":
            # Synchronize audio playback
            pass
    
    async def _send_heartbeat(self):
        """Send periodic heartbeat to control plane."""
        # Throttle to every 30 seconds
        pass
    
    async def _download_audio(self, url: str) -> bytes:
        """Download audio from URL."""
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.content


async def main():
    """Main entry point."""
    config = DeviceConfig.from_env()
    agent = DeviceAgent(config)
    
    # Handle shutdown signals
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(agent.stop()))
    
    try:
        await agent.start()
    except KeyboardInterrupt:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
```

### 11.4 Hardware Interface - GPIO Controller

```python
# device_agent/hardware/gpio.py
"""
GPIO Controller for buttons and LEDs on Raspberry Pi.
"""

import logging
from typing import Callable, Dict
from enum import Enum

try:
    import RPi.GPIO as GPIO
    RPI_AVAILABLE = True
except ImportError:
    RPI_AVAILABLE = False
    
logger = logging.getLogger(__name__)


class LEDState(str, Enum):
    OFF = "off"
    IDLE = "idle"           # Solid blue
    LISTENING = "listening"  # Pulsing blue
    PROCESSING = "processing"  # Yellow
    SPEAKING = "speaking"    # Green
    ERROR = "error"         # Red
    EMERGENCY = "emergency"  # Flashing red


class GPIOController:
    """Controls buttons and LEDs on Raspberry Pi."""
    
    # Default pin mappings
    DEFAULT_BUTTON_PINS = {
        "red": 17,      # Emergency
        "green": 27,    # Companion
        "blue": 22      # Activity
    }
    
    DEFAULT_LED_PINS = {
        "red": 5,
        "green": 6,
        "blue": 13
    }
    
    def __init__(
        self,
        button_pins: Dict[str, int] = None,
        led_pins: Dict[str, int] = None,
        use_mock: bool = False
    ):
        self.button_pins = button_pins or self.DEFAULT_BUTTON_PINS
        self.led_pins = led_pins or self.DEFAULT_LED_PINS
        self.use_mock = use_mock or not RPI_AVAILABLE
        self._button_callbacks: Dict[str, Callable] = {}
        
        if not self.use_mock:
            self._setup_gpio()
        else:
            logger.warning("Running in mock GPIO mode")
    
    def _setup_gpio(self):
        """Initialize GPIO pins."""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Setup buttons as inputs with pull-up resistors
        for name, pin in self.button_pins.items():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(
                pin,
                GPIO.FALLING,
                callback=lambda ch, n=name: self._button_pressed(n),
                bouncetime=300
            )
        
        # Setup LEDs as outputs
        for name, pin in self.led_pins.items():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
    
    def on_button_press(self, button_name: str, callback: Callable):
        """Register callback for button press."""
        self._button_callbacks[button_name] = callback
    
    def _button_pressed(self, button_name: str):
        """Handle button press event."""
        logger.info(f"Button pressed: {button_name}")
        if button_name in self._button_callbacks:
            # Run callback in asyncio context
            import asyncio
            callback = self._button_callbacks[button_name]
            asyncio.create_task(callback())
    
    def set_led_state(self, state: str):
        """Set LED display state."""
        if self.use_mock:
            logger.info(f"LED state: {state}")
            return
        
        # Turn off all LEDs first
        for pin in self.led_pins.values():
            GPIO.output(pin, GPIO.LOW)
        
        if state == LEDState.OFF:
            pass
        elif state == LEDState.IDLE:
            GPIO.output(self.led_pins["blue"], GPIO.HIGH)
        elif state == LEDState.LISTENING:
            # TODO: Implement pulsing with PWM
            GPIO.output(self.led_pins["blue"], GPIO.HIGH)
        elif state == LEDState.PROCESSING:
            GPIO.output(self.led_pins["red"], GPIO.HIGH)
            GPIO.output(self.led_pins["green"], GPIO.HIGH)
        elif state == LEDState.SPEAKING:
            GPIO.output(self.led_pins["green"], GPIO.HIGH)
        elif state == LEDState.ERROR:
            GPIO.output(self.led_pins["red"], GPIO.HIGH)
        elif state == LEDState.EMERGENCY:
            # TODO: Implement flashing
            GPIO.output(self.led_pins["red"], GPIO.HIGH)
    
    def cleanup(self):
        """Cleanup GPIO on shutdown."""
        if not self.use_mock:
            GPIO.cleanup()
```

### 11.5 Audio Handler

```python
# device_agent/hardware/audio.py
"""
Audio Handler for microphone input and speaker output.
"""

import asyncio
import base64
import logging
import numpy as np
from typing import Optional

try:
    import pyaudio
    import sounddevice as sd
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

logger = logging.getLogger(__name__)


class AudioHandler:
    """Handles audio input/output on the device."""
    
    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_size: int = 1024,
        use_mock: bool = False
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.use_mock = use_mock or not AUDIO_AVAILABLE
        
        self._pyaudio: Optional[pyaudio.PyAudio] = None
        self._stream = None
        
        if not self.use_mock:
            self._setup_audio()
    
    def _setup_audio(self):
        """Initialize audio system."""
        self._pyaudio = pyaudio.PyAudio()
    
    def detect_voice_activity(self) -> bool:
        """
        Simple voice activity detection.
        Returns True if voice is detected.
        """
        if self.use_mock:
            return False
        
        try:
            # Record small chunk
            audio = sd.rec(
                int(0.1 * self.sample_rate),  # 100ms
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='float32'
            )
            sd.wait()
            
            # Check energy level
            energy = np.sqrt(np.mean(audio ** 2))
            return energy > 0.02  # Threshold
            
        except Exception as e:
            logger.error(f"VAD error: {e}")
            return False
    
    async def record_until_silence(
        self,
        max_duration: float = 30,
        silence_threshold: float = 0.5,
        silence_duration: float = 1.5
    ) -> Optional[str]:
        """
        Record audio until silence is detected.
        Returns base64-encoded audio data.
        """
        if self.use_mock:
            logger.info("Mock recording...")
            await asyncio.sleep(2)
            return None
        
        logger.info("Recording...")
        frames = []
        silence_count = 0
        max_silence_chunks = int(silence_duration * self.sample_rate / self.chunk_size)
        
        stream = self._pyaudio.open(
            format=pyaudio.paFloat32,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        try:
            total_chunks = int(max_duration * self.sample_rate / self.chunk_size)
            
            for _ in range(total_chunks):
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                frames.append(data)
                
                # Check for silence
                audio_chunk = np.frombuffer(data, dtype=np.float32)
                energy = np.sqrt(np.mean(audio_chunk ** 2))
                
                if energy < 0.02:
                    silence_count += 1
                    if silence_count >= max_silence_chunks:
                        logger.info("Silence detected, stopping recording")
                        break
                else:
                    silence_count = 0
            
            stream.stop_stream()
            stream.close()
            
            # Convert to bytes and base64 encode
            audio_data = b''.join(frames)
            return base64.b64encode(audio_data).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Recording error: {e}")
            stream.stop_stream()
            stream.close()
            return None
    
    async def play(self, audio_data: str):
        """
        Play base64-encoded audio data.
        """
        if self.use_mock:
            logger.info("Mock playback...")
            await asyncio.sleep(1)
            return
        
        try:
            # Decode base64
            audio_bytes = base64.b64decode(audio_data)
            audio_array = np.frombuffer(audio_bytes, dtype=np.float32)
            
            # Play audio
            sd.play(audio_array, self.sample_rate)
            sd.wait()
            
        except Exception as e:
            logger.error(f"Playback error: {e}")
    
    async def speak_text(self, text: str):
        """
        Convert text to speech and play.
        Uses local TTS fallback if available.
        """
        logger.info(f"Speaking: {text}")
        # TODO: Implement local TTS fallback
        pass
    
    def cleanup(self):
        """Cleanup audio resources."""
        if self._pyaudio:
            self._pyaudio.terminate()
```

### 11.6 WebSocket Client

```python
# device_agent/network/websocket_client.py
"""
WebSocket client for real-time communication with control plane.
"""

import asyncio
import json
import logging
from typing import Callable, Dict, Optional

import websockets
from websockets.exceptions import ConnectionClosed

logger = logging.getLogger(__name__)


class WebSocketClient:
    """WebSocket client with auto-reconnection."""
    
    def __init__(
        self,
        url: str,
        device_id: str,
        auth_token: str,
        reconnect_delay: float = 5.0
    ):
        self.url = url
        self.device_id = device_id
        self.auth_token = auth_token
        self.reconnect_delay = reconnect_delay
        
        self._ws = None
        self._connected = False
        self._handlers: Dict[str, Callable] = {}
        self._message_queue: asyncio.Queue = asyncio.Queue()
    
    async def connect(self):
        """Establish WebSocket connection."""
        while True:
            try:
                headers = {
                    "Authorization": f"Bearer {self.auth_token}",
                    "X-Device-ID": self.device_id
                }
                
                self._ws = await websockets.connect(
                    self.url,
                    extra_headers=headers,
                    ping_interval=30,
                    ping_timeout=10
                )
                
                self._connected = True
                logger.info(f"Connected to control plane: {self.url}")
                
                # Start message receiver
                asyncio.create_task(self._receive_loop())
                return
                
            except Exception as e:
                logger.error(f"Connection failed: {e}, retrying in {self.reconnect_delay}s")
                await asyncio.sleep(self.reconnect_delay)
    
    async def disconnect(self):
        """Close WebSocket connection."""
        self._connected = False
        if self._ws:
            await self._ws.close()
    
    async def send(self, message: dict):
        """Send message to control plane."""
        if not self._connected or not self._ws:
            logger.warning("Not connected, queueing message")
            await self._message_queue.put(message)
            return
        
        try:
            await self._ws.send(json.dumps(message))
        except ConnectionClosed:
            logger.warning("Connection closed, queueing message")
            await self._message_queue.put(message)
            asyncio.create_task(self.connect())
    
    def on_message(self, message_type: str, handler: Callable):
        """Register handler for message type."""
        self._handlers[message_type] = handler
    
    async def _receive_loop(self):
        """Receive and dispatch messages."""
        try:
            async for message in self._ws:
                data = json.loads(message)
                message_type = data.get("type")
                
                if message_type in self._handlers:
                    asyncio.create_task(
                        self._handlers[message_type](data)
                    )
                else:
                    logger.warning(f"Unhandled message type: {message_type}")
                    
        except ConnectionClosed:
            logger.warning("Connection closed")
            self._connected = False
            asyncio.create_task(self.connect())
    
    async def process_messages(self):
        """Process any queued messages after reconnection."""
        while self._connected and not self._message_queue.empty():
            message = await self._message_queue.get()
            await self.send(message)
```

### 11.7 Persona Cache

```python
# device_agent/cache/persona_cache.py
"""
Local persona cache for offline fallback.
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class PersonaCache:
    """Local cache for personas enabling offline operation."""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._memory_cache: Dict[str, dict] = {}
    
    def get(self, persona_id: str) -> Optional[dict]:
        """Get persona from cache."""
        # Check memory cache first
        if persona_id in self._memory_cache:
            return self._memory_cache[persona_id]
        
        # Check disk cache
        cache_file = self.cache_dir / f"{persona_id}.json"
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    persona = json.load(f)
                    self._memory_cache[persona_id] = persona
                    return persona
            except Exception as e:
                logger.error(f"Error loading cached persona: {e}")
        
        return None
    
    def save(self, persona_id: str, persona: dict):
        """Save persona to cache."""
        self._memory_cache[persona_id] = persona
        
        cache_file = self.cache_dir / f"{persona_id}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(persona, f)
        except Exception as e:
            logger.error(f"Error saving persona to cache: {e}")
    
    async def get_or_fetch(
        self,
        persona_id: str,
        ws_client
    ) -> Optional[dict]:
        """Get persona from cache or fetch from control plane."""
        # Try cache first
        persona = self.get(persona_id)
        if persona:
            return persona
        
        # Fetch from control plane
        try:
            await ws_client.send({
                "type": "persona_request",
                "payload": {"persona_id": persona_id}
            })
            # Note: Actual implementation would await response
            return None
            
        except Exception as e:
            logger.error(f"Error fetching persona: {e}")
            return None
```

### 11.8 Device Configuration

```python
# device_agent/config.py
"""
Device configuration management.
"""

import os
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class DeviceConfig:
    """Device agent configuration."""
    
    # Identity
    device_id: str
    device_name: str
    
    # Network
    control_plane_url: str
    auth_token: str
    
    # Audio
    audio_sample_rate: int = 16000
    audio_channels: int = 1
    
    # Hardware pins
    button_pins: Dict[str, int] = None
    led_pins: Dict[str, int] = None
    
    # Cache
    cache_dir: str = "/var/cache/ai-companion"
    
    @classmethod
    def from_env(cls) -> "DeviceConfig":
        """Load configuration from environment variables."""
        return cls(
            device_id=os.getenv("DEVICE_ID", ""),
            device_name=os.getenv("DEVICE_NAME", "ai-companion"),
            control_plane_url=os.getenv("CONTROL_PLANE_URL", "wss://api.ai-companion.io/ws"),
            auth_token=os.getenv("DEVICE_AUTH_TOKEN", ""),
            audio_sample_rate=int(os.getenv("AUDIO_SAMPLE_RATE", "16000")),
            audio_channels=int(os.getenv("AUDIO_CHANNELS", "1")),
            cache_dir=os.getenv("CACHE_DIR", "/var/cache/ai-companion")
        )
```

### 11.9 Hardware Bill of Materials

| Component | Model | Cost | Purpose |
|-----------|-------|------|---------|
| Raspberry Pi 4 | 4GB RAM | $55 | Compute |
| USB Speakerphone | Jabra Speak 410 or similar | $30 | Audio I/O |
| 3-Button Keypad | Custom PCB or arcade buttons | $8 | Persona triggers |
| RGB LED Strip | WS2812B (short segment) | $5 | Visual status |
| Power Supply | 5V 3A USB-C | $10 | Power |
| MicroSD Card | 32GB Class 10 | $8 | Storage |
| Enclosure | 3D printed | $12 | Professional appearance |
| **Total per unit** | | **$128** | |

---
