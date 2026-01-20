"""
Session Handoff Manager - Transfer sessions between devices.
"""

import asyncio
from typing import Optional
from datetime import datetime
import logging

from core.events.bus import EventBus, Event, EventType
from core.session.manager import SessionManager

logger = logging.getLogger(__name__)


class HandoffManager:
    """Manages session handoffs between devices."""
    
    def __init__(
        self,
        event_bus: EventBus,
        session_manager: SessionManager
    ):
        self.event_bus = event_bus
        self.session_manager = session_manager
        self._pending_handoffs: dict = {}
    
    async def initiate_handoff(
        self,
        session_id: str,
        from_device_id: str,
        to_device_id: str,
        notify_user: bool = True
    ) -> bool:
        """
        Initiate a session handoff between devices.
        
        Returns True if handoff successful.
        """
        logger.info(f"Initiating handoff: {from_device_id} -> {to_device_id}")
        
        # Get current session
        session = await self.session_manager.get_session(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return False
        
        # Notify source device to prepare handoff
        await self.event_bus.emit(Event(
            type=EventType.SESSION_HANDOFF,
            source_device_id=from_device_id,
            target_device_ids=[from_device_id],
            payload={
                "action": "prepare_handoff",
                "session_id": session_id,
                "target_device": to_device_id
            }
        ))
        
        # Perform the handoff in session manager
        await self.session_manager.handoff_session(
            session_id=session_id,
            from_device_id=from_device_id,
            to_device_id=to_device_id
        )
        
        # Notify target device to accept handoff
        await self.event_bus.emit(Event(
            type=EventType.SESSION_HANDOFF,
            source_device_id=from_device_id,
            target_device_ids=[to_device_id],
            payload={
                "action": "accept_handoff",
                "session_id": session_id,
                "context": session.context_snapshot if hasattr(session, 'context_snapshot') else {},
                "persona_id": session.persona_id,
                "notify_user": notify_user
            }
        ))
        
        logger.info(f"Handoff complete: {from_device_id} -> {to_device_id}")
        return True
    
    async def request_nearby_devices(
        self,
        device_id: str,
        group_id: Optional[str] = None
    ) -> list:
        """Get list of nearby/same-group devices for handoff candidates."""
        # This would query the device registry
        # For now, return empty list
        return []
