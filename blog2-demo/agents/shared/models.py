"""Simplified models for agent communication"""
from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime

class MessageType(str, Enum):
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"

class A2AMessage(BaseModel):
    """Message structure for agent-to-agent communication"""
    from_agent: str
    to_agent: str
    message_type: MessageType = MessageType.REQUEST
    action: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    correlation_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class A2AResponse(BaseModel):
    """Response structure for A2A messages"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)