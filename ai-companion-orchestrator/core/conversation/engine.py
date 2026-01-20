"""
Conversation Engine - Handles dialog generation using LLM APIs.
Supports both Ollama (local) and Anthropic Claude (cloud).
"""

import asyncio
import httpx
from typing import Optional, List, AsyncGenerator
from datetime import datetime

from pydantic import BaseModel

from core.config import settings
from core.exceptions import LLMAPIError
from core.persona.models import Persona
from core.session.models import ConversationMessage, MessageRole
from core.conversation.models import ConversationContext, GenerationConfig


class ConversationEngine: 
    """
    Handles conversation generation using Ollama or Claude API.
    
    Features:
    - Multi-provider support (Ollama, Anthropic)
    - Persona-aware prompting
    - Context window management
    - Streaming responses
    - Fallback handling
    """
    
    MAX_CONTEXT_MESSAGES = 20
    MAX_CONTEXT_TOKENS = 8000
    
    def __init__(self):
        self.provider = settings.llm_provider
        
        # Initialize based on provider
        if self.provider == "ollama":
            self.base_url = settings.ollama_base_url
            self.model = settings.ollama_model
            self.client = None  # Use httpx for Ollama
        elif self.provider == "anthropic":
            from anthropic import AsyncAnthropic
            if not settings.anthropic_api_key:
                raise ValueError("Anthropic API key not configured")
            self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
            self.model = settings.anthropic_model
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")
    
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
            user_message: User's input message
            context: Conversation history and state
            config: Optional generation parameters
            
        Returns:
            Generated response text
            
        Raises:
            LLMAPIError: If API call fails
        """
        config = config or GenerationConfig()
        
        if self.provider == "ollama":
            return await self._generate_ollama(persona, user_message, context, config)
        elif self.provider == "anthropic":
            return await self._generate_anthropic(persona, user_message, context, config)
    
    async def _generate_ollama(
        self,
        persona: Persona,
        user_message: str,
        context: ConversationContext,
        config: GenerationConfig
    ) -> str:
        """Generate response using Ollama."""
        try:
            # Build messages for Ollama
            messages = []
            
            # Add system message
            messages.append({
                "role": "system",
                "content": persona.get_full_system_prompt()
            })
            
            # Add conversation history
            for msg in context.messages[-self.MAX_CONTEXT_MESSAGES:]:
                messages.append({
                    "role": msg.role.value,
                    "content": msg.content
                })
            
            # Add current message
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Call Ollama API
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False,
                        "options": {
                            "temperature": config.temperature or persona.config.temperature or 0.7,
                            "num_predict": config.max_tokens or persona.config.max_response_tokens or 500
                        }
                    }
                )
                
                if response.status_code != 200:
                    raise LLMAPIError(
                        provider="ollama",
                        reason=f"Status {response.status_code}: {response.text}"
                    )
                
                result = response.json()
                return result["message"]["content"]
                
        except httpx.HTTPError as e:
            raise LLMAPIError(provider="ollama", reason=f"HTTP error: {str(e)}")
        except Exception as e:
            raise LLMAPIError(provider="ollama", reason=str(e))
    
    async def _generate_anthropic(
        self,
        persona: Persona,
        user_message: str,
        context: ConversationContext,
        config: GenerationConfig
    ) -> str:
        """Generate response using Anthropic Claude."""
        messages = self._build_messages(user_message, context)
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=config.max_tokens or persona.config.max_response_tokens,
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
        user_message: str,
        context: ConversationContext,
        config: Optional[GenerationConfig] = None
    ) -> AsyncGenerator[str, None]: 
        """
        Stream a response token by token.
        
        Yields:
            Response tokens as they're generated
        """
        config = config or GenerationConfig()
        
        if self.provider == "ollama":
            async for token in self._generate_ollama_stream(persona, user_message, context, config):
                yield token
        elif self.provider == "anthropic":
            async for token in self._generate_anthropic_stream(persona, user_message, context, config):
                yield token
    
    async def _generate_ollama_stream(
        self,
        persona: Persona,
        user_message: str,
        context: ConversationContext,
        config: GenerationConfig
    ) -> AsyncGenerator[str, None]:
        """Stream response from Ollama."""
        try:
            messages = []
            messages.append({
                "role": "system",
                "content": persona.get_full_system_prompt()
            })
            
            for msg in context.messages[-self.MAX_CONTEXT_MESSAGES:]:
                messages.append({
                    "role": msg.role.value,
                    "content": msg.content
                })
            
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": True,
                        "options": {
                            "temperature": config.temperature or persona.config.temperature or 0.7
                        }
                    }
                ) as response:
                    async for line in response.aiter_lines():
                        if line:
                            import json
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                yield data["message"]["content"]
                                
        except Exception as e:
            raise LLMAPIError(provider="ollama", reason=str(e))
    
    async def _generate_anthropic_stream(
        self,
        persona: Persona,
        user_message: str,
        context: ConversationContext,
        config: GenerationConfig
    ) -> AsyncGenerator[str, None]:
        """Stream response from Anthropic."""
        messages = self._build_messages(user_message, context)
        
        try: 
            from anthropic import AsyncAnthropic
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=config.max_tokens or persona.config.max_response_tokens,
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
        context: ConversationContext
    ) -> List[dict]:
        """Build the messages array for the API call."""
        messages = []
        
        # Add conversation history
        for msg in context.messages[-self.MAX_CONTEXT_MESSAGES:]:
            messages.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages
    
    async def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        # Rough estimation: ~4 chars per token for English
        return len(text) // 4
