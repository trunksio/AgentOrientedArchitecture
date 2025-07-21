from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime
from enum import Enum
import uuid

class AgentType(str, Enum):
    DATA = "data"
    VISUALIZATION = "visualization"
    RESEARCH = "research"
    NARRATIVE = "narrative"
    PREDICTION = "prediction"
    GUI = "gui"
    CUSTOM = "custom"

class AgentCapability(BaseModel):
    name: str = Field(..., description="Capability name")
    description: str = Field(..., description="What the capability does")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Required parameters")
    output_type: str = Field(..., description="Type of output (e.g., 'chart', 'text', 'table')")
    examples: List[str] = Field(default_factory=list, description="Example queries this handles")

class AgentStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    STARTING = "starting"

class AgentRegistration(BaseModel):
    id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Human-readable agent name")
    type: AgentType = Field(..., description="Type of agent")
    description: str = Field(..., description="What the agent does")
    capabilities: List[AgentCapability] = Field(..., description="List of capabilities")
    endpoint: str = Field(..., description="API endpoint for the agent")
    version: str = Field(default="1.0.0", description="Agent version")
    status: AgentStatus = Field(default=AgentStatus.ACTIVE, description="Agent status")
    registered_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class DiscoveryQuery(BaseModel):
    intent: str = Field(..., description="User's intent or query")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")
    max_results: int = Field(default=5, description="Maximum number of agents to return")

class DiscoveryResult(BaseModel):
    agent: AgentRegistration
    relevance_score: float = Field(..., description="Semantic similarity score")
    matched_capabilities: List[str] = Field(..., description="Which capabilities matched")

class MessageType(str, Enum):
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"

class A2AMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique message ID")
    from_agent: str = Field(..., description="Sender agent ID")
    to_agent: str = Field(..., description="Recipient agent ID")
    message_type: MessageType = Field(..., description="Type of message")
    action: str = Field(..., description="Action to perform or tool to execute")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Message payload")
    context: Dict[str, Any] = Field(default_factory=dict, description="Message context")
    correlation_id: Optional[str] = Field(None, description="For request-response correlation")
    timestamp: datetime = Field(default_factory=datetime.now)

class A2AResponse(BaseModel):
    success: bool = Field(..., description="Whether the operation succeeded")
    result: Optional[Any] = Field(None, description="Operation result")
    error: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict)