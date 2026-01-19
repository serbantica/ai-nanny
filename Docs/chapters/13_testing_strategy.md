## 13. Testing Strategy - Full Implementation

### 13.1 Testing Overview

The platform uses a comprehensive testing strategy covering unit, integration, and end-to-end tests.

### 13.2 Test Categories

| Category | Scope | Tools | Coverage Target |
|----------|-------|-------|-----------------|
| Unit | Individual functions/classes | pytest | 80% |
| Integration | Module interactions | pytest-asyncio | 70% |
| E2E | Full system flows | pytest + httpx | Critical paths |
| Performance | Latency, throughput | locust | SLA compliance |
| Hardware | Device agent | Mock GPIO | Device flows |

### 13.3 Unit Tests

#### Persona Manager Tests

```python
# tests/unit/test_persona_manager.py
"""Unit tests for PersonaManager."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
from datetime import datetime

from core.persona.manager import PersonaManager
from core.persona.models import Persona, PersonaConfig, PersonaArtifacts, VoiceConfig
from core.exceptions import PersonaNotFoundError, PersonaLoadError


@pytest.fixture
def mock_redis():
    """Create mock Redis client."""
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.setex = AsyncMock()
    redis.set = AsyncMock()
    redis.delete = AsyncMock()
    return redis


@pytest.fixture
def persona_manager(mock_redis, tmp_path):
    """Create PersonaManager with mock dependencies."""
    return PersonaManager(
        redis_client=mock_redis,
        personas_dir=tmp_path / "personas"
    )


@pytest.fixture
def sample_persona():
    """Create sample persona for testing."""
    return Persona(
        id="test_companion",
        config=PersonaConfig(
            name="Test Companion",
            description="A test persona",
            voice=VoiceConfig(voice_id="test_voice"),
            max_response_tokens=300,
            temperature=0.7
        ),
        artifacts=PersonaArtifacts(
            system_prompt="You are a test assistant."
        ),
        loaded_at=datetime.utcnow()
    )


class TestPersonaManager:
    """Tests for PersonaManager class."""
    
    @pytest.mark.asyncio
    async def test_load_persona_from_cache(
        self, persona_manager, mock_redis, sample_persona
    ):
        """Test loading persona from Redis cache."""
        # Setup: persona in Redis cache
        mock_redis.get.return_value = sample_persona.model_dump_json()
        
        # Act
        result = await persona_manager.load_persona("test_companion")
        
        # Assert
        assert result.id == "test_companion"
        assert result.config.name == "Test Companion"
        mock_redis.get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_load_persona_not_found(self, persona_manager, mock_redis):
        """Test PersonaNotFoundError when persona doesn't exist."""
        mock_redis.get.return_value = None
        
        with pytest.raises(PersonaNotFoundError) as exc_info:
            await persona_manager.load_persona("nonexistent")
        
        assert "nonexistent" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_switch_persona_success(
        self, persona_manager, mock_redis, sample_persona
    ):
        """Test successful persona switch."""
        mock_redis.get.return_value = sample_persona.model_dump_json()
        
        result = await persona_manager.switch_persona(
            device_id="dev_001",
            from_persona_id="old_persona",
            to_persona_id="test_companion"
        )
        
        assert result.id == "test_companion"
        mock_redis.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_invalidate_cache(self, persona_manager, mock_redis):
        """Test cache invalidation."""
        await persona_manager.invalidate_cache("test_persona")
        
        mock_redis.delete.assert_called_once()
```

#### Conversation Engine Tests

```python
# tests/unit/test_conversation_engine.py
"""Unit tests for ConversationEngine."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from core.conversation.engine import ConversationEngine, GenerationConfig
from core.conversation.models import ConversationContext
from core.persona.models import Persona, PersonaConfig, PersonaArtifacts, VoiceConfig
from core.session.models import ConversationMessage, MessageRole
from core.exceptions import LLMAPIError


@pytest.fixture
def mock_anthropic_client():
    """Create mock Anthropic client."""
    with patch('core.conversation.engine.AsyncAnthropic') as mock:
        client = AsyncMock()
        mock.return_value = client
        
        # Mock successful response
        response = MagicMock()
        response.content = [MagicMock(text="Hello! How can I help you today?")]
        client.messages.create = AsyncMock(return_value=response)
        
        yield client


@pytest.fixture
def conversation_engine(mock_anthropic_client):
    """Create ConversationEngine with mock client."""
    with patch('core.conversation.engine.settings') as mock_settings:
        mock_settings.anthropic_api_key = "test_key"
        mock_settings.anthropic_model = "claude-3-sonnet"
        return ConversationEngine()


@pytest.fixture
def sample_persona():
    """Create sample persona."""
    return Persona(
        id="companion",
        config=PersonaConfig(
            name="Companion",
            voice=VoiceConfig(voice_id="test"),
            max_response_tokens=300,
            temperature=0.7
        ),
        artifacts=PersonaArtifacts(
            system_prompt="You are a friendly companion."
        ),
        loaded_at=datetime.utcnow()
    )


@pytest.fixture
def sample_context():
    """Create sample conversation context."""
    return ConversationContext(
        messages=[
            ConversationMessage(
                id="msg_1",
                role=MessageRole.USER,
                content="Hello!",
                timestamp=datetime.utcnow(),
                persona_id="companion"
            )
        ]
    )


class TestConversationEngine:
    """Tests for ConversationEngine class."""
    
    @pytest.mark.asyncio
    async def test_generate_response_success(
        self, conversation_engine, sample_persona, sample_context
    ):
        """Test successful response generation."""
        result = await conversation_engine.generate_response(
            persona=sample_persona,
            user_message="How are you?",
            context=sample_context
        )
        
        assert result == "Hello! How can I help you today?"
    
    @pytest.mark.asyncio
    async def test_generate_response_with_config(
        self, conversation_engine, sample_persona, sample_context
    ):
        """Test response generation with custom config."""
        config = GenerationConfig(
            max_tokens=100,
            temperature=0.5
        )
        
        result = await conversation_engine.generate_response(
            persona=sample_persona,
            user_message="Tell me a short story",
            context=sample_context,
            config=config
        )
        
        assert isinstance(result, str)
    
    @pytest.mark.asyncio
    async def test_build_messages_includes_history(
        self, conversation_engine, sample_context
    ):
        """Test that message building includes conversation history."""
        messages = conversation_engine._build_messages(
            user_message="New message",
            context=sample_context
        )
        
        # Should include history + new message
        assert len(messages) == 2
        assert messages[-1]["content"] == "New message"
        assert messages[-1]["role"] == "user"
```

### 13.4 Integration Tests

#### API Integration Tests

```python
# tests/integration/test_api_devices.py
"""Integration tests for device API endpoints."""

import pytest
from httpx import AsyncClient
from datetime import datetime

from api.main import app
from db.session import get_db


@pytest.fixture
async def async_client():
    """Create async test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def auth_headers():
    """Create authorization headers with test token."""
    return {"Authorization": "Bearer test_token"}


class TestDeviceAPI:
    """Integration tests for device endpoints."""
    
    @pytest.mark.asyncio
    async def test_register_device(self, async_client, auth_headers):
        """Test device registration endpoint."""
        response = await async_client.post(
            "/api/v1/devices",
            json={
                "name": "test-device",
                "device_type": "raspberry_pi",
                "location": "Test Room",
                "capabilities": ["audio_input", "audio_output"]
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "device_id" in data
        assert "auth_token" in data
        assert "websocket_url" in data
    
    @pytest.mark.asyncio
    async def test_get_device_state(self, async_client, auth_headers):
        """Test getting device state."""
        # First register a device
        register_response = await async_client.post(
            "/api/v1/devices",
            json={"name": "test-device", "device_type": "raspberry_pi"},
            headers=auth_headers
        )
        device_id = register_response.json()["device_id"]
        
        # Get device state
        response = await async_client.get(
            f"/api/v1/devices/{device_id}/state",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["device_id"] == device_id
        assert "status" in data
    
    @pytest.mark.asyncio
    async def test_switch_persona(self, async_client, auth_headers):
        """Test persona switch endpoint."""
        # Register device first
        register_response = await async_client.post(
            "/api/v1/devices",
            json={"name": "test-device", "device_type": "raspberry_pi"},
            headers=auth_headers
        )
        device_id = register_response.json()["device_id"]
        
        # Switch persona
        response = await async_client.post(
            f"/api/v1/devices/{device_id}/persona/switch",
            json={
                "target_persona_id": "companion",
                "preserve_context": True
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["new_persona_id"] == "companion"
```

### 13.5 End-to-End Tests

```python
# tests/e2e/test_persona_switch.py
"""End-to-end tests for persona switching flow."""

import pytest
import asyncio
from datetime import datetime

from tests.fixtures import create_test_device, create_test_session


class TestPersonaSwitchE2E:
    """E2E tests for complete persona switch flow."""
    
    @pytest.mark.asyncio
    async def test_full_persona_switch_flow(self, test_environment):
        """
        Test complete persona switch:
        1. Device registers
        2. Session starts with persona A
        3. Persona switches to B
        4. Context is preserved
        5. New response uses persona B behavior
        """
        # Setup
        device = await create_test_device(test_environment)
        session = await create_test_session(
            device_id=device.id,
            persona_id="companion"
        )
        
        # Send initial message
        response1 = await test_environment.dialog.send(
            device_id=device.id,
            session_id=session.id,
            message="Hello, how are you?"
        )
        assert "companion" in response1.persona_id
        
        # Switch persona
        switch_result = await test_environment.persona.switch(
            device_id=device.id,
            from_persona="companion",
            to_persona="medication_nurse"
        )
        
        # Verify switch completed within SLA
        assert switch_result.switch_latency_ms < 2000
        
        # Send message with new persona
        response2 = await test_environment.dialog.send(
            device_id=device.id,
            session_id=session.id,
            message="What should I do now?"
        )
        
        # Verify new persona is active
        assert response2.persona_id == "medication_nurse"
    
    @pytest.mark.asyncio
    async def test_persona_switch_latency_sla(self, test_environment):
        """Test that persona switch meets < 2 second SLA."""
        device = await create_test_device(test_environment)
        
        # Perform multiple switches and measure
        latencies = []
        personas = ["companion", "medication_nurse", "storyteller", "entertainer"]
        
        for i in range(len(personas) - 1):
            start = datetime.utcnow()
            await test_environment.persona.switch(
                device_id=device.id,
                from_persona=personas[i],
                to_persona=personas[i + 1]
            )
            latency = (datetime.utcnow() - start).total_seconds() * 1000
            latencies.append(latency)
        
        # All switches should be under 2 seconds
        assert all(l < 2000 for l in latencies)
        
        # Average should be well under 2 seconds
        avg_latency = sum(latencies) / len(latencies)
        assert avg_latency < 1500
```

### 13.6 Performance Tests

```python
# tests/performance/locustfile.py
"""Performance tests using Locust."""

from locust import HttpUser, task, between


class AICompanionUser(HttpUser):
    """Simulates device behavior for load testing."""
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """Register device on start."""
        response = self.client.post(
            "/api/v1/devices",
            json={
                "name": f"load-test-device-{self.user_id}",
                "device_type": "raspberry_pi"
            }
        )
        self.device_id = response.json()["device_id"]
        self.auth_token = response.json()["auth_token"]
        self.session_id = None
    
    @task(5)
    def send_dialog(self):
        """Send dialog message (most common operation)."""
        self.client.post(
            "/api/v1/dialog/send",
            json={
                "device_id": self.device_id,
                "session_id": self.session_id,
                "message": "Hello, how are you today?"
            },
            headers={"Authorization": f"Bearer {self.auth_token}"}
        )
    
    @task(1)
    def switch_persona(self):
        """Switch persona (less frequent)."""
        import random
        personas = ["companion", "medication_nurse", "storyteller"]
        
        self.client.post(
            f"/api/v1/devices/{self.device_id}/persona/switch",
            json={
                "target_persona_id": random.choice(personas),
                "preserve_context": True
            },
            headers={"Authorization": f"Bearer {self.auth_token}"}
        )
    
    @task(1)
    def get_device_state(self):
        """Check device state."""
        self.client.get(
            f"/api/v1/devices/{self.device_id}/state",
            headers={"Authorization": f"Bearer {self.auth_token}"}
        )
```

### 13.7 Success Criteria

| Metric | Target | Test Method |
|--------|--------|-------------|
| Persona switch latency | < 2 seconds | E2E timing tests |
| Multi-device coordination | 3+ devices sync | Integration tests |
| Continuous operation | 8 hours | Stability tests |
| Voice recognition accuracy | ≥ 60% | Manual + automated |
| API response time (p95) | < 500ms | Load tests |
| Session handoff | Context preserved | E2E tests |

### 13.8 CI/CD Test Pipeline

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
        ports:
          - 5432:5432
      redis:
        image: redis:7
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      
      - name: Run unit tests
        run: pytest tests/unit -v --cov=core --cov-report=xml
      
      - name: Run integration tests
        run: pytest tests/integration -v
        env:
          DATABASE_URL: postgresql://postgres:test@localhost:5432/test
          REDIS_URL: redis://localhost:6379/0
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---
