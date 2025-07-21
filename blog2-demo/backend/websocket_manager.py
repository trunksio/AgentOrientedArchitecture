"""WebSocket Manager for broadcasting agent communication"""
from typing import List, Dict, Any
import json
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept and store a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast_agent_message(self, message_data: Dict[str, Any]):
        """Broadcast agent message to all connected clients"""
        if not self.active_connections:
            return
        
        # Prepare the message
        ws_message = {
            "type": "agent_message",
            "id": message_data.get("id"),
            "from_agent": message_data.get("from_agent"),
            "to_agent": message_data.get("to_agent"),
            "action": message_data.get("action"),
            "status": message_data.get("status", "sent"),
            "payload": message_data.get("payload"),
            "result": message_data.get("result")
        }
        
        # Send to all connected clients
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(ws_message)
            except Exception as e:
                logger.error(f"Error sending to WebSocket: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            self.disconnect(conn)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)

# Global instance
ws_manager = WebSocketManager()