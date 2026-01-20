# AI Companion Orchestrator

Backend service for the AI Companion platform.

## Setup

1.  **Install Dependencies**
    ```bash
    pip install .
    # OR using PDM
    pdm install
    ```

2.  **Environment Variables**
    Copy `.env.example` to `.env` and configure your API keys.
    ```bash
    cp .env.example .env
    ```

3.  **Run with Docker**
    ```bash
    docker-compose up -d
    ```

## Structure

*   `core/`: Core logic (Personas, Conversation, Session, etc.)
*   `api/`: FastAPI application (Routes, Schemas)

