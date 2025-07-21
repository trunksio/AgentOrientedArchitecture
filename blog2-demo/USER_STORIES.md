# Agent Oriented Architecture: User Stories

## Overview
This document contains all user stories needed to transform the current codebase into the target Agent Oriented Architecture and prepare for the blog post. Each story includes acceptance criteria and a Claude Code prompt.

---

## Epic 1: Agent Blueprint Compliance

### Story 1.1: Standardize Agent Interfaces
**As a** system architect  
**I want** all agents to implement standard interfaces  
**So that** agents are interoperable and discoverable

**Acceptance Criteria:**
- All agents expose `/agent-card` endpoint
- All agents expose `/health` endpoint
- All agents expose `/mcp/tools` endpoint
- All agents expose `/mcp/execute/{tool_name}` endpoint
- Agent cards follow the schema in AGENT_BLUEPRINT.md

**Claude Code Prompt:**
```
Review all agents in the agents/ directory. Update each agent to implement the four required endpoints defined in AGENT_BLUEPRINT.md:
1. GET /agent-card - returns agent metadata
2. GET /health - returns health status
3. GET /mcp/tools - returns available MCP tools
4. POST /mcp/execute/{tool_name} - executes an MCP tool

Ensure all responses match the schemas in the blueprint. Create a shared base class if needed to reduce duplication.
```

---

### Story 1.2: Implement Agent Auto-Registration
**As a** system operator  
**I want** agents to auto-register with the A2A Registry on startup  
**So that** agents are immediately discoverable without configuration

**Acceptance Criteria:**
- Agents register on startup without manual intervention
- Registration includes agent card with capabilities
- Failed registration retries with exponential backoff
- Health endpoint reflects registration status

**Claude Code Prompt:**
```
Implement auto-registration for all agents. Each agent should:
1. On startup, POST its agent card to {A2A_REGISTRY_URL}/api/registry/register
2. Retry registration if it fails (network issues, registry not ready)
3. Use exponential backoff: 1s, 2s, 4s, 8s... up to 60s
4. Include registration status in health endpoint response
5. Use environment variables for configuration (AGENT_ID, AGENT_PORT, A2A_REGISTRY_URL)
```

---

## Epic 2: Minimal MCP Tools

### Story 2.1: Refactor Data Agent to Minimal MCP Tools
**As a** data analyst  
**I want** the Data Agent to only have data access capabilities  
**So that** it follows the single responsibility principle

**Acceptance Criteria:**
- Data Agent has only `query_data` and `aggregate_data` MCP tools
- Remove any web search, text generation, or visualization capabilities
- Data Agent cannot access external APIs or generate UI components
- All data operations work correctly with just these tools

**Claude Code Prompt:**
```
Refactor the Data Agent to have exactly two MCP tools:
1. query_data - reads from CSV/database with optional filters
2. aggregate_data - performs sum, avg, min, max operations with optional grouping

Remove any tools for trend analysis (move to Prediction Agent), web search, or UI generation. Ensure the agent can still fulfill all data retrieval needs with just these two tools. Update the agent card capabilities to reflect this focused scope.
```

---

### Story 2.2: Refactor Visualization Agent for Pure Visualization
**As a** data analyst  
**I want** the Visualization Agent to only create visual components  
**So that** it has no dependencies on data access or text generation

**Acceptance Criteria:**
- Viz Agent has tools: `create_chart`, `create_table`, `create_metrics`, `create_diagram`
- Cannot access data directly (receives data as input)
- Cannot generate text narratives
- Returns only UI component specifications
- Supports all common visualization types

**Claude Code Prompt:**
```
Refactor the Visualization Agent to be purely about creating visual components. It should:
1. Have 4 MCP tools: create_chart, create_table, create_metrics, create_diagram
2. Each tool accepts data as input (no direct data access)
3. Return component specifications like: {component_type: "BarChart", props: {...}, layout_hints: {...}}
4. Support chart types: line, bar, pie, scatter, area
5. Remove any text generation or data access code
```

---

### Story 2.3: Focus Research Agent on External Information
**As a** researcher  
**I want** the Research Agent to only access external information  
**So that** it doesn't overlap with other agents' responsibilities

**Acceptance Criteria:**
- Research Agent has only `search_web` and `extract_content` MCP tools
- Cannot access internal data or databases
- Cannot create visualizations
- Returns structured research findings
- Mock implementation for blog demo predictability

**Claude Code Prompt:**
```
Refactor the Research Agent to focus only on external information:
1. Implement two MCP tools: search_web, extract_content
2. For the blog demo, use mock responses (no real API calls)
3. Create realistic mock data for renewable energy searches
4. Remove any data analysis or visualization code
5. Return structured findings with sources and summaries
```

---

### Story 2.4: Restrict Narrative Agent to Text Generation
**As a** content creator  
**I want** the Narrative Agent to only generate text  
**So that** it focuses on creating compelling narratives

**Acceptance Criteria:**
- Narrative Agent has only `generate_story`, `create_summary`, `extract_insights` tools
- Cannot search web or access data directly
- Works with data provided by other agents
- Returns only text content (no UI components)
- Supports different narrative styles

**Claude Code Prompt:**
```
Refactor the Narrative Agent for pure text generation:
1. Implement 3 MCP tools: generate_story, create_summary, extract_insights
2. Each tool accepts data/context as input (no direct access)
3. Remove any UI component generation code
4. Return structured text: {content: "...", sections: {...}, metadata: {...}}
5. Support different styles: technical, executive, general audience
```

---

### Story 2.5: Ensure Prediction Agent Has Minimal Tools
**As a** analyst  
**I want** the Prediction Agent to focus on forecasting  
**So that** it provides specialized prediction capabilities

**Acceptance Criteria:**
- Prediction Agent has only `analyze_trend` and `generate_forecast` tools
- Works with historical data provided by Data Agent
- Cannot access raw data directly
- Returns prediction data and confidence levels

**Claude Code Prompt:**
```
Ensure the Prediction Agent has exactly two MCP tools:
1. analyze_trend - identifies patterns in historical data
2. generate_forecast - creates future predictions with confidence intervals

The agent should work with data passed to it (no direct data access). Return structured predictions that the Viz Agent can visualize. Include confidence levels and methodology notes.
```

---

## Epic 3: Service Architecture

### Story 3.1: Split GUI Agent into Orchestrator Service
**As a** system architect  
**I want** to extract orchestration logic into a separate service  
**So that** concerns are properly separated

**Acceptance Criteria:**
- New Orchestrator Service handles query processing
- Discovers agents via A2A Registry
- Coordinates agent execution
- Returns assembled results
- No UI rendering logic

**Claude Code Prompt:**
```
Extract orchestration logic from GUI Agent into a new Orchestrator Service:
1. Create services/orchestrator/ with FastAPI app
2. Implement POST /orchestrate endpoint that accepts queries
3. Use A2A Registry to discover capable agents
4. Execute agents in appropriate order
5. Assemble and return results
6. No UI logic - just coordination
```

---

### Story 3.2: Create Query Interface Service
**As a** end user  
**I want** a simple interface to enter queries  
**So that** I can interact with the agent system

**Acceptance Criteria:**
- Simple web UI for query input
- Sends queries to Orchestrator Service
- Renders Generative UI components dynamically
- No business logic or orchestration
- Clean, intuitive design

**Claude Code Prompt:**
```
Create a Query Interface Service:
1. Create services/query-interface/ with a simple web UI
2. Single page with query input field
3. POST queries to Orchestrator Service
4. Dynamically render returned UI components
5. Use React or vanilla JS for component rendering
6. No agent logic - pure UI
```

---

### Story 3.3: Create Admin Service
**As a** system administrator  
**I want** to monitor agent health and system state  
**So that** I can manage the AOA system

**Acceptance Criteria:**
- Shows all registered agents and their health
- Displays A2A Registry contents
- Shows recent agent communications
- Allows viewing agent capabilities
- Read-only interface (no configuration changes)

**Claude Code Prompt:**
```
Create an Admin Service for system monitoring:
1. Create services/admin/ with web interface
2. Dashboard showing all registered agents and health status
3. A2A Registry browser with search capability
4. Recent communications log (last 100 messages)
5. Agent capability viewer
6. Auto-refresh every 5 seconds
7. Read-only - no modification capabilities
```

---

## Epic 4: Live Extensibility

### Story 4.1: Implement Live Agent Addition
**As a** system operator  
**I want** to add new agents without restarting the system  
**So that** the system can evolve dynamically

**Acceptance Criteria:**
- Can run `docker run -d new-agent` and agent appears in system
- New agent auto-registers with A2A Registry
- Next query can immediately use new agent
- No configuration files need updating
- No service restarts required

**Claude Code Prompt:**
```
Ensure live agent addition works smoothly:
1. Verify agents join the Docker network properly
2. Test auto-registration happens within 5 seconds
3. Ensure A2A Registry immediately indexes new agents
4. Create test script that adds Prediction Agent and verifies it's discoverable
5. Document the exact commands needed for the blog demo
```

---

### Story 4.2: Implement Agent Health Monitoring
**As a** system administrator  
**I want** the A2A Registry to track agent health  
**So that** only healthy agents are used

**Acceptance Criteria:**
- Registry polls agent /health endpoints every 30 seconds
- Unhealthy agents are marked but not removed
- Orchestrator only uses healthy agents
- Health status visible in Admin Service

**Claude Code Prompt:**
```
Add health monitoring to A2A Registry:
1. Background task polls each agent's /health endpoint every 30s
2. Store health status with timestamp
3. Mark agents as unhealthy after 3 failed checks
4. Modify discovery to only return healthy agents by default
5. Add GET /api/registry/health endpoint showing all agent health
```

---

## Epic 5: Generative UI

### Story 5.1: Implement Component Specification Protocol
**As a** frontend developer  
**I want** a standard format for UI component specifications  
**So that** any agent can generate UI components

**Acceptance Criteria:**
- Standard schema for component specifications
- Support for charts, tables, text panels, metric cards
- Layout hints (width, priority, order)
- Type-safe component props
- Validation of specifications

**Claude Code Prompt:**
```
Create a standard component specification protocol:
1. Define TypeScript interfaces for component specs
2. Support types: Chart, Table, MetricCard, TextPanel, Diagram
3. Include layout hints: {width: "full|half|third", priority: "high|medium|low"}
4. Create validator function to ensure specs are valid
5. Document the protocol in ARCHITECTURE.md
```

---

### Story 5.2: Implement Dynamic Component Renderer
**As a** end user  
**I want** UI components to render dynamically from specifications  
**So that** I see custom interfaces for each query

**Acceptance Criteria:**
- Renders any valid component specification
- Handles unknown component types gracefully
- Smooth animations when components appear
- Responsive layout that adapts to content
- Error boundaries for failed components

**Claude Code Prompt:**
```
Implement dynamic component rendering in Query Interface:
1. Create DynamicComponent that accepts component specifications
2. Map component types to React components
3. Handle props passing and data binding
4. Add error boundaries around each component
5. Implement smooth entry animations
6. Create responsive grid layout that adapts to component count
```

---

## Epic 6: Blog Preparation

### Story 6.1: Create Demo Data and Scenarios
**As a** blog author  
**I want** compelling demo data and scenarios  
**So that** the blog demonstrations are impressive

**Acceptance Criteria:**
- Rich renewable energy dataset with multiple countries and years
- 3 demo queries that show increasing complexity
- Predictable, impressive results
- Mock data for Research Agent that's realistic
- Clear narrative flow from simple to complex

**Claude Code Prompt:**
```
Prepare demo data and scenarios:
1. Enhance renewable_energy.csv with 10 countries, 10 years of data
2. Create 3 demo queries:
   - Simple: "Show renewable energy by country"
   - Complex: "Analyze trends and tell me the story"
   - Live addition: "Predict future growth"
3. Ensure Research Agent has relevant mock responses
4. Test each scenario produces impressive results
```

---

### Story 6.2: Create Blog Code Examples
**As a** blog author  
**I want** clean code examples for the blog  
**So that** readers understand the concepts

**Acceptance Criteria:**
- Extracted code snippets for key concepts
- Examples of: agent registration, MCP tools, discovery, component generation
- Code is simplified and well-commented
- Each example is self-contained
- Examples match the running system

**Claude Code Prompt:**
```
Extract blog-worthy code examples:
1. Create examples/ directory with standalone snippets
2. Include: agent_registration.py, minimal_mcp_tools.py, semantic_discovery.py, component_generation.js
3. Simplify code to focus on concepts
4. Add clear comments explaining each part
5. Ensure examples actually match the implementation
```

---

### Story 6.3: Document Live Agent Addition Process
**As a** blog reader  
**I want** clear instructions for adding agents  
**So that** I can try it myself

**Acceptance Criteria:**
- Step-by-step guide with exact commands
- Screenshots or diagrams of the process
- Explanation of what happens at each step
- Troubleshooting common issues
- Video script for demo recording

**Claude Code Prompt:**
```
Document the live agent addition process:
1. Create LIVE_AGENT_DEMO.md with exact steps
2. Include all commands with expected output
3. Add diagram showing system state before/after
4. Create troubleshooting section
5. Write video script (30-60 seconds) for blog demo
```

---

### Story 6.4: Performance Optimization
**As a** blog presenter  
**I want** the system to respond quickly  
**So that** demos are smooth and impressive

**Acceptance Criteria:**
- Agent discovery < 100ms
- Simple queries complete in < 2 seconds
- Complex queries complete in < 5 seconds
- Live agent registration < 3 seconds
- UI renders without flicker

**Claude Code Prompt:**
```
Optimize system performance for demos:
1. Add caching to A2A Registry discovery
2. Ensure agents respond quickly (add timeouts)
3. Optimize component rendering performance
4. Add loading states for better UX
5. Profile and fix any bottlenecks
Target: All demos should feel instant and smooth
```

---

### Story 6.5: Create README for Blog Readers
**As a** blog reader  
**I want** a clear README to run the demo  
**So that** I can experiment with AOA myself

**Acceptance Criteria:**
- Prerequisites clearly listed
- One-command startup with Docker Compose
- Common issues and solutions
- Links to blog post and documentation
- Encouragement to extend the system

**Claude Code Prompt:**
```
Update README.md for blog readers:
1. Clear prerequisites (Docker, Git)
2. Simple quickstart: git clone, docker compose up
3. What to try first (the 3 demo queries)
4. How to add your own agent
5. Architecture overview with diagram
6. Links to blog series and further reading
Make it exciting and approachable!
```

---

## Summary

Total User Stories: 20
- Epic 1 (Blueprint Compliance): 2 stories
- Epic 2 (Minimal MCP Tools): 5 stories  
- Epic 3 (Service Architecture): 3 stories
- Epic 4 (Live Extensibility): 2 stories
- Epic 5 (Generative UI): 2 stories
- Epic 6 (Blog Preparation): 6 stories

These stories transform the current system into a clean demonstration of Agent Oriented Architecture suitable for an impressive blog post.