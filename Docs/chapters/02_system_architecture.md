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