# Agent Interface Standard v1.0

This document defines the standard interfaces that all agents in the Agent Oriented Architecture must implement to ensure interoperability and discoverability.

## Overview

The Agent Interface Standard provides:
- Consistent endpoints across all agents
- Unified discovery mechanism
- Standardized health monitoring
- Common tool execution interface
- Predictable response schemas

## Required Endpoints

All agents MUST implement the following endpoints:

### 1. Agent Card - `/agent-card`

**Method:** GET  
**Purpose:** Provides comprehensive metadata about the agent

**Response Schema:**
```json
{
  "agent_id": "string",
  "name": "string",
  "description": "string",
  "capabilities": ["string"],
  "tags": ["string"],
  "tools": [
    {
      "name": "string",
      "description": "string"
    }
  ],
  "status": {
    "status": "healthy|degraded|unhealthy",
    "uptime_seconds": "integer",
    "request_count": "integer",
    "error_count": "integer",
    "error_rate": "float"
  },
  "metadata": {
    "llm_model": "string",
    "semantic_tool_selection": "boolean",
    "version": "string"
  }
}
```

### 2. Health Check - `/health`

**Method:** GET  
**Purpose:** Reports agent health status and availability

**Response Schema:**
```json
{
  "status": "healthy|degraded|unhealthy",
  "uptime_seconds": "integer",
  "request_count": "integer",
  "error_count": "integer",
  "error_rate": "float",
  "last_error": "string|null",
  "llm_available": "boolean",
  "timestamp": "ISO 8601 datetime"
}
```

**Health Status Definitions:**
- `healthy`: Error rate < 10%, all systems operational
- `degraded`: Error rate 10-50%, experiencing issues
- `unhealthy`: Error rate > 50%, major problems

### 3. MCP Tools List - `/mcp/tools`

**Method:** GET  
**Purpose:** Lists all available MCP tools with their schemas

**Response Schema:**
```json
{
  "tools": [
    {
      "name": "string",
      "description": "string",
      "parameters": {
        "type": "object",
        "properties": {
          "param_name": {
            "type": "string|number|boolean|object|array",
            "description": "string"
          }
        },
        "required": ["string"]
      },
      "returns": "string",
      "examples": ["string"]
    }
  ],
  "agent_id": "string",
  "agent_name": "string"
}
```

### 4. MCP Tool Execution - `/mcp/execute/{tool_name}`

**Method:** POST  
**Purpose:** Executes a specific MCP tool

**Request Body:**
```json
{
  "parameters": {
    "param_name": "value"
  },
  "context": {}  // Optional context
}
```

**Response Schema:**
```json
{
  "success": "boolean",
  "result": "any",  // Tool-specific result
  "error": "string|null",
  "metadata": {
    "agent": "string",
    "tool": "string",
    "timestamp": "ISO 8601 datetime"
  }
}
```

## A2A Message Handling

Agents must also support the standard A2A message endpoint:

### A2A Message - `/a2a/message`

**Method:** POST  
**Purpose:** Handles inter-agent communication

**Request Schema:**
```json
{
  "from_agent": "string",
  "to_agent": "string",
  "action": "string",
  "payload": {},
  "message_type": "REQUEST|RESPONSE|NOTIFICATION",
  "context": {}  // Optional
}
```

**Response Schema:**
```json
{
  "success": "boolean",
  "result": "any",
  "error": "string|null",
  "tools_used": ["string"],
  "semantic_selection": "boolean",
  "timestamp": "ISO 8601 datetime"
}
```

## Implementation Guide

### Using the Unified Base Agent

The easiest way to implement the standard is to inherit from `UnifiedBaseAgent`:

```python
from unified_base_agent import UnifiedBaseAgent
from mcp.schemas import MCPTool, ToolParameter, ParameterType

class MyAgent(UnifiedBaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="my-agent-001",
            name="My Agent",
            description="Description of what my agent does",
            capabilities=[
                "Capability 1",
                "Capability 2"
            ],
            tags=["tag1", "tag2"]
        )
    
    def _register_tools(self):
        """Register MCP tools"""
        self.register_tool(
            MCPTool(
                name="my_tool",
                description="What this tool does",
                parameters=[
                    ToolParameter(
                        name="param1",
                        type=ParameterType.STRING,
                        description="Parameter description",
                        required=True
                    )
                ],
                returns="Description of return value"
            ),
            self._execute_my_tool
        )
    
    async def _execute_my_tool(self, parameters: Dict[str, Any]):
        """Tool implementation"""
        # Tool logic here
        return {"result": "data"}
```

### Using the Standard Agent Runner

For containerized agents, use `StandardAgentRunner`:

```python
from shared.standard_agent_runner import StandardAgentRunner
from my_agent import MyAgent

async def main():
    runner = StandardAgentRunner(MyAgent)
    await runner.run()

if __name__ == "__main__":
    asyncio.run(main())
```

## Testing Compliance

Use the provided test script to verify your agent implements all standard interfaces:

```bash
python tests/test_standard_interfaces.py [backend_url]
```

The test will check:
- All required endpoints are available
- Response schemas match the standard
- Health checks work correctly
- Tools can be listed and executed

## Benefits

Implementing the standard interface provides:

1. **Automatic Discovery** - Agents can be found via semantic search
2. **Interoperability** - Any agent can communicate with any other
3. **Monitoring** - Health status visible across the system
4. **Tool Sharing** - MCP tools discoverable and executable
5. **UI Generation** - Frontends can automatically generate interfaces

## Migration Guide

To migrate existing agents:

1. Replace `BaseAgent` with `UnifiedBaseAgent`
2. Add `capabilities` and `tags` to constructor
3. Update main.py to use `StandardAgentRunner`
4. Test with the compliance script
5. Deploy and verify discovery works

## Version History

- **v1.0** (2024-01) - Initial standard with 4 core endpoints

## Future Enhancements

Planned additions for v2.0:
- Streaming responses for long-running operations
- Batch tool execution
- Agent composition and chaining
- Advanced telemetry and tracing