"""Base agent class with MCP support and A2A communication"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging
from mcp.schemas import MCPTool, ToolResult, ToolParameter
from mcp.tool_registry import MCPToolRegistry
from llm import LLMClient, LLMConfig
from registry.models import A2AMessage, MessageType

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all agents with MCP tool support"""
    
    def __init__(self, agent_id: str, name: str, description: str, llm_config: Optional[LLMConfig] = None):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.tools: Dict[str, MCPTool] = {}
        
        # Initialize LLM client with Claude 3.5 Sonnet by default
        self.llm_config = llm_config or LLMConfig(
            provider="anthropic",
            model="claude-3-5-sonnet-20241022",
            temperature=0.7
        )
        self.llm = LLMClient(self.llm_config)
        
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
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> ToolResult:
        """Execute a tool by name"""
        if tool_name not in self.tools:
            return ToolResult(
                success=False,
                error=f"Tool '{tool_name}' not found in {self.name}"
            )
        
        try:
            executor = getattr(self, f"_execute_{tool_name}", None)
            if not executor:
                return ToolResult(
                    success=False,
                    error=f"No executor found for tool '{tool_name}'"
                )
            
            result = await executor(parameters)
            return ToolResult(
                success=True,
                result=result,
                metadata={
                    "agent": self.name,
                    "tool": tool_name
                }
            )
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return ToolResult(
                success=False,
                error=str(e),
                metadata={
                    "agent": self.name,
                    "tool": tool_name
                }
            )
    
    async def handle_a2a_message(self, message: A2AMessage) -> Any:
        """Handle incoming A2A messages"""
        logger.info(f"{self.name} received A2A message: {message.action}")
        
        # If it's a tool execution request, execute the tool
        if message.action in self.tools:
            result = await self.execute_tool(message.action, message.payload)
            return result.result if result.success else {"error": result.error}
        
        # Handle other message types
        if message.message_type == MessageType.NOTIFICATION:
            logger.info(f"{self.name} received notification: {message.payload}")
            return {"acknowledged": True}
        
        return {"error": f"Unknown action: {message.action}"}
    
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