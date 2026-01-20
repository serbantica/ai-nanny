"""
Group Activity Coordinator - Manages synchronized multi-device activities.
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import uuid
import logging

from core.events.bus import EventBus, Event, EventType

logger = logging.getLogger(__name__)

class ActivityType(str, Enum):
    TRIVIA = "trivia"
    STORY = "story"
    SYNC_PLAYBACK = "sync_playback"
    SING_ALONG = "sing_along"


class ActivityState(str, Enum):
    PENDING = "pending"
    STARTING = "starting"
    ACTIVE = "active"
    PAUSED = "paused"
    ENDING = "ending"
    ENDED = "ended"


@dataclass
class GroupActivity:
    """Represents an active group activity."""
    id: str
    activity_type: ActivityType
    device_ids: List[str]
    persona_id: str
    config: dict
    state: ActivityState
    current_step: int
    scores: Dict[str, int]  # device_id -> score
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None


class GroupActivityCoordinator:
    """Coordinates multi-device group activities."""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self._active_activities: Dict[str, GroupActivity] = {}
        
        # Register event handlers
        self.event_bus.on(EventType.GROUP_ACTIVITY_START, self._handle_start)
        self.event_bus.on(EventType.GROUP_ACTIVITY_END, self._handle_end)
    
    async def start_activity(
        self,
        activity_type: ActivityType,
        device_ids: List[str],
        persona_id: str,
        config: dict = None
    ) -> GroupActivity:
        """Start a new group activity."""
        activity = GroupActivity(
            id=str(uuid.uuid4()),
            activity_type=activity_type,
            device_ids=device_ids,
            persona_id=persona_id,
            config=config or {},
            state=ActivityState.STARTING,
            current_step=0,
            scores={device_id: 0 for device_id in device_ids}
        )
        
        self._active_activities[activity.id] = activity
        
        # Notify all devices to join
        await self.event_bus.emit(Event(
            type=EventType.GROUP_ACTIVITY_START,
            source_device_id=None,
            target_device_ids=device_ids,
            payload={
                "activity_id": activity.id,
                "activity_type": activity_type.value,
                "persona_id": persona_id,
                "config": config
            }
        ))
        
        # Wait for all devices to acknowledge
        # (simplified - actual implementation would track acks)
        await asyncio.sleep(2)
        
        activity.state = ActivityState.ACTIVE
        activity.started_at = datetime.utcnow()
        
        return activity
    
    async def end_activity(self, activity_id: str):
        """End a group activity."""
        if activity_id not in self._active_activities:
            return
        
        activity = self._active_activities[activity_id]
        activity.state = ActivityState.ENDING
        
        # Notify all devices
        await self.event_bus.emit(Event(
            type=EventType.GROUP_ACTIVITY_END,
            source_device_id=None,
            target_device_ids=activity.device_ids,
            payload={
                "activity_id": activity_id,
                "final_scores": activity.scores
            }
        ))
        
        activity.state = ActivityState.ENDED
        activity.ended_at = datetime.utcnow()
        
        del self._active_activities[activity_id]
    
    async def sync_playback(
        self,
        device_ids: List[str],
        audio_url: str,
        start_offset: float = 0
    ):
        """Synchronize audio playback across devices."""
        sync_time = datetime.utcnow().timestamp() + 1  # Start in 1 second
        
        await self.event_bus.emit(Event(
            type=EventType.SYNC_PLAYBACK,
            source_device_id=None,
            target_device_ids=device_ids,
            payload={
                "audio_url": audio_url,
                "start_time": sync_time,
                "offset": start_offset
            }
        ))
    
    async def _handle_start(self, event: Event):
        """Handle group activity start event."""
        pass  # Device-side handling
    
    async def _handle_end(self, event: Event):
        """Handle group activity end event."""
        pass  # Device-side handling
