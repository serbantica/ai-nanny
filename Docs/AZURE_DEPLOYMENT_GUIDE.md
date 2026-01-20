# Azure Cloud Deployment Guide

## 🚀 Deploy AI-Nanny RAG System to Azure (IBM Subscription)

### Prerequisites

**Azure Subscription Information:**
- **Subscription ID:** `61c73643-16a0-423c-979c-32cd61ff664d`
- **Resource Group:** `ST-multi-agent-edge-platform`
- **Region:** `eastus` (or your preferred region)

**Required Tools:**
```bash
# Install Azure CLI
brew install azure-cli  # macOS
# OR
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash  # Linux

# Verify installation
az --version

# Login to Azure
az login

# Set subscription
az account set --subscription 61c73643-16a0-423c-979c-32cd61ff664d

# Verify resource group exists
az group show --name ST-multi-agent-edge-platform
```

---

## 📋 Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Azure Cloud                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐         ┌──────────────────┐        │
│  │  Container App   │         │  Container App   │        │
│  │  (FastAPI API)   │◄────────┤  (Streamlit UI)  │        │
│  │  Port: 8000      │         │  Port: 8501      │        │
│  └────────┬─────────┘         └──────────────────┘        │
│           │                                                 │
│           ▼                                                 │
│  ┌──────────────────┐         ┌──────────────────┐        │
│  │  Azure Blob      │         │  Azure Container │        │
│  │  Storage         │         │  Registry        │        │
│  │  (Documents)     │         │  (Docker Images) │        │
│  └──────────────────┘         └──────────────────┘        │
│                                                             │
│  ┌──────────────────────────────────────────────┐         │
│  │  Azure File Share (ChromaDB Vector Store)    │         │
│  └──────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🐳 Step 1: Containerize Applications

### 1.1 Create Dockerfile for FastAPI Backend

Create `ai-nanny/ai-companion-orchestrator/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml .

# Install Python dependencies
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/vector_store data/documents

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 1.2 Create Dockerfile for Streamlit Dashboard

Create `ai-nanny/dashboard/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Start Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 1.3 Create .dockerignore files

Create `ai-nanny/ai-companion-orchestrator/.dockerignore`:
```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
.env
*.log
.git/
.gitignore
*.md
tests/
.pytest_cache/
data/vector_store/*
data/documents/*
```

Create `ai-nanny/dashboard/.dockerignore`:
```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
.env
*.log
.git/
.gitignore
*.md
```

---

## 🏗️ Step 2: Build and Push Docker Images

```bash
# Set variables
SUBSCRIPTION_ID="61c73643-16a0-423c-979c-32cd61ff664d"
RESOURCE_GROUP="ST-multi-agent-edge-platform"
LOCATION="eastus"
ACR_NAME="stainannyreg"  # Must be globally unique, lowercase, alphanumeric
PROJECT_NAME="ai-nanny"

# Create Azure Container Registry
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --location $LOCATION

# Login to ACR
az acr login --name $ACR_NAME

# Get ACR login server
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer --output tsv)
echo "ACR Login Server: $ACR_LOGIN_SERVER"

# Build and push backend image
cd ai-nanny/ai-companion-orchestrator
docker build -t $ACR_LOGIN_SERVER/ai-nanny-api:latest .
docker push $ACR_LOGIN_SERVER/ai-nanny-api:latest

# Build and push dashboard image
cd ../dashboard
docker build -t $ACR_LOGIN_SERVER/ai-nanny-dashboard:latest .
docker push $ACR_LOGIN_SERVER/ai-nanny-dashboard:latest

# Verify images
az acr repository list --name $ACR_NAME --output table
```

---

## ☁️ Step 3: Create Azure Storage for Documents & Vector Store

```bash
# Create Storage Account
STORAGE_ACCOUNT_NAME="stainannystore"  # Must be globally unique, lowercase
az storage account create \
  --name $STORAGE_ACCOUNT_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS

# Get storage connection string
STORAGE_CONNECTION_STRING=$(az storage account show-connection-string \
  --name $STORAGE_ACCOUNT_NAME \
  --resource-group $RESOURCE_GROUP \
  --query connectionString \
  --output tsv)

# Create blob container for documents
az storage container create \
  --name documents \
  --connection-string "$STORAGE_CONNECTION_STRING"

# Create file share for vector store (ChromaDB)
az storage share create \
  --name vectorstore \
  --connection-string "$STORAGE_CONNECTION_STRING" \
  --quota 10  # 10GB quota

echo "Storage Connection String: $STORAGE_CONNECTION_STRING"
```

---

## 🚢 Step 4: Deploy to Azure Container Apps

### 4.1 Create Container Apps Environment

```bash
# Install Container Apps extension
az extension add --name containerapp --upgrade

# Create Container Apps environment
CONTAINERAPPS_ENV="ai-nanny-env"
az containerapp env create \
  --name $CONTAINERAPPS_ENV \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Create storage mount for vector store
az containerapp env storage set \
  --name $CONTAINERAPPS_ENV \
  --resource-group $RESOURCE_GROUP \
  --storage-name vectorstore \
  --azure-file-account-name $STORAGE_ACCOUNT_NAME \
  --azure-file-account-key $(az storage account keys list \
    --account-name $STORAGE_ACCOUNT_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "[0].value" -o tsv) \
  --azure-file-share-name vectorstore \
  --access-mode ReadWrite
```

### 4.2 Deploy FastAPI Backend

```bash
# Enable ACR admin credentials
az acr update --name $ACR_NAME --admin-enabled true

# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value --output tsv)

# Deploy backend API
az containerapp create \
  --name ai-nanny-api \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINERAPPS_ENV \
  --image $ACR_LOGIN_SERVER/ai-nanny-api:latest \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --target-port 8000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 1.0 \
  --memory 2Gi \
  --env-vars \
    "APP_ENV=production" \
    "RAG_EMBEDDING_PROVIDER=sentence-transformers" \
    "RAG_EMBEDDING_MODEL=all-MiniLM-L6-v2" \
    "RAG_EMBEDDING_DIMENSION=384" \
    "RAG_VECTOR_STORE_PATH=/mnt/vectorstore" \
    "AZURE_STORAGE_CONNECTION_STRING=$STORAGE_CONNECTION_STRING"

# Mount vector store volume
az containerapp update \
  --name ai-nanny-api \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars "RAG_VECTOR_STORE_PATH=/mnt/vectorstore" \
  --volume-name vectorstore \
  --volume-type StorageMountType.AzureFile \
  --volume-storage-name vectorstore \
  --volume-mount-path /mnt/vectorstore

# Get API URL
API_URL=$(az containerapp show \
  --name ai-nanny-api \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

echo "✅ API deployed at: https://$API_URL"
```

### 4.3 Deploy Streamlit Dashboard

```bash
# Deploy dashboard
az containerapp create \
  --name ai-nanny-dashboard \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINERAPPS_ENV \
  --image $ACR_LOGIN_SERVER/ai-nanny-dashboard:latest \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --target-port 8501 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 2 \
  --cpu 0.5 \
  --memory 1Gi \
  --env-vars \
    "API_BASE_URL=https://$API_URL"

# Get Dashboard URL
DASHBOARD_URL=$(az containerapp show \
  --name ai-nanny-dashboard \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

echo "✅ Dashboard deployed at: https://$DASHBOARD_URL"
```

---

## 🔐 Step 5: Configure Secrets & Environment Variables

### 5.1 Create Azure Key Vault

```bash
# Create Key Vault
KEY_VAULT_NAME="st-ai-nanny-kv"
az keyvault create \
  --name $KEY_VAULT_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Store secrets
az keyvault secret set \
  --vault-name $KEY_VAULT_NAME \
  --name "openai-api-key" \
  --value "your-openai-key-if-using-openai"

az keyvault secret set \
  --vault-name $KEY_VAULT_NAME \
  --name "app-secret-key" \
  --value "$(openssl rand -hex 32)"

az keyvault secret set \
  --vault-name $KEY_VAULT_NAME \
  --name "storage-connection-string" \
  --value "$STORAGE_CONNECTION_STRING"
```

### 5.2 Grant Container Apps Access to Key Vault

```bash
# Get Container App identity
API_IDENTITY=$(az containerapp show \
  --name ai-nanny-api \
  --resource-group $RESOURCE_GROUP \
  --query identity.principalId \
  --output tsv)

# Grant access
az keyvault set-policy \
  --name $KEY_VAULT_NAME \
  --object-id $API_IDENTITY \
  --secret-permissions get list
```

---

## 📊 Step 6: Upload Sample Documents

```bash
# Upload sample documents to blob storage
cd ai-nanny/ai-companion-orchestrator/data/documents

az storage blob upload \
  --container-name documents \
  --file emergency_protocols.md \
  --name emergency_protocols.md \
  --connection-string "$STORAGE_CONNECTION_STRING"

az storage blob upload \
  --container-name documents \
  --file activity_guidelines.md \
  --name activity_guidelines.md \
  --connection-string "$STORAGE_CONNECTION_STRING"

az storage blob upload \
  --container-name documents \
  --file health_kinetics_procedures.md \
  --name health_kinetics_procedures.md \
  --connection-string "$STORAGE_CONNECTION_STRING"

# Verify uploads
az storage blob list \
  --container-name documents \
  --connection-string "$STORAGE_CONNECTION_STRING" \
  --output table
```

---

## 🧪 Step 7: Test Deployment

```bash
# Test API health
curl https://$API_URL/health

# Test API devices endpoint
curl https://$API_URL/api/v1/devices

# Test RAG config
curl https://$API_URL/api/v1/knowledge/config

# Open dashboard in browser
echo "Dashboard URL: https://$DASHBOARD_URL"
```

---

## 🔄 Step 8: Set Up CI/CD with GitHub Actions (Optional)

Create `.github/workflows/azure-deploy.yml`:

```yaml
name: Deploy to Azure

on:
  push:
    branches: [ main ]
  workflow_dispatch:

env:
  AZURE_SUBSCRIPTION_ID: 61c73643-16a0-423c-979c-32cd61ff664d
  RESOURCE_GROUP: ST-multi-agent-edge-platform
  ACR_NAME: stainannyreg
  
jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Azure Login
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Build and Push API Image
      run: |
        az acr login --name ${{ env.ACR_NAME }}
        cd ai-nanny/ai-companion-orchestrator
        docker build -t ${{ env.ACR_NAME }}.azurecr.io/ai-nanny-api:${{ github.sha }} .
        docker push ${{ env.ACR_NAME }}.azurecr.io/ai-nanny-api:${{ github.sha }}
    
    - name: Build and Push Dashboard Image
      run: |
        cd ai-nanny/dashboard
        docker build -t ${{ env.ACR_NAME }}.azurecr.io/ai-nanny-dashboard:${{ github.sha }} .
        docker push ${{ env.ACR_NAME }}.azurecr.io/ai-nanny-dashboard:${{ github.sha }}
    
    - name: Deploy to Container Apps
      run: |
        az containerapp update \
          --name ai-nanny-api \
          --resource-group ${{ env.RESOURCE_GROUP }} \
          --image ${{ env.ACR_NAME }}.azurecr.io/ai-nanny-api:${{ github.sha }}
        
        az containerapp update \
          --name ai-nanny-dashboard \
          --resource-group ${{ env.RESOURCE_GROUP }} \
          --image ${{ env.ACR_NAME }}.azurecr.io/ai-nanny-dashboard:${{ github.sha }}
```

---

## 📈 Step 9: Monitoring & Logging

### 9.1 Enable Application Insights

```bash
# Create Application Insights
APP_INSIGHTS_NAME="ai-nanny-insights"
az monitor app-insights component create \
  --app $APP_INSIGHTS_NAME \
  --location $LOCATION \
  --resource-group $RESOURCE_GROUP \
  --application-type web

# Get instrumentation key
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --app $APP_INSIGHTS_NAME \
  --resource-group $RESOURCE_GROUP \
  --query instrumentationKey \
  --output tsv)

# Update container apps with instrumentation key
az containerapp update \
  --name ai-nanny-api \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars "APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=$INSTRUMENTATION_KEY"
```

### 9.2 View Logs

```bash
# Stream API logs
az containerapp logs show \
  --name ai-nanny-api \
  --resource-group $RESOURCE_GROUP \
  --follow

# Stream Dashboard logs
az containerapp logs show \
  --name ai-nanny-dashboard \
  --resource-group $RESOURCE_GROUP \
  --follow

# View metrics
az monitor metrics list \
  --resource $(az containerapp show \
    --name ai-nanny-api \
    --resource-group $RESOURCE_GROUP \
    --query id -o tsv) \
  --metric Requests
```

---

## 💰 Step 10: Cost Optimization

### Estimated Monthly Costs (Basic Tier)

| Resource | Configuration | Est. Cost/Month |
|----------|--------------|-----------------|
| Container Apps (API) | 1-3 replicas, 1vCPU, 2GB | $30-90 |
| Container Apps (Dashboard) | 1-2 replicas, 0.5vCPU, 1GB | $15-30 |
| Azure Container Registry | Basic tier | $5 |
| Azure Storage (Blob + File) | 10GB | $2-3 |
| Application Insights | Basic monitoring | $0-5 |
| **Total** | | **~$52-133/month** |

### Cost Optimization Tips

1. **Scale to Zero** (for dev/test):
```bash
az containerapp update \
  --name ai-nanny-dashboard \
  --resource-group $RESOURCE_GROUP \
  --min-replicas 0 \
  --max-replicas 1
```

2. **Use Azure Cost Management**:
```bash
# Set budget alerts
az consumption budget create \
  --amount 100 \
  --budget-name ai-nanny-budget \
  --category Cost \
  --time-grain Monthly \
  --time-period "{'start-date':'2026-01-01'}"
```

3. **Stop non-production environments**:
```bash
# Stop dashboard when not in use
az containerapp revision set-mode \
  --name ai-nanny-dashboard \
  --resource-group $RESOURCE_GROUP \
  --mode single
```

---

## 🔧 Troubleshooting

### Issue: Container fails to start

```bash
# Check logs
az containerapp logs show \
  --name ai-nanny-api \
  --resource-group $RESOURCE_GROUP \
  --tail 100

# Check revision status
az containerapp revision list \
  --name ai-nanny-api \
  --resource-group $RESOURCE_GROUP \
  --output table
```

### Issue: Cannot connect to API

```bash
# Check ingress configuration
az containerapp show \
  --name ai-nanny-api \
  --resource-group $RESOURCE_GROUP \
  --query "properties.configuration.ingress"

# Test health endpoint
curl https://$API_URL/health
```

### Issue: Vector store not persisting

```bash
# Verify storage mount
az containerapp show \
  --name ai-nanny-api \
  --resource-group $RESOURCE_GROUP \
  --query "properties.template.volumes"

# Check file share
az storage file list \
  --share-name vectorstore \
  --connection-string "$STORAGE_CONNECTION_STRING"
```

---

## 🎯 Production Checklist

- [ ] Enable HTTPS (Container Apps provides automatic SSL)
- [ ] Set up custom domain (optional)
- [ ] Configure authentication (Azure AD)
- [ ] Enable auto-scaling rules
- [ ] Set up alerts and monitoring
- [ ] Configure backup strategy
- [ ] Document API endpoints
- [ ] Test disaster recovery
- [ ] Security scanning (Azure Defender)
- [ ] Compliance review

---

## 🚀 Quick Deployment Script

Save as `deploy-to-azure.sh`:

```bash
#!/bin/bash
set -e

# Configuration
SUBSCRIPTION_ID="61c73643-16a0-423c-979c-32cd61ff664d"
RESOURCE_GROUP="ST-multi-agent-edge-platform"
LOCATION="eastus"
ACR_NAME="stainannyreg"
STORAGE_ACCOUNT_NAME="stainannystore"
CONTAINERAPPS_ENV="ai-nanny-env"

echo "🚀 Deploying AI-Nanny to Azure..."

# Set subscription
az account set --subscription $SUBSCRIPTION_ID

# Create ACR
echo "📦 Creating Azure Container Registry..."
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --location $LOCATION

# Build and push images
echo "🐳 Building and pushing Docker images..."
az acr login --name $ACR_NAME
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)

cd ai-nanny/ai-companion-orchestrator
docker build -t $ACR_LOGIN_SERVER/ai-nanny-api:latest .
docker push $ACR_LOGIN_SERVER/ai-nanny-api:latest

cd ../dashboard
docker build -t $ACR_LOGIN_SERVER/ai-nanny-dashboard:latest .
docker push $ACR_LOGIN_SERVER/ai-nanny-dashboard:latest

cd ../..

# Create storage
echo "💾 Creating storage account..."
az storage account create \
  --name $STORAGE_ACCOUNT_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS

STORAGE_CONNECTION_STRING=$(az storage account show-connection-string \
  --name $STORAGE_ACCOUNT_NAME \
  --resource-group $RESOURCE_GROUP \
  --query connectionString -o tsv)

az storage container create --name documents --connection-string "$STORAGE_CONNECTION_STRING"
az storage share create --name vectorstore --connection-string "$STORAGE_CONNECTION_STRING"

# Create Container Apps environment
echo "☁️ Creating Container Apps environment..."
az containerapp env create \
  --name $CONTAINERAPPS_ENV \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Deploy applications
echo "🚢 Deploying applications..."
az acr update --name $ACR_NAME --admin-enabled true
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)

az containerapp create \
  --name ai-nanny-api \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINERAPPS_ENV \
  --image $ACR_LOGIN_SERVER/ai-nanny-api:latest \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --target-port 8000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 1.0 \
  --memory 2Gi

API_URL=$(az containerapp show --name ai-nanny-api --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv)

az containerapp create \
  --name ai-nanny-dashboard \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINERAPPS_ENV \
  --image $ACR_LOGIN_SERVER/ai-nanny-dashboard:latest \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --target-port 8501 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 2 \
  --cpu 0.5 \
  --memory 1Gi \
  --env-vars "API_BASE_URL=https://$API_URL"

DASHBOARD_URL=$(az containerapp show --name ai-nanny-dashboard --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv)

echo "✅ Deployment complete!"
echo "📍 API URL: https://$API_URL"
echo "📍 Dashboard URL: https://$DASHBOARD_URL"
```

Make it executable:
```bash
chmod +x deploy-to-azure.sh
./deploy-to-azure.sh
```

---

## 📚 Additional Resources

- [Azure Container Apps Documentation](https://docs.microsoft.com/azure/container-apps/)
- [Azure Container Registry](https://docs.microsoft.com/azure/container-registry/)
- [Azure Storage Documentation](https://docs.microsoft.com/azure/storage/)
- [Azure CLI Reference](https://docs.microsoft.com/cli/azure/)

---

## 🆘 Support

For deployment issues:
1. Check Azure Portal logs
2. Review Container App revision history
3. Test locally with Docker first
4. Contact IBM Azure support team

**Azure Portal:** https://portal.azure.com
**Resource Group:** ST-multi-agent-edge-platform
**Subscription:** 61c73643-16a0-423c-979c-32cd61ff664d
