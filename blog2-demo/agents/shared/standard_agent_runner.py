"""Standardized agent runner with all required endpoints"""
import os
import asyncio
import logging
import json
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import uvicorn
import httpx
from datetime import datetime

from llm import LLMConfig
from models import A2AMessage, MessageType
from standard_schemas import (
    A2AMessageRequest, A2AMessageResponse,
    AgentCardResponse, HealthResponse,
    MCPToolsResponse, MCPExecuteRequest, MCPExecuteResponse,
    ErrorResponse
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StandardAgentRunner:
    """Runs a single agent as a standalone service with standard interfaces"""
    
    def __init__(self, agent_class, agent_instance=None):
        self.agent_class = agent_class
        self.port = int(os.getenv("PORT", "8080"))
        self.registry_url = os.getenv("A2A_REGISTRY_URL", "http://localhost:8000")
        
        # Initialize agent with LLM config from environment
        if agent_instance:
            self.agent = agent_instance
        else:
            # Read LLM configuration from environment variables
            llm_provider = os.getenv("LLM_PROVIDER", "anthropic")
            llm_model = os.getenv("LLM_MODEL", "claude-3-7-sonnet-20250219")
            
            # Get the appropriate API key based on provider
            api_key = None
            if llm_provider == "anthropic":
                api_key = os.getenv("ANTHROPIC_API_KEY")
            elif llm_provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
            
            llm_config = LLMConfig(
                provider=llm_provider,
                model=llm_model,
                api_key=api_key
            )
            
            logger.info(f"Initializing agent with LLM: {llm_provider}/{llm_model}")
            self.agent = agent_class(llm_config=llm_config)
        
        self.app = None
        
    async def register_with_a2a(self):
        """Register this agent with the A2A registry"""
        if not self.agent:
            logger.error("Agent not initialized")
            return False
            
        logger.info(f"Attempting to register {self.agent.name} with A2A registry at {self.registry_url}")
            
        # Get agent type - use class attribute or map from agent name
        agent_type = getattr(self.agent_class, 'AGENT_TYPE', None)
        if not agent_type:
            # Map common agent names to types
            agent_name_lower = self.agent.name.lower()
            if 'data' in agent_name_lower:
                agent_type = 'data'
            elif 'viz' in agent_name_lower or 'visual' in agent_name_lower:
                agent_type = 'visualization'
            elif 'research' in agent_name_lower:
                agent_type = 'research'
            elif 'narrative' in agent_name_lower:
                agent_type = 'narrative'
            elif 'gui' in agent_name_lower:
                agent_type = 'gui'
            else:
                agent_type = 'custom'
        
        # Build capabilities list with proper structure
        capabilities = []
        for tool in self.agent.get_tools():
            capability = {
                "name": tool.name,
                "description": tool.description,
                "parameters": {},
                "output_type": "object",  # Default, could be enhanced
                "examples": []
            }
            
            # Add parameter information
            for param in tool.parameters:
                capability["parameters"][param.name] = {
                    "type": param.type.value,
                    "description": param.description,
                    "required": param.required
                }
            
            # Add examples if available
            for example in tool.examples[:2]:  # Limit to 2 examples
                if "description" in example:
                    capability["examples"].append(example["description"])
            
            capabilities.append(capability)
        
        # Map agent IDs to container names
        container_names = {
            "data-agent-001": "data-agent",
            "viz-agent-001": "viz-agent",
            "research-agent-001": "research-agent",
            "narrative-agent-001": "narrative-agent",
            "gui-agent-001": "gui-agent"
        }
        container_name = container_names.get(self.agent.agent_id, self.agent.agent_id)
        
        # Prepare registration data
        registration_data = {
            "id": self.agent.agent_id,
            "name": self.agent.name,
            "type": agent_type,
            "description": self.agent.description,
            "endpoint": f"http://{container_name}:{self.port}",
            "capabilities": capabilities,
            "version": "1.0.0",
            "metadata": {
                "container": True,
                "started_at": datetime.now().isoformat()
            }
        }
        
        # Wait a bit for backend to be fully ready
        await asyncio.sleep(5)
        
        # First, test connectivity to the backend
        logger.info(f"Testing connectivity to backend...")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                health_response = await client.get(f"{self.registry_url}/health")
                if health_response.status_code == 200:
                    logger.info(f"Backend is reachable. Health: {health_response.json()}")
                else:
                    logger.error(f"Backend returned status {health_response.status_code}")
        except Exception as e:
            logger.error(f"Cannot reach backend at {self.registry_url}: {type(e).__name__}: {e}")
        
        # Try to register with the A2A registry
        max_retries = 10
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    logger.debug(f"Sending registration data: {json.dumps(registration_data, indent=2)}")
                    response = await client.post(
                        f"{self.registry_url}/api/registry/register",
                        json=registration_data
                    )
                    
                    logger.debug(f"Registration response status: {response.status_code}")
                    if response.status_code == 200:
                        result = response.json()
                        logger.debug(f"Registration response: {result}")
                        if result.get("success"):
                            logger.info(f"Successfully registered agent {self.agent.agent_id} with A2A registry")
                            return True
                        else:
                            logger.error(f"Failed to register: {result.get('error')}")
                    else:
                        error_text = response.text
                        logger.error(f"Registration failed with status {response.status_code}: {error_text}")
                        
            except httpx.ConnectError as e:
                logger.warning(f"Cannot connect to A2A registry at {self.registry_url}, retrying... ({retry_count + 1}/{max_retries})")
                logger.debug(f"Connection error: {e}")
            except Exception as e:
                logger.error(f"Error registering with A2A: {type(e).__name__}: {e}")
                import traceback
                logger.debug(f"Traceback: {traceback.format_exc()}")
            
            retry_count += 1
            await asyncio.sleep(5)  # Wait 5 seconds before retry
        
        logger.error(f"Failed to register with A2A registry after {max_retries} attempts")
        return False
    
    def create_app(self):
        """Create FastAPI app for the agent with standard endpoints"""
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            logger.info(f"Starting {self.agent.name} on port {self.port}")
            await self.register_with_a2a()
            yield
            # Shutdown
            logger.info(f"Shutting down {self.agent.name}")
        
        app = FastAPI(
            title=f"{self.agent.name} API",
            description=f"Standard API for {self.agent.name}",
            version="1.0.0",
            lifespan=lifespan
        )
        
        @app.get("/agent-card", response_model=AgentCardResponse)
        async def get_agent_card():
            """Get agent metadata card"""
            try:
                # Use the agent's built-in method if available
                if hasattr(self.agent, 'get_agent_card'):
                    return self.agent.get_agent_card()
                
                # Otherwise construct from available info
                return AgentCardResponse(
                    agent_id=self.agent.agent_id,
                    name=self.agent.name,
                    description=self.agent.description,
                    capabilities=getattr(self.agent, 'capabilities', []),
                    tags=getattr(self.agent, 'tags', []),
                    tools=[
                        {"name": tool.name, "description": tool.description}
                        for tool in self.agent.get_tools()
                    ],
                    status=self.agent.get_health_status() if hasattr(self.agent, 'get_health_status') else {
                        "status": "healthy",
                        "uptime_seconds": 0
                    },
                    metadata={
                        "llm_model": self.agent.llm_config.model,
                        "semantic_tool_selection": getattr(self.agent, 'semantic_tool_selection', False),
                        "version": "1.0.0"
                    }
                )
            except Exception as e:
                logger.error(f"Error getting agent card: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/health", response_model=HealthResponse)
        async def health_check():
            """Get agent health status"""
            try:
                if hasattr(self.agent, 'get_health_status'):
                    health_data = self.agent.get_health_status()
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
            except Exception as e:
                logger.error(f"Error checking health: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/mcp/tools", response_model=MCPToolsResponse)
        async def list_mcp_tools():
            """List available MCP tools"""
            try:
                if hasattr(self.agent, 'get_mcp_tools'):
                    tools = self.agent.get_mcp_tools()
                else:
                    # Fallback to basic tool info
                    tools = []
                    for tool in self.agent.get_tools():
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
                    agent_id=self.agent.agent_id,
                    agent_name=self.agent.name
                )
            except Exception as e:
                logger.error(f"Error listing MCP tools: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.post("/mcp/execute/{tool_name}", response_model=MCPExecuteResponse)
        async def execute_mcp_tool(tool_name: str, request: MCPExecuteRequest):
            """Execute a specific MCP tool"""
            try:
                result = await self.agent.execute_tool(tool_name, request.parameters)
                
                return MCPExecuteResponse(
                    success=result.success,
                    result=result.result if result.success else None,
                    error=result.error if not result.success else None,
                    metadata=result.metadata if hasattr(result, 'metadata') else {}
                )
            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {e}")
                return MCPExecuteResponse(
                    success=False,
                    error=str(e),
                    metadata={"error_type": type(e).__name__}
                )
        
        @app.post("/a2a/message", response_model=A2AMessageResponse)
        async def handle_a2a_message(request: A2AMessageRequest):
            """Handle incoming A2A messages"""
            logger.info(f"{self.agent.name} received A2A message: action={request.action} from={request.from_agent}")
            
            try:
                # Convert to A2AMessage
                message = A2AMessage(
                    from_agent=request.from_agent,
                    to_agent=self.agent.agent_id,
                    action=request.action,
                    payload=request.payload,
                    correlation_id=getattr(request, 'correlation_id', None),
                    message_type=MessageType(request.message_type)
                )
                
                logger.debug(f"Message payload: {json.dumps(request.payload, indent=2)}")
                
                # Use agent's A2A message handler
                result = await self.agent.handle_a2a_message(message)
                
                # Check if result indicates an error
                if isinstance(result, dict):
                    if "error" in result:
                        logger.warning(f"{self.agent.name} returned error: {result['error']}")
                        return A2AMessageResponse(
                            success=False,
                            error=result["error"],
                            semantic_selection=result.get("semantic_selection", False)
                        )
                    elif result.get("success") is False:
                        logger.warning(f"{self.agent.name} returned failure: {result}")
                        return A2AMessageResponse(
                            success=False,
                            error=result.get("error", "Unknown error"),
                            tools_used=result.get("tools_used"),
                            semantic_selection=result.get("semantic_selection", False)
                        )
                
                logger.info(f"{self.agent.name} successfully handled {request.action}")
                logger.debug(f"Result: {json.dumps(result, indent=2) if isinstance(result, dict) else str(result)}")
                
                # Extract tools used if present
                tools_used = None
                semantic_selection = False
                if isinstance(result, dict):
                    tools_used = result.get("tools_used") or result.get("tool_sequence")
                    semantic_selection = result.get("semantic_selection", False)
                
                return A2AMessageResponse(
                    success=True,
                    result=result,
                    tools_used=tools_used,
                    semantic_selection=semantic_selection
                )
                
            except Exception as e:
                logger.error(f"Error handling A2A message in {self.agent.name}: {type(e).__name__}: {e}")
                import traceback
                logger.debug(f"Traceback: {traceback.format_exc()}")
                
                return A2AMessageResponse(
                    success=False,
                    error=str(e)
                )
        
        # Legacy endpoints for backward compatibility
        @app.get("/tools")
        async def list_tools():
            """List available tools (legacy endpoint)"""
            return {
                "agent": self.agent.agent_id,
                "tools": self.agent.get_tool_info()
            }
        
        @app.post("/tools/{tool_name}/execute")
        async def execute_tool(tool_name: str, parameters: Dict[str, Any]):
            """Execute a specific tool (legacy endpoint)"""
            try:
                result = await self.agent.execute_tool(tool_name, parameters)
                return result.model_dump()
            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        self.app = app
        return app
    
    async def run(self):
        """Run the agent service"""
        app = self.create_app()
        
        config = uvicorn.Config(
            app,
            host="0.0.0.0",
            port=self.port,
            log_level="info"
        )
        
        server = uvicorn.Server(config)
        await server.serve()