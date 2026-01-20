## 9. Database Schema - Full Implementation

### 9.1 Overview

The platform uses PostgreSQL for persistent storage with SQLAlchemy ORM.

### 9.2 Entity Relationship Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Users     │────<│   Devices   │────<│  Sessions   │
└─────────────┘     └─────────────┘     └─────────────┘
                          │                    │
                          │                    │
                    ┌─────┴─────┐        ┌─────┴─────┐
                    │  Groups   │        │  Messages │
                    └───────────┘        └───────────┘
                    
┌─────────────┐     ┌─────────────┐
│  Personas   │────<│  Versions   │
└─────────────┘     └─────────────┘

┌─────────────┐
│   Events    │ (Telemetry / Audit Log)
└─────────────┘
```

### 9.3 SQLAlchemy Models

```python
# db/models/user.py
"""User model for admin and API access."""

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from db.base import Base
from datetime import datetime
import uuid


class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default="user")  # admin, user, device
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    devices = relationship("Device", back_populates="owner")
```

```python
# db/models/device.py
"""Device model for registered edge devices."""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from db.base import Base
from datetime import datetime
import uuid
import enum


class DeviceStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"


class DeviceType(str, enum.Enum):
    RASPBERRY_PI = "raspberry_pi"
    SMART_SPEAKER = "smart_speaker"
    TABLET = "tablet"
    CUSTOM = "custom"


class Device(Base):
    __tablename__ = "devices"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    device_type = Column(Enum(DeviceType), nullable=False)
    status = Column(Enum(DeviceStatus), default=DeviceStatus.OFFLINE)
    
    # Location and grouping
    location = Column(String(255))
    group_id = Column(String(36), ForeignKey("device_groups.id"), nullable=True)
    
    # Capabilities
    capabilities = Column(JSON, default=list)  # ["audio_input", "audio_output", "buttons"]
    
    # Authentication
    auth_token_hash = Column(String(255))
    
    # Owner
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    # Current state
    active_persona_id = Column(String(50), ForeignKey("personas.id"), nullable=True)
    active_session_id = Column(String(36), nullable=True)
    
    # Timestamps
    last_heartbeat = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="devices")
    group = relationship("DeviceGroup", back_populates="devices")
    sessions = relationship("Session", back_populates="device")
    active_persona = relationship("Persona")
```

```python
# db/models/device_group.py
"""Device groups for multi-device coordination."""

from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from db.base import Base
from datetime import datetime
import uuid


class DeviceGroup(Base):
    __tablename__ = "device_groups"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    
    # Configuration
    settings = Column(JSON, default=dict)  # Group-wide settings
    
    # Owner
    owner_id = Column(String(36), ForeignKey("users.id"))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    devices = relationship("Device", back_populates="group")
```

```python
# db/models/persona.py
"""Persona model for versioned persona definitions."""

from sqlalchemy import Column, String, DateTime, Boolean, JSON, Text, Integer
from sqlalchemy.orm import relationship
from db.base import Base
from datetime import datetime
import uuid


class Persona(Base):
    __tablename__ = "personas"
    
    id = Column(String(50), primary_key=True)  # e.g., "companion", "medication_nurse"
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    
    # Current version
    current_version = Column(String(20), default="1.0.0")
    
    # Adaptation mode
    adaptation_mode = Column(String(20), default="instruction_only")
    
    # Configuration (denormalized for quick access)
    voice_config = Column(JSON)
    behavior_config = Column(JSON)
    
    # System prompt
    system_prompt = Column(Text)
    
    # Metadata
    tags = Column(JSON, default=list)
    priority = Column(Integer, default=0)  # For emergency personas
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    versions = relationship("PersonaVersion", back_populates="persona")


class PersonaVersion(Base):
    __tablename__ = "persona_versions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    persona_id = Column(String(50), ForeignKey("personas.id"), nullable=False)
    version = Column(String(20), nullable=False)
    
    # Full artifact snapshot
    artifacts = Column(JSON)  # Complete persona definition
    
    # Audit info
    created_by = Column(String(36), ForeignKey("users.id"))
    change_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    persona = relationship("Persona", back_populates="versions")
```

```python
# db/models/session.py
"""Session model for conversation state."""

from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Enum, Text
from sqlalchemy.orm import relationship
from db.base import Base
from datetime import datetime
import uuid
import enum


class SessionState(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"
    HANDED_OFF = "handed_off"


class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Device and persona
    device_id = Column(String(36), ForeignKey("devices.id"), nullable=False)
    persona_id = Column(String(50), ForeignKey("personas.id"), nullable=False)
    
    # Optional user (for user-specific context)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    # State
    state = Column(Enum(SessionState), default=SessionState.ACTIVE)
    
    # Context (stored in Redis for speed, backed up here)
    context_snapshot = Column(JSON, default=dict)
    
    # Handoff tracking
    handoff_history = Column(JSON, default=list)
    
    # Metadata
    metadata = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime)
    ended_at = Column(DateTime, nullable=True)
    
    # Relationships
    device = relationship("Device", back_populates="sessions")
    messages = relationship("Message", back_populates="session", order_by="Message.created_at")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    
    # Content
    role = Column(String(20))  # user, assistant
    content = Column(Text)
    
    # Audio reference (if applicable)
    audio_url = Column(String(500), nullable=True)
    
    # Persona at time of message
    persona_id = Column(String(50))
    
    # Metrics
    response_latency_ms = Column(Integer, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("Session", back_populates="messages")
```

```python
# db/models/event.py
"""Event model for telemetry and audit logging."""

from sqlalchemy import Column, String, DateTime, JSON, Integer
from db.base import Base
from datetime import datetime
import uuid


class Event(Base):
    __tablename__ = "events"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Event classification
    event_type = Column(String(50), nullable=False, index=True)
    # Types: device_connect, device_disconnect, persona_switch, 
    #        session_start, session_end, handoff, error, api_call
    
    # Source
    device_id = Column(String(36), index=True, nullable=True)
    user_id = Column(String(36), nullable=True)
    session_id = Column(String(36), nullable=True)
    
    # Event data
    payload = Column(JSON)
    
    # Severity
    severity = Column(String(20), default="info")  # debug, info, warning, error, critical
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Partitioning hint (for large-scale deployments)
    partition_key = Column(Integer, default=0)
```

### 9.4 Indexes and Performance

```python
# db/indexes.py
"""Database indexes for performance optimization."""

from sqlalchemy import Index
from db.models import Device, Session, Message, Event

# Device lookups
Index('idx_device_status', Device.status)
Index('idx_device_group', Device.group_id)
Index('idx_device_owner', Device.owner_id)

# Session lookups
Index('idx_session_device', Session.device_id)
Index('idx_session_state', Session.state)
Index('idx_session_active', Session.device_id, Session.state)

# Message retrieval
Index('idx_message_session', Message.session_id)
Index('idx_message_created', Message.created_at)

# Event analytics
Index('idx_event_type_time', Event.event_type, Event.created_at)
Index('idx_event_device_time', Event.device_id, Event.created_at)
```

### 9.5 Migration Script

```python
# db/migrations/versions/001_initial_schema.py
"""Initial schema creation.

Revision ID: 001
Create Date: 2026-01-19
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255)),
        sa.Column('role', sa.String(50), default='user'),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )
    op.create_index('idx_users_email', 'users', ['email'])
    
    # Device groups table
    op.create_table(
        'device_groups',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(500)),
        sa.Column('settings', sa.JSON()),
        sa.Column('owner_id', sa.String(36), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )
    
    # Personas table
    op.create_table(
        'personas',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(500)),
        sa.Column('current_version', sa.String(20)),
        sa.Column('adaptation_mode', sa.String(20)),
        sa.Column('voice_config', sa.JSON()),
        sa.Column('behavior_config', sa.JSON()),
        sa.Column('system_prompt', sa.Text()),
        sa.Column('tags', sa.JSON()),
        sa.Column('priority', sa.Integer(), default=0),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )
    
    # Devices table
    op.create_table(
        'devices',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('device_type', sa.String(20)),
        sa.Column('status', sa.String(20)),
        sa.Column('location', sa.String(255)),
        sa.Column('group_id', sa.String(36), sa.ForeignKey('device_groups.id')),
        sa.Column('capabilities', sa.JSON()),
        sa.Column('auth_token_hash', sa.String(255)),
        sa.Column('owner_id', sa.String(36), sa.ForeignKey('users.id')),
        sa.Column('active_persona_id', sa.String(50), sa.ForeignKey('personas.id')),
        sa.Column('active_session_id', sa.String(36)),
        sa.Column('last_heartbeat', sa.DateTime()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )
    op.create_index('idx_devices_status', 'devices', ['status'])
    op.create_index('idx_devices_group', 'devices', ['group_id'])
    
    # Sessions table
    op.create_table(
        'sessions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('device_id', sa.String(36), sa.ForeignKey('devices.id'), nullable=False),
        sa.Column('persona_id', sa.String(50), sa.ForeignKey('personas.id'), nullable=False),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id')),
        sa.Column('state', sa.String(20)),
        sa.Column('context_snapshot', sa.JSON()),
        sa.Column('handoff_history', sa.JSON()),
        sa.Column('metadata', sa.JSON()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('expires_at', sa.DateTime()),
        sa.Column('ended_at', sa.DateTime()),
    )
    op.create_index('idx_sessions_device', 'sessions', ['device_id'])
    op.create_index('idx_sessions_state', 'sessions', ['state'])
    
    # Messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('session_id', sa.String(36), sa.ForeignKey('sessions.id'), nullable=False),
        sa.Column('role', sa.String(20)),
        sa.Column('content', sa.Text()),
        sa.Column('audio_url', sa.String(500)),
        sa.Column('persona_id', sa.String(50)),
        sa.Column('response_latency_ms', sa.Integer()),
        sa.Column('tokens_used', sa.Integer()),
        sa.Column('created_at', sa.DateTime()),
    )
    op.create_index('idx_messages_session', 'messages', ['session_id'])
    
    # Events table
    op.create_table(
        'events',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('device_id', sa.String(36)),
        sa.Column('user_id', sa.String(36)),
        sa.Column('session_id', sa.String(36)),
        sa.Column('payload', sa.JSON()),
        sa.Column('severity', sa.String(20)),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('partition_key', sa.Integer()),
    )
    op.create_index('idx_events_type_time', 'events', ['event_type', 'created_at'])
    op.create_index('idx_events_device_time', 'events', ['device_id', 'created_at'])
    
    # Persona versions table
    op.create_table(
        'persona_versions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('persona_id', sa.String(50), sa.ForeignKey('personas.id'), nullable=False),
        sa.Column('version', sa.String(20), nullable=False),
        sa.Column('artifacts', sa.JSON()),
        sa.Column('created_by', sa.String(36), sa.ForeignKey('users.id')),
        sa.Column('change_notes', sa.Text()),
        sa.Column('created_at', sa.DateTime()),
    )


def downgrade():
    op.drop_table('persona_versions')
    op.drop_table('events')
    op.drop_table('messages')
    op.drop_table('sessions')
    op.drop_table('devices')
    op.drop_table('personas')
    op.drop_table('device_groups')
    op.drop_table('users')
```

---
