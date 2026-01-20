"""
Conversation Router - Handles conversation generation endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
import logging
from datetime import datetime

from core.conversation.engine import ConversationEngine
from core.conversation.models import ConversationContext
from core.persona.manager import PersonaManager
from core.session.manager import SessionManager
from core.config import settings
from api.dependencies import get_redis

logger = logging.getLogger(__name__)

router = APIRouter()  # Prefix is added in main.py


class ConversationRequest(BaseModel):
    """Request model for conversation generation"""
    device_id: str = Field(..., description="Device identifier")
    user_message: str = Field(..., min_length=1, description="User's input message")
    persona_id: str = Field(..., description="Persona to use (companion, activity, emergency, etc.)")
    session_id: Optional[str] = Field(None, description="Optional session ID for context")


class ConversationResponse(BaseModel):
    """Response model for conversation generation"""
    response: str = Field(..., description="Generated response text")
    session_id: str = Field(..., description="Session ID for context tracking")
    persona_id: str = Field(..., description="Persona used")
    timestamp: str = Field(..., description="Response timestamp")
    tokens_used: Optional[int] = Field(None, description="Tokens used in generation")


# Global instances (initialized on startup)
_conversation_engine: Optional[ConversationEngine] = None
_persona_manager: Optional[PersonaManager] = None
_session_manager: Optional[SessionManager] = None


async def get_conversation_engine():
    """Dependency to get conversation engine"""
    global _conversation_engine
    if _conversation_engine is None:
        _conversation_engine = ConversationEngine()
    return _conversation_engine


async def get_persona_manager():
    """Dependency to get persona manager"""
    global _persona_manager
    if _persona_manager is None:
        async for redis_client in get_redis():
            _persona_manager = PersonaManager(redis_client=redis_client)
            break
    return _persona_manager


async def get_session_manager():
    """Dependency to get session manager"""
    global _session_manager
    if _session_manager is None:
        async for redis_client in get_redis():
            _session_manager = SessionManager(redis_client=redis_client)
            break
    return _session_manager


@router.post("/generate", response_model=ConversationResponse)
async def generate_conversation(
    request: ConversationRequest,
    engine: ConversationEngine = Depends(get_conversation_engine),
    persona_mgr: PersonaManager = Depends(get_persona_manager),
    session_mgr: SessionManager = Depends(get_session_manager)
):
    """
    Generate a conversation response using the specified persona.
    
    This endpoint:
    1. Loads the requested persona with its system prompt
    2. Retrieves or creates a session for context
    3. Generates a response using Claude API
    4. Updates session history
    
    Returns persona-aware responses based on the loaded system prompt.
    """
    try:
        # Load persona
        try:
            persona = await persona_mgr.load_persona(request.persona_id)
            logger.info(f"Loaded persona: {persona.config.name}")
        except Exception as e:
            logger.error(f"Failed to load persona '{request.persona_id}': {e}")
            raise HTTPException(
                status_code=404,
                detail=f"Persona '{request.persona_id}' not found"
            )
        
        # Get or create session
        if request.session_id:
            try:
                session = await session_mgr.get_session(request.session_id)
            except:
                logger.warning(f"Session {request.session_id} not found, creating new one")
                session = await session_mgr.create_session(
                    device_id=request.device_id,
                    persona_id=request.persona_id
                )
        else:
            session = await session_mgr.create_session(
                device_id=request.device_id,
                persona_id=request.persona_id
            )
        
        # Build conversation context from session
        context = ConversationContext(
            messages=session.messages,
            device_id=request.device_id,
            user_preferences={}
        )
        
        # Generate response
        logger.info(f"Generating response for: {request.user_message[:50]}...")
        response_text = await engine.generate_response(
            persona=persona,
            user_message=request.user_message,
            context=context
        )
        
        # Update session with new messages
        await session_mgr.add_message(
            session_id=session.id,
            role="user",
            content=request.user_message
        )
        await session_mgr.add_message(
            session_id=session.id,
            role="assistant",
            content=response_text
        )
        
        logger.info(f"Response generated successfully: {response_text[:50]}...")
        
        return ConversationResponse(
            response=response_text,
            session_id=session.id,
            persona_id=request.persona_id,
            timestamp=datetime.utcnow().isoformat(),
            tokens_used=None  # TODO: Extract from API response
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating conversation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate response: {str(e)}"
        )


@router.get("/personas")
async def list_available_personas(
    persona_mgr: PersonaManager = Depends(get_persona_manager)
):
    """List all available personas"""
    try:
        # Get personas from filesystem
        personas_dir = persona_mgr.personas_dir
        personas = []
        
        if personas_dir.exists():
            for persona_path in personas_dir.iterdir():
                if persona_path.is_dir():
                    personas.append({
                        "id": persona_path.name,
                        "name": persona_path.name.replace("_", " ").title()
                    })
        
        return {"personas": personas}
    
    except Exception as e:
        logger.error(f"Error listing personas: {e}")
        raise HTTPException(status_code=500, detail=str(e))
