"""Standard schemas for agent interfaces"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

class HealthStatus(str, Enum):
    """Health status values"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class ToolParameter(BaseModel):
    """MCP tool parameter schema"""
    name: str
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None

class ToolDefinition(BaseModel):
    """MCP tool definition"""
    name: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    returns: Optional[str] = None
    examples: Optional[List[str]] = None

class AgentMetadata(BaseModel):
    """Agent metadata"""
    llm_model: str
    semantic_tool_selection: bool = True
    version: str = "1.0.0"
    custom_fields: Dict[str, Any] = Field(default_factory=dict)

class AgentCardResponse(BaseModel):
    """Response schema for /agent-card endpoint"""
    agent_id: str
    name: str
    description: str
    capabilities: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    tools: List[Dict[str, str]] = Field(default_factory=list)
    status: Dict[str, Any]
    metadata: AgentMetadata

class HealthResponse(BaseModel):
    """Response schema for /health endpoint"""
    status: HealthStatus
    uptime_seconds: int
    request_count: int = 0
    error_count: int = 0
    error_rate: float = 0.0
    last_error: Optional[str] = None
    llm_available: bool = True
    registration_status: Optional[str] = None  # pending, registered, failed
    registration_attempts: Optional[int] = None
    registration_error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class MCPToolsResponse(BaseModel):
    """Response schema for /mcp/tools endpoint"""
    tools: List[ToolDefinition]
    agent_id: str
    agent_name: str

class MCPExecuteRequest(BaseModel):
    """Request schema for /mcp/execute/{tool_name}"""
    parameters: Dict[str, Any] = Field(default_factory=dict)
    context: Optional[Dict[str, Any]] = None

class MCPExecuteResponse(BaseModel):
    """Response schema for /mcp/execute/{tool_name}"""
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class A2AMessageRequest(BaseModel):
    """Request schema for A2A message handling"""
    from_agent: str
    to_agent: str
    action: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    message_type: str = "REQUEST"
    context: Optional[Dict[str, Any]] = None

class A2AMessageResponse(BaseModel):
    """Response schema for A2A message handling"""
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    tools_used: Optional[List[str]] = None
    semantic_selection: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    error_type: Optional[str] = None
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)