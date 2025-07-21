"""Register example agents on startup"""
import asyncio
import logging
from datetime import datetime
from registry.models import AgentRegistration, AgentCapability, AgentType

logger = logging.getLogger(__name__)

EXAMPLE_AGENTS = [
    {
        "id": "data-agent-001",
        "name": "Data Agent",
        "type": AgentType.DATA,
        "description": "Provides access to renewable energy datasets and performs data analysis",
        "capabilities": [
            {
                "name": "query_data",
                "description": "Query renewable energy data by country, year, or energy type",
                "parameters": {
                    "country": "string",
                    "year": "number",
                    "energy_type": "string"
                },
                "output_type": "table",
                "examples": [
                    "Show renewable energy data for Germany",
                    "What's the solar capacity in 2023?",
                    "Compare wind energy across countries"
                ]
            },
            {
                "name": "aggregate_data",
                "description": "Aggregate and summarize energy data with calculations",
                "parameters": {
                    "metric": "string",
                    "groupBy": "string"
                },
                "output_type": "table",
                "examples": [
                    "Total renewable capacity by country",
                    "Average growth rate over time",
                    "Sum of all energy types"
                ]
            }
        ],
        "endpoint": "/api/agents/data",
        "metadata": {
            "keywords": ["data", "renewable", "energy", "statistics", "query", "dataset"]
        }
    },
    {
        "id": "viz-agent-001",
        "name": "Visualization Agent",
        "type": AgentType.VISUALIZATION,
        "description": "Creates charts, graphs, and visual representations of data",
        "capabilities": [
            {
                "name": "create_chart",
                "description": "Generate interactive charts from data",
                "parameters": {
                    "chart_type": "string",
                    "data": "object",
                    "options": "object"
                },
                "output_type": "chart",
                "examples": [
                    "Create a line chart of renewable energy trends",
                    "Show a bar chart comparing countries",
                    "Pie chart of energy distribution"
                ]
            },
            {
                "name": "create_map",
                "description": "Generate geographic visualizations",
                "parameters": {
                    "data": "object",
                    "metric": "string"
                },
                "output_type": "map",
                "examples": [
                    "Map of renewable capacity by country",
                    "Heatmap of growth rates",
                    "Geographic distribution of solar energy"
                ]
            }
        ],
        "endpoint": "/api/agents/visualization",
        "metadata": {
            "keywords": ["chart", "graph", "visualization", "plot", "diagram", "visual"]
        }
    },
    {
        "id": "research-agent-001",
        "name": "Research Agent",
        "type": AgentType.RESEARCH,
        "description": "Gathers external context and insights about renewable energy",
        "capabilities": [
            {
                "name": "research_trends",
                "description": "Research current trends and news in renewable energy",
                "parameters": {
                    "topic": "string",
                    "timeframe": "string"
                },
                "output_type": "text",
                "examples": [
                    "Latest renewable energy innovations",
                    "Policy changes affecting solar",
                    "Market trends in wind energy"
                ]
            },
            {
                "name": "analyze_context",
                "description": "Provide contextual analysis for data",
                "parameters": {
                    "data": "object",
                    "focus": "string"
                },
                "output_type": "text",
                "examples": [
                    "Why is China leading in solar?",
                    "Impact of policies on growth",
                    "Future outlook for renewables"
                ]
            }
        ],
        "endpoint": "/api/agents/research",
        "metadata": {
            "keywords": ["research", "analysis", "trends", "insights", "context", "news"]
        }
    },
    {
        "id": "narrative-agent-001",
        "name": "Narrative Agent",
        "type": AgentType.NARRATIVE,
        "description": "Generates data-driven stories and explanations",
        "capabilities": [
            {
                "name": "generate_story",
                "description": "Create narrative explanations from data",
                "parameters": {
                    "data": "object",
                    "theme": "string",
                    "length": "string"
                },
                "output_type": "narrative",
                "examples": [
                    "Tell the story of renewable energy growth",
                    "Explain the energy transition",
                    "Narrative about solar adoption"
                ]
            },
            {
                "name": "create_summary",
                "description": "Summarize complex data insights",
                "parameters": {
                    "data": "object",
                    "focus_points": "array"
                },
                "output_type": "text",
                "examples": [
                    "Summarize key findings",
                    "Executive summary of trends",
                    "Brief overview of data"
                ]
            }
        ],
        "endpoint": "/api/agents/narrative",
        "metadata": {
            "keywords": ["story", "narrative", "explain", "summary", "insight", "description"]
        }
    },
    {
        "id": "gui-agent-001",
        "name": "GUI Agent",
        "type": AgentType.GUI,
        "description": "Orchestrates other agents and manages the user interface",
        "capabilities": [
            {
                "name": "orchestrate_query",
                "description": "Coordinate multiple agents to answer complex queries",
                "parameters": {
                    "query": "string",
                    "agents": "array"
                },
                "output_type": "component",
                "examples": [
                    "Analyze renewable energy with charts and insights",
                    "Complete analysis with all available agents",
                    "Coordinate data and visualization"
                ]
            },
            {
                "name": "manage_ui",
                "description": "Dynamically compose UI components",
                "parameters": {
                    "components": "array",
                    "layout": "string"
                },
                "output_type": "component",
                "examples": [
                    "Arrange multiple visualizations",
                    "Create dashboard layout",
                    "Compose interactive interface"
                ]
            }
        ],
        "endpoint": "/api/agents/gui",
        "metadata": {
            "keywords": ["orchestrate", "coordinate", "ui", "interface", "compose", "manage"]
        }
    }
]

async def register_startup_agents(registry):
    """Register example agents with the A2A registry"""
    registered_count = 0
    
    for agent_data in EXAMPLE_AGENTS:
        try:
            # Check if agent already exists
            existing_agents = await registry.list_agents()
            if any(a.id == agent_data["id"] for a in existing_agents):
                logger.info(f"Agent {agent_data['name']} already registered")
                continue
            
            # Register the agent
            result = await registry.register_agent(agent_data)
            if result["success"]:
                logger.info(f"Registered agent: {agent_data['name']}")
                registered_count += 1
            else:
                logger.error(f"Failed to register {agent_data['name']}: {result.get('error')}")
        except Exception as e:
            logger.error(f"Error registering {agent_data['name']}: {e}")
    
    logger.info(f"Startup complete: {registered_count} new agents registered")
    return registered_count