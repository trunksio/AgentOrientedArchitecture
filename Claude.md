# Agent Oriented Architecture Blog 2 Demo

## Project Overview
This is a demonstration of Agent Oriented Architecture (AOA) showcasing three core concepts:
1. **A2A Protocol** - Enables semantic agent discovery through a registry
2. **MCP (Model Context Protocol)** - Gives agents capabilities through standardized tools
3. **Generative UI** - Agents generate UI components, not just data

## Architecture

### Core Components
- **A2A Registry**: Semantic vector store for agent discovery
- **GUI Agent**: Orchestrates the user experience
- **Data Agent**: Provides data access and analysis
- **Visualization Agent**: Creates ALL visualizations (charts, tables, diagrams)
- **Research Agent**: Gathers external context
- **Narrative Agent**: Generates data-driven stories
- **Prediction Agent**: Added live during demo to show extensibility

### Tech Stack
- Backend: FastAPI (Python)
- Frontend: Next.js with TypeScript
- Vector Store: ChromaDB (for semantic search)
- Styling: Tailwind CSS
- Animation: Framer Motion
- Charts: Chart.js/Recharts

## Key Features to Implement

### 1. A2A Registry
- Semantic search using embeddings
- Agent capability registration
- Dynamic discovery based on intent
- Visual registry browser

### 2. MCP Integration
- Tool definitions for each agent
- Type-safe tool execution
- Self-documenting capabilities
- Tool discovery endpoint

### 3. Generative UI System
- Agents return React component code
- Dynamic component loading
- Runtime composition
- Smooth animations for component appearance

### 4. Live Agent Addition
- Register new agent while system running
- Immediate discovery in next query
- No restart required
- Visual confirmation of registration

## Implementation Guidelines

### Agent Structure
Each agent should:
- Register capabilities with A2A registry
- Expose MCP tools with clear descriptions
- Generate UI components, not just data
- Be domain-focused, not application-specific

### Generative UI Rules
- Components should be self-contained
- Use Tailwind for consistent styling
- Include loading and error states
- Animate entry for visual appeal

### Demo Scenarios
1. **Basic Analysis**: "Analyze renewable energy by country"
2. **Trend Analysis**: "Show renewable energy trends over time"
3. **With Prediction**: "Predict future renewable energy growth" (after adding Prediction Agent)

## Code Generation Instructions

### Project Structure
```
blog2-demo/
├── docker-compose.yml       # One-command startup
├── README.md               # Setup and usage instructions
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py              # FastAPI application
│   ├── registry/           # A2A Protocol implementation
│   │   ├── __init__.py
│   │   ├── a2a_registry.py # Semantic search registry
│   │   └── models.py       # Agent capability models
│   ├── agents/             # Agent implementations
│   │   ├── __init__.py
│   │   ├── base_agent.py   # Base class with MCP support
│   │   ├── gui_agent.py    # Orchestrator
│   │   ├── data_agent.py   # Data access
│   │   ├── viz_agent.py    # All visualizations
│   │   ├── research_agent.py    # External context
│   │   ├── narrative_agent.py   # Story generation
│   │   └── prediction_agent.py  # Future predictions
│   ├── mcp/                # MCP tool definitions
│   │   ├── __init__.py
│   │   ├── tool_registry.py # MCP tool management
│   │   └── schemas.py      # Tool definitions
│   └── data/               # Demo datasets
│       └── renewable_energy.csv # Demo data
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── next.config.js
│   ├── app/                # Next.js app directory
│   │   ├── page.tsx        # Main demo page
│   │   └── layout.tsx      # App layout
│   ├── components/         # React components
│   │   ├── GUIAgent.tsx    # Main orchestrator UI
│   │   ├── AgentDiscovery.tsx   # Discovery visualization
│   │   ├── DynamicComponent.tsx # Component loader
│   │   ├── AgentStatus.tsx      # Real-time status
│   │   └── GeneratedUI/         # Generated components
│   │       ├── Charts.tsx
│   │       ├── Tables.tsx
│   │       └── Narratives.tsx
│   └── lib/                # Utilities
│       ├── api.ts          # Backend communication
│       ├── websocket.ts    # Real-time updates
│       └── componentLoader.ts # Dynamic loading
└── docs/
    ├── architecture.md     # System architecture
    ├── agent-guide.md      # How to create agents
    └── demo-script.md      # Demo walkthrough
```

### Key Implementation Details

1. **A2A Registry** should use ChromaDB for semantic search
2. **MCP tools** should have clear parameter schemas
3. **Visualization Agent** must handle multiple output types intelligently
4. **Component generation** should produce valid React/TypeScript code
5. **Live updates** via WebSocket for agent discovery visualization

### Demo Data
Create a rich renewable energy dataset with:
- Countries
- Energy types (solar, wind, hydro)
- Capacity metrics
- Time series data (2015-2024)
- Growth rates

### Docker Setup
- Use docker-compose for one-command startup
- Backend container with FastAPI and all Python dependencies
- Frontend container with Next.js
- ChromaDB container for vector storage
- Shared network for communication

### Frontend Notes
- Use Next.js App Router (app directory)
- Tailwind CSS for styling (already configured in Next.js setup)
- Framer Motion for animations
- Dynamic imports for generated components
- WebSocket connection for real-time updates

### Backend Notes
- FastAPI with async support
- ChromaDB client for semantic search
- WebSocket endpoint for live updates
- CORS properly configured for frontend
- Environment variables for configuration

## Success Criteria
- One-command startup (docker-compose up)
- Semantic agent discovery works reliably
- UI components generate and render correctly
- Live agent addition demonstrates extensibility
- Different queries produce different UIs
- Blog-ready code that's clean and understandable

## Blog Code Examples to Highlight
1. A2A agent registration
2. Semantic discovery process
3. MCP tool definitions
4. Generative UI component creation
5. Live agent addition

Remember: The goal is to demonstrate the power of AOA through working code that readers can understand and extend.