from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import uvicorn
from typing import Dict, List, Optional, Any
import json
from cryptography.fernet import Fernet
import asyncio
import time
from datetime import datetime

# Import our modules
from registry.a2a_registry import A2ARegistry
from registry.models import AgentRegistration, DiscoveryQuery, A2AMessage, MessageType
from mcp.tool_registry import MCPToolRegistry
from mcp.schemas import ToolExecution
from startup_agents import register_startup_agents
from agents.distributed_agent_manager import DistributedAgentManager
from websocket_manager import ws_manager

# Global registries
a2a_registry = None
mcp_registry = None
agent_manager = None

# Configuration storage (in production, use a proper database)
agent_configs: Dict[str, Dict[str, Any]] = {}

# Generate or load encryption key for API keys
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key().decode())
cipher_suite = Fernet(ENCRYPTION_KEY.encode())

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global a2a_registry, mcp_registry, agent_manager
    a2a_registry = A2ARegistry()
    mcp_registry = MCPToolRegistry()
    
    # Initialize distributed agent manager
    agent_manager = DistributedAgentManager(mcp_registry, a2a_registry)
    await agent_manager.start()
    
    # No need to register agents here - they self-register when containers start
    print("Started AOA Demo Backend")
    yield
    # Shutdown
    await agent_manager.stop()
    print("Shutting down AOA Demo Backend")

app = FastAPI(
    title="Agent Oriented Architecture Demo",
    description="Demonstrates A2A Protocol, MCP, and Generative UI",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "AOA Demo Backend",
        "version": "1.0.0",
        "features": ["A2A Protocol", "MCP", "Generative UI"]
    }

@app.get("/health")
async def health_check():
    # Get agent count
    agent_count = 0
    if a2a_registry:
        try:
            agents = await a2a_registry.list_agents()
            agent_count = len(agents)
        except:
            pass
    
    return {
        "status": "healthy",
        "services": {
            "a2a_registry": a2a_registry is not None,
            "mcp_registry": mcp_registry is not None,
            "chromadb": a2a_registry.is_connected() if a2a_registry else False,
            "registered_agents": agent_count
        }
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message["type"] == "ping":
                await websocket.send_json({"type": "pong"})
            elif message["type"] == "agent_status":
                # Broadcast agent status to all clients
                await ws_manager.broadcast_agent_message({
                    "type": "agent_status",
                    **message
                })
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)

# Agent Registry endpoints
@app.post("/api/registry/register")
async def register_agent(agent: AgentRegistration):
    """Register a new agent with the A2A registry"""
    # Convert to dict for registry
    agent_data = agent.model_dump()
    
    # Ensure ID is set
    if not agent_data.get("id"):
        import uuid
        agent_data["id"] = str(uuid.uuid4())
    
    result = await a2a_registry.register_agent(agent_data)
    
    if result["success"]:
        # Notify all connected clients about new agent
        await ws_manager.broadcast_agent_message({
            "type": "agent_registered",
            "agent": agent_data
        })
    
    return result

@app.post("/api/registry/discover")
async def discover_agents(query: DiscoveryQuery):
    """Discover agents based on semantic search"""
    results = await a2a_registry.discover_agents(
        intent=query.intent,
        max_results=query.max_results
    )
    
    # Convert to dict for JSON serialization
    return [
        {
            "agent": result.agent.model_dump(),
            "relevance_score": result.relevance_score,
            "matched_capabilities": result.matched_capabilities
        }
        for result in results
    ]

@app.get("/api/registry/agents")
async def list_agents():
    """List all registered agents"""
    agents = await a2a_registry.list_agents()
    return [agent.model_dump() for agent in agents]

# MCP Tool endpoints
@app.get("/api/mcp/tools")
async def list_tools():
    """List all available MCP tools"""
    return await mcp_registry.list_tools()

@app.get("/api/mcp/tools/{agent_id}")
async def list_agent_tools(agent_id: str):
    """List tools for a specific agent"""
    return agent_manager.get_agent_tools(agent_id)

@app.post("/api/mcp/discover")
async def discover_tools(query: dict):
    """Discover tools based on intent"""
    intent = query.get("intent", "")
    # For distributed agents, use A2A discovery
    if a2a_registry:
        results = await a2a_registry.discover_agents(intent)
        tools = []
        for result in results:
            agent_id = result.agent.id
            for capability in result.agent.capabilities:
                tools.append({
                    "agent_id": agent_id,
                    "name": f"{agent_id}.{capability}",
                    "description": f"{capability} from {result.agent.name}"
                })
        return tools
    return []

@app.post("/api/mcp/execute")
async def execute_tool(execution: ToolExecution):
    """Execute an MCP tool"""
    result = await mcp_registry.execute_tool(execution.tool, execution.parameters)
    return result.model_dump()

# Agent orchestration endpoints
@app.post("/api/orchestrate")
async def orchestrate_query(query_request: dict):
    """Orchestrate multiple agents to handle a complex query"""
    query = query_request.get("query", "")
    context = query_request.get("context", {})
    
    # Use A2A to send message to GUI agent
    if a2a_registry:
        import uuid
        message = A2AMessage(
            id=str(uuid.uuid4()),
            from_agent="api",
            to_agent="gui-agent-001",
            message_type=MessageType.REQUEST,
            action="orchestrate_query",
            payload={"query": query, "context": context}
        )
        
        try:
            response = await a2a_registry.send_message(message)
            if response.success:
                return response.result or {"message": "Orchestration completed"}
            else:
                return {"error": response.error or "Orchestration failed"}
        except Exception as e:
            return {"error": str(e)}
    
    return {"error": "A2A registry not available"}

@app.post("/api/agents/{agent_id}/config")
async def update_agent_config(agent_id: str, config: Dict[str, Any]):
    """Update agent configuration including LLM settings"""
    try:
        # Encrypt API key if provided
        if "llm_config" in config and "api_key" in config["llm_config"]:
            api_key = config["llm_config"]["api_key"]
            if api_key:  # Only encrypt if not empty
                encrypted_key = cipher_suite.encrypt(api_key.encode()).decode()
                config["llm_config"]["api_key"] = encrypted_key
        
        # Store configuration
        agent_configs[agent_id] = config
        
        # Notify the agent about configuration update if it's connected
        # This would trigger the agent to reload its configuration
        await a2a_registry.send_message(A2AMessage(
            from_agent="config-manager",
            to_agent=agent_id,
            message_type=MessageType.NOTIFICATION,
            action="config_update",
            payload={"config": config}
        ))
        
        return {"success": True, "message": "Configuration updated"}
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error updating agent config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents/{agent_id}/config")
async def get_agent_config(agent_id: str):
    """Get agent configuration (without exposing API keys)"""
    config = agent_configs.get(agent_id, {})
    
    # Remove encrypted API key from response
    if "llm_config" in config and "api_key" in config["llm_config"]:
        config = config.copy()
        config["llm_config"] = config["llm_config"].copy()
        config["llm_config"]["api_key"] = "***" if config["llm_config"]["api_key"] else ""
    
    return config

@app.post("/api/a2a/message")
async def handle_a2a_message(message: Dict[str, Any]):
    """Route A2A messages between agents with improved error handling"""
    try:
        # Validate message structure
        required_fields = ["from_agent", "to_agent", "action", "payload"]
        for field in required_fields:
            if field not in message:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        a2a_message = A2AMessage(
            from_agent=message["from_agent"],
            to_agent=message["to_agent"],
            message_type=MessageType(message.get("message_type", "request")),
            action=message["action"],
            payload=message["payload"]
        )
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Routing A2A message: {a2a_message.from_agent} -> {a2a_message.to_agent} ({a2a_message.action})")
        
        result = await a2a_registry.send_message(a2a_message)
        
        if result.success:
            logger.info(f"A2A message successfully delivered to {a2a_message.to_agent}")
            return {"success": True, "result": result.result}
        else:
            logger.error(f"A2A message failed: {result.error}")
            # Don't raise HTTPException for agent errors, return them gracefully
            return {"success": False, "error": result.error, "details": f"Agent {a2a_message.to_agent} returned an error"}
            
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error handling A2A message: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e), "type": "routing_error"}

@app.get("/api/a2a/messages")
async def get_message_history(limit: int = 100, agent_id: Optional[str] = None):
    """Get A2A message history"""
    messages = a2a_registry.get_message_history(limit, agent_id)
    return [msg.model_dump() for msg in messages]

@app.post("/api/a2a/orchestrate")
async def orchestrate_via_a2a(request: dict):
    """Orchestrate agents using A2A Protocol"""
    intent = request.get("intent", "")
    initiator = request.get("initiator", "user")
    
    result = await a2a_registry.orchestrate_agents(intent, initiator)
    return result

@app.get("/api/debug/test-agent/{agent_id}")
async def test_agent_communication(agent_id: str):
    """Test direct communication with an agent"""
    if not a2a_registry:
        return {"error": "A2A registry not available"}
    
    # Send a simple test message
    import uuid
    message = A2AMessage(
        id=str(uuid.uuid4()),
        from_agent="api-debug",
        to_agent=agent_id,
        message_type=MessageType.REQUEST,
        action="handle_intent",
        payload={
            "intent": "test connectivity",
            "context": {"test": True}
        }
    )
    
    try:
        response = await a2a_registry.send_message(message)
        return {
            "success": response.success,
            "result": response.result,
            "error": response.error,
            "metadata": response.metadata
        }
    except Exception as e:
        return {"error": str(e), "agent_id": agent_id}

@app.post("/api/agents/add-live")
async def add_agent_live(request: dict):
    """Add a new agent to the system dynamically"""
    import logging
    import traceback
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Received live agent addition request: {request}")
        
        agent_config = request.get("agent_config", {})
        logger.info(f"Agent config: {agent_config}")
        
        # Validate required fields
        required_fields = ["name", "description", "capabilities", "endpoint"]
        for field in required_fields:
            if field not in agent_config:
                logger.error(f"Missing required field: {field}")
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Create proper AgentRegistration object
        from registry.models import AgentRegistration, AgentType, AgentCapability, AgentStatus
        
        logger.info("Creating AgentCapability objects...")
        
        # Convert simple capabilities list to AgentCapability objects
        capabilities = []
        for cap in agent_config["capabilities"]:
            if isinstance(cap, str):
                # Simple capability name - create basic AgentCapability
                capability = AgentCapability(
                    name=cap.replace(" ", "_").lower(),
                    description=f"Capability for {cap}",
                    parameters={},
                    output_type="object",
                    examples=[f"Use {cap} capabilities"]
                )
                capabilities.append(capability)
                logger.info(f"Created capability: {capability.name}")
            else:
                # Already formatted capability
                capability = AgentCapability(**cap)
                capabilities.append(capability)
                logger.info(f"Used existing capability: {capability.name}")
        
        # Determine agent type
        agent_type = AgentType.PREDICTION if "prediction" in agent_config["name"].lower() else AgentType.CUSTOM
        logger.info(f"Determined agent type: {agent_type}")
        
        # Create AgentRegistration
        logger.info("Creating AgentRegistration object...")
        agent = AgentRegistration(
            id=agent_config.get("agent_id", f"{agent_config['name'].lower().replace(' ', '-')}-001"),
            name=agent_config["name"],
            type=agent_type,
            description=agent_config["description"],
            capabilities=capabilities,
            endpoint=agent_config["endpoint"],
            status=AgentStatus.ACTIVE,
            metadata={
                "added_live": True,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        logger.info(f"Created agent registration: {agent.id}")
        
        # Register the agent using the proper registry method
        logger.info("Attempting to register agent with A2A registry...")
        result = await a2a_registry.register_agent(agent.model_dump())
        logger.info(f"Registry result: {result}")
        
        if result.get("success"):
            # Broadcast agent addition via WebSocket
            try:
                await ws_manager.broadcast_agent_message({
                    "type": "agent_added",
                    "agent": agent.model_dump(),
                    "message": f"New agent '{agent.name}' added to the system"
                })
                logger.info("Broadcasted agent addition via WebSocket")
            except Exception as ws_error:
                logger.warning(f"Failed to broadcast WebSocket message: {ws_error}")
            
            logger.info(f"Live agent added successfully: {agent.name}")
            
            return {
                "success": True,
                "agent": agent.model_dump(),
                "message": f"Agent '{agent.name}' successfully added to the system"
            }
        else:
            logger.error(f"Registry registration failed: {result}")
            raise HTTPException(status_code=500, detail=f"Failed to register agent: {result}")
        
    except HTTPException as he:
        # Re-raise HTTP exceptions
        logger.error(f"HTTP exception in live agent addition: {he.detail}")
        raise he
    except Exception as e:
        # Log the full traceback for debugging
        logger.error(f"Unexpected error adding live agent: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to add agent: {str(e)}")

@app.post("/api/agents/deploy")
async def deploy_agent_container(request: dict):
    """Deploy a new agent container dynamically"""
    try:
        agent_type = request.get("agent_type")
        agent_name = request.get("agent_name", f"{agent_type}-agent")
        
        # Supported agent types for live deployment
        supported_types = {
            "prediction": {
                "image": "prediction-agent",
                "port": 8007,
                "capabilities": ["forecasting", "trend analysis", "predictions"]
            }
        }
        
        if agent_type not in supported_types:
            raise HTTPException(status_code=400, detail=f"Unsupported agent type: {agent_type}")
        
        agent_spec = supported_types[agent_type]
        
        # In a real implementation, this would use Docker API or Kubernetes API
        # For demo purposes, we'll simulate the deployment
        
        # Simulate container deployment
        container_id = f"container-{agent_name}-{int(time.time())}"
        
        # Register the agent
        agent_data = {
            "agent_id": f"{agent_name}-001",
            "name": agent_name.title(),
            "description": f"Dynamically deployed {agent_type} agent",
            "capabilities": agent_spec["capabilities"],
            "endpoint": f"http://{agent_name}:{agent_spec['port']}",
            "container_id": container_id,
            "status": "deploying",
            "added_live": True,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to registry
        await a2a_registry.register_agent(agent_data)
        
        # Simulate deployment completion after a short delay
        asyncio.create_task(simulate_deployment_completion(agent_data))
        
        # Broadcast deployment started
        await ws_manager.broadcast_agent_message({
            "type": "agent_deploying",
            "agent": agent_data,
            "message": f"Deploying {agent_name}..."
        })
        
        return {
            "success": True,
            "agent": agent_data,
            "container_id": container_id,
            "message": f"Deployment started for {agent_name}"
        }
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error deploying agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to deploy agent: {str(e)}")

async def simulate_deployment_completion(agent_data: dict):
    """Simulate deployment completion for demo purposes"""
    try:
        # Wait a few seconds to simulate deployment
        await asyncio.sleep(3)
        
        # Update agent status
        agent_data["status"] = "active"
        
        # Update in registry
        await a2a_registry.update_agent(agent_data["agent_id"], agent_data)
        
        # Broadcast completion
        await ws_manager.broadcast_agent_message({
            "type": "agent_deployed",
            "agent": agent_data,
            "message": f"Agent '{agent_data['name']}' is now active and ready!"
        })
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Agent deployment completed: {agent_data['name']}")
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in deployment simulation: {e}")

@app.get("/api/agents/available-types")
async def get_available_agent_types():
    """Get available agent types for live deployment"""
    return {
        "agent_types": [
            {
                "type": "prediction",
                "name": "Prediction Agent",
                "description": "Forecasting and trend analysis agent",
                "capabilities": ["forecasting", "trend analysis", "scenario planning"],
                "ready_to_deploy": True
            },
            {
                "type": "sentiment",
                "name": "Sentiment Agent", 
                "description": "Market sentiment analysis agent",
                "capabilities": ["sentiment analysis", "market mood", "social listening"],
                "ready_to_deploy": False,
                "note": "Coming in future demo"
            }
        ]
    }

@app.delete("/api/agents/{agent_id}")
async def remove_agent(agent_id: str):
    """Remove an agent from the system"""
    try:
        # Get agent info before removal
        agent = await a2a_registry.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Remove from registry
        await a2a_registry.unregister_agent(agent_id)
        
        # Broadcast removal
        await ws_manager.broadcast_agent_message({
            "type": "agent_removed",
            "agent_id": agent_id,
            "message": f"Agent '{agent['name']}' removed from system"
        })
        
        return {
            "success": True,
            "message": f"Agent '{agent['name']}' removed successfully"
        }
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error removing agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to remove agent: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        ws="auto"
    )