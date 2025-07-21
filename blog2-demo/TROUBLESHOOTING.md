# Troubleshooting Guide

## Query Processing Issues

### Problem: "Processing query" but nothing happens

This usually means the orchestration request is failing. Here's how to debug:

### 1. Check Agent Registration

First, verify all agents are registered:

```bash
curl http://localhost:8000/api/registry/agents
```

You should see 5 agents registered. If not, check:
- Agent containers are running: `docker compose ps`
- Agent logs: `docker compose logs data-agent`
- Registration errors in agent logs

### 2. Test Individual Agents

Test direct communication with each agent:

```bash
# Test data agent
curl http://localhost:8000/api/debug/test-agent/data-agent-001

# Test GUI agent
curl http://localhost:8000/api/debug/test-agent/gui-agent-001
```

### 3. Check Health Status

```bash
curl http://localhost:8000/health
```

Should show:
- `registered_agents`: 5 or more
- All services as `true`

### 4. Monitor WebSocket Messages

1. Open browser developer console
2. Go to Network tab
3. Filter by WS (WebSocket)
4. Look for `/ws` connection
5. Check Messages tab for agent communication

### 5. Common Issues and Solutions

#### Agents Not Registering
- **Issue**: Agents show 0 in health check
- **Solution**: 
  ```bash
  # Restart agents
  docker compose restart data-agent viz-agent research-agent narrative-agent gui-agent
  ```

#### GUI Agent Not Found
- **Issue**: Error "Agent gui-agent-001 not found in registry"
- **Solution**: GUI agent may have failed to start. Check logs:
  ```bash
  docker compose logs gui-agent
  ```

#### No LLM Response
- **Issue**: Agents return basic responses without AI
- **Solution**: Check .env files have valid ANTHROPIC_API_KEY

#### WebSocket Not Connecting
- **Issue**: Agent Communication panel shows "Disconnected"
- **Solution**: 
  - Check NEXT_PUBLIC_WS_URL in frontend .env
  - Ensure it's set to `ws://localhost:8000`

### 6. Debug Mode

Enable debug logging by adding to agent .env files:
```
LOG_LEVEL=DEBUG
```

### 7. Test Queries

Start with simple queries:
1. "list countries" - Tests data agent
2. "show a chart" - Tests viz agent
3. "research solar energy" - Tests research agent

### 8. Manual Agent Test

Test agent endpoints directly:

```bash
# Test data agent health
curl http://localhost:8081/health

# Test data agent tools
curl http://localhost:8081/tools
```

### 9. Check A2A Message Flow

```bash
# Get message history
curl http://localhost:8000/api/a2a/messages?limit=10
```

### 10. Full System Reset

If nothing works:

```bash
# Stop everything
docker compose down

# Remove volumes
docker compose down -v

# Rebuild and start
docker compose up --build
```

## Debugging Orchestration

To see what's happening during orchestration:

1. Open browser console (F12)
2. Submit a query
3. Look for:
   - "Orchestration result:" log
   - Network requests to `/api/orchestrate`
   - WebSocket messages in Agent Communication panel

## Agent-Specific Issues

### Data Agent
- Check CSV file exists: `/app/data/renewable_energy.csv`
- Verify pandas can load the data

### Viz Agent
- Ensure visualization libraries are installed
- Check component generation code

### GUI Agent
- Verify orchestration logic
- Check A2A message handling

### Research/Narrative Agents
- Require valid LLM API key
- Check LLM client initialization

## Getting Help

If issues persist:
1. Collect logs: `docker compose logs > debug.log`
2. Check agent registration: `curl http://localhost:8000/api/registry/agents`
3. Test individual agents with debug endpoint
4. Review WebSocket messages in browser console