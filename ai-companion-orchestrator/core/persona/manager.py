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
try:
    from redis import asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    aioredis = None

from core.config import settings
from core.exceptions import PersonaNotFoundError, PersonaLoadError, PersonaSwitchError
from core.persona.models import Persona, PersonaConfig, PersonaArtifacts


class PersonaManager:
    """
    Manages persona lifecycle including loading, caching, and switching. 
    
    Features:
    - Load personas from filesystem or database
    - Cache active personas in Redis (if available) or memory
    - Hot-swap personas in < 2 seconds
    - Version tracking and rollback support
    """
    
    PERSONA_CACHE_PREFIX = "persona:"
    ACTIVE_PERSONA_PREFIX = "active_persona:"
    CACHE_TTL_SECONDS = 3600  # 1 hour
    
    def __init__(
        self,
        redis_client = None,
        personas_dir: Path = Path("personas")
    ):
        self.redis = redis_client
        self.use_redis = redis_client is not None and REDIS_AVAILABLE
        self.personas_dir = personas_dir
        self._persona_cache: Dict[str, Persona] = {}
        # In-memory fallback storage
        self._memory_cache: Dict[str, str] = {}
        self._active_personas: Dict[str, str] = {}
    
    async def load_persona(self, persona_id: str) -> Persona:
        """
        Load a persona by ID. Checks cache first, then filesystem.
        
        Args:
            persona_id: Unique identifier for the persona
            
        Returns:
            Loaded Persona object
            
        Raises: 
            PersonaNotFoundError: If persona doesn't exist
            PersonaLoadError: If persona fails to load
        """
        # Check local cache
        if persona_id in self._persona_cache:
            return self._persona_cache[persona_id]
        
        # Check Redis cache (if available)
        if self.use_redis:
            try:
                cached = await self.redis.get(f"{self.PERSONA_CACHE_PREFIX}{persona_id}")
                if cached: 
                    persona = Persona.model_validate_json(cached)
                    self._persona_cache[persona_id] = persona
                    return persona
            except Exception:
                pass  # Fall back to filesystem
        else:
            # Check memory cache
            if f"{self.PERSONA_CACHE_PREFIX}{persona_id}" in self._memory_cache:
                persona = Persona.model_validate_json(self._memory_cache[f"{self.PERSONA_CACHE_PREFIX}{persona_id}"])
                self._persona_cache[persona_id] = persona
                return persona
        
        # Load from filesystem
        persona_path = self.personas_dir / persona_id
        if not persona_path.exists():
            raise PersonaNotFoundError(persona_id)
        
        try:
            persona = await self._load_from_filesystem(persona_id, persona_path)
            return persona
            
        except Exception as e: 
            raise PersonaLoadError(persona_id, str(e))
    
    async def _load_from_filesystem(self, persona_id: str, persona_path: Path) -> Persona: 
        """Load persona artifacts from filesystem."""
        
        # Load config
        config_path = persona_path / "config.yaml"
        if not config_path.exists():
            raise PersonaLoadError(persona_id, "config.yaml not found")
        
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
            for example_file in examples_path.glob("*.json"):
                with open(example_file) as f:
                    examples.extend(json.load(f))
        
        # Build artifacts
        artifacts = PersonaArtifacts(
            system_prompt=system_prompt,
            examples=examples,
            knowledge_docs=[]  # Load from knowledge/ if exists
        )
        
        persona = Persona(
            id=persona_id,
            config=config,
            artifacts=artifacts,
            loaded_at=datetime.utcnow()
        )
        
        # Cache in Redis or memory
        if self.use_redis:
            try:
                await self.redis.setex(
                    f"{self.PERSONA_CACHE_PREFIX}{persona_id}",
                    self.CACHE_TTL_SECONDS,
                    persona.model_dump_json()
                )
            except Exception:
                pass  # Continue without cache
        else:
            # Store in memory
            self._memory_cache[f"{self.PERSONA_CACHE_PREFIX}{persona_id}"] = persona.model_dump_json()
        
        # Also cache locally
        self._persona_cache[persona_id] = persona
        
        return persona
    
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
            from_persona_id: Current persona (for context preservation)
            to_persona_id: Target persona
            
        Returns: 
            The newly activated Persona
            
        Raises: 
            PersonaSwitchError: If switch fails
        """
        try:
            # Load target persona
            new_persona = await self.load_persona(to_persona_id)
            
            # Update active persona for device
            if self.use_redis:
                try:
                    await self.redis.set(
                        f"{self.ACTIVE_PERSONA_PREFIX}{device_id}",
                        to_persona_id
                    )
                except Exception:
                    pass  # Continue without Redis
            else:
                # Store in memory
                self._active_personas[device_id] = to_persona_id
            
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
        persona_id = None
        
        if self.use_redis:
            try:
                persona_id = await self.redis.get(f"{self.ACTIVE_PERSONA_PREFIX}{device_id}")
                if persona_id:
                    persona_id = persona_id.decode() if isinstance(persona_id, bytes) else persona_id
            except Exception:
                pass
        else:
            # Get from memory
            persona_id = self._active_personas.get(device_id)
        
        if persona_id: 
            return await self.load_persona(persona_id)
        return None
    
    async def list_personas(self) -> List[str]:
        """List all available persona IDs."""
        personas = []
        if self.personas_dir.exists():
            for path in self.personas_dir.iterdir():
                if path.is_dir() and (path / "config.yaml").exists():
                    personas.append(path.name)
        return sorted(personas)
    
    async def invalidate_cache(self, persona_id: str) -> None:
        """Invalidate cached persona (e.g., after update)."""
        if self.use_redis:
            try:
                await self.redis.delete(f"{self.PERSONA_CACHE_PREFIX}{persona_id}")
            except Exception:
                pass
        else:
            # Remove from memory
            self._memory_cache.pop(f"{self.PERSONA_CACHE_PREFIX}{persona_id}", None)
        
        self._persona_cache.pop(persona_id, None)
