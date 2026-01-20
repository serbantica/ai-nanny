"""
AI Companion Orchestrator API
"""
from contextlib import asynccontextmanager
import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.logging_config import setup_logging
from core.events.bus import EventBus
from core.coordination.group_activity import GroupActivityCoordinator
from core.coordination.handoff import HandoffManager
from core.session.manager import SessionManager
from api.routers import devices, personas, health, coordination, knowledge, admin, conversation

# Setup logging
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # Create persistent Redis connection for EventBus
    redis_bus = aioredis.from_url(
        settings.redis_url, 
        password=settings.redis_password,
        encoding="utf-8", 
        decode_responses=True
    )
    
    # Create Redis connection for Managers
    redis_mgr = aioredis.from_url(
        settings.redis_url, 
        password=settings.redis_password,
        encoding="utf-8", 
        decode_responses=True
    )
    
    # Initialize services
    app.state.event_bus = EventBus(redis_bus)
    app.state.session_manager = SessionManager(redis_mgr)
    
    app.state.group_coordinator = GroupActivityCoordinator(app.state.event_bus)
    app.state.handoff_manager = HandoffManager(app.state.event_bus, app.state.session_manager)
    
    # Start EventBus
    try:
        await app.state.event_bus.start()
    except Exception as e:
        import logging
        logging.getLogger("uvicorn.error").error(f"Failed to connect to Redis: {e}. Multi-device coordination will not work.")
    
    yield
    
    # Shutdown
    await app.state.event_bus.stop()
    await redis_bus.close()
    await redis_mgr.close()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Authentication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(devices.router, prefix="/api/v1/devices", tags=["devices"])
app.include_router(personas.router, prefix="/api/v1/personas", tags=["personas"])
app.include_router(coordination.router, prefix="/api/v1/coordination", tags=["coordination"])
app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["knowledge"])
app.include_router(admin.router, prefix="/api/v1/admin/activity", tags=["admin"])
app.include_router(conversation.router, prefix="/api/v1/conversation", tags=["conversation"])

@app.get("/")
async def root():
    return {"message": "AI Companion Orchestrator API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
