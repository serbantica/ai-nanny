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