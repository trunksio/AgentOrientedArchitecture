# Agent Oriented Architecture: GitHub Issues Summary

## Quick Issue Creation Guide

Copy each section below to create a GitHub issue. Each includes title, labels, and description.

---

### Issue #1: Standardize Agent Interfaces
**Labels:** `enhancement`, `agents`, `blueprint`
```
All agents need to implement the standard interfaces defined in AGENT_BLUEPRINT.md:
- GET /agent-card
- GET /health  
- GET /mcp/tools
- POST /mcp/execute/{tool_name}

See USER_STORIES.md Story 1.1 for full details and Claude Code prompt.
```

---

### Issue #2: Implement Agent Auto-Registration
**Labels:** `enhancement`, `agents`, `infrastructure`
```
Agents should auto-register with A2A Registry on startup without manual intervention.

Requirements:
- Auto-registration on startup
- Retry with exponential backoff
- Health endpoint shows registration status

See USER_STORIES.md Story 1.2 for full details and Claude Code prompt.
```

---

### Issue #3: Refactor Data Agent to Minimal MCP Tools
**Labels:** `refactor`, `data-agent`, `mcp`
```
Data Agent should only have:
- query_data: Read from data sources
- aggregate_data: Basic aggregations

Remove: trend analysis, web search, UI generation

See USER_STORIES.md Story 2.1 for full details and Claude Code prompt.
```

---

### Issue #4: Refactor Visualization Agent for Pure Visualization
**Labels:** `refactor`, `viz-agent`, `mcp`
```
Visualization Agent should only create visual components:
- create_chart
- create_table
- create_metrics
- create_diagram

Remove: data access, text generation

See USER_STORIES.md Story 2.2 for full details and Claude Code prompt.
```

---

### Issue #5: Focus Research Agent on External Information
**Labels:** `refactor`, `research-agent`, `mcp`
```
Research Agent should only have:
- search_web
- extract_content

Use mock implementation for blog demo.

See USER_STORIES.md Story 2.3 for full details and Claude Code prompt.
```

---

### Issue #6: Restrict Narrative Agent to Text Generation
**Labels:** `refactor`, `narrative-agent`, `mcp`
```
Narrative Agent should only generate text:
- generate_story
- create_summary
- extract_insights

Remove: web search, data access, UI components

See USER_STORIES.md Story 2.4 for full details and Claude Code prompt.
```

---

### Issue #7: Ensure Prediction Agent Has Minimal Tools
**Labels:** `refactor`, `prediction-agent`, `mcp`
```
Prediction Agent should only have:
- analyze_trend
- generate_forecast

Works with provided data, no direct access.

See USER_STORIES.md Story 2.5 for full details and Claude Code prompt.
```

---

### Issue #8: Split GUI Agent into Orchestrator Service
**Labels:** `refactor`, `architecture`, `services`
```
Extract orchestration logic into separate service:
- Create services/orchestrator/
- Handle query processing
- Coordinate agent execution
- No UI logic

See USER_STORIES.md Story 3.1 for full details and Claude Code prompt.
```

---

### Issue #9: Create Query Interface Service  
**Labels:** `feature`, `frontend`, `services`
```
Create simple web UI for queries:
- services/query-interface/
- Query input field
- Render Generative UI components
- No business logic

See USER_STORIES.md Story 3.2 for full details and Claude Code prompt.
```

---

### Issue #10: Create Admin Service
**Labels:** `feature`, `admin`, `services`
```
Create admin interface for monitoring:
- services/admin/
- Show agent health
- Browse A2A Registry
- View communications
- Read-only

See USER_STORIES.md Story 3.3 for full details and Claude Code prompt.
```

---

### Issue #11: Implement Live Agent Addition
**Labels:** `feature`, `infrastructure`, `demo`
```
Enable adding agents without restarts:
- docker run adds new agent
- Auto-registration works
- Immediately discoverable
- Document process

See USER_STORIES.md Story 4.1 for full details and Claude Code prompt.
```

---

### Issue #12: Implement Agent Health Monitoring
**Labels:** `feature`, `infrastructure`, `registry`
```
A2A Registry should monitor agent health:
- Poll /health every 30s
- Mark unhealthy agents
- Only return healthy agents
- Show in admin UI

See USER_STORIES.md Story 4.2 for full details and Claude Code prompt.
```

---

### Issue #13: Implement Component Specification Protocol
**Labels:** `feature`, `frontend`, `generative-ui`
```
Standard format for UI components:
- Define TypeScript interfaces
- Support all component types
- Include layout hints
- Create validator

See USER_STORIES.md Story 5.1 for full details and Claude Code prompt.
```

---

### Issue #14: Implement Dynamic Component Renderer
**Labels:** `feature`, `frontend`, `generative-ui`
```
Render components from specifications:
- DynamicComponent React component
- Handle all component types
- Error boundaries
- Smooth animations

See USER_STORIES.md Story 5.2 for full details and Claude Code prompt.
```

---

### Issue #15: Create Demo Data and Scenarios
**Labels:** `demo`, `blog`, `data`
```
Prepare compelling demos:
- Rich renewable energy dataset
- 3 progressive demo queries
- Mock research data
- Predictable results

See USER_STORIES.md Story 6.1 for full details and Claude Code prompt.
```

---

### Issue #16: Create Blog Code Examples
**Labels:** `documentation`, `blog`
```
Extract clean code examples:
- examples/ directory
- Key concepts illustrated
- Self-contained snippets
- Well commented

See USER_STORIES.md Story 6.2 for full details and Claude Code prompt.
```

---

### Issue #17: Document Live Agent Addition Process
**Labels:** `documentation`, `demo`, `blog`
```
Clear guide for live demo:
- Step-by-step instructions
- Exact commands
- Diagrams
- Video script

See USER_STORIES.md Story 6.3 for full details and Claude Code prompt.
```

---

### Issue #18: Performance Optimization
**Labels:** `performance`, `demo`
```
Optimize for smooth demos:
- Agent discovery < 100ms
- Simple queries < 2s
- Complex queries < 5s
- No UI flicker

See USER_STORIES.md Story 6.4 for full details and Claude Code prompt.
```

---

### Issue #19: Create README for Blog Readers
**Labels:** `documentation`, `blog`
```
Update README for blog audience:
- Clear prerequisites
- One-command startup
- What to try first
- How to extend

See USER_STORIES.md Story 6.5 for full details and Claude Code prompt.
```

---

### Issue #20: Integration Testing
**Labels:** `testing`, `infrastructure`
```
Ensure everything works together:
- All demos run smoothly
- Live agent addition works
- Performance targets met
- Blog examples accurate

This is a meta-issue to verify all components work together.
```

---

## Suggested Milestones

### Milestone 1: Agent Compliance (Issues #1-7)
All agents follow blueprint with minimal MCP tools

### Milestone 2: Service Architecture (Issues #8-10)
GUI split into proper services

### Milestone 3: Live Extensibility (Issues #11-12)
Dynamic agent addition working

### Milestone 4: Generative UI (Issues #13-14)
Dynamic UI rendering complete

### Milestone 5: Blog Ready (Issues #15-20)
System polished and documented for blog

## Priority Order

1. **Critical Path**: #1, #2, #8, #11 (core architecture)
2. **Agent Refactoring**: #3-7 (parallel work possible)
3. **UI/Frontend**: #9, #13, #14 (can start after #8)
4. **Polish**: #10, #12, #15-20 (for blog quality)