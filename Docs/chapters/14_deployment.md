## 14. Deployment - Full Implementation

### 14.1 Deployment Overview

The platform is deployed as:
- **Control Plane**: Cloud-hosted (AWS/Azure)
- **Edge Devices**: Raspberry Pi running device agent

### 14.2 Control Plane Deployment

#### Docker Production Build

```dockerfile
# Dockerfile
FROM python:3.11-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY core/ ./core/
COPY api/ ./api/
COPY db/ ./db/
COPY personas/ ./personas/

# Production stage
FROM base as production

ENV PYTHONUNBUFFERED=1
ENV APP_ENV=production

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### Docker Compose Production

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    image: ai-companion-api:latest
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY}
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1'
          memory: 1G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - ai-companion-prod

  worker:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    command: celery -A core.tasks worker --loglevel=info --concurrency=4
    environment:
      - APP_ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    deploy:
      replicas: 2
    networks:
      - ai-companion-prod

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - api
    networks:
      - ai-companion-prod

networks:
  ai-companion-prod:
    driver: overlay
```

#### Nginx Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream api_servers {
        server api:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;

    server {
        listen 80;
        server_name api.ai-companion.io;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name api.ai-companion.io;

        ssl_certificate /etc/nginx/certs/fullchain.pem;
        ssl_certificate_key /etc/nginx/certs/privkey.pem;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # API routes
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            
            proxy_pass http://api_servers;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # WebSocket routes
        location /ws/ {
            proxy_pass http://api_servers;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_read_timeout 86400;
        }

        # Health check
        location /health {
            proxy_pass http://api_servers;
        }
    }
}
```

### 14.3 Cloud Infrastructure (AWS)

#### Terraform Configuration

```hcl
# terraform/main.tf
provider "aws" {
  region = var.aws_region
}

# VPC
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  
  name = "ai-companion-vpc"
  cidr = "10.0.0.0/16"
  
  azs             = ["${var.aws_region}a", "${var.aws_region}b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]
  
  enable_nat_gateway = true
  single_nat_gateway = true
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "ai-companion-cluster"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# RDS PostgreSQL
resource "aws_db_instance" "postgres" {
  identifier        = "ai-companion-db"
  engine            = "postgres"
  engine_version    = "16"
  instance_class    = "db.t3.medium"
  allocated_storage = 20
  
  db_name  = "ai_companion"
  username = var.db_username
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 7
  multi_az               = true
  skip_final_snapshot    = false
}

# ElastiCache Redis
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "ai-companion-redis"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
  
  security_group_ids = [aws_security_group.redis.id]
  subnet_group_name  = aws_elasticache_subnet_group.main.name
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "ai-companion-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = module.vpc.public_subnets
}

# ECS Service
resource "aws_ecs_service" "api" {
  name            = "ai-companion-api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = 2
  launch_type     = "FARGATE"
  
  network_configuration {
    subnets         = module.vpc.private_subnets
    security_groups = [aws_security_group.ecs.id]
  }
  
  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "api"
    container_port   = 8000
  }
}
```

### 14.4 Edge Device Deployment

#### Device Setup Script

```bash
#!/bin/bash
# scripts/setup_device.sh
# Run on Raspberry Pi to configure device agent

set -e

echo "=== AI Companion Device Setup ==="

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    portaudio19-dev \
    libffi-dev \
    libssl-dev

# Create application directory
sudo mkdir -p /opt/ai-companion
sudo chown $USER:$USER /opt/ai-companion
cd /opt/ai-companion

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install device agent
pip install --upgrade pip
pip install -r requirements.txt

# Configure environment
cat > .env << EOF
DEVICE_ID=${DEVICE_ID:-$(cat /sys/class/net/eth0/address | tr -d ':')}
DEVICE_NAME=${DEVICE_NAME:-ai-companion-device}
CONTROL_PLANE_URL=${CONTROL_PLANE_URL:-wss://api.ai-companion.io/ws}
DEVICE_AUTH_TOKEN=${DEVICE_AUTH_TOKEN}
AUDIO_SAMPLE_RATE=16000
AUDIO_CHANNELS=1
CACHE_DIR=/var/cache/ai-companion
EOF

# Create cache directory
sudo mkdir -p /var/cache/ai-companion
sudo chown $USER:$USER /var/cache/ai-companion

# Create systemd service
sudo cat > /etc/systemd/system/ai-companion.service << EOF
[Unit]
Description=AI Companion Device Agent
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/ai-companion
EnvironmentFile=/opt/ai-companion/.env
ExecStart=/opt/ai-companion/venv/bin/python -m device_agent.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable ai-companion
sudo systemctl start ai-companion

echo "=== Setup Complete ==="
echo "Device ID: $(cat .env | grep DEVICE_ID | cut -d= -f2)"
echo "Service Status: $(sudo systemctl status ai-companion --no-pager | head -3)"
```

#### Device Registration

```bash
#!/bin/bash
# scripts/register_device.sh
# Register device with control plane

API_URL="${CONTROL_PLANE_URL:-https://api.ai-companion.io}"
ADMIN_TOKEN="${ADMIN_API_TOKEN}"
DEVICE_NAME="${1:-ai-companion-$(hostname)}"
DEVICE_TYPE="${2:-raspberry_pi}"

response=$(curl -s -X POST "${API_URL}/api/v1/devices" \
    -H "Authorization: Bearer ${ADMIN_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{
        \"name\": \"${DEVICE_NAME}\",
        \"device_type\": \"${DEVICE_TYPE}\",
        \"capabilities\": [\"audio_input\", \"audio_output\", \"buttons\", \"leds\"]
    }")

DEVICE_ID=$(echo $response | jq -r '.device_id')
AUTH_TOKEN=$(echo $response | jq -r '.auth_token')

echo "Device registered successfully!"
echo "DEVICE_ID=${DEVICE_ID}"
echo "DEVICE_AUTH_TOKEN=${AUTH_TOKEN}"

# Update local config
echo "DEVICE_AUTH_TOKEN=${AUTH_TOKEN}" >> /opt/ai-companion/.env
sudo systemctl restart ai-companion
```

### 14.5 Monitoring & Observability

#### Prometheus Metrics

```python
# core/monitoring/metrics.py
"""Prometheus metrics for monitoring."""

from prometheus_client import Counter, Histogram, Gauge

# Request metrics
REQUEST_COUNT = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'api_request_latency_seconds',
    'API request latency',
    ['method', 'endpoint']
)

# Persona metrics
PERSONA_SWITCH_COUNT = Counter(
    'persona_switches_total',
    'Total persona switches',
    ['from_persona', 'to_persona']
)

PERSONA_SWITCH_LATENCY = Histogram(
    'persona_switch_latency_seconds',
    'Persona switch latency',
    ['persona_id']
)

# Device metrics
ACTIVE_DEVICES = Gauge(
    'active_devices',
    'Number of currently connected devices'
)

DEVICE_SESSIONS = Gauge(
    'active_sessions',
    'Number of active sessions',
    ['device_id']
)

# LLM metrics
LLM_REQUESTS = Counter(
    'llm_requests_total',
    'Total LLM API requests',
    ['provider', 'model', 'status']
)

LLM_LATENCY = Histogram(
    'llm_request_latency_seconds',
    'LLM API request latency',
    ['provider', 'model']
)

LLM_TOKENS = Counter(
    'llm_tokens_total',
    'Total LLM tokens used',
    ['provider', 'type']  # type: input/output
)
```

#### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "AI Companion Platform",
    "panels": [
      {
        "title": "Active Devices",
        "type": "stat",
        "targets": [{"expr": "active_devices"}]
      },
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [{"expr": "rate(api_requests_total[5m])"}]
      },
      {
        "title": "Persona Switch Latency (p95)",
        "type": "graph",
        "targets": [{"expr": "histogram_quantile(0.95, rate(persona_switch_latency_seconds_bucket[5m]))"}]
      },
      {
        "title": "LLM Costs (Tokens/Hour)",
        "type": "graph",
        "targets": [{"expr": "rate(llm_tokens_total[1h])"}]
      }
    ]
  }
}
```

### 14.6 Security Checklist

| Item | Status | Notes |
|------|--------|-------|
| TLS everywhere | Required | All API and WebSocket traffic |
| API key rotation | Required | 90-day rotation policy |
| JWT token expiry | Required | 24-hour expiry |
| Device authentication | Required | Per-device tokens |
| Rate limiting | Required | 100 req/min per device |
| Input validation | Required | Pydantic schemas |
| Secrets management | Required | AWS Secrets Manager / Vault |
| Audit logging | Required | All auth and admin actions |
| Vulnerability scanning | Required | Weekly container scans |

### 14.7 Deployment Checklist

#### Pre-Deployment
- [ ] All tests passing
- [ ] Security scan completed
- [ ] Database migrations tested
- [ ] Secrets configured in production vault
- [ ] SSL certificates valid
- [ ] Monitoring dashboards configured

#### Deployment
- [ ] Database backup completed
- [ ] Run migrations
- [ ] Deploy new containers
- [ ] Verify health checks
- [ ] Smoke test critical paths
- [ ] Monitor error rates

#### Post-Deployment
- [ ] Verify metrics flowing
- [ ] Check for anomalies
- [ ] Update runbook if needed
- [ ] Notify stakeholders

---
