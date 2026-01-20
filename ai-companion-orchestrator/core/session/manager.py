"""
Session Manager - Handles conversation state and context. 
"""

import json
from typing import Optional, List
from datetime import datetime, timedelta
from uuid import uuid4

from redis import asyncio as aioredis

from core.config import settings
from core.exceptions import SessionNotFoundError, SessionExpiredError
from core.session.models import (
    Session, 
    SessionState, 
    ConversationMessage, 
    MessageRole
)


class SessionManager: 
    """
    Manages conversation sessions and their state.
    
    Features:
    - Session creation and lifecycle
    - Message history management
    - Context preservation across persona switches
    - Session handoff between devices
    """
    
    SESSION_PREFIX = "session:"
    DEVICE_SESSION_PREFIX = "device_session:"
    DEFAULT_TTL_HOURS = 24
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
    
    async def create_session(
        self,
        device_id: str,
        persona_id: str,
        user_id: Optional[str] = None
    ) -> Session:
        """
        Create a new conversation session.
        
        Args:
            device_id: Device initiating the session
            persona_id: Initial persona for the session
            user_id: Optional user identifier
            
        Returns:
            New Session object
        """
        session = Session(
            id=str(uuid4()),
            device_id=device_id,
            persona_id=persona_id,
            user_id=user_id,
            state=SessionState.ACTIVE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=self.DEFAULT_TTL_HOURS),
            messages=[],
            metadata={}
        )
        
        # Store session
        await self._save_session(session)
        
        # Link device to session
        await self.redis.set(
            f"{self.DEVICE_SESSION_PREFIX}{device_id}",
            session.id
        )
        
        return session
    
    async def get_session(self, session_id: str) -> Session:
        """
        Retrieve a session by ID.
        
        Raises:
            SessionNotFoundError: If session doesn't exist
            SessionExpiredError: If session has expired
        """
        data = await self.redis.get(f"{self.SESSION_PREFIX}{session_id}")
        
        if not data:
            raise SessionNotFoundError(session_id)
        
        session = Session.model_validate_json(data)
        
        if session.expires_at < datetime.utcnow():
            await self.end_session(session_id)
            raise SessionExpiredError(session_id)
        
        return session
    
    async def get_device_session(self, device_id: str) -> Optional[Session]:
        """Get the active session for a device."""
        session_id = await self.redis.get(f"{self.DEVICE_SESSION_PREFIX}{device_id}")
        
        if not session_id: 
            return None
        
        try:
            return await self.get_session(session_id.decode())
        except (SessionNotFoundError, SessionExpiredError):
            return None
    
    async def add_message(
        self,
        session_id: str,
        role: MessageRole,
        content: str
    ) -> ConversationMessage:
        """
        Add a message to the session history.
        
        Args:
            session_id: Session to add message to
            role: Who sent the message (user/assistant)
            content: Message content
            
        Returns:
            The created message
        """
        session = await self.get_session(session_id)
        
        message = ConversationMessage(
            id=str(uuid4()),
            role=role,
            content=content,
            timestamp=datetime.utcnow(),
            persona_id=session.persona_id
        )
        
        session.messages.append(message)
        session.updated_at = datetime.utcnow()
        
        await self._save_session(session)
        
        return message
    
    async def update_persona(
        self,
        session_id: str,
        new_persona_id: str,
        preserve_context: bool = True
    ) -> Session:
        """
        Update the session's active persona.
        
        Args:
            session_id: Session to update
            new_persona_id: New persona ID
            preserve_context: Whether to keep message history
            
        Returns:
            Updated session
        """
        session = await self.get_session(session_id)
        
        session.persona_id = new_persona_id
        session.updated_at = datetime.utcnow()
        
        if not preserve_context: 
            session.messages = []
        
        await self._save_session(session)
        
        return session
    
    async def handoff_session(
        self,
        session_id: str,
        from_device_id: str,
        to_device_id: str
    ) -> Session:
        """
        Hand off a session from one device to another. 
        
        This enables "continue conversation in another room" scenarios.
        """
        session = await self.get_session(session_id)
        
        # Remove from old device
        await self.redis.delete(f"{self.DEVICE_SESSION_PREFIX}{from_device_id}")
        
        # Update session
        session.device_id = to_device_id
        session.updated_at = datetime.utcnow()
        if "handoff_history" not in session.metadata:
            session.metadata["handoff_history"] = []
            
        session.metadata["handoff_history"].append({
            "from": from_device_id,
            "to": to_device_id,
            "at": datetime.utcnow().isoformat()
        })
        
        await self._save_session(session)
        
        # Link new device
        await self.redis.set(
            f"{self.DEVICE_SESSION_PREFIX}{to_device_id}",
            session.id
        )
        
        return session
    
    async def end_session(self, session_id: str) -> None:
        """End a session."""
        try:
            session = await self.get_session(session_id)
            session.state = SessionState.ENDED
            session.expires_at = datetime.utcnow()
            await self._save_session(session)
            # Clean up active session
            await self.redis.delete(f"{self.DEVICE_SESSION_PREFIX}{session.device_id}")
        except SessionNotFoundError:
            pass

    async def _save_session(self, session: Session) -> None:
        """Save session to Redis."""
        await self.redis.setex(
            f"{self.SESSION_PREFIX}{session.id}",
            self.DEFAULT_TTL_HOURS * 3600,
            session.model_dump_json()
        )
