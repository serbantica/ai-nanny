"""
Speech-to-Text client implementations.
"""
from typing import Protocol
from core.audio.models import STTResult
from core.config import settings

class STTClient(Protocol):
    async def transcribe(self, audio_data: bytes) -> STTResult: ...

class MockSTTClient:
    async def transcribe(self, audio_data: bytes) -> STTResult:
        # Simulate processing time
        return STTResult(
            text="Hello there, I am testing the system.",
            confidence=0.99,
            language="en",
            duration_seconds=2.5
        )

class OpenAIWhisperClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Initialize OpenAI client here
        
    async def transcribe(self, audio_data: bytes) -> STTResult:
        # Placeholder for real OpenAI Whisper API call
        # In a real impl, we'd use 'openai' package
        return STTResult(
            text="This is a real transcription from Whisper.",
            confidence=0.95,
            language="en",
            duration_seconds=3.0
        )
