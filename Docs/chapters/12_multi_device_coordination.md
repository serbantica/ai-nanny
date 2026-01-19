## 12. Multi-Device Coordination - Full Implementation

### 12.1 Overview

Multi-device coordination enables synchronized experiences across multiple devices in a facility or home.

### 12.2 Coordination Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **Synchronous** | All devices play same content | Group story time |
| **Handoff** | Transfer session between devices | Follow user between rooms |
| **Group Activity** | Coordinated multi-device game | Trivia, sing-along |
| **Event Propagation** | Device A triggers Device B | Emergency alerts |

### 12.3 Event Bus Implementation

```python
# core/events/bus.py
"""
Event Bus - Pub/Sub system for device coordination.
"""

import asyncio
import json
import logging
from typing import Callable, Dict, List, Set, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from redis import asyncio as aioredis

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    # Device events
    DEVICE_CONNECT = "device.connect"
    DEVICE_DISCONNECT = "device.disconnect"
    DEVICE_STATE_CHANGE = "device.state_change"
    
    # Persona events
    PERSONA_SWITCH = "persona.switch"
    PERSONA_SWITCH_COMPLETE = "persona.switch_complete"
    
    # Session events
    SESSION_START = "session.start"
    SESSION_END = "session.end"
    SESSION_HANDOFF = "session.handoff"
    
    # Coordination events
    GROUP_ACTIVITY_START = "coordination.group_start"
    GROUP_ACTIVITY_END = "coordination.group_end"
    SYNC_PLAYBACK = "coordination.sync_playback"
    BROADCAST = "coordination.broadcast"
    
    # Emergency
    EMERGENCY_ALERT = "emergency.alert"


@dataclass
class Event:
    """Event data structure."""
    type: EventType
    source_device_id: Optional[str]
    target_device_ids: List[str]  # Empty = broadcast to all
    payload: dict
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "type": self.type.value,
            "source_device_id": self.source_device_id,
            "target_device_ids": self.target_device_ids,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Event":
        return cls(
            type=EventType(data["type"]),
            source_device_id=data.get("source_device_id"),
            target_device_ids=data.get("target_device_ids", []),
            payload=data.get("payload", {}),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            correlation_id=data.get("correlation_id")
        )


class EventBus:
    """
    Redis-backed event bus for device coordination.
    
    Uses Redis Pub/Sub for real-time event distribution.
    """
    
    CHANNEL_PREFIX = "events:"
    GROUP_CHANNEL = "events:all"
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self._handlers: Dict[EventType, List[Callable]] = {}
        self._device_subscriptions: Dict[str, Set[str]] = {}  # device_id -> channel set
        self._pubsub = None
    
    async def start(self):
        """Start the event bus listener."""
        self._pubsub = self.redis.pubsub()
        await self._pubsub.subscribe(self.GROUP_CHANNEL)
        asyncio.create_task(self._listen())
        logger.info("Event bus started")
    
    async def stop(self):
        """Stop the event bus."""
        if self._pubsub:
            await self._pubsub.unsubscribe()
            await self._pubsub.close()
    
    def on(self, event_type: EventType, handler: Callable):
        """Register handler for event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    async def emit(self, event: Event):
        """Emit an event to the bus."""
        # Determine target channels
        if not event.target_device_ids:
            # Broadcast to all
            channels = [self.GROUP_CHANNEL]
        else:
            # Send to specific devices
            channels = [
                f"{self.CHANNEL_PREFIX}{device_id}"
                for device_id in event.target_device_ids
            ]
        
        # Publish to Redis
        event_data = json.dumps(event.to_dict())
        for channel in channels:
            await self.redis.publish(channel, event_data)
        
        logger.debug(f"Emitted event {event.type} to {len(channels)} channels")
    
    async def subscribe_device(self, device_id: str):
        """Subscribe a device to its private channel."""
        channel = f"{self.CHANNEL_PREFIX}{device_id}"
        await self._pubsub.subscribe(channel)
        
        if device_id not in self._device_subscriptions:
            self._device_subscriptions[device_id] = set()
        self._device_subscriptions[device_id].add(channel)
    
    async def unsubscribe_device(self, device_id: str):
        """Unsubscribe a device from its channels."""
        if device_id in self._device_subscriptions:
            for channel in self._device_subscriptions[device_id]:
                await self._pubsub.unsubscribe(channel)
            del self._device_subscriptions[device_id]
    
    async def _listen(self):
        """Listen for events on subscribed channels."""
        async for message in self._pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    event = Event.from_dict(data)
                    await self._dispatch(event)
                except Exception as e:
                    logger.error(f"Error processing event: {e}")
    
    async def _dispatch(self, event: Event):
        """Dispatch event to registered handlers."""
        if event.type in self._handlers:
            for handler in self._handlers[event.type]:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"Handler error for {event.type}: {e}")
```

### 12.4 Group Activity Coordinator

```python
# core/coordination/group_activity.py
"""
Group Activity Coordinator - Manages synchronized multi-device activities.
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import uuid

from core.events.bus import EventBus, Event, EventType


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
```

### 12.5 Session Handoff Manager

```python
# core/coordination/handoff.py
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
```

### 12.6 Demo Scenarios

#### Scenario 1: Group Trivia Game

```python
# Example usage for group trivia
async def demo_group_trivia():
    """
    Demo: Start group trivia across 3 devices.
    """
    coordinator = GroupActivityCoordinator(event_bus)
    
    activity = await coordinator.start_activity(
        activity_type=ActivityType.TRIVIA,
        device_ids=["dev_001", "dev_002", "dev_003"],
        persona_id="entertainer",
        config={
            "difficulty": "easy",
            "rounds": 10,
            "time_per_question": 15
        }
    )
    
    # Activity runs...
    # Each device gets questions, users answer
    # Scores are synchronized across devices
    
    await coordinator.end_activity(activity.id)
```

#### Scenario 2: Session Handoff

```python
# Example usage for session handoff
async def demo_handoff():
    """
    Demo: User moves from bedroom to kitchen.
    """
    handoff_manager = HandoffManager(event_bus, session_manager)
    
    # User presses button on kitchen device
    success = await handoff_manager.initiate_handoff(
        session_id="sess_current",
        from_device_id="dev_bedroom",
        to_device_id="dev_kitchen",
        notify_user=True  # "Continuing our conversation..."
    )
    
    if success:
        # Kitchen device continues exact conversation context
        pass
```

#### Scenario 3: Synchronized Story Time

```python
# Example usage for synchronized playback
async def demo_sync_story():
    """
    Demo: Play same story audio across all common room devices.
    """
    coordinator = GroupActivityCoordinator(event_bus)
    
    await coordinator.sync_playback(
        device_ids=["dev_001", "dev_002", "dev_003"],
        audio_url="https://storage.example.com/stories/bedtime_story.mp3",
        start_offset=0
    )
```

---
