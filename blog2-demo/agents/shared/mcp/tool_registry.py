from typing import Dict, List, Any, Callable, Optional
import asyncio
from .schemas import MCPTool, ToolExecution, ToolResult, ToolParameter

class MCPToolRegistry:
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self.executors: Dict[str, Callable] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default MCP tools"""
        # Example tool for testing
        self.register_tool(
            MCPTool(
                name="echo",
                description="Echo back the input message",
                parameters=[
                    ToolParameter(
                        name="message",
                        type="string",
                        description="Message to echo",
                        required=True
                    )
                ],
                returns={"type": "string", "description": "The echoed message"},
                examples=[{"parameters": {"message": "Hello"}, "result": "Hello"}]
            ),
            self._echo_executor
        )
    
    async def _echo_executor(self, parameters: Dict[str, Any]) -> Any:
        """Simple echo executor for testing"""
        return parameters.get("message", "")
    
    def register_tool(self, tool: MCPTool, executor: Callable):
        """Register a new MCP tool"""
        self.tools[tool.name] = tool
        self.executors[tool.name] = executor
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List all available MCP tools"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": [param.model_dump() for param in tool.parameters],
                "returns": tool.returns,
                "examples": tool.examples
            }
            for tool in self.tools.values()
        ]
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> ToolResult:
        """Execute an MCP tool"""
        try:
            if tool_name not in self.tools:
                return ToolResult(
                    success=False,
                    error=f"Tool '{tool_name}' not found"
                )
            
            tool = self.tools[tool_name]
            executor = self.executors[tool_name]
            
            # Validate parameters
            validation_error = self._validate_parameters(tool, parameters)
            if validation_error:
                return ToolResult(
                    success=False,
                    error=validation_error
                )
            
            # Execute the tool
            if asyncio.iscoroutinefunction(executor):
                result = await executor(parameters)
            else:
                result = executor(parameters)
            
            return ToolResult(
                success=True,
                result=result,
                metadata={"tool": tool_name}
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                metadata={"tool": tool_name}
            )
    
    def _validate_parameters(self, tool: MCPTool, parameters: Dict[str, Any]) -> Optional[str]:
        """Validate tool parameters"""
        for param in tool.parameters:
            if param.required and param.name not in parameters:
                return f"Missing required parameter: {param.name}"
            
            if param.name in parameters:
                value = parameters[param.name]
                
                # Type validation (simplified)
                if param.type == "string" and not isinstance(value, str):
                    return f"Parameter '{param.name}' must be a string"
                elif param.type == "number" and not isinstance(value, (int, float)):
                    return f"Parameter '{param.name}' must be a number"
                elif param.type == "boolean" and not isinstance(value, bool):
                    return f"Parameter '{param.name}' must be a boolean"
                
                # Enum validation
                if param.enum and value not in param.enum:
                    return f"Parameter '{param.name}' must be one of: {param.enum}"
        
        return None