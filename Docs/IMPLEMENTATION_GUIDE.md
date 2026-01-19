# AI Companion Orchestration Platform
## Complete Implementation Guide

> **Version:** 1.0.0  
> **Last Updated:** 2026-01-19  
> **Status:** Ready for Development

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture](#2-system-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Project Structure](#4-project-structure)
5. [Environment Setup](#5-environment-setup)
6. [Core Modules Implementation](#6-core-modules-implementation)
7. [Persona System](#7-persona-system)
8. [API Specifications](#8-api-specifications)
9. [Database Schema](#9-database-schema)
10. [Dashboard Implementation](#10-dashboard-implementation)
11. [Device Runtime](#11-device-runtime)
12. [Multi-Device Coordination](#12-multi-device-coordination)
13. [Testing Strategy](#13-testing-strategy)
14. [Deployment](#14-deployment)
15. [Development Phases](#15-development-phases)

---

## 1. Executive Summary

### 1.1 Product Vision
Cloud-native orchestration engine enabling any device to instantly switch between specialized AI personas and coordinate multi-device experiences for elderly care, education, and companionship. 

### 1.2 Core Innovation
- Runtime persona switching (< 2 seconds)
- Multi-device choreography and context handoff
- Edge-cloud hybrid architecture

### 1.3 Target Users
| User Type | Description |
|-----------|-------------|
| **End Users** | Elderly individuals, children, people needing companionship |
| **Facility Admins** | Nursing home staff managing multiple devices |
| **Enterprise Clients** | Device manufacturers (Amazon, Google, ElliQ) |
| **Developers** | Third-party persona creators |

### 1.4 Success Metrics
- Persona switch completes in < 2 seconds
- 3+ devices coordinate without manual intervention
- 8-hour continuous operation without restart
- Voice recognition 60%+ accuracy for target demographics
- Dashboard shows live device status

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                                  │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ Admin Web UI │  │ Streamlit    │  │ Mobile App   │              │
│  │ (React)      │  │ Demo Dashboard│  │ (Future)     │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
└─────────┼─────────────────┼─────────────────┼───────────────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     API GATEWAY (FastAPI)                            │
├─────────────────────────────────────────────────────────────────────┤
│  • Authentication & Authorization (JWT)                              │
│  • Rate Limiting                                                     │
│  • Request Routing                                                   │
│  • WebSocket Management                                              │
└─────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  ORCHESTRATION CONTROL PLANE                         │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │ Persona Manager │  │ Session Manager │  │ Device Registry │     │
│  │                 │  │                 │  │                 │     │
│  │ ��� Load/switch   │  │ • Context mgmt  │  │ • Registration  │     │
│  │ • Hot-swap      │  │ • Memory store  │  │ • Health checks │     │
│  │ • Versioning    │  │ • State sync    │  │ • Grouping      │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
│                                                                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │ Conversation    │  │ Event Bus       │  │ Analytics       │     │
│  │ Engine          │  │                 │  │ Engine          │     │
│  │                 │  │ • Pub/Sub       │  │                 │     │
│  │ • LLM API calls │  │ • Device sync   │  │ • Usage metrics │     │
│  │ • Prompt mgmt   │  │ • Webhooks      │  │ • Telemetry     │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
          │                       │
          ▼                       ▼
┌──────────────────────┐  ┌───────────────────────────────────────────┐
│   EXTERNAL SERVICES  │  │              DATA LAYER                    │
├──────────────────────┤  ├───────────────────────────────────────────┤
│ • Claude API (LLM)   │  │  ┌─────────────┐  ┌─────────────┐        │
│ • Whisper (STT)      │  │  │ PostgreSQL  │  │ Redis       │        │
│ • ElevenLabs (TTS)   │  │  │ (Primary DB)│  │ (Cache/Pub) │        │
│ • Deepgram (Alt STT) │  │  └─────────────┘  └─────────────┘        │
└──────────────────────┘  │  ┌─────────────┐  ┌─────────────┐        │
                          │  │ S3/MinIO    │  │ Vector DB   │        │
                          │  │ (Artifacts) │  │ (RAG/Future)│        │
                          │  └─────────────┘  └─────────────┘        │
                          └───────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      EDGE DEVICE LAYER                               │
├─────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────┐     │
│  │                  Device Agent (Python)                      │     │
│  ├────────────────────────────────────────────────────────────┤     │
│  │  • Lightweight runtime (~50MB)                              │     │
│  │  • Audio I/O handler (microphone, speaker)                  │     │
│  │  • Persona cache (offline fallback)                         │     │
│  │  • Hardware interface (GPIO, LEDs, buttons)                 │     │
│  │  • WebSocket connection to Control Plane                    │     │
│  └────────────────────────────────────────────────────────────┘     │
│                                                                      │
│  Target Hardware:  Raspberry Pi 4 (4GB) + USB Speakerphone           │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow Diagram

```
User speaks → Device Agent captures audio
                    │
                    ▼
            Audio sent to Cloud (WebSocket)
                    │
                    ▼
            Whisper API (Speech-to-Text)
                    │
                    ▼
            Conversation Engine receives text
                    │
                    ▼
            Session Manager retrieves context
                    │
                    ▼
            Persona Manager loads active persona
                    │
                    ▼
            Claude API generates response
                    │
                    ▼
            ElevenLabs converts to speech
                    │
                    ▼
            Audio streamed back to Device
                    │
                    ▼
            Device plays audio response
```

### 2.3 Persona Switching Flow

```
Trigger Event (button/schedule/voice command)
                    │
                    ▼
            Event Bus receives switch request
                    │
                    ▼
            Persona Manager validates target persona
                    │
                    ▼
            Session Manager saves current context
                    │
                    ▼
            New persona artifacts loaded
                    │
                    ▼
            Device Agent notified (WebSocket)
                    │
                    ▼
            LED/audio feedback to user
                    │
                    ▼
            Switch complete (< 2 seconds)
```

---

## 3. Technology Stack

### 3.1 Backend (Control Plane)

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Runtime** | Python | 3.11+ | Primary language |
| **Web Framework** | FastAPI | 0.109+ | REST API & WebSocket |
| **Async** | uvicorn | 0.27+ | ASGI server |
| **Task Queue** | Celery | 5.3+ | Background jobs |
| **Message Broker** | Redis | 7.2+ | Pub/Sub & caching |

### 3.2 Database

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Primary DB** | PostgreSQL | 16+ | Persistent storage |
| **ORM** | SQLAlchemy | 2.0+ | Database abstraction |
| **Migrations** | Alembic | 1.13+ | Schema management |
| **Cache** | Redis | 7.2+ | Session state, hot data |

### 3.3 External APIs

| Service | Provider | Purpose | Fallback |
|---------|----------|---------|----------|
| **LLM** | Anthropic Claude | Conversation generation | OpenAI GPT-4 |
| **STT** | OpenAI Whisper | Speech-to-text | Deepgram |
| **TTS** | ElevenLabs | Text-to-speech | Google Cloud TTS |

### 3.4 Frontend (Dashboard)

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Demo UI** | Streamlit | 1.31+ | Quick demos/testing |
| **Admin UI** | React | 18+ | Production dashboard (future) |

### 3.5 Device Runtime

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Runtime** | Python | 3.11+ | Edge device agent |
| **Audio** | PyAudio | 0.2.14+ | Microphone/speaker |
| **GPIO** | RPi.GPIO | 0.7+ | Button/LED control |
| **Async** | asyncio | stdlib | Concurrent operations |

### 3.6 Infrastructure

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Containers** | Docker | Containerization |
| **Orchestration** | Docker Compose | Local development |
| **Cloud** | AWS/Azure | Production deployment |
| **CI/CD** | GitHub Actions | Automated testing/deploy |

---

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

## 5. Environment Setup

### 5.1 Environment Variables

```bash name=.env. example
# =============================================================================
# AI Companion Orchestrator - Environment Configuration
# =============================================================================
# Copy this file to .env and fill in your values

# -----------------------------------------------------------------------------
# Application Settings
# -----------------------------------------------------------------------------
APP_NAME=ai-companion-orchestrator
APP_ENV=development                    # development | staging | production
APP_DEBUG=true
APP_SECRET_KEY=your-secret-key-min-32-chars-here
APP_HOST=0.0.0.0
APP_PORT=8000

# -----------------------------------------------------------------------------
# Database Configuration
# -----------------------------------------------------------------------------
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost: 5432/ai_companion
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# -----------------------------------------------------------------------------
# Redis Configuration
# -----------------------------------------------------------------------------
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=
REDIS_SSL=false

# -----------------------------------------------------------------------------
# Authentication
# -----------------------------------------------------------------------------
JWT_SECRET_KEY=your-jwt-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# -----------------------------------------------------------------------------
# External API Keys
# -----------------------------------------------------------------------------
# Anthropic Claude (Required)
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# OpenAI Whisper (Speech-to-Text)
OPENAI_API_KEY=sk-your-openai-key-here
WHISPER_MODEL=whisper-1

# ElevenLabs (Text-to-Speech)
ELEVENLABS_API_KEY=your-elevenlabs-key-here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM   # Default: Rachel

# Fallback APIs (Optional)
DEEPGRAM_API_KEY=                      # Alternative STT
GOOGLE_CLOUD_TTS_KEY=                  # Alternative TTS

# -----------------------------------------------------------------------------
# Feature Flags
# -----------------------------------------------------------------------------
ENABLE_ANALYTICS=true
ENABLE_MULTI_DEVICE=true
ENABLE_OFFLINE_MODE=true
ENABLE_FINE_TUNING=false               # Enterprise feature

# -----------------------------------------------------------------------------
# Rate Limiting
# -----------------------------------------------------------------------------
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
LOG_LEVEL=INFO                         # DEBUG | INFO | WARNING | ERROR
LOG_FORMAT=json                        # json | text
LOG_FILE=/var/log/ai-companion/app. log

# -----------------------------------------------------------------------------
# CORS (for web dashboard)
# -----------------------------------------------------------------------------
CORS_ORIGINS=http://localhost:3000,http://localhost:8501
CORS_ALLOW_CREDENTIALS=true

# -----------------------------------------------------------------------------
# Device Agent Settings (for Raspberry Pi)
# -----------------------------------------------------------------------------
DEVICE_ID=                             # Auto-generated if empty
DEVICE_NAME=living-room-companion
CONTROL_PLANE_URL=wss://api.example.com/ws
DEVICE_AUTH_TOKEN=                     # Obtained during registration
AUDIO_SAMPLE_RATE=16000
AUDIO_CHANNELS=1
LED_BRIGHTNESS=0.8
```

### 5.2 Requirements Files

```txt name=requirements.txt
# =============================================================================
# AI Companion Orchestrator - Core Dependencies
# =============================================================================

# Web Framework
fastapi==0.109.2
uvicorn[standard]==0.27.1
python-multipart==0.0.9
websockets==12.0

# Database
sqlalchemy[asyncio]==2.0.25
asyncpg==0.29.0
alembic==1.13.1
redis==5.0.1

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Validation
pydantic==2.6.1
pydantic-settings==2.1.0
email-validator==2.1.0

# External APIs
anthropic==0.18.1
openai==1.12.0
elevenlabs==0.2.27
httpx==0.26.0

# Task Queue
celery==5.3.6
redis==5.0.1

# Utilities
python-dotenv==1.0.1
pyyaml==6.0.1
orjson==3.9.13
tenacity==8.2.3

# Logging & Monitoring
structlog==24.1.0
sentry-sdk[fastapi]==1.40.0

# Testing
pytest==8.0.0
pytest-asyncio==0.23.4
pytest-cov==4.1.0
httpx==0.26.0
factory-boy==3.3.0
```

```txt name=dashboard/requirements.txt
# =============================================================================
# Streamlit Dashboard Dependencies
# =============================================================================

streamlit==1.31.0
streamlit-webrtc==0.47.1
plotly==5.18.0
pandas==2.2.0
httpx==0.26.0
websockets==12.0
pydantic==2.6.1
python-dotenv==1.0.1
```

```txt name=device_agent/requirements. txt
# =============================================================================
# Device Agent Dependencies (Raspberry Pi)
# =============================================================================

# Audio
pyaudio==0.2.14
sounddevice==0.4.6
numpy==1.26.3
scipy==1.12.0

# Hardware
RPi.GPIO==0.7.1
rpi_ws281x==5.0.0        # LED strip control
adafruit-circuitpython-neopixel==6.3.11

# Network
websockets==12.0
httpx==0.26.0
aiohttp==3.9.3

# Core
asyncio==3.4.3
pydantic==2.6.1
pyyaml==6.0.1
python-dotenv==1.0.1

# Caching
diskcache==5.6.3
```

### 5.3 Docker Compose

```yaml name=docker-compose.yml
version: '3.8'

services:
  # ==========================================================================
  # API Server
  # ==========================================================================
  api: 
    build: 
      context: . 
      dockerfile: Dockerfile
    container_name: ai-companion-api
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=development
      - DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/ai_companion
      - REDIS_URL=redis://redis:6379/0
    env_file:
      - .env
    volumes:
      - ./core:/app/core
      - ./api:/app/api
      - ./personas:/app/personas
    depends_on: 
      db:
        condition:  service_healthy
      redis:
        condition: service_healthy
    command: uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
    networks:
      - ai-companion-network

  # ==========================================================================
  # PostgreSQL Database
  # ==========================================================================
  db:
    image: postgres:16-alpine
    container_name: ai-companion-db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: ai_companion
    ports:
      - "5432:5432"
    volumes: 
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init_db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - ai-companion-network

  # ==========================================================================
  # Redis Cache & Pub/Sub
  # ==========================================================================
  redis:
    image: redis:7.2-alpine
    container_name: ai-companion-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout:  5s
      retries: 5
    networks:
      - ai-companion-network

  # ==========================================================================
  # Streamlit Dashboard
  # ==========================================================================
  dashboard:
    build:
      context:  ./dashboard
      dockerfile: Dockerfile
    container_name: ai-companion-dashboard
    ports:
      - "8501:8501"
    environment:
      - API_URL=http://api:8000
    volumes:
      - ./dashboard:/app
    depends_on: 
      - api
    command: streamlit run app.py --server. port 8501 --server.address 0.0.0.0
    networks:
      - ai-companion-network

  # ==========================================================================
  # Celery Worker (Background Tasks)
  # ==========================================================================
  worker:
    build:
      context:  . 
      dockerfile: Dockerfile
    container_name: ai-companion-worker
    environment:
      - APP_ENV=development
      - DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/ai_companion
      - REDIS_URL=redis://redis:6379/0
    env_file:
      - . env
    volumes: 
      - ./core:/app/core
    depends_on: 
      - db
      - redis
    command: celery -A core. tasks worker --loglevel=info
    networks:
      - ai-companion-network

volumes:
  postgres_data:
  redis_data:

networks:
  ai-companion-network: 
    driver: bridge
```

---

## 6. Core Modules Implementation

### 6.1 Configuration Management

```python name=core/config. py
"""
Application configuration management using Pydantic Settings.
"""

from functools import lru_cache
from typing import Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Application
    app_name:  str = "ai-companion-orchestrator"
    app_env: str = Field(default="development", pattern="^(development|staging|production)$")
    app_debug: bool = True
    app_secret_key: str = Field(... , min_length=32)
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    
    # Database
    database_url: str
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Redis
    redis_url:  str = "redis://localhost:6379/0"
    redis_password: Optional[str] = None
    
    # JWT Authentication
    jwt_secret_key: str = Field(..., min_length=32)
    jwt_algorithm:  str = "HS256"
    jwt_expiration_hours: int = 24
    
    # Anthropic Claude
    anthropic_api_key: str
    anthropic_model: str = "claude-3-sonnet-20240229"
    
    # OpenAI (Whisper)
    openai_api_key: str
    whisper_model: str = "whisper-1"
    
    # ElevenLabs
    elevenlabs_api_key: str
    elevenlabs_voice_id:  str = "21m00Tcm4TlvDq8ikWAM"
    
    # Feature Flags
    enable_analytics: bool = True
    enable_multi_device: bool = True
    enable_offline_mode:  bool = True
    enable_fine_tuning: bool = False
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window_seconds:  int = 60
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # CORS
    cors_origins:  List[str] = ["http://localhost:3000", "http://localhost:8501"]
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @property
    def is_production(self) -> bool:
        return self.app_env == "production"
    
    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
```

### 6.2 Custom Exceptions

```python name=core/exceptions.py
"""
Custom exception classes for the AI Companion Orchestrator.
"""

from typing import Optional, Dict, Any


class AICompanionError(Exception):
    """Base exception for all application errors."""
    
    def __init__(
        self,
        message: str,
        error_code:  str = "UNKNOWN_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_code": self.error_code,
            "message": self. message,
            "details": self.details
        }


# =============================================================================
# Persona Errors
# =============================================================================

class PersonaError(AICompanionError):
    """Base exception for persona-related errors."""
    pass


class PersonaNotFoundError(PersonaError):
    """Raised when a persona cannot be found."""
    
    def __init__(self, persona_id: str):
        super().__init__(
            message=f"Persona not found: {persona_id}",
            error_code="PERSONA_NOT_FOUND",
            details={"persona_id": persona_id}
        )


class PersonaLoadError(PersonaError):
    """Raised when a persona fails to load."""
    
    def __init__(self, persona_id: str, reason: str):
        super().__init__(
            message=f"Failed to load persona {persona_id}: {reason}",
            error_code="PERSONA_LOAD_ERROR",
            details={"persona_id": persona_id, "reason": reason}
        )


class PersonaSwitchError(PersonaError):
    """Raised when persona switching fails."""
    
    def __init__(self, from_persona:  str, to_persona: str, reason: str):
        super().__init__(
            message=f"Failed to switch from {from_persona} to {to_persona}: {reason}",
            error_code="PERSONA_SWITCH_ERROR",
            details={
                "from_persona": from_persona,
                "to_persona": to_persona,
                "reason": reason
            }
        )


# =============================================================================
# Device Errors
# =============================================================================

class DeviceError(AICompanionError):
    """Base exception for device-related errors."""
    pass


class DeviceNotFoundError(DeviceError):
    """Raised when a device cannot be found."""
    
    def __init__(self, device_id: str):
        super().__init__(
            message=f"Device not found:  {device_id}",
            error_code="DEVICE_NOT_FOUND",
            details={"device_id": device_id}
        )


class DeviceOfflineError(DeviceError):
    """Raised when attempting to communicate with an offline device."""
    
    def __init__(self, device_id: str):
        super().__init__(
            message=f"Device is offline: {device_id}",
            error_code="DEVICE_OFFLINE",
            details={"device_id": device_id}
        )


class DeviceRegistrationError(DeviceError):
    """Raised when device registration fails."""
    
    def __init__(self, reason: str):
        super().__init__(
            message=f"Device registration failed:  {reason}",
            error_code="DEVICE_REGISTRATION_ERROR",
            details={"reason":  reason}
        )


# =============================================================================
# Session Errors
# =============================================================================

class SessionError(AICompanionError):
    """Base exception for session-related errors."""
    pass


class SessionNotFoundError(SessionError):
    """Raised when a session cannot be found."""
    
    def __init__(self, session_id: str):
        super().__init__(
            message=f"Session not found: {session_id}",
            error_code="SESSION_NOT_FOUND",
            details={"session_id":  session_id}
        )


class SessionExpiredError(SessionError):
    """Raised when a session has expired."""
    
    def __init__(self, session_id: str):
        super().__init__(
            message=f"Session has expired: {session_id}",
            error_code="SESSION_EXPIRED",
            details={"session_id": session_id}
        )


# =============================================================================
# Conversation Errors
# =============================================================================

class ConversationError(AICompanionError):
    """Base exception for conversation-related errors."""
    pass


class LLMAPIError(ConversationError):
    """Raised when LLM API call fails."""
    
    def __init__(self, provider: str, reason: str):
        super().__init__(
            message=f"LLM API error ({provider}): {reason}",
            error_code="LLM_API_ERROR",
            details={"provider": provider, "reason": reason}
        )


class AudioProcessingError(ConversationError):
    """Raised when audio processing fails."""
    
    def __init__(self, stage: str, reason:  str):
        super().__init__(
            message=f"Audio processing error at {stage}: {reason}",
            error_code="AUDIO_PROCESSING_ERROR",
            details={"stage": stage, "reason": reason}
        )


# =============================================================================
# Authentication Errors
# =============================================================================

class AuthError(AICompanionError):
    """Base exception for authentication errors."""
    pass


class InvalidCredentialsError(AuthError):
    """Raised when credentials are invalid."""
    
    def __init__(self):
        super().__init__(
            message="Invalid credentials",
            error_code="INVALID_CREDENTIALS"
        )


class TokenExpiredError(AuthError):
    """Raised when a JWT token has expired."""
    
    def __init__(self):
        super().__init__(
            message="Token has expired",
            error_code="TOKEN_EXPIRED"
        )
```

### 6.3 Persona Manager

```python name=core/persona/manager. py
"""
Persona Manager - Handles loading, switching, and managing personas.
"""

import asyncio
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
import yaml
import json

from pydantic import BaseModel, Field
from redis import asyncio as aioredis

from core.config import settings
from core.exceptions import PersonaNotFoundError, PersonaLoadError, PersonaSwitchError
from core.persona.models import Persona, PersonaConfig, PersonaArtifacts


class PersonaManager:
    """
    Manages persona lifecycle including loading, caching, and switching. 
    
    Features:
    - Load personas from filesystem or database
    - Cache active personas in Redis for fast access
    - Hot-swap personas in < 2 seconds
    - Version tracking and rollback support
    """
    
    PERSONA_CACHE_PREFIX = "persona:"
    ACTIVE_PERSONA_PREFIX = "active_persona:"
    CACHE_TTL_SECONDS = 3600  # 1 hour
    
    def __init__(
        self,
        redis_client: aioredis.Redis,
        personas_dir: Path = Path("personas")
    ):
        self.redis = redis_client
        self.personas_dir = personas_dir
        self._persona_cache: Dict[str, Persona] = {}
    
    async def load_persona(self, persona_id:  str) -> Persona:
        """
        Load a persona by ID.  Checks cache first, then filesystem.
        
        Args:
            persona_id:  Unique identifier for the persona
            
        Returns:
            Loaded Persona object
            
        Raises: 
            PersonaNotFoundError: If persona doesn't exist
            PersonaLoadError: If persona fails to load
        """
        # Check local cache
        if persona_id in self._persona_cache:
            return self._persona_cache[persona_id]
        
        # Check Redis cache
        cached = await self.redis. get(f"{self.PERSONA_CACHE_PREFIX}{persona_id}")
        if cached: 
            persona = Persona.model_validate_json(cached)
            self._persona_cache[persona_id] = persona
            return persona
        
        # Load from filesystem
        persona_path = self.personas_dir / persona_id
        if not persona_path. exists():
            raise PersonaNotFoundError(persona_id)
        
        try:
            persona = await self._load_from_filesystem(persona_id, persona_path)
            
            # Cache in Redis
            await self.redis.setex(
                f"{self.PERSONA_CACHE_PREFIX}{persona_id}",
                self. CACHE_TTL_SECONDS,
                persona.model_dump_json()
            )
            
            # Cache locally
            self._persona_cache[persona_id] = persona
            
            return persona
            
        except Exception as e: 
            raise PersonaLoadError(persona_id, str(e))
    
    async def _load_from_filesystem(self, persona_id: str, persona_path: Path) -> Persona: 
        """Load persona artifacts from filesystem."""
        
        # Load config
        config_path = persona_path / "config.yaml"
        if not config_path.exists():
            raise PersonaLoadError(persona_id, "config. yaml not found")
        
        with open(config_path) as f:
            config_data = yaml.safe_load(f)
        config = PersonaConfig(**config_data)
        
        # Load system prompt
        prompt_path = persona_path / "system_prompt.md"
        if not prompt_path.exists():
            raise PersonaLoadError(persona_id, "system_prompt.md not found")
        
        system_prompt = prompt_path.read_text()
        
        # Load examples (optional)
        examples = []
        examples_path = persona_path / "examples"
        if examples_path.exists():
            for example_file in examples_path. glob("*.json"):
                with open(example_file) as f:
                    examples.extend(json.load(f))
        
        # Build artifacts
        artifacts = PersonaArtifacts(
            system_prompt=system_prompt,
            examples=examples,
            knowledge_docs=[]  # Load from knowledge/ if exists
        )
        
        return Persona(
            id=persona_id,
            config=config,
            artifacts=artifacts,
            loaded_at=datetime.utcnow()
        )
    
    async def switch_persona(
        self,
        device_id: str,
        from_persona_id: Optional[str],
        to_persona_id: str
    ) -> Persona:
        """
        Switch a device to a new persona.
        
        Args:
            device_id: Device making the switch
            from_persona_id:  Current persona (for context preservation)
            to_persona_id: Target persona
            
        Returns: 
            The newly activated Persona
            
        Raises: 
            PersonaSwitchError: If switch fails
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Load target persona
            new_persona = await self.load_persona(to_persona_id)
            
            # Update active persona for device
            await self.redis.set(
                f"{self.ACTIVE_PERSONA_PREFIX}{device_id}",
                to_persona_id
            )
            
            # Log switch time
            switch_time = asyncio.get_event_loop().time() - start_time
            if switch_time > 2. 0:
                # Log warning if switch takes > 2 seconds
                pass  # TODO: Add logging
            
            return new_persona
            
        except PersonaNotFoundError: 
            raise PersonaSwitchError(
                from_persona=from_persona_id or "none",
                to_persona=to_persona_id,
                reason="Target persona not found"
            )
        except Exception as e: 
            raise PersonaSwitchError(
                from_persona=from_persona_id or "none",
                to_persona=to_persona_id,
                reason=str(e)
            )
    
    async def get_active_persona(self, device_id: str) -> Optional[Persona]:
        """Get the currently active persona for a device."""
        persona_id = await self.redis.get(f"{self. ACTIVE_PERSONA_PREFIX}{device_id}")
        if persona_id: 
            return await self. load_persona(persona_id. decode())
        return None
    
    async def list_personas(self) -> List[str]:
        """List all available persona IDs."""
        personas = []
        for path in self.personas_dir.iterdir():
            if path.is_dir() and (path / "config. yaml").exists():
                personas.append(path.name)
        return sorted(personas)
    
    async def invalidate_cache(self, persona_id: str) -> None:
        """Invalidate cached persona (e.g., after update)."""
        await self.redis.delete(f"{self. PERSONA_CACHE_PREFIX}{persona_id}")
        self._persona_cache. pop(persona_id, None)
```

### 6.4 Persona Models

```python name=core/persona/models.py
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
    version: str = Field(default="1.0. 0")
    
    # Behavior
    adaptation_mode: AdaptationMode = AdaptationMode. INSTRUCTION_ONLY
    trigger_types: List[TriggerType] = [TriggerType. MANUAL]
    context_retention_hours: int = Field(default=24, ge=1, le=168)
    
    # Voice
    voice:  VoiceConfig
    
    # Constraints
    max_response_tokens: int = Field(default=500, ge=50, le=4000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    
    # Scheduling (if trigger is SCHEDULE)
    schedule_cron: Optional[str] = None
    
    # Tags for categorization
    tags:  List[str] = []


class DialogExample(BaseModel):
    """Example dialog for persona training/testing."""
    user_message: str
    assistant_response:  str
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
    loaded_at:  datetime
    
    # Optional:  fine-tuned model reference
    model_reference: Optional[str] = None
    
    def get_full_system_prompt(self) -> str:
        """Build the complete system prompt including examples."""
        prompt = self.artifacts.system_prompt
        
        if self.artifacts.examples:
            prompt += "\n\n## Example Interactions\n"
            for i, ex in enumerate(self. artifacts.examples[: 3], 1):
                prompt += f"\n### Example {i}\n"
                prompt += f"User: {ex.user_message}\n"
                prompt += f"Assistant: {ex.assistant_response}\n"
        
        return prompt


class PersonaSummary(BaseModel):
    """Lightweight persona info for listings."""
    id: str
    name:  str
    description:  str
    version:  str
    tags: List[str]
    adaptation_mode: AdaptationMode
```

### 6.5 Conversation Engine

```python name=core/conversation/engine.py
"""
Conversation Engine - Handles dialog generation using LLM APIs.
"""

import asyncio
from typing import Optional, List, AsyncGenerator
from datetime import datetime

from anthropic import AsyncAnthropic
from pydantic import BaseModel

from core.config import settings
from core. exceptions import LLMAPIError
from core.persona. models import Persona
from core.session. models import ConversationMessage, MessageRole
from core.conversation.models import ConversationContext, GenerationConfig


class ConversationEngine: 
    """
    Handles conversation generation using Claude API.
    
    Features:
    - Persona-aware prompting
    - Context window management
    - Streaming responses
    - Fallback handling
    """
    
    MAX_CONTEXT_MESSAGES = 20
    MAX_CONTEXT_TOKENS = 8000
    
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model
    
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
            user_message:  User's input message
            context:  Conversation history and state
            config: Optional generation parameters
            
        Returns:
            Generated response text
            
        Raises:
            LLMAPIError:  If API call fails
        """
        config = config or GenerationConfig()
        
        # Build messages array
        messages = self._build_messages(user_message, context)
        
        try:
            response = await self.client. messages.create(
                model=self.model,
                max_tokens=config. max_tokens or persona.config.max_response_tokens,
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
        user_message:  str,
        context: ConversationContext,
        config:  Optional[GenerationConfig] = None
    ) -> AsyncGenerator[str, None]: 
        """
        Stream a response token by token.
        
        Yields:
            Response tokens as they're generated
        """
        config = config or GenerationConfig()
        messages = self._build_messages(user_message, context)
        
        try: 
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=config.max_tokens or persona.config. max_response_tokens,
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
        context:  ConversationContext
    ) -> List[dict]:
        """Build the messages array for the API call."""
        messages = []
        
        # Add conversation history
        for msg in context.messages[-self.MAX_CONTEXT_MESSAGES: ]:
            messages. append({
                "role": msg.role.value,
                "content":  msg.content
            })
        
        # Add current message
        messages. append({
            "role": "user",
            "content": user_message
        })
        
        return messages
    
    async def estimate_tokens(self, text:  str) -> int:
        """Estimate token count for text."""
        # Rough estimation:  ~4 chars per token for English
        return len(text) // 4


class GenerationConfig(BaseModel):
    """Configuration for response generation."""
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    stop_sequences: List[str] = []
```

### 6.6 Session Manager

```python name=core/session/manager.py
"""
Session Manager - Handles conversation state and context. 
"""

import json
from typing import Optional, List
from datetime import datetime, timedelta
from uuid import uuid4

from redis import asyncio as aioredis

from core.config import settings
from core. exceptions import SessionNotFoundError, SessionExpiredError
from core.session.models import (
    Session, 
    SessionState, 
    ConversationMessage, 
    MessageRole
)


class SessionManager: 
    """
    Manages conversation sessions and their state.
    
    Features:
    - Session creation and lifecycle
    - Message history management
    - Context preservation across persona switches
    - Session handoff between devices
    """
    
    SESSION_PREFIX = "session:"
    DEVICE_SESSION_PREFIX = "device_session:"
    DEFAULT_TTL_HOURS = 24
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
    
    async def create_session(
        self,
        device_id: str,
        persona_id: str,
        user_id: Optional[str] = None
    ) -> Session:
        """
        Create a new conversation session.
        
        Args:
            device_id: Device initiating the session
            persona_id: Initial persona for the session
            user_id: Optional user identifier
            
        Returns:
            New Session object
        """
        session = Session(
            id=str(uuid4()),
            device_id=device_id,
            persona_id=persona_id,
            user_id=user_id,
            state=SessionState. ACTIVE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            expires_at=datetime. utcnow() + timedelta(hours=self.DEFAULT_TTL_HOURS),
            messages=[],
            metadata={}
        )
        
        # Store session
        await self._save_session(session)
        
        # Link device to session
        await self. redis.set(
            f"{self.DEVICE_SESSION_PREFIX}{device_id}",
            session.id
        )
        
        return session
    
    async def get_session(self, session_id: str) -> Session:
        """
        Retrieve a session by ID.
        
        Raises:
            SessionNotFoundError: If session doesn't exist
            SessionExpiredError:  If session has expired
        """
        data = await self.redis.get(f"{self.SESSION_PREFIX}{session_id}")
        
        if not data:
            raise SessionNotFoundError(session_id)
        
        session = Session.model_validate_json(data)
        
        if session.expires_at < datetime. utcnow():
            await self. end_session(session_id)
            raise SessionExpiredError(session_id)
        
        return session
    
    async def get_device_session(self, device_id: str) -> Optional[Session]:
        """Get the active session for a device."""
        session_id = await self.redis.get(f"{self. DEVICE_SESSION_PREFIX}{device_id}")
        
        if not session_id: 
            return None
        
        try:
            return await self.get_session(session_id. decode())
        except (SessionNotFoundError, SessionExpiredError):
            return None
    
    async def add_message(
        self,
        session_id: str,
        role: MessageRole,
        content: str
    ) -> ConversationMessage:
        """
        Add a message to the session history.
        
        Args:
            session_id: Session to add message to
            role: Who sent the message (user/assistant)
            content: Message content
            
        Returns:
            The created message
        """
        session = await self.get_session(session_id)
        
        message = ConversationMessage(
            id=str(uuid4()),
            role=role,
            content=content,
            timestamp=datetime.utcnow(),
            persona_id=session. persona_id
        )
        
        session.messages. append(message)
        session.updated_at = datetime.utcnow()
        
        await self._save_session(session)
        
        return message
    
    async def update_persona(
        self,
        session_id: str,
        new_persona_id:  str,
        preserve_context: bool = True
    ) -> Session:
        """
        Update the session's active persona.
        
        Args:
            session_id: Session to update
            new_persona_id:  New persona ID
            preserve_context: Whether to keep message history
            
        Returns:
            Updated session
        """
        session = await self. get_session(session_id)
        
        session.persona_id = new_persona_id
        session.updated_at = datetime. utcnow()
        
        if not preserve_context: 
            session.messages = []
        
        await self._save_session(session)
        
        return session
    
    async def handoff_session(
        self,
        session_id: str,
        from_device_id:  str,
        to_device_id:  str
    ) -> Session:
        """
        Hand off a session from one device to another. 
        
        This enables "continue conversation in another room" scenarios.
        """
        session = await self.get_session(session_id)
        
        # Remove from old device
        await self.redis.delete(f"{self. DEVICE_SESSION_PREFIX}{from_device_id}")
        
        # Update session
        session.device_id = to_device_id
        session.updated_at = datetime.utcnow()
        session.metadata["handoff_history"] = session.metadata.get("handoff_history", [])
        session.metadata["handoff_history"].append({
            "from": from_device_id,
            "to": to_device_id,
            "at": datetime.utcnow().isoformat()
        })
        
        await self._save_session(session)
        
        # Link new device
        await self.redis.set(
            f"{self.DEVICE_SESSION_PREFIX}{to_device_id}",
            session.id
        )
        
        return session
    
    async def end_session(