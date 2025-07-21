"""Unified base agent class with MCP support, A2A communication, and standard interfaces"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
import logging
import json
from datetime import datetime
from .mcp.schemas import MCPTool, ToolResult, ToolParameter
from .mcp.tool_registry import MCPToolRegistry
from .llm import LLMClient, LLMConfig
from .models import A2AMessage, MessageType

logger = logging.getLogger(__name__)

class UnifiedBaseAgent(ABC):
    """Unified base class for all agents with MCP tool support, semantic selection, and standard interfaces"""
    
    def __init__(self, agent_id: str, name: str, description: str, 
                 capabilities: List[str] = None, tags: List[str] = None,
                 llm_config: Optional[LLMConfig] = None):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.capabilities = capabilities or []
        self.tags = tags or []
        self.tools: Dict[str, MCPTool] = {}
        
        # Initialize LLM client with Claude 3.7 Sonnet by default
        self.llm_config = llm_config or LLMConfig(
            provider="anthropic",
            model="claude-3-7-sonnet-20250219",
            temperature=0.7
        )
        self.llm = LLMClient(self.llm_config)
        
        # Enable semantic tool selection by default
        self.semantic_tool_selection = True
        
        # Health tracking
        self._startup_time = datetime.utcnow()
        self._request_count = 0
        self._error_count = 0
        self._last_error = None
        
        self._register_tools()
        
        # A2A Registry will be set by agent manager
        self.a2a_registry = None
    
    @abstractmethod
    def _register_tools(self):
        """Register MCP tools for this agent"""
        pass
    
    def register_tool(self, tool: MCPTool, executor):
        """Register a tool with its executor"""
        self.tools[tool.name] = tool
        setattr(self, f"_execute_{tool.name}", executor)
    
    def get_agent_card(self) -> Dict[str, Any]:
        """Get agent metadata card for discovery"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "tags": self.tags,
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description
                } for tool in self.tools.values()
            ],
            "status": self.get_health_status(),
            "metadata": {
                "llm_model": self.llm_config.model,
                "semantic_tool_selection": self.semantic_tool_selection,
                "version": "1.0.0"
            }
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get agent health status"""
        uptime_seconds = (datetime.utcnow() - self._startup_time).total_seconds()
        error_rate = self._error_count / self._request_count if self._request_count > 0 else 0
        
        status = "healthy"
        if error_rate > 0.1:
            status = "degraded"
        if error_rate > 0.5:
            status = "unhealthy"
        
        return {
            "status": status,
            "uptime_seconds": int(uptime_seconds),
            "request_count": self._request_count,
            "error_count": self._error_count,
            "error_rate": error_rate,
            "last_error": self._last_error,
            "llm_available": self.llm.is_available() if hasattr(self.llm, 'is_available') else True
        }
    
    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """Get MCP tool definitions"""
        return [
            {
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
            }
            for tool in self.tools.values()
        ]
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> ToolResult:
        """Execute a tool by name"""
        self._request_count += 1
        
        if tool_name not in self.tools:
            self._error_count += 1
            self._last_error = f"Tool '{tool_name}' not found"
            return ToolResult(
                success=False,
                error=self._last_error
            )
        
        try:
            executor = getattr(self, f"_execute_{tool_name}", None)
            if not executor:
                self._error_count += 1
                self._last_error = f"No executor found for tool '{tool_name}'"
                return ToolResult(
                    success=False,
                    error=self._last_error
                )
            
            result = await executor(parameters)
            return ToolResult(
                success=True,
                result=result,
                metadata={
                    "agent": self.name,
                    "tool": tool_name,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            logger.error(f"Error executing tool {tool_name}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return ToolResult(
                success=False,
                error=str(e),
                metadata={
                    "agent": self.name,
                    "tool": tool_name,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
    
    async def select_tools_for_query(self, query: str, context: Dict[str, Any] = None) -> List[Tuple[str, Dict[str, Any]]]:
        """Use LLM to select appropriate tools for a query"""
        if not self.semantic_tool_selection:
            return await self._fallback_tool_selection(query, context)
        
        # Prepare tool information
        tools_info = []
        for tool_name, tool in self.tools.items():
            tool_info = {
                "name": tool_name,
                "description": tool.description,
                "parameters": [
                    {
                        "name": p.name,
                        "type": p.type.value,
                        "description": p.description,
                        "required": p.required
                    } for p in tool.parameters
                ],
                "examples": tool.examples if tool.examples else []
            }
            tools_info.append(tool_info)
        
        prompt = f"""Analyze this query and determine which tools to use and in what order:

Query: "{query}"
Context: {json.dumps(context or {}, indent=2)}

Available tools:
{json.dumps(tools_info, indent=2)}

Consider:
1. What the user is trying to achieve
2. Which tools are needed to fulfill the request
3. The optimal order of tool execution
4. What parameters each tool needs

Respond with a JSON array of tool executions:
[
    {{
        "tool": "tool_name",
        "parameters": {{}},
        "purpose": "why this tool is needed",
        "depends_on": [] // list of previous tool indices this depends on
    }}
]

If no tools match, return an empty array with explanation."""

        system_prompt = f"""You are {self.name}, an intelligent agent that can analyze queries and select appropriate tools.
You understand user intent and know how to combine tools effectively to achieve goals.
Be precise with parameter extraction and tool selection."""

        try:
            tool_plan = await self.llm.generate_json(prompt, system_prompt)
            
            if isinstance(tool_plan, list):
                # Convert to the expected format
                selected_tools = []
                for item in tool_plan:
                    if isinstance(item, dict) and "tool" in item:
                        selected_tools.append((
                            item["tool"],
                            item.get("parameters", {})
                        ))
                return selected_tools
            
        except Exception as e:
            logger.error(f"Error in semantic tool selection: {e}")
        
        # Fallback if LLM fails
        return await self._fallback_tool_selection(query, context)
    
    async def _fallback_tool_selection(self, query: str, context: Dict[str, Any] = None) -> List[Tuple[str, Dict[str, Any]]]:
        """Fallback tool selection using keyword matching"""
        query_lower = query.lower()
        selected_tools = []
        
        # Match tools based on keywords in their names or descriptions
        for tool_name, tool in self.tools.items():
            tool_keywords = tool_name.lower().split('_') + tool.description.lower().split()
            if any(keyword in query_lower for keyword in tool_keywords if len(keyword) > 3):
                # Add tool with minimal parameters from context
                selected_tools.append((tool_name, context or {}))
        
        return selected_tools
    
    async def execute_tool_sequence(self, tool_sequence: List[Tuple[str, Dict[str, Any]]]) -> List[ToolResult]:
        """Execute a sequence of tools"""
        results = []
        
        for tool_name, parameters in tool_sequence:
            # Check if parameters reference previous results
            if "_previous_result" in parameters and results:
                # Inject previous result into parameters
                parameters["previous_result"] = results[-1].result if results[-1].success else None
            
            result = await self.execute_tool(tool_name, parameters)
            results.append(result)
            
            # Stop on failure unless specified otherwise
            if not result.success and parameters.get("continue_on_error", False) is False:
                break
        
        return results
    
    async def handle_a2a_message(self, message: A2AMessage) -> Any:
        """Handle incoming A2A messages with enhanced semantic understanding"""
        logger.info(f"{self.name} received A2A message: {message.action}")
        self._request_count += 1
        
        try:
            # Check if this is a semantic query that needs tool selection
            if self.semantic_tool_selection and message.action in ["query", "analyze", "process", "handle"]:
                return await self._handle_semantic_query(message)
            
            # If it's a tool execution request, execute the tool
            if message.action in self.tools:
                logger.info(f"{self.name} executing tool: {message.action}")
                result = await self.execute_tool(message.action, message.payload)
                
                if result.success:
                    logger.info(f"{self.name} tool execution successful")
                    return result.result
                else:
                    logger.error(f"{self.name} tool execution failed: {result.error}")
                    return {"error": result.error, "tool": message.action}
            
            # Handle intent-based requests
            if message.action == "handle_intent":
                logger.info(f"{self.name} handling intent: {message.payload.get('intent', 'unknown')}")
                return await self.handle_intent(message.payload)
            
            # Check for action variations
            action_lower = message.action.lower()
            
            # Map common action names to tools
            action_mappings = {
                "query": "query_data",
                "analyze": "analyze_data",
                "visualize": "create_visualization",
                "chart": "create_chart",
                "research": "search_insights",
                "narrate": "generate_narrative",
                "story": "create_story"
            }
            
            # Try mapped action
            for key, tool_name in action_mappings.items():
                if key in action_lower and tool_name in self.tools:
                    logger.info(f"{self.name} mapping action '{message.action}' to tool '{tool_name}'")
                    result = await self.execute_tool(tool_name, message.payload)
                    return result.result if result.success else {"error": result.error}
            
            # Handle other message types
            if message.message_type == MessageType.NOTIFICATION:
                logger.info(f"{self.name} received notification: {message.payload}")
                return {"acknowledged": True}
            
            # Last resort: try to understand the action with LLM
            if self.semantic_tool_selection:
                logger.info(f"{self.name} using LLM to understand action: {message.action}")
                intent_payload = {
                    "intent": message.action,
                    "context": message.payload
                }
                return await self.handle_intent(intent_payload)
            
            logger.warning(f"{self.name} doesn't know how to handle action: {message.action}")
            return {
                "error": f"Unknown action: {message.action}",
                "available_actions": list(self.tools.keys()) + ["handle_intent"]
            }
            
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            logger.error(f"{self.name} error handling A2A message: {type(e).__name__}: {e}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            
            return {
                "error": f"Error handling message: {str(e)}",
                "error_type": type(e).__name__,
                "agent": self.name
            }
    
    async def _handle_semantic_query(self, message: A2AMessage) -> Any:
        """Handle queries using semantic tool selection"""
        query = message.payload.get("query", message.payload.get("intent", message.action))
        context = message.payload
        
        # Select tools for the query
        tool_sequence = await self.select_tools_for_query(query, context)
        
        if not tool_sequence:
            return {
                "error": "No appropriate tools found for this query",
                "query": query,
                "available_tools": list(self.tools.keys())
            }
        
        # Execute the tool sequence
        results = await self.execute_tool_sequence(tool_sequence)
        
        # Aggregate results
        successful_results = []
        errors = []
        
        for i, (result, (tool_name, _)) in enumerate(zip(results, tool_sequence)):
            if result.success:
                successful_results.append({
                    "tool": tool_name,
                    "result": result.result
                })
            else:
                errors.append({
                    "tool": tool_name,
                    "error": result.error
                })
        
        return {
            "query": query,
            "tool_sequence": [t[0] for t in tool_sequence],
            "results": successful_results,
            "errors": errors,
            "semantic_selection": True
        }
    
    async def handle_intent(self, intent_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle intent-based requests using LLM to determine the best tool"""
        intent = intent_payload.get("intent", "")
        context = intent_payload.get("context", {})
        
        if not self.semantic_tool_selection:
            # Fallback to simple keyword matching
            return await self._handle_intent_fallback(intent, context)
        
        # Use semantic tool selection
        tool_sequence = await self.select_tools_for_query(intent, context)
        
        if tool_sequence:
            # Execute the selected tools
            results = await self.execute_tool_sequence(tool_sequence)
            
            # Return aggregated results
            if results and results[0].success:
                return {
                    "success": True,
                    "tools_used": [t[0] for t in tool_sequence],
                    "results": [r.result for r in results if r.success],
                    "method": "semantic_selection"
                }
            else:
                return {
                    "success": False,
                    "error": results[0].error if results else "No tools executed",
                    "tools_attempted": [t[0] for t in tool_sequence]
                }
        else:
            return {
                "success": False,
                "error": "Could not determine appropriate tools",
                "intent": intent,
                "available_tools": list(self.tools.keys())
            }
    
    async def _handle_intent_fallback(self, intent: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback intent handling using keyword matching"""
        intent_lower = intent.lower()
        
        # Try to match intent to tools based on keywords
        for tool_name, tool in self.tools.items():
            tool_keywords = tool_name.lower().split('_') + tool.description.lower().split()
            if any(keyword in intent_lower for keyword in tool_keywords):
                # Try to execute with minimal parameters
                try:
                    result = await self.execute_tool(tool_name, context)
                    if result.success:
                        return {
                            "success": True,
                            "tool_used": tool_name,
                            "result": result.result,
                            "method": "keyword_matching"
                        }
                except Exception as e:
                    logger.error(f"Fallback execution failed: {e}")
        
        return {
            "success": False,
            "error": "Could not match intent to any available tool",
            "intent": intent,
            "available_tools": list(self.tools.keys())
        }
    
    async def explain_decision(self, decision_type: str, decision_data: Dict[str, Any]) -> str:
        """Explain why a particular decision was made"""
        if not self.semantic_tool_selection:
            return f"{decision_type} decision made based on available data"
        
        prompt = f"""Explain this {decision_type} decision:

Decision Data: {json.dumps(decision_data, indent=2)}

Provide a clear, concise explanation of:
1. What was decided
2. Why this decision was made
3. What alternatives were considered
4. Any relevant context

Keep it under 100 words."""

        try:
            explanation = await self.llm.generate(prompt)
            return explanation
        except:
            return f"{decision_type} decision made based on analysis"
    
    async def send_a2a_message(self, to_agent: str, action: str, payload: Dict[str, Any], 
                              message_type: MessageType = MessageType.REQUEST) -> Optional[Any]:
        """Send a message to another agent via A2A"""
        if not self.a2a_registry:
            logger.error("A2A Registry not initialized")
            return None
        
        message = A2AMessage(
            from_agent=self.agent_id,
            to_agent=to_agent,
            message_type=message_type,
            action=action,
            payload=payload
        )
        
        response = await self.a2a_registry.send_message(message)
        return response.result if response.success else None
    
    def get_tools(self) -> List[MCPTool]:
        """Get all tools for this agent"""
        return list(self.tools.values())
    
    def get_tool_info(self) -> List[Dict[str, Any]]:
        """Get tool information for discovery"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "agent": self.name,
                "agent_id": self.agent_id,
                "parameters": [param.model_dump() for param in tool.parameters],
                "returns": tool.returns,
                "examples": tool.examples
            }
            for tool in self.tools.values()
        ]