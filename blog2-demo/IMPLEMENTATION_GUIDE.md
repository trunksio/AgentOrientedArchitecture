# Agent Oriented Architecture: Implementation Guide

## Core Concept

Each agent is an autonomous service that:
1. **Does ONE thing well**
2. **Uses minimal MCP tools** needed for that purpose
3. **Auto-registers** with the A2A Registry
4. **Provides standard interfaces** (see AGENT_BLUEPRINT.md)

## Agent Specifications

### 1. Data Agent
**Purpose**: Retrieve and query data from storage

**MCP Tools Required**:
- `read_csv` or `query_database` - Access data source
- Nothing else needed

**Capabilities**: 
- `data.retrieval`
- `data.filtering`

**Example Query**: "Get renewable energy data for Germany"

### 2. Visualization Agent
**Purpose**: Create ALL visual components from data

**MCP Tools Required**:
- `render_chart` - Generate chart configurations
- `render_table` - Generate table configurations
- Internal logic for choosing visualization type

**Capabilities**:
- `visualization.charts`
- `visualization.tables`
- `visualization.metrics`

**Example Query**: "Create a bar chart of this data"

### 3. Research Agent
**Purpose**: Gather external context and information

**MCP Tools Required**:
- `web_search` - Search for external information
- `extract_content` - Process web content

**Capabilities**:
- `research.web`
- `research.summarization`

**Example Query**: "Find recent news about solar energy"

### 4. Narrative Agent
**Purpose**: Generate text narratives and summaries

**MCP Tools Required**:
- `generate_text` - LLM for text generation
- Nothing else - works with provided data

**Capabilities**:
- `text.generation`
- `text.summarization`

**Example Query**: "Explain these energy trends"

### 5. Prediction Agent
**Purpose**: Forecast future trends from historical data

**MCP Tools Required**:
- `analyze_timeseries` - Statistical analysis
- `generate_forecast` - Create predictions

**Capabilities**:
- `prediction.forecasting`
- `prediction.trend_analysis`

**Example Query**: "Predict renewable energy growth for next 5 years"

## Service Architecture

### User-Facing Services

#### Query Interface
- Simple web UI for queries
- Renders Generative UI components
- No business logic

#### Admin Service
- Monitor agent health
- Browse A2A Registry
- View system logs

### Core Services

#### A2A Registry
- Semantic agent discovery
- Health monitoring
- No hardcoded dependencies

#### Orchestrator
- Query processing
- Agent coordination
- Result assembly

## Implementation Principles

### 1. Minimal MCP Tools
```
BAD:  Data Agent with web_search, file_access, database_access, api_calls
GOOD: Data Agent with query_database only
```

### 2. Clear Boundaries
```
BAD:  Visualization Agent that also generates text descriptions
GOOD: Visualization Agent creates visuals, Narrative Agent creates text
```

### 3. Docker Deployment
```yaml
# Each agent is a container
data-agent:
  build: ./agents/data-agent
  environment:
    - AGENT_ID=data-agent-001
    - A2A_REGISTRY_URL=http://registry:8000
```

### 4. Auto-Registration
```python
# On startup, every agent must:
async def startup():
    await register_with_a2a_registry()
    await start_health_check_endpoint()
    await expose_mcp_tools()
```

## Live Agent Addition Demo

The key demonstration for the blog:

```bash
# 1. System running with 4 agents
docker compose ps

# 2. Build and run prediction agent
cd agents/prediction-agent
docker build -t prediction-agent .
docker run -d --network aoa-network prediction-agent

# 3. Agent auto-registers (no configuration!)

# 4. Next query uses it automatically
"Predict renewable energy growth"
# System discovers and uses prediction agent!
```

## Blog Code Examples

### Example 1: Agent Registration
```python
# How agents announce themselves
agent_card = {
    "id": "data-agent-001",
    "name": "Data Agent",
    "capabilities": ["data.retrieval", "data.filtering"]
}
await registry.register(agent_card)
```

### Example 2: MCP Tool Usage
```python
# Minimal tools for specific purpose
class DataAgent:
    def __init__(self):
        self.mcp_tools = {
            "query_data": self.handle_query_data
        }
        # That's it! No web search, no text generation
```

### Example 3: Agent Discovery
```python
# Semantic discovery in action
agents = await registry.discover("analyze energy trends")
# Returns: [data-agent, viz-agent, narrative-agent]
```

## Success Criteria

1. **Each agent uses only necessary MCP tools**
2. **Live agent addition works smoothly**
3. **Clear separation of concerns**
4. **No hardcoded integrations**
5. **All UI dynamically generated**

This approach creates a clean demonstration of Agent Oriented Architecture suitable for the blog post.