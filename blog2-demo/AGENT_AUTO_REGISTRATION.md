# Agent Auto-Registration

This document describes the auto-registration functionality implemented for agents in the Agent Oriented Architecture demo.

## Overview

Agents automatically register themselves with the A2A Registry when they start up, making them immediately discoverable without manual configuration. This enables dynamic agent addition and removal at runtime.

## Implementation Details

### Environment Variables

Each agent uses the following environment variables for configuration:

- `AGENT_ID` - Unique identifier for the agent (e.g., "data-agent-001")
- `AGENT_PORT` - Port the agent listens on (e.g., 8081)
- `A2A_REGISTRY_URL` - URL of the A2A Registry (e.g., "http://backend:8000")

### Registration Process

1. **On Startup**: When an agent starts, the `StandardAgentRunner` automatically initiates registration
2. **Agent Card**: The agent sends its capabilities and metadata to the registry:
   ```json
   {
     "id": "data-agent-001",
     "name": "Data Agent",
     "type": "data",
     "description": "Provides data access and analysis",
     "endpoint": "http://data-agent:8081",
     "capabilities": [...],
     "version": "1.0.0",
     "metadata": {
       "container": true,
       "started_at": "2025-01-21T10:00:00Z"
     }
   }
   ```

3. **Retry Mechanism**: If registration fails, the agent retries with exponential backoff:
   - Initial retry: 1 second
   - Subsequent retries: 2s, 4s, 8s, 16s, 32s
   - Maximum interval: 60 seconds
   - Retries continue indefinitely until successful

### Health Endpoint

The `/health` endpoint reflects the registration status:

```json
{
  "status": "healthy",
  "registration_status": "registered",
  "registration_attempts": 3,
  "registration_error": null,
  ...
}
```

Status values:
- `pending` - Registration not yet attempted
- `registered` - Successfully registered with A2A Registry
- `failed` - Registration failed (though retries continue)

The overall health status is `degraded` if the agent is not registered.

## Usage

### Docker Compose

Agents are configured in `docker-compose.yml`:

```yaml
data-agent:
  environment:
    - AGENT_ID=data-agent-001
    - AGENT_PORT=8081
    - A2A_REGISTRY_URL=http://backend:8000
```

### Testing Registration

Use the provided test script to verify registration:

```bash
python test_auto_registration.py
```

This will:
- Check each agent's health endpoint
- Verify registration status
- List all registered agents in the A2A Registry

### Monitoring

To monitor agent registration:

```bash
# Check specific agent health
curl http://localhost:8081/health

# List all registered agents
curl http://localhost:8000/api/registry/agents

# Watch agent logs
docker compose logs -f data-agent
```

## Benefits

1. **Zero Configuration**: Agents register automatically on startup
2. **Dynamic Discovery**: New agents are immediately discoverable
3. **Resilience**: Retry mechanism handles temporary network issues
4. **Observability**: Health endpoints provide registration status
5. **Scalability**: Easy to add new agents without modifying the backend

## Adding New Agents

To add a new agent:

1. Create the agent implementation using `UnifiedBaseAgent`
2. Use `StandardAgentRunner` to run the agent
3. Configure environment variables in docker-compose.yml
4. Start the agent - it will auto-register

Example:

```python
# prediction_agent.py
from shared.standard_agent_runner import StandardAgentRunner
from prediction_agent import PredictionAgent

async def main():
    runner = StandardAgentRunner(PredictionAgent)
    await runner.run()
```

The agent will automatically register and become available for semantic discovery.