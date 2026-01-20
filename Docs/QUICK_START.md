# Quick Start Guide

This guide provides instructions to start the entire AI Nanny stack.

## Prerequisites

- Python 3.11+
- Redis (optional - the system will fall back to local JSON storage if Redis is unavailable)
- Required Python packages installed

## Starting the Stack

### 1. Start the API Server

Open a terminal and run:

```bash
cd /Users/serbantica/Library/CloudStorage/OneDrive-IBM/GitHub/AI-Nanny-Project/ai-nanny/ai-companion-orchestrator
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

The API server will start on `http://localhost:8000`

- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### 2. Start the Dashboard

Open a new terminal and run:

```bash
cd /Users/serbantica/Library/CloudStorage/OneDrive-IBM/GitHub/AI-Nanny-Project/ai-nanny/dashboard
streamlit run app.py
```

The dashboard will start on `http://localhost:8501`

## Verify Installation

1. Check API health: `curl http://localhost:8000/health`
2. Open dashboard in browser: `http://localhost:8501`
3. Navigate to the DEVICES page to see pre-loaded devices (Living Room, Kitchen, Bedroom 1, 2, 3)

## Troubleshooting

### API Server Issues

- **ModuleNotFoundError**: Ensure you're running the command from the correct directory
- **Port 8000 already in use**: Kill existing process with `lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9`
- **Redis connection errors**: The system will continue to work with local JSON storage

### Dashboard Issues

- **Connection refused**: Ensure API server is running on port 8000
- **Port 8501 already in use**: Kill existing Streamlit process or use a different port with `streamlit run app.py --server.port 8502`

## Stopping the Stack

Press `CTRL+C` in each terminal to stop the respective services.
