## 4. Project Structure

```
ai-companion-orchestrator/
│
├── README.md                          # Project overview
├── IMPLEMENTATION_GUIDE. md            # This document
├── LICENSE                            # MIT License
├── . gitignore                         # Git ignore rules
├── . env.example                       # Environment template
├── pyproject.toml                     # Python project config
├── docker-compose.yml                 # Local development stack
├── docker-compose. prod.yml            # Production stack
├── Makefile                           # Development commands
│
├── core/                              # Core orchestration engine
│   ├── __init__.py
│   ├── config.py                      # Configuration management
│   ├── exceptions.py                  # Custom exceptions
│   ├── logging_config.py              # Logging setup
│   │
│   ├── persona/                       # Persona management
│   │   ├── __init__.py
│   │   ├── manager.py                 # PersonaManager class
│   │   ├── loader.py                  # Persona artifact loader
│   │   ├── validator.py               # Schema validation
│   │   └── models.py                  # Persona data models
│   │
│   ├── conversation/                  # Conversation engine
│   │   ├── __init__.py
│   │   ├── engine.py                  # ConversationEngine class
│   │   ├── llm_client.py              # Claude API wrapper
│   │   ├── prompt_builder.py          # Dynamic prompt construction
│   │   └── models.py                  # Conversation data models
│   │
│   ├── session/                       # Session management
│   │   ├── __init__.py
│   │   ├── manager. py                 # SessionManager class
│   │   ├── memory. py                  # Context memory handling
│   │   ├── state.py                   # State machine
│   │   └── models.py                  # Session data models
│   │
│   ├── device/                        # Device registry
│   │   ├── __init__.py
│   │   ├── registry.py                # DeviceRegistry class
│   │   ├── health.py                  # Health check logic
│   │   └── models.py                  # Device data models
│   │
│   ├── audio/                         # Audio pipeline
│   │   ├── __init__.py
│   │   ├── pipeline.py                # AudioPipeline class
│   │   ├── stt.py                     # Speech-to-text clients
│   │   ├── tts. py                     # Text-to-speech clients
│   │   └── models.py                  # Audio data models
│   │
│   ├── events/                        # Event bus
│   │   ├── __init__.py
│   │   ├── bus. py                     # EventBus class
│   │   ├── handlers.py                # Event handlers
│   │   └── models. py                  # Event data models
│   │
│   └── analytics/                     # Analytics engine
│       ├── __init__. py
│       ├── collector.py               # Metrics collection
│       ├── reporter.py                # Report generation
│       └── models.py                  # Analytics data models
│
├── api/                               # FastAPI application
│   ├── __init__.py
│   ├── main.py                        # FastAPI app entry
│   ├── dependencies.py                # Dependency injection
│   │
│   ├── routers/                       # API route handlers
│   │   ├── __init__.py
│   │   ├── devices.py                 # /api/v1/devices
│   │   ├── personas.py                # /api/v1/personas
│   │   ├── sessions.py                # /api/v1/sessions
│   │   ├── dialog.py                  # /api/v1/dialog
│   │   ├── admin.py                   # /api/v1/admin
│   │   └── health.py                  # /api/v1/health
│   │
│   ├── websocket/                     # WebSocket handlers
│   │   ├── __init__.py
│   │   ├── manager.py                 # Connection manager
│   │   └── handlers.py                # Message handlers
│   │
│   ├── schemas/                       # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── device.py
│   │   ├── persona.py
│   │   ├── session.py
│   │   ├── dialog.py
│   │   └── common.py
│   │
│   └── middleware/                    # Custom middleware
│       ├── __init__. py
│       ├── auth.py                    # JWT authentication
│       ├── rate_limit.py              # Rate limiting
│       └── logging.py                 # Request logging
│
├── db/                                # Database layer
│   ├── __init__.py
│   ├── session.py                     # Database session
│   ├── base.py                        # SQLAlchemy base
│   │
│   ├── models/                        # ORM models
│   │   ├── __init__.py
│   │   ├── device.py
│   │   ├── persona.py
│   │   ├── session. py
│   │   ├── conversation.py
│   │   └── user.py
│   │
│   ├── repositories/                  # Data access layer
│   │   ├── __init__.py
│   │   ├── device_repo.py
│   │   ├── persona_repo. py
│   │   └── session_repo. py
│   │
│   └── migrations/                    # Alembic migrations
│       ├── env.py
│       ├── script.py. mako
│       └── versions/
│           └── 001_initial_schema. py
│
├── personas/                          # Persona artifact library
│   ├── companion/
│   │   ├── system_prompt.md
│   │   ├── config.yaml
│   │   └── examples/
│   │       └── dialog_examples.json
│   │
│   ├── medication_nurse/
│   │   ├── system_prompt.md
│   │   ├── config.yaml
│   │   └── examples/
│   │
│   ├── storyteller/
│   │   ├── system_prompt.md
│   │   ├── config.yaml
│   │   └── examples/
│   │
│   ├── entertainer/
│   │   ├── system_prompt.md
│   │   ├── config.yaml
│   │   └── examples/
│   │
│   └── emergency/
│       ├── system_prompt. md
│       ├── config.yaml
│       └── examples/
│
├── dashboard/                         # Streamlit demo dashboard
│   ├── __init__.py
│   ├── app.py                         # Main Streamlit app
│   ├── requirements.txt               # Dashboard dependencies
│   │
│   ├── pages/                         # Multi-page app
│   │   ├── 01_devices.py              # Device management
│   │   ├── 02_personas.py             # Persona library
│   │   ├── 03_simulator.py            # Device simulator
│   │   └── 04_analytics.py            # Usage analytics
│   │
│   └── components/                    # Reusable components
│       ├── __init__.py
│       ├── device_card.py
│       ├── persona_selector.py
│       ├── chat_interface.py
│       └── metrics_display.py
│
├── device_agent/                      # Raspberry Pi runtime
│   ├── __init__.py
│   ├── main.py                        # Agent entry point
│   ├── requirements.txt               # Device dependencies
│   │
│   ├── hardware/                      # Hardware interfaces
│   │   ├── __init__.py
│   │   ├── audio.py                   # Microphone/speaker
│   │   ├── gpio.py                    # Buttons/LEDs
│   │   └── display.py                 # Optional display
│   │
│   ├── network/                       # Network communication
│   │   ├── __init__.py
│   │   ├── websocket_client.py        # WebSocket to cloud
│   │   └── offline_handler.py         # Offline mode
│   │
│   └── cache/                         # Local caching
│       ├── __init__.py
│       ├── persona_cache.py           # Cached personas
│       └── audio_cache.py             # Cached audio
│
├── tests/                             # Test suite
│   ├── __init__.py
│   ├── conftest.py                    # Pytest fixtures
│   │
│   ├── unit/                          # Unit tests
│   │   ├── test_persona_manager.py
│   │   ├── test_conversation_engine.py
│   │   ├── test_session_manager.py
│   │   └── test_event_bus.py
│   │
│   ├── integration/                   # Integration tests
│   │   ├── test_api_devices.py
│   │   ├── test_api_personas.py
│   │   ├── test_websocket. py
│   │   └── test_multi_device. py
│   │
│   └── e2e/                           # End-to-end tests
│       ├── test_persona_switch.py
│       ├── test_conversation_flow.py
│       └── test_device_handoff.py
│
├── scripts/                           # Utility scripts
│   ├── setup_dev. sh                   # Development setup
│   ├── seed_personas.py               # Load default personas
│   ├── generate_api_docs.py           # OpenAPI export
│   └── health_check.py                # System health check
│
├── config/                            # Configuration files
│   ├── logging.yaml                   # Logging configuration
│   ├── personas_schema.json           # Persona JSON schema
│   └── settings/
│       ├── development.yaml
│       ├── staging.yaml
│       └── production.yaml
│
└── docs/                              # Additional documentation
    ├── API. md                         # API documentation
    ├── PERSONAS.md                    # Persona authoring guide
    ├── DEPLOYMENT.md                  # Deployment guide
    └── HARDWARE.md                    # Hardware setup guide
```

---
