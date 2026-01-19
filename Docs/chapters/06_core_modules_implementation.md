## 6. Core Modules Implementation

### 6.1 Configuration Management

```python name=core/config. py
"""
Application configuration management using Pydantic Settings.
"""

from functools import lru_cache
from typing import Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Application
    app_name:  str = "ai-companion-orchestrator"
    app_env: str = Field(default="development", pattern="^(development|staging|production)$")
    app_debug: bool = True
    app_secret_key: str = Field(... , min_length=32)
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    
    # Database
    database_url: str
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Redis
    redis_url:  str = "redis://localhost:6379/0"
    redis_password: Optional[str] = None
    
    # JWT Authentication
    jwt_secret_key: str = Field(..., min_length=32)
    jwt_algorithm:  str = "HS256"
    jwt_expiration_hours: int = 24
    
    # Anthropic Claude
    anthropic_api_key: str
    anthropic_model: str = "claude-3-sonnet-20240229"
    
    # OpenAI (Whisper)
    openai_api_key: str
    whisper_model: str = "whisper-1"
    
    # ElevenLabs
    elevenlabs_api_key: str
    elevenlabs_voice_id:  str = "21m00Tcm4TlvDq8ikWAM"
    
    # Feature Flags
    enable_analytics: bool = True
    enable_multi_device: bool = True
    enable_offline_mode:  bool = True
    enable_fine_tuning: bool = False
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window_seconds:  int = 60
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # CORS
    cors_origins:  List[str] = ["http://localhost:3000", "http://localhost:8501"]
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @property
    def is_production(self) -> bool:
        return self.app_env == "production"
    
    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
```

### 6.2 Custom Exceptions

```python name=core/exceptions.py
"""
Custom exception classes for the AI Companion Orchestrator.
"""

from typing import Optional, Dict, Any


class AICompanionError(Exception):
    """Base exception for all application errors."""
    
    def __init__(
        self,
        message: str,
        error_code:  str = "UNKNOWN_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_code": self.error_code,
            "message": self. message,
            "details": self.details
        }


# =============================================================================
# Persona Errors
# =============================================================================

class PersonaError(AICompanionError):
    """Base exception for persona-related errors."""
    pass


class PersonaNotFoundError(PersonaError):
    """Raised when a persona cannot be found."""
    
    def __init__(self, persona_id: str):
        super().__init__(
            message=f"Persona not found: {persona_id}",
            error_code="PERSONA_NOT_FOUND",
            details={"persona_id": persona_id}
        )


class PersonaLoadError(PersonaError):
    """Raised when a persona fails to load."""
    
    def __init__(self, persona_id: str, reason: str):
        super().__init__(
            message=f"Failed to load persona {persona_id}: {reason}",
            error_code="PERSONA_LOAD_ERROR",
            details={"persona_id": persona_id, "reason": reason}
        )


class PersonaSwitchError(PersonaError):
    """Raised when persona switching fails."""
    
    def __init__(self, from_persona:  str, to_persona: str, reason: str):
        super().__init__(
            message=f"Failed to switch from {from_persona} to {to_persona}: {reason}",
            error_code="PERSONA_SWITCH_ERROR",
            details={
                "from_persona": from_persona,
                "to_persona": to_persona,
                "reason": reason
            }
        )


# =============================================================================
# Device Errors
# =============================================================================

class DeviceError(AICompanionError):
    """Base exception for device-related errors."""
    pass


class DeviceNotFoundError(DeviceError):
    """Raised when a device cannot be found."""
    
    def __init__(self, device_id: str):
        super().__init__(
            message=f"Device not found:  {device_id}",
            error_code="DEVICE_NOT_FOUND",
            details={"device_id": device_id}
        )


class DeviceOfflineError(DeviceError):
    """Raised when attempting to communicate with an offline device."""
    
    def __init__(self, device_id: str):
        super().__init__(
            message=f"Device is offline: {device_id}",
            error_code="DEVICE_OFFLINE",
            details={"device_id": device_id}
        )


class DeviceRegistrationError(DeviceError):
    """Raised when device registration fails."""
    
    def __init__(self, reason: str):
        super().__init__(
            message=f"Device registration failed:  {reason}",
            error_code="DEVICE_REGISTRATION_ERROR",
            details={"reason":  reason}
        )


# =============================================================================
# Session Errors
# =============================================================================

class SessionError(AICompanionError):
    """Base exception for session-related errors."""
    pass


class SessionNotFoundError(SessionError):
    """Raised when a session cannot be found."""
    
    def __init__(self, session_id: str):
        super().__init__(
            message=f"Session not found: {session_id}",
            error_code="SESSION_NOT_FOUND",
            details={"session_id":  session_id}
        )


class SessionExpiredError(SessionError):
    """Raised when a session has expired."""
    
    def __init__(self, session_id: str):
        super().__init__(
            message=f"Session has expired: {session_id}",
            error_code="SESSION_EXPIRED",
            details={"session_id": session_id}
        )


# =============================================================================
# Conversation Errors
# =============================================================================

class ConversationError(AICompanionError):
    """Base exception for conversation-related errors."""
    pass


class LLMAPIError(ConversationError):
    """Raised when LLM API call fails."""
    
    def __init__(self, provider: str, reason: str):
        super().__init__(
            message=f"LLM API error ({provider}): {reason}",
            error_code="LLM_API_ERROR",
            details={"provider": provider, "reason": reason}
        )


class AudioProcessingError(ConversationError):
    """Raised when audio processing fails."""
    
    def __init__(self, stage: str, reason:  str):
        super().__init__(
            message=f"Audio processing error at {stage}: {reason}",
            error_code="AUDIO_PROCESSING_ERROR",
            details={"stage": stage, "reason": reason}
        )


# =============================================================================
# Authentication Errors
# =============================================================================

class AuthError(AICompanionError):
    """Base exception for authentication errors."""
    pass


class InvalidCredentialsError(AuthError):
    """Raised when credentials are invalid."""
    
    def __init__(self):
        super().__init__(
            message="Invalid credentials",
            error_code="INVALID_CREDENTIALS"
        )


class TokenExpiredError(AuthError):
    """Raised when a JWT token has expired."""
    
    def __init__(self):
        super().__init__(
            message="Token has expired",
            error_code="TOKEN_EXPIRED"
        )
```

### 6.3 Persona Manager

```python name=core/persona/manager. py
"""
Persona Manager - Handles loading, switching, and managing personas.
"""

import asyncio
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
import yaml
import json

from pydantic import BaseModel, Field
from redis import asyncio as aioredis

from core.config import settings
from core.exceptions import PersonaNotFoundError, PersonaLoadError, PersonaSwitchError
from core.persona.models import Persona, PersonaConfig, PersonaArtifacts


class PersonaManager:
    """
    Manages persona lifecycle including loading, caching, and switching. 
    
    Features:
    - Load personas from filesystem or database
    - Cache active personas in Redis for fast access
    - Hot-swap personas in < 2 seconds
    - Version tracking and rollback support
    """
    
    PERSONA_CACHE_PREFIX = "persona:"
    ACTIVE_PERSONA_PREFIX = "active_persona:"
    CACHE_TTL_SECONDS = 3600  # 1 hour
    
    def __init__(
        self,
        redis_client: aioredis.Redis,
        personas_dir: Path = Path("personas")
    ):
        self.redis = redis_client
        self.personas_dir = personas_dir
        self._persona_cache: Dict[str, Persona] = {}
    
    async def load_persona(self, persona_id:  str) -> Persona:
        """
        Load a persona by ID.  Checks cache first, then filesystem.
        
        Args:
            persona_id:  Unique identifier for the persona
            
        Returns:
            Loaded Persona object
            
        Raises: 
            PersonaNotFoundError: If persona doesn't exist
            PersonaLoadError: If persona fails to load
        """
        # Check local cache
        if persona_id in self._persona_cache:
            return self._persona_cache[persona_id]
        
        # Check Redis cache
        cached = await self.redis. get(f"{self.PERSONA_CACHE_PREFIX}{persona_id}")
        if cached: 
            persona = Persona.model_validate_json(cached)
            self._persona_cache[persona_id] = persona
            return persona
        
        # Load from filesystem
        persona_path = self.personas_dir / persona_id
        if not persona_path. exists():
            raise PersonaNotFoundError(persona_id)
        
        try:
            persona = await self._load_from_filesystem(persona_id, persona_path)
            
            # Cache in Redis
            await self.redis.setex(
                f"{self.PERSONA_CACHE_PREFIX}{persona_id}",
                self. CACHE_TTL_SECONDS,
                persona.model_dump_json()
            )
            
            # Cache locally
            self._persona_cache[persona_id] = persona
            
            return persona
            
        except Exception as e: 
            raise PersonaLoadError(persona_id, str(e))
    
    async def _load_from_filesystem(self, persona_id: str, persona_path: Path) -> Persona: 
        """Load persona artifacts from filesystem."""
        
        # Load config
        config_path = persona_path / "config.yaml"
        if not config_path.exists():
            raise PersonaLoadError(persona_id, "config. yaml not found")
        
        with open(config_path) as f:
            config_data = yaml.safe_load(f)
        config = PersonaConfig(**config_data)
        
        # Load system prompt
        prompt_path = persona_path / "system_prompt.md"
        if not prompt_path.exists():
            raise PersonaLoadError(persona_id, "system_prompt.md not found")
        
        system_prompt = prompt_path.read_text()
        
        # Load examples (optional)
        examples = []
        examples_path = persona_path / "examples"
        if examples_path.exists():
            for example_file in examples_path. glob("*.json"):
                with open(example_file) as f:
                    examples.extend(json.load(f))
        
        # Build artifacts
        artifacts = PersonaArtifacts(
            system_prompt=system_prompt,
            examples=examples,
            knowledge_docs=[]  # Load from knowledge/ if exists
        )
        
        return Persona(
            id=persona_id,
            config=config,
            artifacts=artifacts,
            loaded_at=datetime.utcnow()
        )
    
    async def switch_persona(
        self,
        device_id: str,
        from_persona_id: Optional[str],
        to_persona_id: str
    ) -> Persona:
        """
        Switch a device to a new persona.
        
        Args:
            device_id: Device making the switch
            from_persona_id:  Current persona (for context preservation)
            to_persona_id: Target persona
            
        Returns: 
            The newly activated Persona
            
        Raises: 
            PersonaSwitchError: If switch fails
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Load target persona
            new_persona = await self.load_persona(to_persona_id)
            
            # Update active persona for device
            await self.redis.set(
                f"{self.ACTIVE_PERSONA_PREFIX}{device_id}",
                to_persona_id
            )
            
            # Log switch time
            switch_time = asyncio.get_event_loop().time() - start_time
            if switch_time > 2. 0:
                # Log warning if switch takes > 2 seconds
                pass  # TODO: Add logging
            
            return new_persona
            
        except PersonaNotFoundError: 
            raise PersonaSwitchError(
                from_persona=from_persona_id or "none",
                to_persona=to_persona_id,
                reason="Target persona not found"
            )
        except Exception as e: 
            raise PersonaSwitchError(
                from_persona=from_persona_id or "none",
                to_persona=to_persona_id,
                reason=str(e)
            )
    
    async def get_active_persona(self, device_id: str) -> Optional[Persona]:
        """Get the currently active persona for a device."""
        persona_id = await self.redis.get(f"{self. ACTIVE_PERSONA_PREFIX}{device_id}")
        if persona_id: 
            return await self. load_persona(persona_id. decode())
        return None
    
    async def list_personas(self) -> List[str]:
        """List all available persona IDs."""
        personas = []
        for path in self.personas_dir.iterdir():
            if path.is_dir() and (path / "config. yaml").exists():
                personas.append(path.name)
        return sorted(personas)
    
    async def invalidate_cache(self, persona_id: str) -> None:
        """Invalidate cached persona (e.g., after update)."""
        await self.redis.delete(f"{self. PERSONA_CACHE_PREFIX}{persona_id}")
        self._persona_cache. pop(persona_id, None)
```

### 6.4 Persona Models

```python name=core/persona/models.py
"""
Persona data models using Pydantic. 
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field


class AdaptationMode(str, Enum):
    """How the persona adapts its behavior."""
    INSTRUCTION_ONLY = "instruction_only"
    INSTRUCTION_RAG = "instruction_rag"
    FINE_TUNED = "fine_tuned"


class TriggerType(str, Enum):
    """What triggers persona activation."""
    SCHEDULE = "schedule"
    BUTTON = "button"
    VOICE_COMMAND = "voice_command"
    MANUAL = "manual"
    EVENT = "event"


class VoiceConfig(BaseModel):
    """Voice synthesis configuration."""
    provider: str = "elevenlabs"
    voice_id: str
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    pitch: float = Field(default=1.0, ge=0.5, le=2.0)
    stability: float = Field(default=0.5, ge=0.0, le=1.0)
    similarity_boost: float = Field(default=0.75, ge=0.0, le=1.0)


class PersonaConfig(BaseModel):
    """Configuration for a persona."""
    
    # Identity
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    version: str = Field(default="1.0. 0")
    
    # Behavior
    adaptation_mode: AdaptationMode = AdaptationMode. INSTRUCTION_ONLY
    trigger_types: List[TriggerType] = [TriggerType. MANUAL]
    context_retention_hours: int = Field(default=24, ge=1, le=168)
    
    # Voice
    voice:  VoiceConfig
    
    # Constraints
    max_response_tokens: int = Field(default=500, ge=50, le=4000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    
    # Scheduling (if trigger is SCHEDULE)
    schedule_cron: Optional[str] = None
    
    # Tags for categorization
    tags:  List[str] = []


class DialogExample(BaseModel):
    """Example dialog for persona training/testing."""
    user_message: str
    assistant_response:  str
    context: Optional[str] = None


class PersonaArtifacts(BaseModel):
    """All artifacts that define a persona's behavior."""
    system_prompt: str
    examples: List[DialogExample] = []
    knowledge_docs: List[str] = []  # For RAG mode
    tone_rules: Dict[str, Any] = {}
    behavior_constraints: Dict[str, Any] = {}


class Persona(BaseModel):
    """Complete persona definition."""
    id: str = Field(..., pattern=r"^[a-z0-9_-]+$")
    config: PersonaConfig
    artifacts: PersonaArtifacts
    loaded_at:  datetime
    
    # Optional:  fine-tuned model reference
    model_reference: Optional[str] = None
    
    def get_full_system_prompt(self) -> str:
        """Build the complete system prompt including examples."""
        prompt = self.artifacts.system_prompt
        
        if self.artifacts.examples:
            prompt += "\n\n## Example Interactions\n"
            for i, ex in enumerate(self. artifacts.examples[: 3], 1):
                prompt += f"\n### Example {i}\n"
                prompt += f"User: {ex.user_message}\n"
                prompt += f"Assistant: {ex.assistant_response}\n"
        
        return prompt


class PersonaSummary(BaseModel):
    """Lightweight persona info for listings."""
    id: str
    name:  str
    description:  str
    version:  str
    tags: List[str]
    adaptation_mode: AdaptationMode
```

### 6.5 Conversation Engine

```python name=core/conversation/engine.py
"""
Conversation Engine - Handles dialog generation using LLM APIs.
"""

import asyncio
from typing import Optional, List, AsyncGenerator
from datetime import datetime

from anthropic import AsyncAnthropic
from pydantic import BaseModel

from core.config import settings
from core. exceptions import LLMAPIError
from core.persona. models import Persona
from core.session. models import ConversationMessage, MessageRole
from core.conversation.models import ConversationContext, GenerationConfig


class ConversationEngine: 
    """
    Handles conversation generation using Claude API.
    
    Features:
    - Persona-aware prompting
    - Context window management
    - Streaming responses
    - Fallback handling
    """
    
    MAX_CONTEXT_MESSAGES = 20
    MAX_CONTEXT_TOKENS = 8000
    
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model
    
    async def generate_response(
        self,
        persona: Persona,
        user_message: str,
        context: ConversationContext,
        config: Optional[GenerationConfig] = None
    ) -> str:
        """
        Generate a response for the given message.
        
        Args:
            persona: Active persona for this conversation
            user_message:  User's input message
            context:  Conversation history and state
            config: Optional generation parameters
            
        Returns:
            Generated response text
            
        Raises:
            LLMAPIError:  If API call fails
        """
        config = config or GenerationConfig()
        
        # Build messages array
        messages = self._build_messages(user_message, context)
        
        try:
            response = await self.client. messages.create(
                model=self.model,
                max_tokens=config. max_tokens or persona.config.max_response_tokens,
                temperature=config.temperature or persona.config.temperature,
                system=persona.get_full_system_prompt(),
                messages=messages
            )
            
            return response.content[0].text
            
        except Exception as e:
            raise LLMAPIError(provider="anthropic", reason=str(e))
    
    async def generate_response_stream(
        self,
        persona: Persona,
        user_message:  str,
        context: ConversationContext,
        config:  Optional[GenerationConfig] = None
    ) -> AsyncGenerator[str, None]: 
        """
        Stream a response token by token.
        
        Yields:
            Response tokens as they're generated
        """
        config = config or GenerationConfig()
        messages = self._build_messages(user_message, context)
        
        try: 
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=config.max_tokens or persona.config. max_response_tokens,
                temperature=config.temperature or persona.config.temperature,
                system=persona.get_full_system_prompt(),
                messages=messages
            ) as stream:
                async for text in stream.text_stream: 
                    yield text
                    
        except Exception as e:
            raise LLMAPIError(provider="anthropic", reason=str(e))
    
    def _build_messages(
        self,
        user_message: str,
        context:  ConversationContext
    ) -> List[dict]:
        """Build the messages array for the API call."""
        messages = []
        
        # Add conversation history
        for msg in context.messages[-self.MAX_CONTEXT_MESSAGES: ]:
            messages. append({
                "role": msg.role.value,
                "content":  msg.content
            })
        
        # Add current message
        messages. append({
            "role": "user",
            "content": user_message
        })
        
        return messages
    
    async def estimate_tokens(self, text:  str) -> int:
        """Estimate token count for text."""
        # Rough estimation:  ~4 chars per token for English
        return len(text) // 4


class GenerationConfig(BaseModel):
    """Configuration for response generation."""
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    stop_sequences: List[str] = []
```

### 6.6 Session Manager

```python name=core/session/manager.py
"""
Session Manager - Handles conversation state and context. 
"""

import json
from typing import Optional, List
from datetime import datetime, timedelta
from uuid import uuid4

from redis import asyncio as aioredis

from core.config import settings
from core. exceptions import SessionNotFoundError, SessionExpiredError
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
            state=SessionState. ACTIVE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            expires_at=datetime. utcnow() + timedelta(hours=self.DEFAULT_TTL_HOURS),
            messages=[],
            metadata={}
        )
        
        # Store session
        await self._save_session(session)
        
        # Link device to session
        await self. redis.set(
            f"{self.DEVICE_SESSION_PREFIX}{device_id}",
            session.id
        )
        
        return session
    
    async def get_session(self, session_id: str) -> Session:
        """
        Retrieve a session by ID.
        
        Raises:
            SessionNotFoundError: If session doesn't exist
            SessionExpiredError:  If session has expired
        """
        data = await self.redis.get(f"{self.SESSION_PREFIX}{session_id}")
        
        if not data:
            raise SessionNotFoundError(session_id)
        
        session = Session.model_validate_json(data)
        
        if session.expires_at < datetime. utcnow():
            await self. end_session(session_id)
            raise SessionExpiredError(session_id)
        
        return session
    
    async def get_device_session(self, device_id: str) -> Optional[Session]:
        """Get the active session for a device."""
        session_id = await self.redis.get(f"{self. DEVICE_SESSION_PREFIX}{device_id}")
        
        if not session_id: 
            return None
        
        try:
            return await self.get_session(session_id. decode())
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
            persona_id=session. persona_id
        )
        
        session.messages. append(message)
        session.updated_at = datetime.utcnow()
        
        await self._save_session(session)
        
        return message
    
    async def update_persona(
        self,
        session_id: str,
        new_persona_id:  str,
        preserve_context: bool = True
    ) -> Session:
        """
        Update the session's active persona.
        
        Args:
            session_id: Session to update
            new_persona_id:  New persona ID
            preserve_context: Whether to keep message history
            
        Returns:
            Updated session
        """
        session = await self. get_session(session_id)
        
        session.persona_id = new_persona_id
        session.updated_at = datetime. utcnow()
        
        if not preserve_context: 
            session.messages = []
        
        await self._save_session(session)
        
        return session
    
    async def handoff_session(
        self,
        session_id: str,
        from_device_id:  str,
        to_device_id:  str
    ) -> Session:
        """
        Hand off a session from one device to another. 
        
        This enables "continue conversation in another room" scenarios.
        """
        session = await self.get_session(session_id)
        
        # Remove from old device
        await self.redis.delete(f"{self. DEVICE_SESSION_PREFIX}{from_device_id}")
        
        # Update session
        session.device_id = to_device_id
        session.updated_at = datetime.utcnow()
        session.metadata["handoff_history"] = session.metadata.get("handoff_history", [])
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
    
    async def end_session(