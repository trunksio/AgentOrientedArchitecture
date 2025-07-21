"""Agent Manager - Manages agent instances and tool execution"""
from typing import Dict, Any, List, Optional
import logging
from .base_agent import BaseAgent
from .data_agent import DataAgent
from .viz_agent import VisualizationAgent
from .gui_agent import GUIAgent
from .research_agent import ResearchAgent
from .narrative_agent import NarrativeAgent
from mcp.tool_registry import MCPToolRegistry

logger = logging.getLogger(__name__)

class AgentManager:
    """Manages all agent instances and their tools"""
    
    def __init__(self, mcp_registry: MCPToolRegistry, a2a_registry=None):
        self.mcp_registry = mcp_registry
        self.a2a_registry = a2a_registry
        self.agents: Dict[str, BaseAgent] = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all available agents"""
        # Create agent instances
        agents = [
            DataAgent(),
            VisualizationAgent(),
            ResearchAgent(),
            NarrativeAgent(),
            GUIAgent(),
        ]
        
        # Register agents and their tools
        for agent in agents:
            self.agents[agent.agent_id] = agent
            
            # Set A2A registry reference in agent
            agent.a2a_registry = self.a2a_registry
            
            # Register agent message handler with A2A
            if self.a2a_registry:
                self.a2a_registry.register_agent_handler(
                    agent.agent_id,
                    agent.handle_a2a_message
                )
            
            # Register all agent tools with MCP registry
            for tool in agent.get_tools():
                # Create executor wrapper with closure
                def make_executor(agent_id, tool_name):
                    async def executor(params):
                        return await self.execute_agent_tool(agent_id, tool_name, params)
                    return executor
                
                self.mcp_registry.register_tool(
                    tool,
                    make_executor(agent.agent_id, tool.name)
                )
            
            logger.info(f"Initialized {agent.name} with {len(agent.get_tools())} tools")
    
    async def execute_agent_tool(self, agent_id: str, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute a tool on a specific agent"""
        agent = self.agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        result = await agent.execute_tool(tool_name, parameters)
        if not result.success:
            raise Exception(result.error)
        
        return result.result
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def get_all_agents(self) -> List[BaseAgent]:
        """Get all agent instances"""
        return list(self.agents.values())
    
    def get_agent_tools(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get tools for a specific agent"""
        agent = self.agents.get(agent_id)
        if not agent:
            return []
        return agent.get_tool_info()
    
    def discover_tools_for_intent(self, intent: str) -> List[Dict[str, Any]]:
        """Discover tools that might handle a given intent"""
        # This could be enhanced with semantic matching
        all_tools = []
        for agent in self.agents.values():
            tools = agent.get_tool_info()
            # Simple keyword matching for now
            intent_lower = intent.lower()
            for tool in tools:
                if (intent_lower in tool['name'].lower() or 
                    intent_lower in tool['description'].lower() or
                    any(intent_lower in ex.get('description', '').lower() for ex in tool.get('examples', []))):
                    all_tools.append(tool)
        
        return all_tools