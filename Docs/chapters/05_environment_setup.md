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
