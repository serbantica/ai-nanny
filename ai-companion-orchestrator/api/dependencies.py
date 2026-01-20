"""
FastAPI Dependency Injection.
"""
from typing import AsyncGenerator
import redis.asyncio as aioredis
from fastapi import Request

from core.config import settings
from core.device.registry import DeviceRegistry
from core.persona.manager import PersonaManager
from core.session.manager import SessionManager

from core.coordination.group_activity import GroupActivityCoordinator
from core.coordination.handoff import HandoffManager
from core.events.bus import EventBus

async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    client =  aioredis.from_url(
        settings.redis_url, 
        password=settings.redis_password,
        encoding="utf-8", 
        decode_responses=True
    )
    try:
        yield client
    finally:
        await client.close()

async def get_device_registry(request: Request) -> DeviceRegistry:
    # In a real app we might cache this on app state
    redis = aioredis.from_url(settings.redis_url, password=settings.redis_password, decode_responses=True)
    return DeviceRegistry(redis)

async def get_persona_manager(request: Request) -> PersonaManager:
    try:
        redis = aioredis.from_url(settings.redis_url, password=settings.redis_password, decode_responses=True)
        # Test connection
        await redis.ping()
    except Exception:
        # Redis not available, use in-memory storage
        redis = None
    return PersonaManager(redis)

async def get_session_manager(request: Request) -> SessionManager:
    redis = aioredis.from_url(settings.redis_url, password=settings.redis_password, decode_responses=True)
    return SessionManager(redis)

async def get_event_bus(request: Request) -> EventBus:
    if not hasattr(request.app.state, "event_bus"):
        raise RuntimeError("EventBus not initialized")
    return request.app.state.event_bus

async def get_group_coordinator(request: Request) -> GroupActivityCoordinator:
    if not hasattr(request.app.state, "group_coordinator"):
        raise RuntimeError("GroupActivityCoordinator not initialized")
    return request.app.state.group_coordinator

async def get_handoff_manager(request: Request) -> HandoffManager:
    if not hasattr(request.app.state, "handoff_manager"):
        raise RuntimeError("HandoffManager not initialized")
    return request.app.state.handoff_manager
