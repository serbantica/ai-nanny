"""
Device data models.
"""
from enum import Enum
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class DeviceStatus(str, Enum):
    """Current connection/operational status of a device."""
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"

class DeviceType(str, Enum):
    """Type of hardware device."""
    RASPBERRY_PI = "raspberry_pi"
    SMART_SPEAKER = "smart_speaker"
    TABLET = "tablet"
    CUSTOM = "custom"
    SIMULATOR = "simulator"

class DeviceCapabilities(BaseModel):
    """Hardware capabilities of a device."""
    audio_input: bool = True
    audio_output: bool = True
    buttons: bool = False
    leds: bool = False
    display: bool = False
    camera: bool = False

class DeviceHealth(BaseModel):
    """Health metrics reported by a device."""
    cpu_usage: float
    memory_usage: float
    temperature: float
    wifi_strength: int
    uptime_seconds: int
    last_updated: datetime

class Device(BaseModel):
    """A registered physical or virtual device."""
    id: str
    name: str = Field(..., min_length=1, max_length=100)
    type: DeviceType
    group_id: Optional[str] = None
    location: Optional[str] = None
    status: DeviceStatus = DeviceStatus.OFFLINE
    capabilities: DeviceCapabilities
    active_persona_id: Optional[str] = None
    last_heartbeat: Optional[datetime] = None
    metadata: Dict[str, Any] = {}
    registered_at: datetime
    auth_token_hash: Optional[str] = None
