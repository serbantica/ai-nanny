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
    version: str = Field(default="1.0.0")
    
    # Behavior
    adaptation_mode: AdaptationMode = AdaptationMode.INSTRUCTION_ONLY
    trigger_types: List[TriggerType] = [TriggerType.MANUAL]
    context_retention_hours: int = Field(default=24, ge=1, le=168)
    
    # Voice
    voice: VoiceConfig
    
    # Constraints
    max_response_tokens: int = Field(default=500, ge=50, le=4000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    
    # Scheduling (if trigger is SCHEDULE)
    schedule_cron: Optional[str] = None
    
    # Tags for categorization
    tags: List[str] = []


class DialogExample(BaseModel):
    """Example dialog for persona training/testing."""
    user_message: str
    assistant_response: str
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
    loaded_at: datetime
    
    # Optional: fine-tuned model reference
    model_reference: Optional[str] = None
    
    def get_full_system_prompt(self) -> str:
        """Build the complete system prompt including examples."""
        prompt = self.artifacts.system_prompt
        
        if self.artifacts.examples:
            prompt += "\n\n## Example Interactions\n"
            for i, ex in enumerate(self.artifacts.examples[:3], 1):
                prompt += f"\n### Example {i}\n"
                prompt += f"User: {ex.user_message}\n"
                prompt += f"Assistant: {ex.assistant_response}\n"
        
        return prompt


class PersonaSummary(BaseModel):
    """Lightweight persona info for listings."""
    id: str
    name: str
    description: str
    version: str
    tags: List[str]
    adaptation_mode: AdaptationMode
