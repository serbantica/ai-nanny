"""
Session data models.
"""
from enum import Enum
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class MessageRole(str, Enum):
    """Role of a message sender."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class SessionState(str, Enum):
    """Current state of a session."""
    ACTIVE = "active"
    ENDED = "ended"
    PAUSED = "paused"

class ConversationMessage(BaseModel):
    """A single message in the conversation history."""
    id: str
    role: MessageRole
    content: str
    timestamp: datetime
    persona_id: str

class Session(BaseModel):
    """A conversation session."""
    id: str
    device_id: str
    persona_id: str
    user_id: Optional[str] = None
    state: SessionState
    created_at: datetime
    updated_at: datetime
    expires_at: datetime
    messages: List[ConversationMessage] = []
    metadata: Dict[str, Any] = {}
