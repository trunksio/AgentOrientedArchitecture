"""Standard agent endpoints for backend agents"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
import logging

from agents.standard_schemas import (
    AgentCardResponse, HealthResponse, 
    MCPToolsResponse, MCPExecuteRequest, MCPExecuteResponse,
    ErrorResponse
)

logger = logging.getLogger(__name__)

def create_agent_router(agent_manager) -> APIRouter:
    """Create router with standard agent endpoints"""
    router = APIRouter(prefix="/api/agents", tags=["agents"])
    
    @router.get("/{agent_id}/agent-card", response_model=AgentCardResponse)
    async def get_agent_card(agent_id: str):
        """Get agent metadata card"""
        try:
            agent = agent_manager.agents.get(agent_id)
            if not agent:
                raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
            
            if hasattr(agent, 'get_agent_card'):
                return agent.get_agent_card()
            
            # Fallback construction
            return AgentCardResponse(
                agent_id=agent.agent_id,
                name=agent.name,
                description=agent.description,
                capabilities=getattr(agent, 'capabilities', []),
                tags=getattr(agent, 'tags', []),
                tools=[
                    {"name": tool.name, "description": tool.description}
                    for tool in agent.get_tools()
                ],
                status=agent.get_health_status() if hasattr(agent, 'get_health_status') else {
                    "status": "healthy",
                    "uptime_seconds": 0
                },
                metadata={
                    "llm_model": agent.llm_config.model if hasattr(agent, 'llm_config') else "unknown",
                    "semantic_tool_selection": getattr(agent, 'semantic_tool_selection', False),
                    "version": "1.0.0"
                }
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting agent card: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/{agent_id}/health", response_model=HealthResponse)
    async def get_agent_health(agent_id: str):
        """Get agent health status"""
        try:
            agent = agent_manager.agents.get(agent_id)
            if not agent:
                raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
            
            if hasattr(agent, 'get_health_status'):
                health_data = agent.get_health_status()
                return HealthResponse(**health_data)
            
            # Basic health response
            return HealthResponse(
                status="healthy",
                uptime_seconds=0,
                request_count=0,
                error_count=0,
                error_rate=0.0,
                llm_available=True
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error checking agent health: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/{agent_id}/mcp/tools", response_model=MCPToolsResponse)
    async def list_agent_mcp_tools(agent_id: str):
        """List available MCP tools for an agent"""
        try:
            agent = agent_manager.agents.get(agent_id)
            if not agent:
                raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
            
            if hasattr(agent, 'get_mcp_tools'):
                tools = agent.get_mcp_tools()
            else:
                # Fallback to basic tool info
                tools = []
                for tool in agent.get_tools():
                    tools.append({
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": {
                            "type": "object",
                            "properties": {
                                param.name: {
                                    "type": param.type.value,
                                    "description": param.description
                                } for param in tool.parameters
                            },
                            "required": [param.name for param in tool.parameters if param.required]
                        },
                        "returns": tool.returns,
                        "examples": tool.examples
                    })
            
            return MCPToolsResponse(
                tools=tools,
                agent_id=agent.agent_id,
                agent_name=agent.name
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error listing MCP tools: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/{agent_id}/mcp/execute/{tool_name}", response_model=MCPExecuteResponse)
    async def execute_agent_mcp_tool(agent_id: str, tool_name: str, request: MCPExecuteRequest):
        """Execute a specific MCP tool for an agent"""
        try:
            agent = agent_manager.agents.get(agent_id)
            if not agent:
                raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
            
            result = await agent.execute_tool(tool_name, request.parameters)
            
            return MCPExecuteResponse(
                success=result.success,
                result=result.result if result.success else None,
                error=result.error if not result.success else None,
                metadata=result.metadata if hasattr(result, 'metadata') else {}
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return MCPExecuteResponse(
                success=False,
                error=str(e),
                metadata={"error_type": type(e).__name__}
            )
    
    @router.get("/list", response_model=Dict[str, Any])
    async def list_all_agents():
        """List all registered agents with their standard info"""
        try:
            agents_info = []
            
            # Get backend agents
            for agent_id, agent in agent_manager.agents.items():
                agent_info = {
                    "agent_id": agent_id,
                    "name": agent.name,
                    "description": agent.description,
                    "type": "backend",
                    "capabilities": getattr(agent, 'capabilities', []),
                    "tags": getattr(agent, 'tags', []),
                    "tools_count": len(agent.get_tools())
                }
                agents_info.append(agent_info)
            
            # Get containerized agents from A2A registry
            if hasattr(agent_manager, 'a2a_registry') and agent_manager.a2a_registry:
                registry_agents = await agent_manager.a2a_registry.list_agents()
                for reg_agent in registry_agents:
                    # Skip if already in backend list
                    if not any(a['agent_id'] == reg_agent['id'] for a in agents_info):
                        agent_info = {
                            "agent_id": reg_agent['id'],
                            "name": reg_agent['name'],
                            "description": reg_agent.get('description', ''),
                            "type": reg_agent.get('type', 'containerized'),
                            "capabilities": [cap['name'] for cap in reg_agent.get('capabilities', [])],
                            "tags": reg_agent.get('tags', []),
                            "endpoint": reg_agent.get('endpoint', '')
                        }
                        agents_info.append(agent_info)
            
            return {
                "agents": agents_info,
                "total_count": len(agents_info)
            }
        except Exception as e:
            logger.error(f"Error listing agents: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return router