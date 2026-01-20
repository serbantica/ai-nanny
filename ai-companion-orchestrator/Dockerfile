FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml poetry.lock* ./

# Install Poetry and dependencies
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi || \
    (pip install --no-cache-dir fastapi uvicorn pydantic pydantic-settings httpx \
     chromadb sentence-transformers torch pypdf2 langchain langchain-community tiktoken && \
     echo "Installed via pip fallback")

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/vector_store data/documents

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Start application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
