"""
Conversation data models.
"""
from typing import List, Optional
from pydantic import BaseModel
from core.session.models import ConversationMessage

class ConversationContext(BaseModel):
    """Context for generating a response."""
    messages: List[ConversationMessage]
    # Future: Add relevant documents, user memories, etc.

class GenerationConfig(BaseModel):
    """Configuration for response generation."""
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    stop_sequences: List[str] = []
