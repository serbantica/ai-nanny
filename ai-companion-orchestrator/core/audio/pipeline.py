"""
Audio Pipeline orchestrator.
"""
from core.audio.models import AudioConfig, STTProvider, TTSProvider, STTResult, TTSResult
from core.audio.stt import STTClient, MockSTTClient, OpenAIWhisperClient
from core.audio.tts import TTSClient, MockTTSClient, ElevenLabsClient
from core.config import settings

class AudioPipeline:
    """
    Manages the conversion of audio <-> text.
    """
    def __init__(self, config: AudioConfig):
        self.config = config
        self.stt_client = self._get_stt_client(config.stt_provider)
        self.tts_client = self._get_tts_client(config.tts_provider)

    def _get_stt_client(self, provider: STTProvider) -> STTClient:
        if provider == STTProvider.OPENAI:
            return OpenAIWhisperClient(settings.openai_api_key)
        return MockSTTClient()

    def _get_tts_client(self, provider: TTSProvider) -> TTSClient:
        if provider == TTSProvider.ELEVENLABS:
            return ElevenLabsClient(settings.elevenlabs_api_key)
        return MockTTSClient()

    async def process_input(self, audio_data: bytes) -> STTResult:
        """Convert incoming audio to text."""
        return await self.stt_client.transcribe(audio_data)

    async def process_output(self, text: str, voice_id: str) -> TTSResult:
        """Convert response text to speech."""
        return await self.tts_client.synthesize(text, voice_id)
