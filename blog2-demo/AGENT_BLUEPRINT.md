# Agent Oriented Architecture: Agent Blueprint

## Purpose
This blueprint defines the required interfaces and capabilities that ALL agents must implement to participate in the Agent Oriented Architecture ecosystem.

## Required Interfaces

### 1. Agent Card Interface
Every agent MUST provide an agent card endpoint that returns:

```json
GET /agent-card

{
  "id": "unique-agent-identifier",
  "name": "Human Readable Agent Name",
  "description": "Clear description of what this agent does",
  "capabilities": ["list", "of", "semantic", "capabilities"],
  "version": "1.0.0"
}
```

### 2. Health Check Interface
```json
GET /health

{
  "status": "healthy|unhealthy",
  "timestamp": "2024-01-20T10:00:00Z"
}
```

### 3. MCP Tool Discovery Interface
```json
GET /mcp/tools

{
  "tools": [
    {
      "name": "tool_name",
      "description": "What this tool does",
      "input_schema": {},
      "output_schema": {}
    }
  ]
}
```

### 4. MCP Tool Execution Interface
```json
POST /mcp/execute/{tool_name}

Request: {
  "parameters": {}
}

Response: {
  "success": true,
  "result": {},
  "error": null
}
```

## Agent Capabilities Guidelines

### MCP Tools Should Enable Core Functionality

MCP tools are for accessing external capabilities the agent needs:
- **Filesystem access** - For agents that need to read/write files
- **Web search** - For agents that need external information
- **Database access** - For agents that need to query data
- **API calls** - For agents that need external services

### Minimal Tool Principle

Each agent should have the MINIMUM MCP tools needed to fulfill its purpose:

#### Data Agent
- ✅ Database/data file access
- ❌ Web search (doesn't need external info)
- ❌ LLM access (just retrieves data)

#### Research Agent  
- ✅ Web search capabilities
- ❌ Database access (gets external info only)
- ✅ LLM for summarization

#### Visualization Agent
- ❌ Web search (works with provided data)
- ❌ Database access (receives data from other agents)
- ✅ Charting libraries/tools

#### Narrative Agent
- ✅ LLM for text generation
- ❌ Web search (uses provided context)
- ❌ Database access (works with provided data)

## Auto-Registration Requirement

Agents MUST auto-register with the A2A Registry on startup:

```
POST /api/registry/register
Content-Type: application/json

{
  "id": "agent-id",
  "name": "Agent Name",
  "endpoint": "http://agent-host:port",
  "capabilities": ["capability1", "capability2"]
}
```

## Configuration Requirements

Agents MUST accept configuration via environment variables:
- `AGENT_ID` - Unique identifier
- `AGENT_PORT` - Port to listen on
- `A2A_REGISTRY_URL` - Registry endpoint
- Additional agent-specific configuration as needed

## Output Requirements

### For UI-Generating Agents

Agents that generate UI components must return specifications, not code:

```json
{
  "component_type": "chart|table|metric_card|text",
  "component_config": {
    "data": {},
    "options": {}
  },
  "layout_hints": {
    "width": "full|half|third",
    "priority": "high|medium|low"
  }
}
```

### For Data-Providing Agents

```json
{
  "data": [],
  "metadata": {
    "source": "data_source_name",
    "timestamp": "2024-01-20T10:00:00Z",
    "row_count": 100
  }
}
```

### For Text-Generating Agents

```json
{
  "content": "Generated text content",
  "sections": {
    "summary": "Brief summary",
    "details": "Detailed content"
  },
  "metadata": {
    "word_count": 500,
    "reading_time": "2 minutes"
  }
}
```

## Capability Definitions

### Standard Capabilities (for agent discovery)

Agents should use these standard capability descriptors:
- `data.retrieval` - Can fetch data
- `data.analysis` - Can analyze data
- `visualization.charts` - Can create charts
- `visualization.tables` - Can create tables
- `text.generation` - Can generate text
- `text.summarization` - Can summarize content
- `research.web` - Can search the web
- `prediction.forecasting` - Can make predictions

## Summary

This blueprint ensures:
1. **Consistent interfaces** across all agents
2. **Minimal MCP tools** for focused functionality
3. **Clear capability declaration** for discovery
4. **Standardized output formats** for interoperability
5. **Auto-registration** for dynamic extensibility

Agents are free to implement these interfaces however they choose (Docker, serverless, etc.) as long as they conform to these requirements.