import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import os
from typing import List, Dict, Any, Optional
import json
import uuid
from datetime import datetime
import logging
import aiohttp
import asyncio
import httpx

from .models import AgentRegistration, DiscoveryResult, AgentCapability, A2AMessage, A2AResponse, MessageType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class A2ARegistry:
    def __init__(self):
        self.chroma_host = os.getenv("CHROMA_HOST", "localhost")
        self.chroma_port = int(os.getenv("CHROMA_PORT", "8001"))
        self.client = None
        self.collection = None
        self._initialize_client()
        
        # Communication components
        self.agent_handlers = {}  # agent_id -> handler function
        self.message_history = []
        self.pending_responses = {}  # correlation_id -> response
        
        # In-memory cache of agents for quick access
        self.agents = {}
    
    def _initialize_client(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Try to use OpenAI embeddings if API key is available
            openai_api_key = os.getenv("OPENAI_API_KEY")
            embedding_function = None
            
            if openai_api_key:
                try:
                    embedding_function = embedding_functions.OpenAIEmbeddingFunction(
                        api_key=openai_api_key,
                        model_name="text-embedding-ada-002"
                    )
                    logger.info("Using OpenAI embeddings for semantic search")
                except Exception as e:
                    logger.warning(f"Failed to initialize OpenAI embeddings: {e}")
            
            if not embedding_function:
                # Use default embedding function (no external dependencies)
                embedding_function = embedding_functions.DefaultEmbeddingFunction()
                logger.info("Using default embeddings for semantic search")
            
            self.client = chromadb.HttpClient(
                host=self.chroma_host,
                port=self.chroma_port,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                    is_persistent=True
                )
            )
            
            # Create or get the agents collection with embedding function
            self.collection = self.client.get_or_create_collection(
                name="agents",
                metadata={"description": "Agent capability registry"},
                embedding_function=embedding_function
            )
            logger.info(f"Connected to ChromaDB at {self.chroma_host}:{self.chroma_port}")
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e}")
            # Fallback to in-memory client for development
            self.client = chromadb.Client()
            self.collection = self.client.get_or_create_collection(
                name="agents",
                embedding_function=embedding_functions.DefaultEmbeddingFunction()
            )
    
    def is_connected(self) -> bool:
        """Check if ChromaDB is connected"""
        try:
            if self.client:
                self.client.heartbeat()
                return True
        except:
            pass
        return False
    
    async def register_agent(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new agent in the A2A registry"""
        try:
            # Create agent registration
            agent = AgentRegistration(**agent_data)
            
            # Generate embedding text from agent description and capabilities
            embedding_text = self._create_embedding_text(agent)
            
            # Store in ChromaDB
            self.collection.add(
                ids=[agent.id],
                documents=[embedding_text],
                metadatas=[{
                    "agent_data": agent.model_dump_json(),
                    "type": agent.type.value,
                    "name": agent.name,
                    "registered_at": agent.registered_at.isoformat()
                }]
            )
            
            # Add to in-memory cache
            self.agents[agent.id] = agent.model_dump()
            
            return {
                "success": True,
                "agent_id": agent.id,
                "message": f"Agent '{agent.name}' registered successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def discover_agents(self, intent: str, max_results: int = 5) -> List[DiscoveryResult]:
        """Discover agents based on semantic search of intent"""
        try:
            # Query ChromaDB for similar agents
            results = self.collection.query(
                query_texts=[intent],
                n_results=max_results
            )
            
            discovered_agents = []
            if results and results['ids'] and len(results['ids'][0]) > 0:
                for i, agent_id in enumerate(results['ids'][0]):
                    metadata = results['metadatas'][0][i]
                    distance = results['distances'][0][i] if 'distances' in results else 0
                    
                    # Parse agent data
                    agent_data = json.loads(metadata['agent_data'])
                    agent = AgentRegistration(**agent_data)
                    
                    # Calculate relevance score (convert distance to similarity)
                    relevance_score = 1.0 - (distance / 2.0) if distance else 1.0
                    
                    # Determine which capabilities matched
                    matched_capabilities = self._find_matched_capabilities(agent, intent)
                    
                    discovered_agents.append(DiscoveryResult(
                        agent=agent,
                        relevance_score=relevance_score,
                        matched_capabilities=matched_capabilities
                    ))
            
            return discovered_agents
        except Exception as e:
            print(f"Error discovering agents: {e}")
            return []
    
    async def list_agents(self) -> List[AgentRegistration]:
        """List all registered agents"""
        try:
            # Get all documents from collection
            all_results = self.collection.get()
            
            agents = []
            if all_results and all_results['ids']:
                for i, agent_id in enumerate(all_results['ids']):
                    metadata = all_results['metadatas'][i]
                    agent_data = json.loads(metadata['agent_data'])
                    agents.append(AgentRegistration(**agent_data))
            
            return agents
        except Exception as e:
            print(f"Error listing agents: {e}")
            return []
    
    def _create_embedding_text(self, agent: AgentRegistration) -> str:
        """Create text for embedding from agent data"""
        parts = [
            f"Agent: {agent.name}",
            f"Type: {agent.type.value}",
            f"Description: {agent.description}",
        ]
        
        # Add capabilities with enhanced context
        for cap in agent.capabilities:
            parts.append(f"Capability: {cap.name} - {cap.description}")
            
            # Add output type for better matching
            parts.append(f"Output: {cap.output_type}")
            
            # Add examples for semantic richness
            if cap.examples:
                parts.append(f"Examples: {', '.join(cap.examples)}")
            
            # Add parameter context
            if cap.parameters:
                param_names = list(cap.parameters.keys())
                parts.append(f"Parameters: {', '.join(param_names)}")
        
        # Add metadata keywords if present
        if agent.metadata.get("keywords"):
            parts.append(f"Keywords: {', '.join(agent.metadata['keywords'])}")
        
        return " | ".join(parts)
    
    def _find_matched_capabilities(self, agent: AgentRegistration, intent: str) -> List[str]:
        """Find which capabilities match the intent"""
        matched = []
        intent_lower = intent.lower()
        
        for cap in agent.capabilities:
            # Check if capability matches intent
            if any(keyword in intent_lower for keyword in [
                cap.name.lower(),
                cap.description.lower()
            ]):
                matched.append(cap.name)
            
            # Check examples
            for example in cap.examples:
                if any(word in intent_lower for word in example.lower().split()):
                    matched.append(cap.name)
                    break
        
        return list(set(matched))  # Remove duplicates
    
    # ========== A2A Communication Methods ==========
    
    def register_agent_handler(self, agent_id: str, handler):
        """Register a message handler for an agent"""
        self.agent_handlers[agent_id] = handler
        logger.info(f"Registered handler for agent {agent_id}")
    
    async def send_message(self, message: A2AMessage, broadcast_ws: bool = True) -> A2AResponse:
        """Send a message to an agent through A2A protocol"""
        logger.info(f"A2A Message: {message.from_agent} -> {message.to_agent} | {message.action}")
        
        # Add to message history
        self.message_history.append(message)
        
        # Broadcast to WebSocket clients if enabled
        if broadcast_ws:
            try:
                from websocket_manager import ws_manager
                await ws_manager.broadcast_agent_message({
                    "id": message.id or str(uuid.uuid4()),
                    "from_agent": message.from_agent,
                    "to_agent": message.to_agent,
                    "action": message.action,
                    "status": "sent",
                    "payload": message.payload
                })
            except Exception as e:
                logger.error(f"Failed to broadcast message: {e}")
        
        # Check if target agent exists
        agents = await self.list_agents()
        target_agent = next((a for a in agents if a.id == message.to_agent), None)
        
        if not target_agent:
            return A2AResponse(
                success=False,
                error=f"Agent {message.to_agent} not found in registry"
            )
        
        # Check if agent has an endpoint (distributed) or handler (local)
        if hasattr(target_agent, 'endpoint') and target_agent.endpoint:
            # Distributed agent - send via HTTP
            return await self._send_http_message(target_agent, message)
        else:
            # Local agent - use handler
            handler = self.agent_handlers.get(message.to_agent)
            if not handler:
                return A2AResponse(
                    success=False,
                    error=f"Agent {message.to_agent} has no handler registered"
                )
            
            try:
                # Execute the handler
                result = await handler(message)
                
                # Create response
                response = A2AResponse(
                    success=True,
                    result=result,
                    metadata={
                        "agent": target_agent.name,
                        "action": message.action,
                        "timestamp": datetime.now().isoformat()
                    }
                )
                
                # Store response if it's a request
                if message.message_type == MessageType.REQUEST and message.id:
                    self.pending_responses[message.id] = response
                
                return response
                
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                return A2AResponse(
                    success=False,
                    error=str(e),
                    metadata={"agent": target_agent.name}
                )
    
    async def broadcast_message(self, message: A2AMessage, agent_type: Optional[str] = None) -> List[A2AResponse]:
        """Broadcast a message to multiple agents"""
        agents = await self.list_agents()
        
        # Filter by type if specified
        if agent_type:
            agents = [a for a in agents if a.type == agent_type]
        
        responses = []
        for agent in agents:
            if agent.id != message.from_agent:  # Don't send to self
                msg = A2AMessage(
                    from_agent=message.from_agent,
                    to_agent=agent.id,
                    message_type=message.message_type,
                    action=message.action,
                    payload=message.payload,
                    context=message.context
                )
                response = await self.send_message(msg)
                responses.append(response)
        
        return responses
    
    async def orchestrate_agents(self, intent: str, initiator: str = "user") -> Dict[str, Any]:
        """Orchestrate multiple agents based on intent"""
        # Discover relevant agents
        discovery_results = await self.discover_agents(intent)
        
        if not discovery_results:
            return {
                "success": False,
                "error": "No agents found for intent",
                "intent": intent
            }
        
        orchestration_result = {
            "intent": intent,
            "agents_involved": [r.agent.id for r in discovery_results],
            "steps": [],
            "results": {}
        }
        
        # Execute agents in order of relevance
        for discovery in discovery_results:
            agent = discovery.agent
            
            # Determine which capability to use
            if discovery.matched_capabilities:
                capability_name = discovery.matched_capabilities[0]
                capability = next((c for c in agent.capabilities if c.name == capability_name), None)
                
                if capability:
                    # Create message for the agent
                    message = A2AMessage(
                        from_agent=initiator,
                        to_agent=agent.id,
                        message_type=MessageType.REQUEST,
                        action=capability.name,
                        payload={"intent": intent},
                        context={"orchestration": True, "original_intent": intent}
                    )
                    
                    # Send message and get response
                    response = await self.send_message(message)
                    
                    step_info = {
                        "agent": agent.name,
                        "action": capability.name,
                        "success": response.success
                    }
                    
                    if response.success:
                        orchestration_result["results"][agent.id] = response.result
                        step_info["result_preview"] = str(response.result)[:200]
                    else:
                        step_info["error"] = response.error
                    
                    orchestration_result["steps"].append(step_info)
        
        orchestration_result["success"] = any(s["success"] for s in orchestration_result["steps"])
        return orchestration_result
    
    def get_message_history(self, limit: int = 100, agent_id: Optional[str] = None) -> List[A2AMessage]:
        """Get message history, optionally filtered by agent"""
        messages = self.message_history
        
        if agent_id:
            messages = [m for m in messages if m.from_agent == agent_id or m.to_agent == agent_id]
        
        return messages[-limit:]
    
    def get_response(self, correlation_id: str) -> Optional[A2AResponse]:
        """Get a response by correlation ID"""
        return self.pending_responses.get(correlation_id)
    
    async def _send_http_message(self, target_agent: AgentRegistration, message: A2AMessage) -> A2AResponse:
        """Send a message to a distributed agent via HTTP"""
        # Broadcast processing status
        try:
            from websocket_manager import ws_manager
            await ws_manager.broadcast_agent_message({
                "id": message.id or str(uuid.uuid4()),
                "from_agent": message.from_agent,
                "to_agent": message.to_agent,
                "action": message.action,
                "status": "processing",
                "payload": message.payload
            })
        except:
            pass
            
        try:
            # Prepare the endpoint URL
            endpoint = target_agent.endpoint
            if not endpoint.startswith('http'):
                endpoint = f"http://{endpoint}"
            
            # Prepare the message payload
            payload = {
                "from_agent": message.from_agent,
                "action": message.action,
                "payload": message.payload,
                "correlation_id": message.id,
                "message_type": message.message_type.value
            }
            
            # Send HTTP request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{endpoint}/a2a/message",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Check if the agent returned an error
                        if isinstance(result, dict):
                            if result.get("success") is False:
                                # Agent returned an error
                                error_msg = result.get("error", "Unknown error")
                                
                                # Broadcast error
                                try:
                                    from websocket_manager import ws_manager
                                    await ws_manager.broadcast_agent_message({
                                        "id": message.id or str(uuid.uuid4()),
                                        "from_agent": message.from_agent,
                                        "to_agent": message.to_agent,
                                        "action": message.action,
                                        "status": "error",
                                        "result": {"error": error_msg}
                                    })
                                except:
                                    pass
                                
                                return A2AResponse(
                                    success=False,
                                    error=error_msg,
                                    metadata={
                                        "agent": target_agent.name,
                                        "action": message.action,
                                        "error_type": result.get("error_type", "AgentError")
                                    }
                                )
                            else:
                                # Extract the actual result
                                actual_result = result.get("result", result)
                        else:
                            actual_result = result
                        
                        # Broadcast success
                        try:
                            from websocket_manager import ws_manager
                            await ws_manager.broadcast_agent_message({
                                "id": message.id or str(uuid.uuid4()),
                                "from_agent": message.from_agent,
                                "to_agent": message.to_agent,
                                "action": message.action,
                                "status": "completed",
                                "result": actual_result
                            })
                        except:
                            pass
                            
                        return A2AResponse(
                            success=True,
                            result=actual_result,
                            metadata={
                                "agent": target_agent.name,
                                "action": message.action,
                                "timestamp": datetime.now().isoformat()
                            }
                        )
                    else:
                        error_text = await response.text()
                        
                        # Broadcast error
                        try:
                            from websocket_manager import ws_manager
                            await ws_manager.broadcast_agent_message({
                                "id": message.id or str(uuid.uuid4()),
                                "from_agent": message.from_agent,
                                "to_agent": message.to_agent,
                                "action": message.action,
                                "status": "error",
                                "result": {"error": f"HTTP {response.status}: {error_text}"}
                            })
                        except:
                            pass
                            
                        return A2AResponse(
                            success=False,
                            error=f"HTTP {response.status}: {error_text}",
                            metadata={"agent": target_agent.name}
                        )
                        
        except asyncio.TimeoutError:
            return A2AResponse(
                success=False,
                error=f"Timeout sending message to {target_agent.name}",
                metadata={"agent": target_agent.name}
            )
        except Exception as e:
            logger.error(f"Error sending HTTP message to {target_agent.name}: {e}")
            return A2AResponse(
                success=False,
                error=str(e),
                metadata={"agent": target_agent.name}
            )

    async def update_agent(self, agent_id: str, agent_data: dict) -> bool:
        """Update an existing agent's information"""
        try:
            # Update in ChromaDB
            collection = self.client.get_collection(name="agents")
            
            # Get existing agent
            existing = collection.get(ids=[agent_id])
            if not existing['ids']:
                logger.warning(f"Agent {agent_id} not found for update")
                return False
            
            # Update metadata
            collection.update(
                ids=[agent_id],
                metadatas=[agent_data],
                documents=[agent_data.get('description', '')]
            )
            
            # Update in memory
            self.agents[agent_id] = agent_data
            
            logger.info(f"Agent updated: {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating agent {agent_id}: {e}")
            return False

    async def get_agent(self, agent_id: str) -> dict:
        """Get a specific agent by ID"""
        try:
            return self.agents.get(agent_id)
        except Exception as e:
            logger.error(f"Error getting agent {agent_id}: {e}")
            return None

    async def unregister_agent(self, agent_id: str) -> bool:
        """Remove an agent from the registry"""
        try:
            # Remove from ChromaDB
            collection = self.client.get_collection(name="agents")
            collection.delete(ids=[agent_id])
            
            # Remove from memory
            if agent_id in self.agents:
                del self.agents[agent_id]
            
            logger.info(f"Agent unregistered: {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error unregistering agent {agent_id}: {e}")
            return False