from pydantic import BaseModel, Field
from typing import Optional, List
from core.device.models import DeviceType, DeviceCapabilities, DeviceStatus

class DeviceRegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    device_type: DeviceType
    location: Optional[str] = None
    group_id: Optional[str] = None
    capabilities: List[str] = ["audio_input", "audio_output"]

class DeviceRegisterResponse(BaseModel):
    device_id: str
    auth_token: str
    websocket_url: str

class DeviceResponse(BaseModel):
    id: str
    name: str
    status: DeviceStatus
    active_persona: Optional[str] = None
    location: Optional[str]
    last_heartbeat: Optional[str]
