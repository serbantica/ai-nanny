## 8. API Specifications - Full Implementation

### 8.1 API Overview

The platform exposes two API layers:
1. **Control Plane API**: Device management, persona library, analytics
2. **Device Runtime API**: Dialog, persona switching, state management

Base URL: `https://api.ai-companion.io/v1`

### 8.2 Authentication

All endpoints require JWT authentication.

```python
# api/middleware/auth.py
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from core.config import settings

security = HTTPBearer()

async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### 8.3 Device Endpoints

#### Register Device

```
POST /devices
```

**Request:**
```python
# api/schemas/device.py
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class DeviceType(str, Enum):
    RASPBERRY_PI = "raspberry_pi"
    SMART_SPEAKER = "smart_speaker"
    TABLET = "tablet"
    CUSTOM = "custom"

class DeviceRegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    device_type: DeviceType
    location: Optional[str] = None
    group_id: Optional[str] = None
    capabilities: List[str] = ["audio_input", "audio_output"]
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "living-room-companion",
                "device_type": "raspberry_pi",
                "location": "Living Room",
                "group_id": "facility-001",
                "capabilities": ["audio_input", "audio_output", "buttons", "leds"]
            }
        }
```

**Response:**
```python
class DeviceRegisterResponse(BaseModel):
    device_id: str
    auth_token: str
    websocket_url: str
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "dev_abc123",
                "auth_token": "eyJ0eXAi...",
                "websocket_url": "wss://api.ai-companion.io/ws/dev_abc123",
                "created_at": "2026-01-19T10:30:00Z"
            }
        }
```

#### Get Device State

```
GET /devices/{device_id}/state
```

**Response:**
```python
class DeviceState(BaseModel):
    device_id: str
    status: str  # online, offline, busy
    active_persona_id: Optional[str]
    active_session_id: Optional[str]
    last_activity: datetime
    metrics: dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "dev_abc123",
                "status": "online",
                "active_persona_id": "companion",
                "active_session_id": "sess_xyz789",
                "last_activity": "2026-01-19T10:45:00Z",
                "metrics": {
                    "uptime_hours": 12.5,
                    "interactions_today": 47,
                    "avg_response_latency_ms": 1250
                }
            }
        }
```

### 8.4 Persona Endpoints

#### List Personas

```
GET /personas
```

**Response:**
```python
class PersonaSummary(BaseModel):
    id: str
    name: str
    description: str
    version: str
    tags: List[str]
    adaptation_mode: str

class PersonaListResponse(BaseModel):
    personas: List[PersonaSummary]
    total: int
```

#### Get Persona Details

```
GET /personas/{persona_id}
```

**Response:**
```python
class PersonaDetail(BaseModel):
    id: str
    name: str
    description: str
    version: str
    voice_config: dict
    behavior_config: dict
    tags: List[str]
    created_at: datetime
    updated_at: datetime
```

#### Switch Persona

```
POST /devices/{device_id}/persona/switch
```

**Request:**
```python
class PersonaSwitchRequest(BaseModel):
    target_persona_id: str
    preserve_context: bool = True
    transition_message: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "target_persona_id": "medication_nurse",
                "preserve_context": True,
                "transition_message": "Switching to medication reminder mode"
            }
        }
```

**Response:**
```python
class PersonaSwitchResponse(BaseModel):
    success: bool
    previous_persona_id: Optional[str]
    new_persona_id: str
    switch_latency_ms: int
    session_id: str
```

### 8.5 Dialog Endpoints

#### Send Message

```
POST /dialog/send
```

**Request:**
```python
class DialogSendRequest(BaseModel):
    device_id: str
    session_id: Optional[str] = None
    message: str
    audio_base64: Optional[str] = None  # If sending audio instead of text
    
    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "dev_abc123",
                "session_id": "sess_xyz789",
                "message": "Good morning! How are you today?"
            }
        }
```

**Response:**
```python
class DialogSendResponse(BaseModel):
    session_id: str
    response_text: str
    response_audio_url: Optional[str]  # Pre-signed URL for audio
    persona_id: str
    latency_ms: int
    tokens_used: int
```

### 8.6 Session Endpoints

#### Create Session

```
POST /sessions
```

**Request:**
```python
class SessionCreateRequest(BaseModel):
    device_id: str
    persona_id: str
    user_id: Optional[str] = None
    metadata: dict = {}
```

#### Handoff Session

```
POST /sessions/{session_id}/handoff
```

**Request:**
```python
class SessionHandoffRequest(BaseModel):
    from_device_id: str
    to_device_id: str
    notify_user: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "from_device_id": "dev_bedroom",
                "to_device_id": "dev_kitchen",
                "notify_user": True
            }
        }
```

### 8.7 Multi-Device Coordination Endpoints

#### Start Group Activity

```
POST /coordination/group-activity
```

**Request:**
```python
class GroupActivityRequest(BaseModel):
    activity_type: str  # trivia, story, sync_playback
    device_ids: List[str]
    persona_id: str
    config: dict = {}
    
    class Config:
        json_schema_extra = {
            "example": {
                "activity_type": "trivia",
                "device_ids": ["dev_001", "dev_002", "dev_003"],
                "persona_id": "entertainer",
                "config": {
                    "difficulty": "easy",
                    "rounds": 10
                }
            }
        }
```

#### Broadcast Event

```
POST /coordination/broadcast
```

**Request:**
```python
class BroadcastRequest(BaseModel):
    event_type: str
    target_devices: List[str]  # or ["all"] for all devices in group
    payload: dict
```

### 8.8 WebSocket Protocol

Devices maintain persistent WebSocket connections for real-time communication.

**Connection URL:** `wss://api.ai-companion.io/ws/{device_id}`

#### Message Types

```python
# Incoming (from device)
class WSMessage(BaseModel):
    type: str  # audio_stream, text_input, button_press, heartbeat
    payload: dict
    timestamp: datetime

# Outgoing (to device)
class WSCommand(BaseModel):
    type: str  # audio_response, persona_switch, led_control, sync_event
    payload: dict
    priority: int = 0  # Higher = more urgent
```

#### Example Flow

```
Device → Server: {"type": "audio_stream", "payload": {"audio_b64": "..."}}
Server → Device: {"type": "audio_response", "payload": {"audio_url": "...", "text": "..."}}

Server → Device: {"type": "persona_switch", "payload": {"persona_id": "medication_nurse"}}
Device → Server: {"type": "ack", "payload": {"switch_complete": true, "latency_ms": 1200}}
```

### 8.9 Error Responses

All errors follow a consistent format:

```python
class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: dict = {}
    request_id: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "error_code": "PERSONA_NOT_FOUND",
                "message": "Persona 'invalid_id' does not exist",
                "details": {"requested_id": "invalid_id"},
                "request_id": "req_abc123"
            }
        }
```

#### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `DEVICE_NOT_FOUND` | 404 | Device ID not registered |
| `DEVICE_OFFLINE` | 503 | Device not connected |
| `PERSONA_NOT_FOUND` | 404 | Persona ID not in library |
| `SESSION_EXPIRED` | 410 | Session timed out |
| `RATE_LIMITED` | 429 | Too many requests |
| `LLM_API_ERROR` | 502 | Upstream LLM failure |

---
