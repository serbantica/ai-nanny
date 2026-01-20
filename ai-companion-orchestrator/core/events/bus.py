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
        self._is_running = False
    
    async def start(self):
        """Start the event bus listener."""
        if self._is_running:
            return
            
        self._pubsub = self.redis.pubsub()
        await self._pubsub.subscribe(self.GROUP_CHANNEL)
        self._is_running = True
        asyncio.create_task(self._listen())
        logger.info("Event bus started")
    
    async def stop(self):
        """Stop the event bus."""
        self._is_running = False
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
        if not self._pubsub:
              logger.warning("EventBus not started, cannot subscribe device")
              return

        channel = f"{self.CHANNEL_PREFIX}{device_id}"
        await self._pubsub.subscribe(channel)
        
        if device_id not in self._device_subscriptions:
            self._device_subscriptions[device_id] = set()
        self._device_subscriptions[device_id].add(channel)
    
    async def unsubscribe_device(self, device_id: str):
        """Unsubscribe a device from its channels."""
        if not self._pubsub:
            return
            
        if device_id in self._device_subscriptions:
            for channel in self._device_subscriptions[device_id]:
                await self._pubsub.unsubscribe(channel)
            del self._device_subscriptions[device_id]
    
    async def _listen(self):
        """Listen for events on subscribed channels."""
        while self._is_running:
            try:
                message = await self._pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message and message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        event = Event.from_dict(data)
                        await self._dispatch(event)
                    except Exception as e:
                        logger.error(f"Error processing event: {e}")
            except Exception as e:
                logger.error(f"PubSub listener error: {e}")
                if not self._is_running:
                    break
                await asyncio.sleep(1)
    
    async def _dispatch(self, event: Event):
        """Dispatch event to registered handlers."""
        if event.type in self._handlers:
            for handler in self._handlers[event.type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(f"Handler error for {event.type}: {e}")
