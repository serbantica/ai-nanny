# 🤖 AI Companion Orchestration Platform

> **A cloud-native, multi-persona AI companion system designed for elderly care with intelligent orchestration, RAG-powered knowledge base, and multi-device coordination.**

---

## 🎯 Purpose

The AI Companion Orchestration Platform is an enterprise-ready solution that enables **intelligent, context-aware AI companions** for elderly care facilities and home care environments. The platform orchestrates multiple AI personas that can seamlessly switch between roles (companion, emergency responder, entertainer, medication nurse) based on user needs and context.

### Key Capabilities

- 🎭 **Multi-Persona System** - Five specialized AI personas with distinct personalities and capabilities
- 📚 **RAG-Powered Intelligence** - Retrieval-Augmented Generation for contextual, knowledge-grounded responses
- 🔄 **Multi-Device Coordination** - Centralized orchestration across multiple devices and locations
- ⚡ **Real-time Interactions** - WebSocket-based communication for instant responses
- 📊 **Analytics & Monitoring** - Comprehensive usage tracking and performance metrics
- ☁️ **Cloud-Native Architecture** - Scalable deployment on Azure Container Apps

---

## 🏗️ Architecture & Design

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                            │
│  ┌──────────────────────────┐    ┌──────────────────────────┐  │
│  │   Streamlit Dashboard    │    │   Device Runtime (RPi)   │  │
│  │   - Admin Interface      │    │   - Voice Interface      │  │
│  │   - Analytics            │    │   - Local Processing     │  │
│  │   - Persona Management   │    │   - Sensor Integration   │  │
│  └──────────┬───────────────┘    └──────────┬───────────────┘  │
└─────────────┼──────────────────────────────┼──────────────────┘
              │                               │
              └───────────────┬───────────────┘
                              │ WebSocket/REST API
┌─────────────────────────────┼──────────────────────────────────┐
│                    Orchestration Layer                          │
│           ┌─────────────────────────────────┐                   │
│           │   FastAPI Backend Service      │                   │
│           │   - Session Management         │                   │
│           │   - Persona Orchestration      │                   │
│           │   - Multi-Device Coordination  │                   │
│           │   - Event Processing           │                   │
│           └─────────┬─────────────┬─────────┘                   │
└─────────────────────┼─────────────┼────────────────────────────┘
                      │             │
         ┌────────────┘             └────────────┐
         │                                       │
┌────────▼──────────────┐          ┌────────────▼────────────────┐
│   Knowledge Layer     │          │      Data Layer             │
│  ┌──────────────────┐ │          │  ┌───────────────────────┐ │
│  │  RAG System      │ │          │  │  PostgreSQL/JSON      │ │
│  │  - ChromaDB      │ │          │  │  - Sessions           │ │
│  │  - Embeddings    │ │          │  │  - Devices            │ │
│  │  - Semantic      │ │          │  │  - Conversations      │ │
│  │    Search        │ │          │  │  - Activity Logs      │ │
│  └──────────────────┘ │          │  └───────────────────────┘ │
│  ┌──────────────────┐ │          │  ┌───────────────────────┐ │
│  │  Document Store  │ │          │  │  Azure Blob Storage   │ │
│  │  - PDF/TXT/DOCX  │ │          │  │  - Documents          │ │
│  │  - Procedures    │ │          │  │  - Vector Store       │ │
│  └──────────────────┘ │          │  └───────────────────────┘ │
└───────────────────────┘          └─────────────────────────────┘
```

### Design Principles

- **Microservices Architecture** - Independent, containerized services
- **Event-Driven Communication** - Async messaging for scalability
- **Persona-Centric Design** - Modular, pluggable persona system
- **RAG-First Approach** - Knowledge-grounded, hallucination-resistant responses
- **Cloud-Native Deployment** - Kubernetes-ready, Azure Container Apps optimized

---

## 🧩 Main Components

### 1. **AI Companion Orchestrator** (Backend Service)

**Location**: `ai-nanny/ai-companion-orchestrator/`

The core backend service built with **FastAPI** that handles:

- **Persona Management** - Load, configure, and orchestrate multiple AI personas
- **Conversation Engine** - Context-aware dialogue management with history
- **RAG System** - Semantic search and knowledge retrieval using ChromaDB
- **Session Management** - Multi-user, multi-device session coordination
- **Device Coordination** - Centralized management of connected devices
- **Event System** - Real-time event processing and distribution
- **Analytics Engine** - Usage tracking, metrics, and reporting

**Tech Stack**: Python 3.11+, FastAPI, ChromaDB, Sentence Transformers, Poetry

### 2. **Interactive Dashboard** (Admin UI)

**Location**: `ai-nanny/dashboard/`

A **Streamlit-based** web interface providing:

- **Device Management** - Monitor and control connected devices
- **Persona Configuration** - Customize and test AI personas
- **Live Simulator** - Test conversations in real-time
- **Analytics Dashboard** - Visualize usage metrics and trends
- **Knowledge Management** - Upload and manage RAG documents
- **RAG Testing Interface** - Test semantic search and retrieval

**Tech Stack**: Python 3.11+, Streamlit, Plotly, Requests

### 3. **RAG Knowledge System**

**Location**: `ai-nanny/ai-companion-orchestrator/core/rag/`

Retrieval-Augmented Generation system featuring:

- **Document Ingestion** - Multi-format support (PDF, TXT, DOCX, MD)
- **Vector Database** - ChromaDB for semantic storage and retrieval
- **Embedding Models** - Configurable (Sentence Transformers, OpenAI)
- **Semantic Search** - Context-aware document retrieval
- **Chunking Strategies** - Optimized text segmentation
- **Query Processing** - Advanced query understanding and expansion

### 4. **Persona Library**

**Location**: `ai-nanny/ai-companion-orchestrator/personas/`

Five specialized AI personas:

| Persona | Purpose | Key Features |
|---------|---------|--------------|
| 🤝 **Companion** | Friendly conversation | Empathy, active listening, general support |
| 🚨 **Emergency** | Critical situations | Medical protocols, emergency response |
| 🎭 **Entertainer** | Joy and engagement | Jokes, games, storytelling |
| 💊 **Medication Nurse** | Medication management | Schedules, reminders, safety checks |
| 📖 **Storyteller** | Engaging narratives | Interactive stories, memory recall |

### 5. **Multi-Device Runtime**

**Location**: `ai-nanny/ai-companion-orchestrator/core/device/`

Device coordination system enabling:

- **Device Registry** - Dynamic device registration and discovery
- **Status Monitoring** - Health checks and heartbeat tracking
- **Session Handoff** - Seamless conversation transfer between devices
- **Conflict Resolution** - Manage simultaneous device interactions

---

## 📦 Installation

### Prerequisites

- **Python 3.11+**
- **Docker** or **Podman** (recommended)
- **Git**
- **Azure CLI** (for cloud deployment)

### Local Development Setup

#### 1. Clone Repository

```bash
git clone <repository-url>
cd AI-Nanny-Project
```

#### 2. Start Backend API

```bash
cd ai-nanny/ai-companion-orchestrator

# Option A: Using Docker Compose (Recommended)
docker-compose up -d

# Option B: Using Poetry
poetry install
poetry run uvicorn api.main:app --reload --port 8000

# Option C: Using pip
pip install -e .
uvicorn api.main:app --reload --port 8000
```

**API Available at**: http://localhost:8000  
**API Documentation**: http://localhost:8000/docs

#### 3. Start Dashboard

```bash
cd ai-nanny/dashboard

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export API_BASE_URL=http://localhost:8000

# Run dashboard
streamlit run app.py
```

**Dashboard Available at**: http://localhost:8501

#### 4. Verify Installation

```bash
# Test API health
curl http://localhost:8000/health

# Test RAG configuration
curl http://localhost:8000/api/v1/knowledge/config

# List available personas
curl http://localhost:8000/api/v1/personas
```

---

## ☁️ Deployment

### Azure Container Apps Deployment

The platform is designed for **Azure Container Apps** with a fully automated deployment script.

#### Prerequisites

```bash
# Install Azure CLI
brew install azure-cli  # macOS
# OR
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash  # Linux

# Login to Azure
az login

# Set your subscription
az account set --subscription <your-subscription-id>

# Verify resource group exists
az group show --name <your-resource-group>
```

#### Deployment Steps

1. **Configure Deployment Script**

Edit `deploy-to-azure.sh` with your Azure details:

```bash
SUBSCRIPTION_ID="<your-subscription-id>"
RESOURCE_GROUP="<your-resource-group>"
LOCATION="eastus"  # or your preferred region
ACR_NAME="<your-acr-name>"
STORAGE_ACCOUNT_NAME="<your-storage-name>"
CONTAINERAPPS_ENV="<your-environment-name>"
```

2. **Run Deployment**

```bash
chmod +x deploy-to-azure.sh
./deploy-to-azure.sh
```

The script will:
- ✅ Create/verify Azure Container Registry
- ✅ Build and push Docker images
- ✅ Create/configure Azure Storage (Blob + File Share)
- ✅ Setup Container Apps Environment
- ✅ Deploy API and Dashboard containers
- ✅ Configure networking and ingress
- ✅ Upload sample documents

3. **Access Your Deployment**

After successful deployment:

```bash
# URLs will be displayed in the output
API URL: https://<your-api>.azurecontainerapps.io
Dashboard URL: https://<your-dashboard>.azurecontainerapps.io
```

#### Deployment Architecture on Azure

```
┌─────────────────────────────────────────────────────────────┐
│                     Azure Cloud                             │
├─────────────────────────────────────────────────────────────┤
│  Container Apps Environment                                 │
│  ┌──────────────────────┐    ┌──────────────────────┐      │
│  │  ai-nanny-api        │    │  ai-nanny-dashboard  │      │
│  │  (FastAPI Backend)   │◄───┤  (Streamlit UI)      │      │
│  │  Port: 8000          │    │  Port: 8501          │      │
│  │  Replicas: 1-3       │    │  Replicas: 1-2       │      │
│  │  CPU: 1.0, Mem: 2Gi  │    │  CPU: 0.5, Mem: 1Gi  │      │
│  └──────────┬───────────┘    └──────────────────────┘      │
├─────────────┼──────────────────────────────────────────────┤
│             │                                               │
│  ┌──────────▼────────────┐    ┌──────────────────────┐    │
│  │  Azure Blob Storage   │    │  Azure File Share    │    │
│  │  - Documents          │    │  - Vector Store      │    │
│  │  - Uploaded files     │    │  - ChromaDB data     │    │
│  └───────────────────────┘    └──────────────────────┘    │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Azure Container Registry                           │  │
│  │  - ai-nanny-api:latest                              │  │
│  │  - ai-nanny-dashboard:latest                        │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

#### Monitoring & Management

```bash
# View API logs
az containerapp logs show --name ai-nanny-api --resource-group <rg-name> --follow

# View Dashboard logs
az containerapp logs show --name ai-nanny-dashboard --resource-group <rg-name> --follow

# Check container status
az containerapp show --name ai-nanny-api --resource-group <rg-name>

# Scale containers
az containerapp update --name ai-nanny-api --resource-group <rg-name> \
  --min-replicas 2 --max-replicas 5
```

### Alternative Deployment Options

#### Docker Compose (Local/Testing)

```bash
cd ai-nanny/ai-companion-orchestrator
docker-compose up -d
```

#### Kubernetes (Coming Soon)

Helm charts for Kubernetes deployment are planned for future releases.

---

## 📚 Documentation

Comprehensive documentation is available in the [ai-nanny/Docs/](ai-nanny/Docs/) directory:

| Document | Description |
|----------|-------------|
| **[QUICK_START.md](ai-nanny/Docs/QUICK_START.md)** | Get started in 5 minutes |
| **[IMPLEMENTATION_GUIDE.md](ai-nanny/Docs/IMPLEMENTATION_GUIDE.md)** | Complete implementation guide |
| **[AZURE_DEPLOYMENT_GUIDE.md](ai-nanny/Docs/AZURE_DEPLOYMENT_GUIDE.md)** | Azure deployment details |
| **[RAG_QUICK_START.md](ai-nanny/Docs/RAG_QUICK_START.md)** | RAG system setup |
| **[RAG_IMPLEMENTATION_GUIDE.md](ai-nanny/Docs/RAG_IMPLEMENTATION_GUIDE.md)** | Advanced RAG configuration |
| **[DEPLOYMENT_TROUBLESHOOTING.md](ai-nanny/Docs/DEPLOYMENT_TROUBLESHOOTING.md)** | Troubleshooting guide |

---

## 🎯 Use Cases

- **Nursing Homes** - 24/7 AI companionship for residents
- **Home Care** - Remote monitoring and engagement
- **Assisted Living** - Medication management and emergency response
- **Memory Care** - Cognitive stimulation and routine support
- **Healthcare Facilities** - Patient engagement and support

---

## 🛣️ Roadmap

- [ ] Multi-language support (Spanish, French, German)
- [ ] Voice integration (speech-to-text, text-to-speech)
- [ ] Mobile app for caregivers
- [ ] Advanced analytics and reporting
- [ ] Integration with EHR systems
- [ ] Emotion detection and sentiment analysis
- [ ] Kubernetes Helm charts
- [ ] Fine-tuning pipeline for custom personas

---

## 🤝 Contributing

This is an internal IBM project. For contributions or questions, please contact the project team.

---

## 📄 License

Internal IBM Project - All Rights Reserved

---

## 🔗 Quick Links

- **[📖 Quick Start Guide](ai-nanny/Docs/QUICK_START.md)** - Start developing in 5 minutes
- **[☁️ Azure Deployment](ai-nanny/Docs/AZURE_DEPLOYMENT_GUIDE.md)** - Deploy to Azure
- **[🔧 Troubleshooting](ai-nanny/Docs/DEPLOYMENT_TROUBLESHOOTING.md)** - Fix common issues
- **[📚 RAG System](ai-nanny/Docs/RAG_QUICK_START.md)** - Setup knowledge base

---

**Status**: Active Development | **Version**: 1.0 | **Last Updated**: January 2026
