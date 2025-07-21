# Agent Oriented Architecture: System Architecture

## Overview

Agent Oriented Architecture (AOA) is a distributed system where autonomous agents discover and collaborate with each other dynamically through semantic protocols.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Users                                │
└─────────────────┬─────────────────────┬─────────────────────┘
                  │                     │
        ┌─────────▼──────────┐ ┌───────▼──────────┐
        │  Query Interface   │ │  Admin Service   │
        │  (User Queries)    │ │  (Monitoring)    │
        └─────────┬──────────┘ └───────┬──────────┘
                  │                     │
        ┌─────────▼──────────────────────▼────────┐
        │           Orchestrator Service          │
        │  - Process queries                      │
        │  - Discover agents                      │
        │  - Coordinate execution                 │
        └─────────┬──────────────────┬────────────┘
                  │                  │
        ┌─────────▼──────────┐       │
        │   A2A Registry     │       │
        │ - Semantic search  │       │
        │ - Agent directory  │       │
        │ - Health checks    │       │
        └─────────▲──────────┘       │
                  │                  │
    Auto-register │                  │ Query agents
    on startup    │                  │
                  │                  ▼
        ┌─────────┴───────────────────────────────┐
        │          Agent Network (Docker)          │
        ├──────────────┬──────────────┬───────────┤
        │              │              │           │
   ┌────▼─────┐  ┌────▼─────┐  ┌────▼─────┐  ┌─▼─────────┐
   │   Data   │  │   Viz    │  │ Research  │  │ Narrative │
   │  Agent   │  │  Agent   │  │  Agent    │  │   Agent   │
   ├──────────┤  ├──────────┤  ├───────────┤  ├───────────┤
   │MCP Tools:│  │MCP Tools:│  │MCP Tools: │  │MCP Tools: │
   │- read_csv│  │- render_ │  │- search_  │  │- generate_│
   │          │  │  chart   │  │  web      │  │  text     │
   └──────────┘  └──────────┘  └───────────┘  └───────────┘
                                                      
                 ┌─────────────┐
                 │ Prediction  │ ← Added dynamically!
                 │   Agent     │
                 ├─────────────┤
                 │MCP Tools:   │
                 │- forecast   │
                 └─────────────┘
```

## Core Components

### 1. User Interfaces

#### Query Interface
- **Purpose**: Accept user queries and display results
- **Technology**: Simple web UI (React/Next.js)
- **Key Feature**: Renders Generative UI components dynamically
- **No Logic**: Just input and display

#### Admin Service
- **Purpose**: Monitor and manage the system
- **Features**:
  - Agent health dashboard
  - A2A Registry browser
  - Inter-agent communication logs
  - System metrics

### 2. Core Services

#### Orchestrator Service
- **Purpose**: Process queries and coordinate agents
- **Responsibilities**:
  - Parse user intent
  - Query A2A Registry for capable agents
  - Execute agent tools in appropriate order
  - Assemble results
- **No Hardcoding**: Discovers agents dynamically

#### A2A Registry
- **Purpose**: Enable semantic agent discovery
- **Technology**: Vector database (ChromaDB)
- **Features**:
  - Semantic search by capability
  - Agent health monitoring
  - No predetermined relationships
- **Protocol**: RESTful API

### 3. Agents (Autonomous Services)

Each agent is:
- **Autonomous**: Runs in its own Docker container
- **Self-Registering**: Announces capabilities on startup
- **Focused**: Has minimal MCP tools for its purpose
- **Stateless**: No shared state between agents

## Agent Specifications

### Data Agent
- **Purpose**: Data retrieval and basic queries
- **MCP Tools**: `read_csv` or `query_database`
- **Capabilities**: `["data.retrieval", "data.filtering"]`
- **Cannot**: Search web, generate text, create visualizations

### Visualization Agent
- **Purpose**: Create ALL visual components
- **MCP Tools**: `render_chart`, `render_table`, `render_metrics`
- **Capabilities**: `["visualization.charts", "visualization.tables", "visualization.metrics"]`
- **Cannot**: Access data directly, generate text

### Research Agent
- **Purpose**: Find external information
- **MCP Tools**: `search_web`, `extract_content`
- **Capabilities**: `["research.web", "research.summarization"]`
- **Cannot**: Access internal data, create visualizations

### Narrative Agent
- **Purpose**: Generate text content
- **MCP Tools**: `generate_text`
- **Capabilities**: `["text.generation", "text.summarization"]`
- **Cannot**: Search web, access data, create visuals

### Prediction Agent (Dynamically Added)
- **Purpose**: Forecast future trends
- **MCP Tools**: `analyze_timeseries`, `generate_forecast`
- **Capabilities**: `["prediction.forecasting", "prediction.trends"]`
- **Cannot**: Access raw data, search web

## Communication Protocols

### Agent Registration
```http
POST /api/registry/register
{
  "id": "agent-unique-id",
  "name": "Human Readable Name",
  "endpoint": "http://agent:port",
  "capabilities": ["capability.list"]
}
```

### Agent Discovery
```http
POST /api/registry/discover
{
  "query": "analyze renewable energy trends"
}

Response:
{
  "agents": [
    {"id": "data-agent-001", "score": 0.95},
    {"id": "viz-agent-001", "score": 0.89}
  ]
}
```

### MCP Tool Execution
```http
POST /mcp/execute/tool_name
{
  "parameters": {}
}

Response:
{
  "success": true,
  "result": {}
}
```

## Generative UI Protocol

Agents return UI specifications, not rendered components:

```json
{
  "component_type": "chart",
  "component_config": {
    "type": "bar",
    "data": {...},
    "options": {...}
  },
  "layout_hints": {
    "width": "full",
    "priority": "high"
  }
}
```

## Live Extensibility

### Adding a New Agent

1. **Build Agent** following the blueprint
2. **Deploy**: `docker run -d --network aoa new-agent`
3. **Auto-Registration**: Agent registers with A2A
4. **Immediate Discovery**: Next query can use it

No configuration files, no service restarts, no code changes.

## Design Principles

1. **No Hardcoded Dependencies**: All discovery is semantic
2. **Minimal Tool Principle**: Each agent has only necessary MCP tools
3. **Single Responsibility**: One agent, one domain
4. **Emergent Workflows**: Behavior emerges from available agents
5. **True Autonomy**: Agents are independent services

## Security Considerations (for Part 3)

- Agent authentication
- Capability-based access control
- Encrypted communication
- Audit logging

## Scalability (for Part 3)

- Horizontal scaling of agents
- Registry sharding
- Caching strategies
- Load balancing

This architecture demonstrates the future of software systems - truly autonomous, dynamically extensible, and intelligently collaborative.