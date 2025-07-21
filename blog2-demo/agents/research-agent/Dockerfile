FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy shared requirements and install
COPY agents/shared/requirements.txt /app/shared/requirements.txt
RUN pip install --no-cache-dir -r /app/shared/requirements.txt

# Copy agent-specific requirements and install
COPY agents/research-agent/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt || true

# Copy shared modules
COPY agents/shared/ /app/shared/

# Copy agent files
COPY agents/research-agent/ /app/

# Expose port
EXPOSE 8083

# Run the agent
CMD ["python", "main.py"]
