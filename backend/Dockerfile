FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for gRPC (required by Google Cloud SDKs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Cloud Run injects $PORT at runtime (default 8080)
ENV PORT=8080

# Run with uvicorn — stateless workers, no sticky sessions
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers 4
