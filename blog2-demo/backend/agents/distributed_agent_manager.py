"""Distributed Agent Manager - Manages remote agent connections via A2A Protocol"""
from typing import Dict, Any, List, Optional
import logging
import asyncio
from mcp.tool_registry import MCPToolRegistry
from registry.models import A2AMessage

logger = logging.getLogger(__name__)

class DistributedAgentManager:
    """Manages distributed agents and their tools via A2A Protocol"""
    
    def __init__(self, mcp_registry: MCPToolRegistry, a2a_registry=None):
        self.mcp_registry = mcp_registry
        self.a2a_registry = a2a_registry
        self.remote_agents: Dict[str, Dict[str, Any]] = {}
        self._monitor_task = None
        
    async def start(self):
        """Start monitoring for agent registrations"""
        if self.a2a_registry:
            # Start monitoring registered agents
            self._monitor_task = asyncio.create_task(self._monitor_agents())
            logger.info("Started distributed agent manager")
    
    async def stop(self):
        """Stop monitoring"""
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
    
    async def _monitor_agents(self):
        """Monitor A2A registry for agent registrations"""
        while True:
            try:
                # Get all registered agents from A2A registry
                if self.a2a_registry:
                    agents_list = await self.a2a_registry.list_agents()
                    current_agents = {}
                    for agent_info in agents_list:
                        agent_id = agent_info.id
                        current_agents[agent_id] = {
                            'id': agent_id,
                            'name': agent_info.name,
                            'type': agent_info.type,
                            'endpoint': agent_info.endpoint,
                            'capabilities': agent_info.capabilities,
                            'status': agent_info.status
                        }
                    logger.info(f"Monitoring: Found {len(current_agents)} agents")
                    
                    # Check for new agents
                    for agent_id, agent_info in current_agents.items():
                        if agent_id not in self.remote_agents:
                            await self._register_remote_agent(agent_id, agent_info)
                    
                    # Check for removed agents
                    removed_agents = set(self.remote_agents.keys()) - set(current_agents.keys())
                    for agent_id in removed_agents:
                        await self._unregister_remote_agent(agent_id)
                    
                    # Update existing agents
                    self.remote_agents = current_agents
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring agents: {e}")
                await asyncio.sleep(10)  # Wait longer on error
    
    async def _register_remote_agent(self, agent_id: str, agent_info: Dict[str, Any]):
        """Register tools from a remote agent"""
        logger.info(f"Registering remote agent: {agent_id} ({agent_info['name']})")
        
        # For each capability, create an MCP tool wrapper
        for capability in agent_info.get('capabilities', []):
            # Parse capability as tool name
            tool_name = capability
            
            # Create executor that sends A2A messages
            def make_executor(aid, tool):
                async def executor(params):
                    return await self.execute_remote_tool(aid, tool, params)
                return executor
            
            # Register with MCP registry using agent-prefixed name
            prefixed_name = f"{agent_id}.{tool_name}"
            try:
                # Create a simple tool definition for remote tools
                from mcp.schemas import MCPTool, ParameterType
                tool_def = MCPTool(
                    name=prefixed_name,
                    description=f"{tool_name} from {agent_info['name']}",
                    parameters=[],  # Remote tools handle their own parameter validation
                    returns={"type": "object", "description": "Agent-specific response"}
                )
                
                self.mcp_registry.register_tool(
                    tool_def,
                    make_executor(agent_id, tool_name)
                )
                logger.info(f"Registered remote tool: {prefixed_name}")
            except Exception as e:
                logger.error(f"Failed to register tool {prefixed_name}: {e}")
    
    async def _unregister_remote_agent(self, agent_id: str):
        """Unregister tools from a removed agent"""
        logger.info(f"Unregistering remote agent: {agent_id}")
        # Note: MCP registry doesn't support unregistration currently
        # This would need to be implemented if agents can be removed
    
    async def execute_remote_tool(self, agent_id: str, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute a tool on a remote agent via A2A"""
        if not self.a2a_registry:
            raise ValueError("A2A Registry not available")
        
        # Send A2A message to execute the tool
        message = A2AMessage(
            from_agent="agent-manager",
            to_agent=agent_id,
            action=tool_name,
            payload=parameters
        )
        
        try:
            response = await self.a2a_registry.send_message(message)
            if response.success:
                return response.data
            else:
                raise Exception(response.error or "Remote tool execution failed")
        except Exception as e:
            logger.error(f"Failed to execute remote tool {agent_id}.{tool_name}: {e}")
            raise
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get remote agent info by ID"""
        return self.remote_agents.get(agent_id)
    
    def get_all_agents(self) -> List[Dict[str, Any]]:
        """Get all remote agent info"""
        return list(self.remote_agents.values())
    
    def get_agent_tools(self, agent_id: str) -> List[str]:
        """Get tools for a specific agent"""
        agent = self.remote_agents.get(agent_id)
        if not agent:
            return []
        return agent.get('capabilities', [])