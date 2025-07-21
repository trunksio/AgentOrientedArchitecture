from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Callable
from enum import Enum

class ParameterType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"

class ToolParameter(BaseModel):
    name: str = Field(..., description="Parameter name")
    type: ParameterType = Field(..., description="Parameter type")
    description: str = Field(..., description="Parameter description")
    required: bool = Field(default=True, description="Is this parameter required")
    default: Optional[Any] = Field(default=None, description="Default value if not required")
    enum: Optional[List[Any]] = Field(default=None, description="Allowed values")

class MCPTool(BaseModel):
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="What the tool does")
    parameters: List[ToolParameter] = Field(default_factory=list, description="Tool parameters")
    returns: Dict[str, Any] = Field(..., description="Return type description")
    examples: List[Dict[str, Any]] = Field(default_factory=list, description="Usage examples")
    
    class Config:
        arbitrary_types_allowed = True

class ToolExecution(BaseModel):
    tool: str = Field(..., description="Tool name to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters to pass")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Execution context")

class ToolResult(BaseModel):
    success: bool = Field(..., description="Whether execution succeeded")
    result: Optional[Any] = Field(default=None, description="Execution result")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")