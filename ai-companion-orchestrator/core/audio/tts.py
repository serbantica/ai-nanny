"""
Text-to-Speech client implementations.
"""
from typing import Protocol
from core.audio.models import TTSResult
from core.config import settings

class TTSClient(Protocol):
    async def synthesize(self, text: str, voice_id: str) -> TTSResult: ...

class MockTTSClient:
    async def synthesize(self, text: str, voice_id: str) -> TTSResult:
        # Return mock silence or sine wave
        return TTSResult(
            audio_data=b"mock_audio_bytes",
            duration_seconds=len(text) * 0.1
        )

class ElevenLabsClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Initialize ElevenLabs client
        
    async def synthesize(self, text: str, voice_id: str) -> TTSResult:
        # Placeholder for real ElevenLabs API call
        return TTSResult(
            audio_data=b"real_audio_bytes_from_elevenlabs",
            duration_seconds=3.0
        )
