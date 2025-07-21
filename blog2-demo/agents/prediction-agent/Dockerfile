FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules
COPY ../shared ./shared

# Copy agent files
COPY prediction_agent.py .
COPY main.py .

# Expose port
EXPOSE 8007

# Run the agent
CMD ["python", "main.py"] 