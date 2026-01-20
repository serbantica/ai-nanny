AI Companion Orchestrator - Software Build Guide

> File location (project): docs/software-build-guide.md

This document is intended to live as a standalone Markdown file inside the repository and be referenced by README.md.



Overview

Build the persona orchestration engine in two parallel tracks:

1. Demo Dashboard (Streamlit) - For licensing pitches, investor demos, testing


2. Device Software (Python) - Runs on Raspberry Pi 4 + ReSpeaker HAT



Key principle: Same core engine, different interfaces. Dashboard simulates device behavior without hardware.


---

Part 1: Core Orchestration Engine

Architecture

┌─────────────────────────────────────────────────────┐
│           Persona Orchestration Engine              │
│                  (Core Library)                     │
├─────────────────────────────────────────────────────┤
│  • PersonaManager (load/switch personas)            │
│  • ConversationEngine (Claude API client)           │
│  • StateManager (context, memory, transitions)      │
│  • AudioPipeline (speech-to-text, text-to-speech)   │
│  • EventBus (device coordination, webhooks)         │
└─────────────────────────────────────────────────────┘
              ↓                           ↓
    ┌──────────────────┐        ┌──────────────────┐
    │  Streamlit UI    │        │  Device Runtime  │
    │  (Demo/Testing)  │        │  (Raspberry Pi)  │
    └──────────────────┘        └──────────────────┘


---

Project Structure

ai-companion-orchestrator/
├── core/
│   ├── __init__.py
│   ├── persona_manager.py      # Load/switch personas
│   ├── conversation_engine.py  # Claude API integration
│   ├── state_manager.py        # Session state, memory
│   ├── audio_pipeline.py       # STT/TTS integrations
│   └── event_bus.py            # Multi-device coordination
├── personas/
│   ├── storyteller.yaml
│   ├── lullaby.yaml
│   ├── morning_companion.yaml
│   ├── homework_helper.yaml
│   └── fitness_coach.yaml
├── dashboard/
│   ├── app.py                  # Streamlit main app
│   ├── components/
│   │   ├── device_simulator.py
│   │   ├── persona_library.py
│   │   └── analytics.py
│   └── requirements.txt
├── device/
│   ├── main.py                 # Pi runtime
│   ├── hardware_interface.py  # GPIO, LED, mic control
│   └── requirements.txt
├── tests/
│   ├── test_persona_manager.py
│   └── test_conversation_engine.py
├── config/
│   ├── config.yaml
│   └── .env.example
└── README.md


---

Part 2: Week-by-Week Build Plan

Week 1: Core Engine + Persona System

Day 1-2: Persona Manager

File: core/persona_manager.py

# (content unchanged – persona_manager.py)

File: personas/storyteller.yaml

# (content unchanged – storyteller.yaml)

Day 3-4: Conversation Engine (Claude Integration)

File: core/conversation_engine.py

# (content unchanged – conversation_engine.py)

Day 5: State Manager

File: core/state_manager.py

# (content unchanged – state_manager.py)


---

Week 2: Audio Pipeline + Demo Dashboard

Day 1-2: Audio Pipeline (Stub for Dashboard, Real for Device)

File: core/audio_pipeline.py

# (content unchanged – audio_pipeline.py)

Day 3-5: Streamlit Dashboard

File: dashboard/app.py

# (content unchanged – dashboard/app.py)