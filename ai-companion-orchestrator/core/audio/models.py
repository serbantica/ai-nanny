"""
Audio processing data models.
"""
from enum import Enum
from pydantic import BaseModel
from typing import Optional

class STTProvider(str, Enum):
    OPENAI = "openai"
    DEEPGRAM = "deepgram"
    MOCK = "mock"

class TTSProvider(str, Enum):
    ELEVENLABS = "elevenlabs"
    OPENAI = "openai"
    GOOGLE = "google"
    MOCK = "mock"

class AudioConfig(BaseModel):
    stt_provider: STTProvider = STTProvider.MOCK
    tts_provider: TTSProvider = TTSProvider.MOCK
    sample_rate: int = 16000
    channels: int = 1

class STTResult(BaseModel):
    text: str
    confidence: float
    language: str
    duration_seconds: float

class TTSResult(BaseModel):
    audio_data: bytes
    format: str = "mp3"
    duration_seconds: float
